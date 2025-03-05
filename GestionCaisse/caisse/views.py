from decimal import Decimal
import random
from urllib import request
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from datetime import datetime
from django.contrib.auth.decorators import login_required
import uuid
from caisse.form import *
from django.template.loader import render_to_string
import pdfkit
from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from django.db.models import Sum, Q
import logging
import datetime


def generer_matricule(): #methode pour generer un idetifiant unique pour chaque eleve
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d%H%M%S")
    prefix = "FLamy"
    atteinte = 0
    while atteinte < 100 :
        id = str(uuid.uuid4().int)[:4]
        matricule_id = f"{date_str}{id}"

        if not Student.objects.filter(matricule=matricule_id).exists():
            return matricule_id
        atteinte = atteinte + 1
        raise Exception("imposible de generer un matricule, il semble que la limite est atteinte")

def get_new_matricule():
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d%H%M%S")  # Format : YYYYMMDDHHMMSS
    nbre_student = Student.objects.count()
    
    if nbre_student != 0:
        new_number = nbre_student + 1
    else:
        new_number = 1

    return f"{date_str}{new_number:05d}"  # Format : YYYYMMDDHHMMSS0001

# fonction pour generr un num de reçu
def numero_recu():
    dates = datetime.datetime.now().strftime("%Y-%m-%d")
    prefix = "Flamy"
    nombre = random.randint(1000, 9999)
    num = f"{prefix}{nombre}"
    return num

#list year_school  
def index_year(request):  
    annee_sc = School_year.objects.all()
    for elt in annee_sc:
        reste = (elt.date_fin - elt.date_debut).days
        if reste <=0:
            elt.statut = STATUT_YEAR[1][1]
            elt.save()
        else:
            elt.statut = STATUT_YEAR[0][1]
            elt.save()
    context = {'annee_sc': annee_sc}
    return render(request, 'annee_sc/index.html', context)

# afficher les details d'une année scolaire
def details_year(reqest, id):
    annee_scolaire = get_object_or_404(School_year, pk=id)
    revenu_total = 0
    reste = 0
   
    # Nombre total d'inscrits
    total_inscrits = Inscription.objects.filter(annee_scolaire=annee_scolaire).count()
    
    # Revenu total de l'année (somme des frais de scolarité de tous les inscrits)
    inscriptions = Inscription.objects.filter(annee_scolaire=annee_scolaire).select_related('classe')
    for inscription in inscriptions:
        revenu_total += inscription.classe.frais_scolarite

    # Revenu total des paiements effectués
    recu = Payment.objects.filter(inscription__annee_scolaire = annee_scolaire).aggregate(total = Sum('montant'))['total'] or 0
    reste = revenu_total - recu

    # eleve irreguliers 
    paie =0
    reste_paie=0
    eleves_irreguliers = []
    for inscrit in inscriptions:
        frais = inscrit.classe.frais_scolarite
        paie = Payment.objects.filter(inscription = inscrit).aggregate(total=Sum('montant'))['total'] or 0
        if paie < frais:
            reste_paie = frais - paie
            eleves_irreguliers.append({
                'inscrit': inscrit,
                'reste_paie': reste_paie,
                'paie': paie
            })

    context = {
        'annee_scolaire': annee_scolaire,
        'total_inscrits': total_inscrits,
        'revenu_total': revenu_total,
        'recu': recu,
        'reste': reste,
        'eleve_irregulier': eleves_irreguliers
    }

    return render(reqest, 'annee_sc/details.html', context)

#create year_school
def create_year(request):
    # Vérifier s'il existe une année scolaire active
    annee_active = School_year.objects.filter(statut=STATUT_YEAR[0][1]).exists()
    msg = ""
    reste = 0
    
    form = AnneeScolaireForm()

    if request.method == 'POST':
        form = AnneeScolaireForm(request.POST)
        if form.is_valid():
            if not annee_active:
                event = form.save(commit=False)
                reste = (event.date_fin - event.date_debut).days
                print(reste)
                if reste < 363:
                    msg = "La durée normale de l'année scolaire est definie à 365 jours."
                else:
                    event.save()
                    return redirect('index_year')
            else:
                print(reste)
                msg = "Impossible d'effectuer cette opération, car une année est déjà en cours."
        else:
            msg = f"Une erreur s'est produite : {form.errors}"
            print(msg)

    return render(request, 'annee_sc/create.html', {"form": form, 'msg': msg})
