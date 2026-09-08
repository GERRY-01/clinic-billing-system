from django.urls import path
from .views import bills, patients

urlpatterns = [
    path('bills/', bills, name='bills'),
    path('patients/', patients, name='patients'),
]