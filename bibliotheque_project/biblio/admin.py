# This code is used to manage the display of the library admins. 
# For each table we have: 
# an instance creation class, an instance modification class 
# and a class adding information to the table.


from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models import F
import datetime


from biblio.models import User, Reference, Subscription, Bad_borrower, Loan


######### Reference ###########

class ReferenceCreationForm(forms.ModelForm):
    """A form for creating new references."""
    pass

class ReferenceAdmin(admin.ModelAdmin):
    form = ReferenceCreationForm
    list_display = ('name',  'author', 'publish_date', 'ref_type', 'borrowable')







######### Subscription ###########

# a form to create a subscription
class SubscriptionCreationForm(forms.ModelForm):
    """A form for creating new subscriptions."""

    # a field to be sure that the admin has been paid by the user
    payment = forms.BooleanField (label="L'utilisateur a-t-il bien payé?",required=True)

    # only users that aren't bad borrowers can have a subscription
    bad_borrowers = Bad_borrower.objects.all()
    only_good_borrowers = User.objects.exclude(pk__in=bad_borrowers)
    user = forms.ModelChoiceField(queryset=only_good_borrowers,widget=forms.Select())

    # validation of all fields
    def clean(self):
        cleaned_data = super().clean()

        beginning_date = cleaned_data.get("beginning_date")
        ending_date = cleaned_data.get("ending_date")
        
        # check if the ending_date is 30 days after beginning date
        if ending_date!=(datetime.timedelta(weeks=52)+beginning_date):
            self.add_error('ending_date', "La durée d'un abonnement est d'1 an")

        return cleaned_data


class SubscriptionAdmin(admin.ModelAdmin):
    # The form to add Subscription instances
    form = SubscriptionCreationForm

    # The fields to be used in displaying the Subscription model.
    list_display = ('user',  'beginning_date', 'ending_date')

# to add a subscription info on user profil
class SubscriptionInline(admin.TabularInline):
    model = Subscription 
    readonly_fields = ["ending_date", "beginning_date"]










######### Loan ###########

class LoanCreationForm(forms.ModelForm):
    """A form for creating new loan. Includes all the required
    fields"""

    class Meta:
        model = Loan
        #fields = '__all__'
        exclude = ('returned',)

    ###### we don't use it here to allow
    # validation of beginning_date
    #def clean_beginning_date(self):

    #    date = self.cleaned_data["beginning_date"]

        # check if the beginning date is superioir to today
    #    today = datetime.date.today()
    #    if date<today:
    #        raise ValidationError(
    #                "La date de début d'emprunt doit être postérieure à la date du jour"
    #            )

    #    return date

    # validation of all fields
    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        reference = cleaned_data.get("reference")
        beginning_date = cleaned_data.get("beginning_date")
        ending_date = cleaned_data.get("ending_date")

        # check if the user has a subscription
        today = datetime.date.today()
        valid_subscriptions_users = Subscription.objects.filter(ending_date__gte=today).values_list('user__email',flat=True)
        
        if user.email not in valid_subscriptions_users:
            self.add_error('user',
                    "Cet utilisateur n'a pas d'abonnement à jour"
                )

        # check if the book can be borrowed
        not_borrowable_ref = Reference.objects.filter(loan__returned=False).union(Reference.objects.filter(borrowable=False)).values_list('name',flat=True)
        if reference.name in not_borrowable_ref:
            self.add_error('reference', "Ce livre n'est pas disponible pour le moment")
            

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
                self.add_error('reference', "Cet utilisateur emprunte déjà 3 livres")
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
                self.add_error('reference', "Cet utilisateur emprunte déjà 2 revues")

        # check if the ending_date is 30 days after beginning date
        if ending_date!=(datetime.timedelta(days=30)+beginning_date):
            self.add_error('ending_date', "La durée d'un emprunt est de 30 jours")

        return cleaned_data


class LoanAdmin(admin.ModelAdmin):
    # The form to add Subscription instances
    form = LoanCreationForm

    # The fields to be used in displaying the Borrowed model.
    list_display = ('reference', 'user', 'beginning_date', 'ending_date','returned')

    actions = ['return_loan']

    # function to return one or several selected references
    def return_loan(modeladmin, request, queryset):
        for q in queryset:
            # if not already returned
            if not q.returned:
                q.returned='True' #mark as returned
                q.save()

    return_loan.short_description = "Retourner les ouvrages sélectionnés"


# to add a user borrowings on user profil
class LoanInline(admin.TabularInline):
    model = Loan 

    readonly_fields = ["reference","beginning_date","ending_date","returned"]

    def has_add_permission(self, request, s):
        return False

    def has_delete_permission(self, request, s):
        return False








######### Bad_borrower ###########

class Bad_borrowerAdmin(admin.ModelAdmin):
    pass

class Bad_borrowerInline(admin.TabularInline):
    model = Bad_borrower
    readonly_fields = ["ending_date"]


######### User ###########

# a form to create a new user
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'social_status')


    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# a form to modify a user
class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password',  'first_name', 'last_name', 'social_status', 'is_active', 'is_admin','balance')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


# class userAdmin to control what is print for this model
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email',  'first_name', 'last_name', 'social_status', 'is_admin','balance')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ( 'first_name', 'last_name', 'social_status','balance')}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


    actions = ['pay_balance']
    inlines = [SubscriptionInline,LoanInline,Bad_borrowerInline]

    # function to return one or several selected references
    def pay_balance(modeladmin, request, queryset):
        for q in queryset:
            
            q.balance=0
            q.save()
            
    pay_balance.short_description = "Marquer que l'utilisateur à régler son solde"



# dire à Django quelle table afficher dans la partie admin
admin.site.register(Reference, ReferenceAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(Bad_borrower, Bad_borrowerAdmin)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
