from django.urls import path
from .views import bills, patients,cash_payment,mpesa_webhook

urlpatterns = [
    path('bills/', bills, name='bills'),
    path('patients/', patients, name='patients'),
    path('bills/<int:bill_id>/cash_payment/', cash_payment, name='cash_payment'),
    path('payments/mpesa_webhook/', mpesa_webhook, name='mpesa_webhook'),
]