from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import User, Reference, Subscription, Bad_borrower, Loan
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse 
import datetime
  

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
def booking(request, reference_id):

    reference = get_object_or_404(Reference, pk=reference_id)

    if request.method == 'POST':
        loan = Loan(
            user=request.user,
            reference=reference,
            beginning_date = datetime.date.today(),
            ending_date = datetime.date.today() + datetime.timedelta(weeks=4)
            )
        loan.save()
        return HttpResponseRedirect(reverse('index'))

    context = {
        'reference': reference,
    }

    return render(request, 'biblio/booking.html', context)