#edit year_school
def edit_year(request, id):
    anneesc = get_object_or_404(School_year, pk=id)
    print(anneesc.date_debut)
   
    form = AnneeScolaireForm(request.POST or None, instance=anneesc)
    if form.is_valid():
        #event = form.save(commit=False)
        #reste = (event.date_fin - event.date_debut).days
        #print(reste)
        #if reste < 363:
         #   msg = "La durée normale de l'année scolaire est definie à 365 jours."
        #else:
         #   event.save()
          #  return redirect('index_year')
        form.save()
        return redirect('index_year')
    
  
    return render(request, 'annee_sc/edit.html', {'form': form})

def delete_year(request, id):
    annee = get_object_or_404(School_year, pk=id)
    
    annee.delete()
    return redirect('index_year')

   






@login_required()
def index_payement(request): # acceuil payement
    liste_payement = Payment.objects.filter(inscription__annee_scolaire__statut=STATUT_YEAR[0][1]).order_by('-id')

    if request.method == "GET":
        name=request.GET.get('recherche')
        if name is not None:
            liste_payement = Payment.objects.filter(inscription__eleve__matricule__icontains=name)

    return render(request, 'payment/index.html', {'liste': liste_payement})

@login_required()
def index_formations(request): # acceuil formation
    liste_formation = Formation.objects.all()
    if request.method == "GET":
        name=request.GET.get('recherche')
        if name is not None:
            liste_formation = Formation.objects.filter(libele__icontains=name)
    return render(request, 'formation/index.html', {'liste': liste_formation})

@login_required()
def index_eleves(request):  # acceuil eleve
    liste_eleve = Student.objects.all()
    if request.method == "GET":
        name=request.GET.get('recherche')
        if name is not None:
            liste_eleve = Student.objects.filter(models.Q(matricule__icontains=name) | models.Q(nom__icontains=name))

    return render(request, 'students/index.html', {'liste': liste_eleve})

logger = logging.getLogger(__name__)
@login_required()
def index_inscription(request):
    list_inscrit = []
    inscrit = Inscription.objects.select_related('classe').all()
    formations = Formation.objects.all()
    if request.method == 'GET':
        formation = request.GET.get('formation')
        statuts = request.GET.get('statut')
        if formation is not None and statuts is not None:
            inscrit = Inscription.objects.filter(classe__libele__icontains=formation , statut__icontains=statuts)

    for ins in inscrit:
        try:
            montant_formation = Formation.objects.get(libele=ins.classe)
            frais = montant_formation.frais_scolarite
            paie = Payment.objects.filter(inscription=ins).aggregate(total=Sum('montant'))['total'] or 0
            reste = frais - paie

            #frais_inscription = montant_formation.frais_inscription or 0
            #tranche1 = montant_formation.tranche1 or 0
            #tranche2 = montant_formation.tranche2 or 0
            #tranche3 = montant_formation.tranche3 or 0

            if paie >= frais:
                ins.statut = STATUTS_INSCRIPTION[2][1]
            elif paie > 0 and paie < frais:
                ins.statut = STATUTS_INSCRIPTION[1][1]
            elif paie == 0:
                ins.statut = STATUTS_INSCRIPTION[0][1]
            
            ins.save()
            logger.debug(f"Statut de l'inscription {ins.id} : {ins.statut}")
        
        except Formation.DoesNotExist:
            logger.error(f"Formation non trouvée pour l'inscription {ins.id}")
            continue

        list_inscrit.append({
            'list': ins,
            'reste': reste,
            'paye':paie
             })
    context = {
            'inscrit': list_inscrit,
            'classe':formations }
    
    return render(request, 'inscription/index.html', context)
      
# generer un fichier pdf pour le payement
def generate_pdf(request, id):
    payement = Payment.objects.get(pk=id)
    formation = payement.inscription.classe #obtenir le nom de la formation
    montant_formation = Formation.objects.get(libele=formation) # obtebir le frais de formation
    frais = montant_formation.frais_scolarite
    #obtenir la somme de paiement effectuer par un apprenant
    paie = Payment.objects.filter(inscription = payement.inscription).aggregate(total=Sum('montant'))['total']
    all_paie = paie or 0
    reste = frais - all_paie # obtenir le reste à payer
    
    context = {'payement': payement , "all_paie": all_paie, "frais":frais, 'reste': reste}
    html = render_to_string('base/reçu.html', context )
    pdf = pdfkit.from_string(html, False)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="document.pdf"'
    return response

