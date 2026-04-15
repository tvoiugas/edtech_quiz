from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.contrib.auth.models import User
from quiz.models import UserProfile, QuizSession


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=False, label='Имя')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password1', 'password2']


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            import random
            colors = ['#6366f1', '#8b5cf6', '#ec4899', '#14b8a6', '#f59e0b', '#10b981']
            UserProfile.objects.create(user=user, avatar_color=random.choice(colors))
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверный логин или пароль.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    sessions = QuizSession.objects.filter(user=request.user, status='completed').select_related('category')[:20]
    level, level_icon = profile.get_level()
    
    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        github = request.POST.get('github_url', '')
        profile.bio = bio[:200]
        profile.github_url = github
        profile.save()
        
        first_name = request.POST.get('first_name', '')
        request.user.first_name = first_name
        request.user.save()
        messages.success(request, 'Профиль обновлён!')
        return redirect('profile')
    
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'sessions': sessions,
        'level': level,
        'level_icon': level_icon,
    })
