from caisse.models import *

from django import forms
from .models import School_year

class AnneeScolaireForm(forms.ModelForm):
    class Meta:
        model = School_year
        fields = ['libelle', 'date_debut', 'date_fin']
        
        labels = {
            'libelle': 'Libellé',
        }

        widgets = {
            
            'date_debut': forms.DateInput(attrs={'type': 'date', 'format': 'yyyy-mm-dd'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'format': 'yyyy-mm-dd'}),

        }


class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation

        fields = ['niveau', 'libele', 'cycle','frais_inscription', 'mensualite', 'tranche1', 'tranche2','tranche3']

        labels = {
            'niveau': 'Niveau',
            'libele': 'Libelé',
            'cycle': 'Cycle',
            'frais_inscription': 'Frais inscription',
            'mensualite': 'Mensualité',
            'tranche1': '1er Tranche',
            'tranche2': '2nd Tranche',
            'tranche3': '3éme Tranche',
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



class EleveForm(forms.ModelForm):
    class Meta:
        model = Student

        fields = ['nom', 'prenom', 'date_naissance', 'sexe', 'address', 'parent_contact', 'email']

        labels ={
            'nom' : 'Nom',
            'prenom' : 'Prenom',
            'date_naissance' : 'Date de naissance',
            'sexe' : 'Sexe',
            'address' : 'Adresse',
            'parent_contact' : 'Contact Parent',
            'email' : 'Email',
            }
        
        widgets = {
            
             "date_naissance": forms.DateInput(
                attrs={
                    'placeholder': 'Entrez le matricule',
                    'class': 'form-control',
                    'type': 'date'}),
            "parent_contact": forms.TextInput(
                attrs={
                   
                    'class': 'form-control',  # Classe CSS pour le style
                    'pattern': '[+][0-9]*',  # Exemple de pattern pour valider le format
            }),      
                    }


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription

        fields = ['eleve', 'classe', 'annee_scolaire', ]

        labels ={
            'eleve': 'Eleve',
            'classe' : 'Classe',
            'annee_scolaire' : 'Anne Scolaire',
            }
        
        widgets = {
            "matricule": forms.TextInput(
                attrs={
                    'placeholder': 'Entrez le matricule',
                    'class': 'form-control'}),   
            
            }
        

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['inscription', 'motif', 'mode_paiement']
        

        labels = {
            'inscription': 'Inscription',
            'motif': 'Motif',
            'montant': 'Montant (FCFA)',
            'mode_paiement': 'Mode de Paiement',
        }
        
        widgets = {
            'montant': forms.NumberInput(attrs={'min': 0}),
        }

class Archive_paie_Form(forms.ModelForm):
    class Meta:
        model = Archive_Payment
        fields = ['motif_edition']
        motif_edition = forms.CharField(
        label="Motif de suppression",
        max_length=200,
        widget=forms.Textarea(attrs={'rows': 3, 'cols': 40}),
        required=True
    )



        
        