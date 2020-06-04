from django.shortcuts import render, redirect
import requests
from bs4 import BeautifulSoup
from .models import Show, UserRating
from django.contrib.auth.models import User


def home(request):
    return render(request, 'tv/home.html')


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
            'query': query
        }
        return render(request, 'tv/search.html', context)


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
                    return render(request, 'tv/show.html', {'show': resp, 'watched': False, 'rating': 0})
                else:
                    try:
                        ur = UserRating.objects.get(show=sh, user=request.user)
                    except UserRating.DoesNotExist:
                        ur = UserRating(show=sh, user=request.user)
                    ur.rating = value
                    ur.save()
                    return render(request, 'tv/show.html', {'show': resp, 'watched': True, 'rating': value,
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
                return render(request, 'tv/show.html', {'show': resp, 'watched': True, 'rating': ur.rating,
                                                        'position': ur.position})

    if not request.user.is_authenticated:
        return render(request, 'tv/show.html', {'show': resp, "watched": False, "rating": 0})

    try:
        ur = UserRating.objects.get(show=Show.objects.get(showid=showid), user=request.user)
        return render(request, 'tv/show.html', {'show': resp, 'watched': True, 'rating': ur.rating,
                                                'position': ur.position})
    except UserRating.DoesNotExist:
        return render(request, 'tv/show.html', {'show': resp, "watched": False, "rating": 0})
