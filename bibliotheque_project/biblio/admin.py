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

from biblio.models import User, Reference, Subscription, Bad_borrower, Loan

######### User ###########

# a form to create a new user
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)
    
    test = forms.CharField(label="L'utilisateur a-t-il bien payé?", widget=forms.CheckboxInput)

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
        fields = ('email', 'password',  'first_name', 'last_name', 'social_status', 'is_active', 'is_admin')

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
    list_display = ('email',  'first_name', 'last_name', 'social_status', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ( 'first_name', 'last_name', 'social_status',)}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email',  'first_name', 'last_name', 'social_status', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

######### Reference ###########

class ReferenceAdmin(admin.ModelAdmin):
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
    user = forms.ModelMultipleChoiceField(queryset=only_good_borrowers,widget=forms.Select())


class SubscriptionAdmin(admin.ModelAdmin):
    # The form to add Subscription instances
    form = SubscriptionCreationForm

    # The fields to be used in displaying the Subscription model.
    list_display = ('user',  'beginning_date', 'ending_date')


######### Loan ###########

class LoanCreationForm(forms.ModelForm):
    """A form for creating new loan. Includes all the required
    fields, plus a repeated password."""

    # only reference borowable can be borrowed
    borrowable_ref = Reference.objects.filter(borrowable=True)
    reference = forms.ModelMultipleChoiceField(queryset=borrowable_ref,widget=forms.Select())

    # only users that have a subscription can borrow
    user = forms.ModelMultipleChoiceField(queryset=Subscription.objects.all(),widget=forms.Select())

class LoanAdmin(admin.ModelAdmin):
    # The fields to be used in displaying the Borrowed model.
    list_display = ('reference', 'user', 'beginning_date', 'ending_date')



class Bad_borrowerAdmin(admin.ModelAdmin):
    pass


# dire à Django quelle table afficher dans la partie admin
admin.site.register(Reference, ReferenceAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(Bad_borrower, Bad_borrowerAdmin)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
