from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from accounts.forms import UserLoginForm, UserRegistrationForm, UserUpdateForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout, login

def login_view(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        data = form.cleaned_data
        email = data.get('email')
        password = data.get('password')
        user = authenticate(request, email=email, password=password)
        login(request, user)
        return redirect('home')
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def register_view(request):
    form = UserRegistrationForm(request.POST or None)
    if form.is_valid():
        new_user = form.save(commit=False)
        new_user.set_password(form.cleaned_data['password'])
        new_user.save()

        u_email = form.cleaned_data.get('email')
        u_password = form.cleaned_data['password']

        user = authenticate(email=u_email,
                            password=u_password)
        login(request, user)
        return render(request, 'app/home.html',
                      {'new_user': new_user})
        #return render(request, 'accounts/register_done.html', {'new_user': new_user})
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            form = UserUpdateForm(request.POST, instance=user)
            if form.is_valid():
                user.save()
                return redirect('accounts:profile')
        else:
            form = UserUpdateForm(instance=user)
        return render(request, 'accounts/profile.html', {'form': form})
    else:
        return redirect('accounts:login')
