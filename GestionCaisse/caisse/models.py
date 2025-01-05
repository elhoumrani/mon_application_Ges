from django.db import models
from django.contrib.auth.models import User



class AnneeScolaire(models.Model):
    libelle = models.CharField(max_length=9)  # ex: 2023-2024
    STATUT_CHOICES = [
        ('active', 'Active'),
        ('cloturee', 'Cloturée'),
    ]
    statut = models.CharField(max_length=8, choices=STATUT_CHOICES)

    def __str__(self):
        return self.libelle

class Classe(models.Model):
    niveau = models.CharField(max_length=100)  # ex: "Second", "Terminale"
    libele = models.CharField(max_length=20) # ex: "Second A, Second B"
    CYCLE = [
        ('Premier','1er Cycle'),
        ('Second', '2end Cycle')]
    cycle = models.CharField(max_length=30, choices=CYCLE)
    frais_scolarite = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.libele

class Eleve(models.Model):
    matricule = models.CharField(max_length=20)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    SEXE_CHOICES = [
        ('masculin', 'M'),
        ('feminin', 'F'),
    ]
    sexe = models.CharField(max_length=12, choices=SEXE_CHOICES)

    def __str__(self):
        return f"{self.matricule} ,{self.prenom} {self.nom}"


class Inscription(models.Model):
    eleve = models.ForeignKey(Eleve, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    annee_scolaire = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE)
    date_inscription = models.DateField()

    def __str__(self):
        return f"{self.eleve} - {self.annee_scolaire}"


class Paiement(models.Model):
    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE)
    motif = models.CharField(max_length=30)
    montant = models.IntegerField()
    date_paiement = models.DateField()
    numero_recu = models.CharField(max_length=12)
    MODE_PAYE = [
        ('virement', 'Virement'),
        ('cheque', 'Cheque'),
        ('espce', 'Espce')]
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAYE)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reference = models.CharField(max_length=45)

    def __str__(self):
        return f"{self.montant} - {self.date_paiement} ({self.inscription})"