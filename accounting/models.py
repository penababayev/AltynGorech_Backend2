from django.db import models, transaction
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
# from courses.models import *
from django.core.exceptions import ValidationError
from django.db import models, transaction, IntegrityError
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model
import uuid
import re


# Create your models here.


# --- Muhasebe ---

class PaymentPlan(models.Model):
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name="payment_plans")
    name = models.CharField(max_length=120)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    installments = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.course} - {self.name}"


class Discount(models.Model):
    name = models.CharField(max_length=120)
    percent = models.DecimalField(max_digits=5, decimal_places=2, help_text="Örn: %10 için 10.00")

    def __str__(self):
        return f"{self.name} %{self.percent}"




class Invoice(models.Model):
    enrollment = models.ForeignKey("courses.Enrollment", on_delete=models.CASCADE, related_name="invoices")
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.SET_NULL, null=True, blank=True)
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # indirimsiz/indirimli net tutar tercihinize göre
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.id} - {self.enrollment}"


class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_at = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=30, default="CASH")  # CASH/CARD/TRANSFER

    def __str__(self):
        return f"Payment #{self.id} - Invoice {self.invoice_id}"