from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import AccountRegisterForm, RoleLoginForm


def _redirect_for_user(request, user):
    # Cek apakah ada parameter 'next' di URL
    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url:
        return redirect(next_url)

    # Redirect default berdasarkan peran pengguna
    if user.is_asisten:
        return redirect('schedule:list')
    return redirect('schedule:list')


def login_view(request):
    if request.user.is_authenticated:
        return _redirect_for_user(request, request.user)

    form = RoleLoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = authenticate(
            request,
            role=form.cleaned_data['role'],
            identifier=form.cleaned_data['identifier'],
            password=form.cleaned_data['password'],
        )

        if user is not None:
            login(request, user)
            messages.success(request, 'Login berhasil.')
            return _redirect_for_user(request, user)

        messages.error(request, 'Login gagal. Periksa role, NPM/ID, dan password.')

    return render(request, 'authentication/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return _redirect_for_user(request, request.user)

    form = AccountRegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Akun berhasil dibuat. Silakan login.')
        return redirect('authentication:login')

    return render(request, 'authentication/register.html', {'form': form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'Kamu sudah logout.')
    return redirect('authentication:login')