#liste des appreants en situation d'irregularité
def imprimer_liste(request, id):
    formation = get_object_or_404(Formation, pk=id)
    inscrits = Inscription.objects.filter(classe=formation)
    frais = formation.frais_scolarite
    recalcitrants = []
    reste = 0
    for elt in inscrits:
        paye = Payment.objects.filter(inscription=elt).aggregate(total=Sum('montant'))['total']or 0
        if paye < frais:
            reste = frais - paye
            recalcitrants.append({
                'inscrits': elt,
                'reste': reste,
                'paye': paye})
    context = {'recals': recalcitrants, 'classe':formation} 

    html = render_to_string('base/liste_irregulier.html', context )
    pdf = pdfkit.from_string(html, False)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="liste_irregulier.pdf"'
    return response

# effectuer un payementinline
@login_required()
def create_payement(request):
    msg = ""
    dates = datetime.datetime.now().strftime("%Y%m%d")
    utilisateur = request.user.username
    prefix = "Flamy"
    ref = f"{dates} - {utilisateur}"
    montants = {}
    formulaire = PaiementForm()
    if request.method == "POST":
        formulaire = PaiementForm(request.POST)
        if formulaire.is_valid():
            event = formulaire.save(commit=False)
            event.numero_recu = numero_recu()
            event.reference = ref
            event.utilisateur_id = request.user.id  
            if event.motif == 'Annuel':
                event.montant = event.inscription.classe.frais_scolarite
            elif event.motif == 'inscriptions':
                event.montant = event.inscription.classe.frais_inscription
            elif event.motif == 'mensuel':
                nbre_mois = request.POST.get('nombre_mois')
                nbre_mois = int(nbre_mois)
                event.montant = event.inscription.classe.mensualite*nbre_mois
            elif event.motif == 'tranche1':
                event.montant = event.inscription.classe.tranche1
            elif event.motif == 'tranche2':
                event.montant = event.inscription.classe.tranche2
            if not event.inscription:
                msg = "Erreur : l'inscription doit être définie."
                return render(request, 'payment/create.html', {'form': formulaire, 'msg': msg})

            formation = event.inscription.classe  # obtenir le nom de la formation
            montant_formation = Formation.objects.get(libele=formation)  # obtenir le frais de formation
            frais = montant_formation.frais_scolarite

            # obtenir la somme de paiement effectuée par un apprenant
            paie = Payment.objects.filter(inscription=event.inscription).aggregate(total=Sum('montant'))['total']
            all_paie = paie or 0
            reste = frais - all_paie  # obtenir le reste à payer
            if reste < 0:
                msg = f"{event.montant}: Il n'est pas possible d'effectuer cette opération, car l'apprenant a déjà tout versé."
            else:
                montant_float = float(event.montant)
                # Enregistrer les données de paiement dans la session
                request.session['payment_data'] = {
                    'montant': montant_float,
                    'motif': event.motif,
                    'inscription_id': event.inscription.id,
                    'reference': event.reference,
                    'utilisateur_id': event.utilisateur.id,
                    'numero_recu': event.numero_recu,
                    'mode_paiement': event.mode_paiement,
                }
                return redirect('payment_confirm') 
    return render(request, 'payment/create.html', {
        'form': formulaire,
        'msg': msg,
        
    })

def confim_payement(request):
    payment_data = request.session.get('payment_data', None)
    
    if not payment_data:
        return redirect('create_payement') 
    # Convertir le montant float en Decimal si nécessaire
    payment_data['montant'] = Decimal(str(payment_data['montant']))
    # Obtenir les objets Inscription et Utilisateur
    inscriptions = get_object_or_404(Inscription, id=payment_data['inscription_id'])
    utilisateurs = get_object_or_404(User, id=payment_data['utilisateur_id'])
    if request.method == 'POST':
        #creons un objet payement
        payment = Payment(
            montant=payment_data['montant'],
            motif=payment_data['motif'],
            inscription=inscriptions,
            reference=payment_data['reference'],
            utilisateur=utilisateurs,
            numero_recu=payment_data['numero_recu'],
            mode_paiement=payment_data['mode_paiement'],
        )
        payment.save()
        del request.session['payment_data']  # Supprimer les données de la session
        return redirect('payment_index')  # Rediriger vers une page de succès
    
    return render(request, 'payment/confirmation.html', 
                  {'payment_data': payment_data,
                    'inscription': inscriptions, 
                    'utilisateur': utilisateurs,})

