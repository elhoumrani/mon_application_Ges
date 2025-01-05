from django.contrib import admin
from django.urls import path
from comptes import views

urlpatterns = [
    path('', views.connexion, name="acceuil" ),
    path('deconnexion/', views.deconnexion, name="deconnexion"),
]