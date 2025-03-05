from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth import decorators
from django.contrib.auth.models import User 
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator # generer un token par defaut
from django.utils.encoding import force_bytes, force_str  # forcer la conversion en bit
from django.utils.http import urlsafe_base64_encode , urlsafe_base64_decode# encoder en base 64
import codecs
from .forms import CustomUserCreationForm


def connexion(request):
    message = ""
    if request.method == 'POST':
        nom = request.POST.get('username')
        pwd = request.POST.get('password')

        utilisateur = authenticate(username=nom, password=pwd)
        if utilisateur is not None:
            login(request, utilisateur)
            return redirect('payment_index')
        else:
            message="identifications invalides" 
            return render(request, 'login.html', {"msg": message})
  
    return render(request, "login.html")

def deconnexion(request):
    logout(request)
    return redirect('login')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        utilisateur = User.objects.filter(email=email).first() 
        if utilisateur is not None : 
            print("user found")
            tk = default_token_generator.make_token(utilisateur)
            uid = urlsafe_base64_encode(force_bytes(utilisateur.id))
            domain_site =  request.META['HTTP_HOST']
            context = {
                "uidd": uid, 
                "tok": tk,
                "domain_site": f"http://{domain_site}"
            }
            html_text = render_to_string('email.html', context)   
            msg = EmailMessage(
                "Récupération de mot de passe",
                 html_text,
                "NISCG <abdoulayeattamouyoussouf@gmail.com>",
                [utilisateur.email])
            msg.content_subtype = "html"
            msg.send()
        else:  
            print("user not found")
            #abdallahbenyous515@gmail.com
    return render(request, "forgot_pwd.html")

def update_password(request, tk, uid):
    msg = ""
    try:
        user_id = urlsafe_base64_decode(uid)
        decode_uid = codecs.decode(user_id, 'utf-8')
        user = User.objects.get(id=decode_uid)
    except:
        return HttpResponse("Invalid token")
    check_tk = default_token_generator.check_token(user, tk)
    print(check_tk)
    if not check_tk:
        return HttpResponse("Invalid token")
    if request.method == 'POST':
        pwd = request.POST.get('new_pwd')
        confirm = request.POST.get('confirm_pwd')
        if pwd == confirm:
            user.set_password(pwd)
            user.save()
            return redirect('acceuil')
        else:
            msg = "Les mots de passe ne correspondent pas"
            return render(request, "update_pwd.html", {"msg": msg})
    return render(request, "update_pwd.html")

@decorators.login_required
def list_user(request):
    users = User.objects.filter(is_superuser = False)
    return render(request, 'list_user.html', {'users':users})

@decorators.login_required
def desactive_user(request, id):
    user = User.objects.get(id=id)
    user.is_active = False
    user.save()
    return redirect('list_users')

@decorators.login_required
def active_user(request, id):
    user = User.objects.get(id=id)
    user.is_active = True
    user.save()
    return redirect('list_users')

@decorators.login_required
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('acceuil')  # Redirige vers la page d'accueil
    else:
        form = CustomUserCreationForm()
    return render(request, 'create_user.html', {'form': form})