#Sup payement
def delete_payement(request, id):
    try:
        payement = get_object_or_404(Payment, pk=id)
    except Payment.DoesNotExist:
        return redirect('payment_index')
    
    if request.method=='POST':
        form = Archive_paie_Form(request.POST)
        if form.is_valid():
            # Récupérer le motif saisi par l'utilisateur
            motif_edition = form.cleaned_data['motif_edition']           
            # Créer une archive avant de supprimer
            Archive_Payment.objects.create(
                payment=payement,
                inscription=payement.inscription,
                motif=payement.motif,
                montant=payement.montant,
                date_paiement=payement.date_paiement,
                numero_recu=payement.numero_recu,
                mode_paiement=payement.mode_paiement,
                utilisateur=payement.utilisateur,
                reference=payement.reference,
                motif_edition=motif_edition  # Utiliser le motif saisi
            )
            # Supprimer le paiement
            payement.delete()
            return redirect('payment_index')
    else:
        form = Archive_paie_Form() 
    return render(request, "payment/delete.html", {"form": form, "payment": payement})

#Edit payement
def edit_paye(request, id):
    payment = get_object_or_404(Payment, pk=id)
    formulaire = PaiementForm(request.POST or None, instance=payment)
    
    if formulaire.is_valid():
        # Enregistrer les valeurs avant modification
        old_payment = Payment.objects.get(pk=id)
        
        # Créer une archive avant de sauvegarder les modifications
        Archive_Payment.objects.create(
            payment=old_payment,
            inscription=old_payment.inscription,
            motif=old_payment.motif,
            montant=old_payment.montant,
            date_paiement=old_payment.date_paiement,
            numero_recu=old_payment.numero_recu,
            mode_paiement=old_payment.mode_paiement,
            utilisateur=old_payment.utilisateur,
            reference=old_payment.reference,
            motif_edition="Modification du paiement"
        )
        
        # Sauvegarder les modifications
        event = formulaire.save(commit=False)
        if event.motif == 'Annuel':
            event.montant = event.inscription.classe.frais_scolarite
        elif event.motif == 'inscriptions':
            event.montant = event.inscription.classe.frais_inscription
        elif event.motif == 'mensuel':
            event.montant = event.inscription.classe.mensualite
        elif event.motif == 'tranche1':
            event.montant = event.inscription.classe.tranche1
        elif event.motif == 'tranche2':
            event.montant = event.inscription.classe.tranche2
        event.save()      
        return redirect('payment_index')
    
    return render(request, "payment/edit.html", {"form": formulaire})

#afficher les apprenant recalcitrants d'une classe
def index_recalcitrants(request, id):
    formation = get_object_or_404(Formation, pk=id)
    inscrits = Inscription.objects.filter(classe=formation)
    frais = formation.frais_scolarite
    recalcitrants = []
    reste = 0

    if request.method == 'GET':
         statuts = request.GET.get('statut')
         if statuts is not None:
            inscrits = Inscription.objects.filter(classe__libele__icontains=formation.libele, statut__icontains=statuts)
            print(inscrits)

    for elt in inscrits:
        paye = Payment.objects.filter(inscription=elt).aggregate(total=Sum('montant'))['total']or 0
        if paye < frais:
            reste = frais - paye
            recalcitrants.append({
                'inscrits': elt,
                'reste': reste,
                'paye': paye})
    context = {
            'recals': recalcitrants,
            'classe':formation}
    return render(request, 'payment/recalcitrant.html', context)


# ajouter un apprenant
@login_required()
def create_students(request):
    msg = ""
    formulaire = EleveForm()
    if request.method == "POST":
        formulaire = EleveForm(request.POST)
        if formulaire.is_valid():
            event = formulaire.save(commit=False)
            event.matricule = get_new_matricule()
            # calcul de l'age de l'eleve
            today = timezone.now().date()
            age = today.year - event.date_naissance.year # obtenir l'age exact de l'eleve
            # verifier si l'anniversaire de l'eleve n'est pas atteint et faire moins 1 sur son age.
            if ((today.month, today.year) < (event.date_naissance.month, event.date_naissance.year)):
                age = age - 1
            if age < 10 : 
                msg = "L'apprenant doit avoir au moins 10 ans."
            else:
                event.save()
                return redirect('eleve_index')

    return render(request, 'students/create.html', {'form': formulaire, "msg":msg} )

#editer un apprenant
def edit_students(request, id):
    apprenant = get_object_or_404(Student, pk=id)
    formualire = EleveForm(request.POST or None, instance=apprenant)
    if formualire.is_valid():
        formualire.save()
        return redirect('eleve_index')
    return render(request, 'students/edit.html', {'form': formualire})

