from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.models import User
from tv.models import UserRating

# Create your views here.


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Successfully registered, {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form, 'title': 'Register'})


def profile(request, username: str = ""):
    if not username:
        return redirect('tv-home')
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('tv-home')

    uo = UserRating.objects.filter(user=user).order_by('-pk')
    top = [False]*5
    recent = []
    total = len(uo)
    average, ongoing, ended = 0, 0, 0
    count = 0
    for ur in uo:
        count += 1
        if count <= 5:
            recent += [ur]
        average += ur.rating
        if ur.position:
            top[ur.position-1] = ur.show
        if ur.show.status == "Running":
            ongoing += 1
        if ur.show.status == "Ended":
            ended += 1
    if total:
        average = round(average/total, 2)

    return render(request, 'users/profile.html',
                  {'username': username,
                   'title': f"{username}'s Profile",
                   'recent': recent,
                   'top1': top[0],
                   'top2': top[1],
                   'top3': top[2],
                   'top4': top[3],
                   'top5': top[4],
                   'average': average,
                   'ongoing': ongoing,
                   'ended': ended,
                   'total': total})
