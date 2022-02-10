from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect


def home(request):
    if request.user.is_authenticated:
        return render(request, 'app/home.html')
    else:
        return redirect('accounts:login')

@login_required()
def admin_action(request):
    return render(request, 'admin/dashboard.html')
