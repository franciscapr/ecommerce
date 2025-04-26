from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'phone', 'last_name', 'email', 'addres_line_1', 'addres_line_2', 'country', 'state', 'city', 'order_note'] 