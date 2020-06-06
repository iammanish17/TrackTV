from django.shortcuts import render, redirect
import requests
from random import shuffle
from bs4 import BeautifulSoup
from .models import Show, UserRating
from django.contrib.auth.models import User
from django.core.paginator import Paginator


def home(request):
    shows = list(Show.objects.all())
    shuffle(shows)
    return render(request, 'tv/home.html', {'shows': shows[:5]})


def about(request):
    return render(request, 'tv/about.html', {'title': "About"})


def search(request, query: str = ""):
    if request.method == 'POST' and 'query' in request.POST:
        query = request.POST['query']
    if not query:
        return render(request, 'tv/search.html')
    url = "http://api.tvmaze.com/search/shows?q=%s" % query
    resp = requests.get(url).json()
    if not resp:
        return render(request, 'tv/search.html', {'query': query})
    else:
        for each in resp:
            if each["show"]["summary"]:
                each["show"]["summary"] = BeautifulSoup(each["show"]["summary"], "lxml").text
            if not each["show"]["image"]:
                each["show"]["image"] = {"original": "/static/tv/default.png"}
        context = {
            'results': resp,
            'query': query,
            'title': "Search"
        }
        return render(request, 'tv/search.html', context)


def showlist(request, username: str = ""):
    if not username:
        return redirect('tv-home')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('tv-home')
    sort_type = request.GET.get('sort')
    if not sort_type or not sort_type.isdigit():
        sort_type = 1
    sort_type = int(sort_type)
    if sort_type == 2:
        results = UserRating.objects.filter(user=user).order_by('pk')
    elif sort_type == 3:
        results = UserRating.objects.filter(user=user).order_by('-rating')
    elif sort_type == 4:
        results = UserRating.objects.filter(user=user).order_by('rating')
    else:
        results = UserRating.objects.filter(user=user).order_by('-pk')
    paginator = Paginator(results, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    for result in page_obj:
        result.show.genres = result.show.genres.split(",")
    return render(request, 'tv/list.html', {'username': username,
                                            'title': f"{username}'s list",
                                            'page_obj': page_obj,
                                            'total': paginator.count,
                                            'sort_type': sort_type})


def show(request, showid: int = 0):
    if not showid:
        return redirect('tv-home')
    url = f"http://api.tvmaze.com/shows/{showid}"
    resp = requests.get(url).json()
    if resp['status'] == 404:
        return redirect('tv-show')
    if resp["summary"]:
        resp["summary"] = BeautifulSoup(resp["summary"], "lxml").text
    if not resp["image"]:
        resp["image"] = {"original": "/static/tv/default.png"}

    if request.user.is_authenticated:
        try:
            sh = Show.objects.get(showid=showid)
            sh.image = resp['image']['original']
            sh.status = resp['status']
            sh.genres = ','.join(resp['genres'])
            sh.name = resp['name']
            sh.save()
        except Show.DoesNotExist:
            sh = Show.objects.create(showid=showid,
                                     image=resp['image']['original'],
                                     status=resp['status'],
                                     genres=','.join(resp['genres']),
                                     name=resp['name'])

        if request.method == 'POST':
            if "rating" in request.POST:
                value = int(request.POST['rating'])
                if value == 0:
                    UserRating.objects.get(show=sh, user=request.user).delete()
                    return render(request, 'tv/show.html', {'show': resp, 'title': resp['name'], 
                                                            'watched': False, 'rating': 0})
                else:
                    try:
                        ur = UserRating.objects.get(show=sh, user=request.user)
                    except UserRating.DoesNotExist:
                        ur = UserRating(show=sh, user=request.user)
                    ur.rating = value
                    ur.save()
                    return render(request, 'tv/show.html', {'show': resp, 'title': resp['name'],  'watched': True,
                                                            'rating': value,
                                                            'position': ur.position})
            if "#" in request.POST:
                try:
                    value = int(request.POST['#'])
                except ValueError:
                    value = 0
                try:
                    ur = UserRating.objects.get(user=request.user, position=value)
                    ur.position = 0
                    ur.save()
                except UserRating.DoesNotExist:
                    pass
                ur = UserRating.objects.get(show=sh, user=request.user)
                ur.position = value
                ur.save()
                return render(request, 'tv/show.html', {'show': resp, 'title': resp['name'],  'watched': True,
                                                        'rating': ur.rating,
                                                        'position': ur.position})

    if not request.user.is_authenticated:
        return render(request, 'tv/show.html', {'show': resp, 'title': resp['name'],  "watched": False, "rating": 0})

    try:
        ur = UserRating.objects.get(show=Show.objects.get(showid=showid), user=request.user)
        return render(request, 'tv/show.html', {'show': resp, 'title': resp['name'],  'watched': True,
                                                'rating': ur.rating,
                                                'position': ur.position})
    except UserRating.DoesNotExist:
        return render(request, 'tv/show.html', {'show': resp, 'title': resp['name'],  "watched": False, "rating": 0})
