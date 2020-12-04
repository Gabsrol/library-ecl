# import form class from django 
import django_filters

# import  from models.py 
from .models import User, Reference, Subscription, Bad_borrower, Loan

class ReferenceFilter(django_filters.FilterSet):

    author = django_filters.CharFilter(lookup_expr='icontains',label='Auteur')
    name = django_filters.CharFilter(lookup_expr='icontains',label='Titre')
    class Meta:
        model = Reference
        fields = ['name','author','ref_type']