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
