from caisse.models import *

from django import forms
from .models import AnneeScolaire

class AnneeScolaireForm(forms.ModelForm):
    class Meta:
        model = AnneeScolaire
        fields = ['libelle',  'statut']
        
        labels = {
            'libelle': 'Libellé',
            'statut': 'Statut',
        }


class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ['niveau', 'libele', 'cycle', 'frais_scolarite']

        labels = {
            'niveau': 'Niveau',
            'libele' : 'Libellé',
            'cycle': 'Cycle',
            'frais_scolarite': 'Frais de scolarité'}

class EleveForm(forms.ModelForm):
    class Meta:
        model = Eleve

        fields = ['nom', 'prenom', 'date_naissance', 'sexe']

        labels ={
            'nom' : 'Nom',
            'prenom' : 'Prenom',
            'date_naissance' : 'Date de naissance',
            'sexe' : 'Sexe'
            }
        
        widgets = {
            
             "date_naissance": forms.DateInput(
                attrs={
                    'placeholder': 'Entrez le matricule',
                    'class': 'form-control',
                    'type': 'date'}),       
                    }

class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription

        fields = ['eleve', 'classe', 'annee_scolaire', 'date_inscription']

        labels ={
            'eleve': 'Eleve',
            'classe' : 'Classe',
            'annee_scolaire' : 'Anne Scolaire',
            'date_inscription' : 'Date Inscription',
            }
        
        widgets = {
            "matricule": forms.TextInput(
                attrs={
                    'placeholder': 'Entrez le matricule',
                    'class': 'form-control'}),

             "date_inscription": forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date'}),       
                    }
        

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['inscription', 'motif', 'montant', 'date_paiement', 'mode_paiement']
        

        labels = {
            'inscription': 'Inscription',
            'motif': 'Motif',
            'montant': 'Montant (FCFA)',
            'date_paiement': 'Date de Paiement',
            'mode_paiement': 'Mode de Paiement',
        }
        
        widgets = {
            'date_paiement': forms.DateInput(attrs={'type': 'date'}),
            'montant': forms.NumberInput(attrs={'min': 0}),
        }

class FormationForm(forms.ModelForm):
    class Meta:
        model = Classe

        fields = ['niveau', 'libele', 'cycle', 'frais_scolarite']

        labels = {
            'niveau': 'Niveau',
            'libele': 'Libelé',
            'cycle': 'Cycle',
            'frais_scolarite': 'Frais scolarité'
            }
        
        widgets = {
            "niveau": forms.TextInput(
                attrs={
                    'placeholder': 'Entrez le niveau ',
                    'class': 'form-control'}),
            
            "libele": forms.TextInput(
                attrs={
                    'placeholder': 'Entrez le libelé ',
                    'class': 'form-control'}),

            "cycle": forms.Select(
                attrs={
                    'placeholder': 'choisir le cycle ',
                    'class': 'form-control'}),
        
            "montant": forms.NumberInput(attrs={'min': 0}),

                    }
        
        