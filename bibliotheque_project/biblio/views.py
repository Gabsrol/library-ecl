from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import User, Reference, Subscription, Bad_borrower, Loan
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse 
from django.db.models import Q
import datetime
  

def index(request):

    query = request.GET.get('query')

    if not query :
        references = Reference.objects.all().order_by('name')
    else :
        references = Reference.objects.filter(Q(name__icontains=query) | Q(author__icontains=query)).order_by('name')

    not_available_references = references.filter(loan__returned=False).union(references.filter(borrowable=False))

    context = {
        'references': references,
        'not_available_references': not_available_references,
    }
    
    return render(request, 'biblio/index.html', context)

@login_required
def board(request):

    user = request.user

    # get user subscription
    if Subscription.objects.filter(user__email=user.email).exists():
        sub = Subscription.objects.get(user__email=user.email)
    
    else:
        sub = None

    # get user borrowings
    borrowings = Loan.objects.filter(user__email=user.email)
    not_returned_borrowings = Loan.objects.filter(user__email=user.email).filter(returned=False)

    context = {
        'subscription' : sub,
        'borrowings' : borrowings,
        'not_returned_borrowings': not_returned_borrowings,
    }
    
    return render(request, 'biblio/board.html', context)

@login_required
def booking(request, reference_id):

    # get reference object
    reference = get_object_or_404(Reference, pk=reference_id)

    # get user object
    user = request.user


    if request.method == 'POST':
        loan = Loan(
            user=user,
            reference=reference,
            beginning_date = datetime.date.today(),
            ending_date = datetime.date.today() + datetime.timedelta(days=30)
            )
        loan.save()
        return HttpResponseRedirect(reverse('index'))

    context = {
        'reference': reference,
    }

    return render(request, 'biblio/booking.html', context)