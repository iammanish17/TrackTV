from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from django.contrib.auth.models import User

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
    return render(request, 'users/register.html', {'form': form})


def profile(request, user: str = ""):
    if not user:
        if request.user.is_authenticated:
            return render(request, 'users/profile.html', {'user': request.user})
        else:
            return redirect('login')
    try:
        user = User.objects.get(username=user)
    except User.DoesNotExist:
        return render(request, 'users/profile.html', {'user': None})
    return render(request, 'users/profile.html', {'user': user})
