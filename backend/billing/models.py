from django.db import models

# Create your models here.

class Patient(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Bill(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='bills')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bill #{self.id} - {self.patient.name}"

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()


    def __str__(self):
        return f"{self.description} - Bill #{self.bill.id}"
   