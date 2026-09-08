from decimal import Decimal

from django.test import TestCase

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