from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout  

# Create your views here.

def connexion(request):
    message = ""
    if request.method == 'POST':
        nom = request.POST.get('username')
        pwd = request.POST.get('password')

        utilisateur = authenticate(username=nom, password=pwd)
        if utilisateur is not None:
            login(request, utilisateur)
            return redirect('acceuilP')
        else:
            message="identifications invalides" 
            return render(request, 'login.html', {"msg": message})
  
    return render(request, "login.html")

def deconnexion(request):
    logout(request)
    return redirect('login')