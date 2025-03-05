from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError
from phonenumber_field.modelfields import PhoneNumberField


STATUTS_INSCRIPTION =  [
    ('non_inscrit', 'Non Inscrit'),
    ('inscrit', 'Inscrit'),
    ('termine', 'Terminé'),
    ]
CYCLE = [
        ('Premier','1er Cycle'),
        ('Second', '2end Cycle')]

STATUT_YEAR = [
        ('active', 'Active'),
        ('cloturee', 'Cloturée'),
    ]

class School_year(models.Model):
    date_debut = models.DateField()
    date_fin = models.DateField()
    libelle = models.CharField(max_length=12)  # ex: 2023-2024
    statut = models.CharField(max_length=8, choices=STATUT_YEAR, default=STATUT_YEAR[0][1])

    def __str__(self):
        return self.libelle

class Formation(models.Model):
    niveau = models.CharField(max_length=100)  # ex: "Second", "Terminale"
    libele = models.CharField(max_length=20) # ex: "Second A, Second B"
    cycle = models.CharField(max_length=30, choices=CYCLE)
    frais_inscription = models.DecimalField(max_digits=10, decimal_places=2)
    mensualite = models.DecimalField(max_digits=10, decimal_places=2)
    tranche1 = models.DecimalField(max_digits=10, decimal_places=2)
    tranche2 = models.DecimalField(max_digits=10, decimal_places=2)
    tranche3 = models.DecimalField(max_digits=10, decimal_places=2)
    frais_scolarite = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.libele


class Student(models.Model):
    matricule = models.CharField(max_length=20)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    SEXE_CHOICES = [
        ('masculin', 'M'),
        ('feminin', 'F'),
    ]
    sexe = models.CharField(max_length=12, choices=SEXE_CHOICES)
    parent_contact = PhoneNumberField()
    email = models.EmailField()
    address = models.CharField(max_length=20)


    def __str__(self):
        return f"{self.matricule} |  {self.nom} {self.prenom}"
    
    


class Inscription(models.Model):
    eleve = models.ForeignKey(Student, on_delete=models.CASCADE)
    classe = models.ForeignKey(Formation, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(School_year, on_delete=models.CASCADE)
    date_inscription = models.DateField(auto_now_add=True)
   
    statut = models.CharField(max_length=125, choices=STATUTS_INSCRIPTION, default=STATUTS_INSCRIPTION[0])

    def __str__(self):
        return f"{self.eleve}  {self.annee_scolaire}"


class Payment(models.Model):
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE)
    MOTIF = [
        ('inscriptions', 'Inscription'),
        ('mensuel', 'Mensuel'),
        ('tranche1', '1er Tranche'),
        ('tranche2', '2nd Tranche'),
        ('Annuel', 'Annuel'),
        ]
    motif = models.CharField(max_length=30, choices=MOTIF)
    montant = models.IntegerField()
    date_paiement = models.DateField(auto_now_add=True)
    numero_recu = models.CharField(max_length=12)
    MODE_PAYE = [
        ('espece', 'Espece'),
        ('virement', 'Virement'),
        ]
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAYE)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reference = models.CharField(max_length=45)

    def __str__(self):
        return f"{self.montant} - {self.date_paiement} ({self.inscription})"
    
class Archive_Payment(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, related_name='archives')
    inscription = models.ForeignKey(Inscription, on_delete=models.SET_NULL, null=True)
    motif = models.CharField(max_length=30)
    montant = models.IntegerField()
    date_paiement = models.DateField()
    numero_recu = models.CharField(max_length=12)
    mode_paiement = models.CharField(max_length=20)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reference = models.CharField(max_length=45)
    motif_edition = models.CharField(max_length=200)
    date_archive = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Archive: {self.montant} - {self.date_paiement} ({self.inscription})"
