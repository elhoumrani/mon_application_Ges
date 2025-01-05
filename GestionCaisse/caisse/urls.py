from django.contrib import admin
from django.urls import path
from caisse import views

urlpatterns = [
    path('Payement/', views.acceuil_payement, name="acceuilP" ),
    path('ajout_paye/', views.form_payement, name='effectuer_paye'),
    path('eleves/', views.acceuileleves, name='acceuilE'),
    path('formation/', views.acceuil_formations, name='acceuilF'),
    path('ajouter_apprenant/', views.ajout_apprenant, name="ajouter_apprenant"),
    path('inscription/', views.ajout_inscription, name='ajouter_inscription'),
    path('ajout_formation/', views.enregistrer_classe, name="ajouter_classe"),
]