# effacer un apprenant de la base de données
def delete_students(request, id):
    apprenant = get_object_or_404(Student, pk=id)
    apprenant.delete()
    return redirect('eleve_index')

# faire une inscription
@login_required() 
def create_inscription(request):
    formulaire = InscriptionForm()
    msg = ""

    if request.method == 'POST':
        formulaire = InscriptionForm(request.POST)

        if formulaire.is_valid():
            even = formulaire.save(commit=False)

            # Vérifier si l'élève a déjà une inscription active
            inscriptions_existantes = Inscription.objects.filter(eleve=even.eleve)

            if inscriptions_existantes.exists():
                doublon = False
                for inscription in inscriptions_existantes:
                    # Vérifier le statut de l'année scolaire
                    if inscription.annee_scolaire.statut == "actif":
                        doublon = True
                        break
                
                if doublon:
                    msg = "Erreur: inscription existe."
                else:
                    # Sauvegarder l'inscription si aucune inscription active n'est trouvée
                    even.save()
                    return redirect('inscription_index')
            else:
                # Pas d'inscriptions existantes, donc on peut sauvegarder
                even.save()
                return redirect('inscription_index')
        else:
            msg = "Le formulaire contient des erreurs."

    return render(request, 'inscription/create.html', {'form': formulaire, 'msg': msg})

# edit inscription
def edit_inscription(request, id):
    inscription = get_object_or_404(Inscription, pk=id)
    formulaire = InscriptionForm(request.POST or None, instance=inscription)
    if formulaire.is_valid():
        formulaire.save()
        return redirect('inscription_index')
    
    return render(request, 'inscription/edit.html', {'form': formulaire})


# enregistrer une formation
@login_required()
def create_formation(request):
    formulaire = FormationForm()

    if request.method == 'POST':
        formulaire = FormationForm(request.POST)

        if formulaire.is_valid():
            event = formulaire.save(commit=False)
            event.frais_scolarite = event.frais_inscription + event.tranche1 + event.tranche2 + event.tranche2
            event.save()
            return redirect('formation_index')
        
    return render(request, 'formation/create.html', {'form': formulaire})

# editer une formation
def edit_formation(request, id):
    formation = get_object_or_404(Formation, pk=id)
    formulaire = FormationForm(request.POST or None, instance=formation)
    if formulaire.is_valid():
        formulaire.save()
        return redirect('formation_index')
    return render(request, 'formation/edit.html', {'form': formulaire})

#supprimer formation
def delete_formation(request, id):
    formation = get_object_or_404(Formation, pk=id)
    formation.delete()
    return redirect('formation_index')


# dashboard
def index_dashboard(request):
    today = timezone.now().date() # Récupérer la date d'aujourd'hui
    revenu_classe = 0
    reste  = 0
    data= []
    #reccuperer toutes les classes et determiner leur revenu
    classe = Formation.objects.all().order_by('libele')
    for i in classe:
        payement_classe = Payment.objects.filter(inscription__classe=i).aggregate(total=Sum('montant'))['total']or 0
        nombre_apprenant = Inscription.objects.filter(classe=i).count()
        frais = i.frais_scolarite
        revenu_net = frais*nombre_apprenant
        reste = revenu_net - payement_classe
        #passer les données de classe dans la liste 
        data.append({
            'classe':i,
            'reste': reste,
            'paye':payement_classe,
            'nbre_apprenant': nombre_apprenant,
            'revenu_net': revenu_net
            })

    # Filtrer les paiements effectués aujourd'hui
    revenu_journalier = Payment.objects.filter(date_paiement=today).aggregate(total=Sum('montant'))['total']
    transaction = Payment.objects.filter(date_paiement=today).count() # transaction du jour
    revenu = revenu_journalier or 0
    nbre_inscrit = Inscription.objects.all().count() #nbre inscrits
    nbre_eleve = Student.objects.all().count()  # nombre des eleves

    caissier = User.objects.all() #reccuperer les users
    annee_sc = School_year.objects.all().count()

    nbre_classe = Formation.objects.all().count() #reccuperer nombre des classes disponible
    context = { 'revenu_jour':revenu, 
                'nbre_inscrit': nbre_inscrit,
                'nbre_eleve':nbre_eleve, 
                 'data': data, 
                 'users': caissier,
                 'nombre_classe': nbre_classe,
                  'transaction': transaction, 
                  'annee_sc': annee_sc}

    return render(request, 'base/index.html', context)