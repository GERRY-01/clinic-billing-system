from django.utils import timezone
from django.shortcuts import get_object_or_404
from decimal import Decimal, InvalidOperation
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import PatientSerializer, BillSerializer, BillItemSerializer, PaymentSerializer
from .models import Bill,Patient, BillItem, Payment

# Create your views here.

@api_view(['GET', 'POST'])
def patients(request):

    if request.method == 'GET':
        patients = Patient.objects.all()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = PatientSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET', 'POST'])
def bills(request):
    
    if request.method == 'GET':
        bills = Bill.objects.all().order_by('-created_at')
        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BillSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def cash_payment(request, bill_id):

    bill = get_object_or_404(Bill, id=bill_id)

    amount = request.data.get('amount')

    if amount is None:
        return Response(
            {"error": "Payment amount is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        amount = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        return Response(
            {"error": "Invalid payment amount."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if amount <= 0:
        return Response(
            {"error": "Payment amount must be greater than zero."},
            status=status.HTTP_400_BAD_REQUEST
        )

    total_amount = sum(
        (
            item.unit_price * item.quantity
            for item in bill.items.all()
        ),
        Decimal('0.00')
    )

    total_paid = sum(
        (
            payment.amount
            for payment in bill.payments.all()
        ),
        Decimal('0.00')
    )

    balance_due = total_amount - total_paid

    if amount > balance_due:
        return Response(
            {"error": "Payment exceeds the outstanding balance."},
            status=status.HTTP_400_BAD_REQUEST
        )

    payment = Payment.objects.create(
        bill=bill,
        amount=amount,
        method="CASH",
        paid_at=timezone.now()
    )

    return Response(
        {
            "message": "Cash payment recorded successfully.",
            "payment_id": payment.id,
            "amount": payment.amount,
            "bill_id": bill.id,
            "balance_due": balance_due - amount
        },
        status=status.HTTP_201_CREATED
    )