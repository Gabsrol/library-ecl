from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import User, Reference, Subscription, Bad_borrower, Loan
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse 
from django.db.models import Q
from django.contrib import messages
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

    subscription = None
    sub_state = None
    # get user subscription
    if Subscription.objects.filter(user__email=user.email).exists():
        subscription = Subscription.objects.get(user__email=user.email)
        if subscription.ending_date>datetime.date.today():
            sub_state = 'valid'
        else :
            sub_state = 'expired'


    # calculate subscription price
    price = 'Demi-tarif'
    if user.social_status=='AU':
        price = 'Plein Tarif'
    
    if user.social_status=='CH':
        price = 'Gratuit'

    # get user borrowings
    borrowings = Loan.objects.filter(user__email=user.email)
    not_returned_borrowings = Loan.objects.filter(user__email=user.email).filter(returned=False)

    if request.method == 'POST':
        
        user.balance=0
        user.save()
        messages.success(request, f"Votre solde a été réglé")
        return HttpResponseRedirect(reverse('biblio:board'))


    context = {
        'sub_state' : sub_state,
        'subscription' : subscription,
        'borrowings' : borrowings,
        'not_returned_borrowings': not_returned_borrowings,
        'price' : price,
        'solde' : user.balance,
    }
    
    return render(request, 'biblio/board.html', context)

@login_required
def booking(request, reference_id):

    # get reference object
    reference = get_object_or_404(Reference, pk=reference_id)

    # get user object
    user = request.user


    today = datetime.date.today()
    valid_subscriptions_users = Subscription.objects.filter(ending_date__gte=today).values_list('user__email',flat=True)
    # check if the user has a subscription
    if user.email not in valid_subscriptions_users:
        return HttpResponseRedirect(reverse('biblio:no_subscription'))



    # check if the user can borrow this type of reference
    if reference.ref_type=='BK':
        # books borrowing by the user
        nb_books_not_returned = Loan.objects.filter(
                user__email=user.email
            ).filter(
                Q(returned=False) 
                & 
                Q(reference__ref_type='BK')
            ).count() 
        
        # check if is borrowing less than 3 books
        if nb_books_not_returned>=3:
            messages.warning(request, f"Vous ne pouvez pas emprunter plus de 3 livres désolé.")
            return HttpResponseRedirect(reverse('index'))
    else:
        # reviews borrowing by the user
        nb_reviews_not_returned = Loan.objects.filter(
                user__email=user.email
            ).filter(
                Q(returned=False)
            ).exclude(
                Q(reference__ref_type='BK')
            ).count() 

        # check if is borrowing less than 2 reviews
        if nb_reviews_not_returned>=2:
            messages.warning(request, f"Vous ne pouvez pas emprunter plus de 2 revues désolé.")
            return HttpResponseRedirect(reverse('index'))


    if request.method == 'POST':
        loan = Loan(
            user=user,
            reference=reference,
            beginning_date = datetime.date.today(),
            ending_date = datetime.date.today() + datetime.timedelta(days=30)
            )
        loan.save()
        messages.success(request, f"Votre emprunt a bien été pris en compte")
        return HttpResponseRedirect(reverse('index'))

    context = {
        'reference': reference,
    }

    return render(request, 'biblio/booking.html', context)


@login_required
def no_subscription(request):

    context = {
        
    }
    
    return render(request, 'biblio/no_subscription.html', context)

@login_required
def subscribe(request):

    # get user object
    user = request.user


    # check if the user is not a bad borrower
    if user.email not in Bad_borrower.objects.all().values_list('user__email',flat=True):
        messages.warning(request, f"Vous faites partis de la liste mauvais emprunteurs. Vous ne pouvez pas prendre d'abonnements")
        return HttpResponseRedirect(reverse('biblio:index'))

    # calculate subscription price
    price = 'Demi-tarif'
    if user.social_status=='AU':
        price = 'Plein Tarif'
    
    if user.social_status=='CH':
        price = 'Gratuit'

    
    # create or modify subscription
    if request.method == 'POST':

        if Subscription.objects.filter(user__email=user.email).exists():
            subscription = Subscription.objects.get(user__email=user.email)
            subscription.ending_date = datetime.date.today() + datetime.timedelta(weeks=52)
            subscription.save()
            
        else:
            subscription = Subscription(
                user = user,
                ending_date = datetime.date.today() + datetime.timedelta(weeks=52)
            )
            subscription.save()

        messages.success(request, f"Votre abonnement a bien été pris en compte")
        return HttpResponseRedirect(reverse('index'))

    context = {
        'price':price,
    }
    
    return render(request, 'biblio/subscribe.html', context)