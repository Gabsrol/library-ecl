from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import User, Reference, Subscription, Bad_borrower, Loan

def index(request):

    query = request.GET.get('query')

    if not query :
        references = Reference.objects.all().order_by('name')
    else :
        references = Reference.objects.filter(name__icontains=query).order_by('name')

    context = {
        'references': references
    }
    
    return render(request, 'biblio/index.html', context)

@login_required
def board(request):

    user = request.user

    if Subscription.objects.filter(user=user).exists():
        sub = Subscription.objects.filter(user=user)
    
    else:
        sub = None

    context = {
        'subscription' : sub
    }
    
    return render(request, 'biblio/board.html', context)

@login_required
def booking(request):

    return render(request, 'biblio/booking.html', context)