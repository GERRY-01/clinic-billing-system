from rest_framework import serializers
from decimal import Decimal
from .models import Patient, Bill, BillItem, Payment

class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'name']

class BillItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillItem
        fields = ['id', 'description', 'unit_price', 'quantity']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'method', 'transaction_id', 'paid_at']

class BillSerializer(serializers.ModelSerializer):
    items = BillItemSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    total_paid = serializers.SerializerMethodField()
    balance_due = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = ['id', 'patient', 'created_at', 'items', 'payments', 'total_amount', 'total_paid', 'balance_due']

    def get_total_amount(self, obj):
        return sum(item.unit_price * item.quantity for item in obj.items.all())

    def get_total_paid(self, obj):
        return sum(payment.amount for payment in obj.payments.all())

    def get_balance_due(self, obj):
        total_amount = self.get_total_amount(obj)
        total_paid = self.get_total_paid(obj)
        return Decimal(total_amount) - Decimal(total_paid)