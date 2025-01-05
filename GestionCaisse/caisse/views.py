from io import BytesIO
import random
from urllib import request
from django.http import HttpResponse
from django.shortcuts import redirect, render
from datetime import datetime
from django.contrib.auth.decorators import login_required
import uuid
from caisse.form import *
from django.template.loader import render_to_string
from xhtml2pdf import pisa


# views.py
from django.shortcuts import render
from django.http import HttpResponse
from .models import Payment
from weasyprint import HTML

def payment_pdf(request, payment_id):
    payment = Payment.objects.get(id=payment_id)
    html_string = render_to_string('payment_template.html', {'payment': payment})
    html = HTML(string=html_string)
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="payment_{payment_id}.pdf"'
    return response


# Create your views here.

def generer_matricule(): #methode pour generer un idetifiant unique pour chaque eleve
    dates = datetime.now().strftime("%Y%m%d")
    
    prefix = "FLamy"
    atteinte = 0
    while atteinte < 100 :
        id = str(uuid.uuid4().int)[:4]
        matricule_id = f"{prefix}{dates}{id}"

        if not Eleve.objects.filter(matricule=matricule_id).exists():
            return matricule_id
        atteinte = atteinte + 1

        raise Exception("imposible de generer un matricule, il semble que la limite est atteinte")

def numero_recu():
    dates = datetime.now().strftime("%Y-%m-%d")
    prefix = "Flamy"
    nombre = random.randint(1000, 9999)
    num = f"{prefix}{nombre}"
    return num


   
@login_required()
def acceuil_payement(request): # acceuil payement
    liste_payement = Paiement.objects.all()
    return render(request, 'Acceuilpayement.html', {'liste': liste_payement})
@login_required()
def acceuil_formations(request): # acceuil formation
    liste_formation = Classe.objects.all()
    return render(request, 'acceuilFormations.html', {'liste': liste_formation})
@login_required()
def acceuileleves(request):  # acceuil eleve
    liste_eleve = Eleve.objects.all()
    return render(request, 'Accuileleves.html', {'liste': liste_eleve})

    
# generer un fichier pdf pour le payement


# effectuer un payement
@login_required()
def form_payement(request):

    dates = datetime.now().strftime("%Y%m%d")
    utilisateur = request.user.username
    prefix = "Flamy"
    ref = f"{dates} - {prefix} - {utilisateur}"
    formulaire = PaiementForm()
    if request.method == "POST":
        formulaire = PaiementForm(request.POST)
        if formulaire.is_valid():

            event = formulaire.save(commit=False)
            event.numero_recu = numero_recu()
            event.reference = ref
            event.utitlisateur_id = request.user.id
            event.save()
            return redirect('acceuilP')
        
        print("une erreur s'est produite")

    return render(request, 'ajoutP.html', {"form": formulaire})

# ajouter un apprenant
@login_required()
def ajout_apprenant(request):
    
    formulaire = EleveForm()

    if request.method == "POST":
        formulaire = EleveForm(request.POST)

        if formulaire.is_valid():
            event = formulaire.save(commit=False)
            event.matricule = generer_matricule()
            event.save()
            return redirect('acceuilE')

    return render(request, 'ajoutE.html', {'form': formulaire} )

# faire une inscription
@login_required() 
def ajout_inscription(request):
    formulaire = InscriptionForm()

    if request.method == 'POST':
        formulaire = InscriptionForm(request.POST)

        if formulaire.is_valid():
            formulaire.save()
            return redirect('acceuilE')
    
    return render(request, 'ajoutInscription.html', {'form': formulaire})

# enregistrer une formation
@login_required()
def enregistrer_classe(request):
    formulaire = FormationForm()

    if request.method == 'POST':
        formulaire = FormationForm(request.POST)

        if formulaire.is_valid():
            formulaire.save()
            return redirect('acceuilF')
        
    return render(request, 'ajoutFormation.html', {'form': formulaire})
