# # models.py
# models.py
from django.db import models
from django.contrib.auth.models import User

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pid = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=15)
    course = models.CharField(max_length=50)
    dob = models.DateField(null=True, blank=True)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)  # Profile image field

    def __str__(self):
        return self.user.username


class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    seller = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    id = models.BigAutoField(primary_key=True)  # This is auto-incremented by default
    buyer = models.ForeignKey(UserProfile, related_name="transactions_buyer", on_delete=models.CASCADE)
    seller = models.ForeignKey(UserProfile, related_name="transactions_seller", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    confirmed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.id} for {self.product.name}"


class SoldItem(models.Model):
    seller = models.ForeignKey(UserProfile, related_name="sold_items", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_sold = models.DateTimeField(auto_now_add=True)
    buyer_pid = models.CharField(max_length=10)  # Changed from IntegerField to CharField

    def __str__(self):
        return self.name


class BoughtItem(models.Model):
    buyer = models.ForeignKey(UserProfile, related_name="bought_items", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    date_bought = models.DateTimeField(auto_now_add=True)
    seller_pid = models.CharField(max_length=10)  # Changed from IntegerField to CharField

    def __str__(self):
        return self.name




from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date'})  # Date picker widget
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user