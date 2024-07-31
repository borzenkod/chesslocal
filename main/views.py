from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

@login_required
def logout(req):
    auth_logout(req)
    return redirect("/")


def profile_view(request):
    return render(request, "registration/profile.html")
