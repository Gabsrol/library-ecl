# import form class from django 
from django import forms 
  
# import  from models.py 
from .models import User, Reference, Subscription, Bad_borrower, Loan

# create a Loan ModelForm 
class LoanForm(forms.ModelForm): 

    class Meta: 
        model = Loan
        fields = "__all__"

#https://stackoverflow.com/questions/53773149/how-to-pass-bookinstance-id-for-a-particular-book-to-function-based-view-in-djan
