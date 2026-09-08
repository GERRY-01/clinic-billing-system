from decimal import Decimal

from django.test import TestCase

from django.utils import timezone
from rest_framework.test import APIClient

from .models import Patient, Bill, BillItem, Payment


class PaymentTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.patient = Patient.objects.create(
            name="Maurice Odhiambo"
        )

        self.bill = Bill.objects.create(
            patient=self.patient
        )

        BillItem.objects.create(
            bill=self.bill,
            description="Medication",
            unit_price=Decimal("1000.00"),
            quantity=2
        )

    def test_cash_payment_is_recorded(self):
        url = f'/api/bills/{self.bill.id}/cash_payment/'
        data = {
            "amount": "1500.00"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)

        payment = Payment.objects.get(bill=self.bill)

        self.assertEqual(payment.amount, Decimal("1500.00"))
        self.assertEqual(payment.method, "CASH")


    def test_mpesa_payment_is_recorded(self):
        url = '/api/payments/mpesa_webhook/'

        data = {
            "transaction_id": "TEST12345",
            "bill_id": self.bill.id,
            "amount": "500.00",
            "status": "SUCCESS",
            "paid_at": timezone.now().isoformat()
        }

        response = self.client.post(
            url,
            data,
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        payment = Payment.objects.get(bill=self.bill)

        self.assertEqual(payment.amount, Decimal("500.00"))
        self.assertEqual(payment.method, "MPESA")
        self.assertEqual(payment.transaction_id, "TEST12345")


    def test_duplicate_mpesa_webhook_does_not_create_payment(self):
        data = {
            "transaction_id": "DUPLICATE123",
            "bill_id": self.bill.id,
            "amount": "500.00",
            "status": "SUCCESS",
            "paid_at": timezone.now().isoformat()
        }

        first_response = self.client.post(
            '/api/payments/mpesa_webhook/',
            data,
            format='json'
        )

        second_response = self.client.post(
            '/api/payments/mpesa_webhook/',
            data,
            format='json'
        )

        self.assertEqual(first_response.status_code, 201)
        self.assertEqual(second_response.status_code, 200)

        self.assertEqual(Payment.objects.count(), 1)

        payment = Payment.objects.first()

        self.assertEqual(payment.transaction_id, 'DUPLICATE123')
        self.assertEqual(payment.amount, Decimal('500.00'))
        self.assertEqual(payment.bill_id, self.bill.id)

    def test_failed_mpesa_webhook_does_not_create_payment(self):
        data = {
            "transaction_id": "FAILED123",
            "bill_id": self.bill.id,
            "amount": "500.00",
            "status": "FAILED",
            "paid_at": timezone.now().isoformat()
        }

        response = self.client.post(
            '/api/payments/mpesa_webhook/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(Payment.objects.count(), 0)

    def test_cash_payment_overpayment_is_rejected(self):
        data = {
            "amount": "2500.00"
        }

        response = self.client.post(
            f'/api/bills/{self.bill.id}/cash_payment/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, 400)

        self.assertEqual(Payment.objects.count(), 0)

    def test_partial_cash_payment_leaves_outstanding_balance(self):
        data = {
            "amount": "500.00"
        }

        response = self.client.post(
            f'/api/bills/{self.bill.id}/cash_payment/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        self.assertEqual(Payment.objects.count(), 1)

        payment = Payment.objects.first()
        self.assertEqual(payment.amount, Decimal("500.00"))

        self.assertEqual(response.data["balance_due"], Decimal("1500.00"))