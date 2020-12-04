from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.db.models import F


class MyUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, social_status, password=None):
        """
        Creates and saves a User with the given email, first_name, last_name, social_status
        and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            social_status=social_status,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, social_status, password=None):
        """
        Creates and saves a superuser with the given email, first_name, last_name, social_status
        and password.
        """
        user = self.create_user(
            email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            social_status=social_status,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    SOCIAL_STATUS = (
        ('CH', 'Chômeur'),
        ('ET', 'Étudiant'),
        ('SR', 'Senior'),
        ('ML', 'Militaire'),
        ('AU', 'Autre'),
    )
    social_status = models.CharField(max_length=2, choices=SOCIAL_STATUS, default='AU')
    first_name = models.CharField(max_length=60, default='first_name')
    last_name = models.CharField(max_length=60, default='last_name')
    balance = models.IntegerField(default=0, verbose_name="Solde €")

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'social_status',]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin





class Reference(models.Model):
    author = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    publish_date = models.DateField()

    REF_TYPE = (
        ('BK', 'Livre'),
        ('RV', 'Revue'),
        ('CD', 'CD'),
        ('BD', 'BD'),
        ('DVD', 'DVD'),
    )
    ref_type = models.CharField(max_length=3, choices=REF_TYPE, default='BK')
    borrowable = models.BooleanField(default=False) 

    def __str__(self):
        return self.name


def now_plus_1_year():
    return(timezone.timedelta(weeks=52) + timezone.now())

class Subscription(models.Model):
    beginning_date = models.DateField(default=timezone.now)
    ending_date = models.DateField(default=now_plus_1_year)
    #A priori le one-to-one accepte le one-to-zero : un client peut avoir un abonnement / un abonnement est forcément lié à un client
    user = models.OneToOneField(User, on_delete=models.CASCADE, default="")

    def __str__(self):
        return self.user.email


def now_plus_30_days():
    return(timezone.timedelta(days=30) + timezone.now())

class Loan(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="")
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE, default="")
    beginning_date = models.DateField(default=timezone.now)
    ending_date = models.DateField(default=now_plus_30_days)
    returned = models.BooleanField(default = False)


    # to keep in memory the last value of returned because we want to make an action when returned changes from False to True
    __original_returned = None

    def __init__(self, *args, **kwargs):
        super(Loan, self).__init__(*args, **kwargs)
        self.__original_returned = self.returned
        

    # override save method to apply penalties or add bad borrower
    def save(self, *args, **kwargs):

        if self.returned:
            if self.__original_returned!=self.returned:
                today = datetime.date.today()
                # apply penalties if the book is returned 3 days later
                if (today-datetime.timedelta(days=3))>self.ending_date:
                    self.user.balance -= abs((today - self.ending_date).days)
                    self.user.save()

                self.ending_date = datetime.date.today() #change ending date to today
                # add to bad borrowers if it is the third time he is late
                nb_lates = Loan.objects.filter(
                        user=self.user # find the user
                    ).filter(
                        ending_date__gt=F('beginning_date')+datetime.timedelta(days=30) # ref returned in late
                    ).filter(
                        beginning_date__gte=today-datetime.timedelta(weeks=52) # only last year borrowings
                    ).count()

                if nb_lates>=3:
                    # test if the user has already been a bad borrower
                    if Bad_borrower.objects.filter(user=self.user).exists():
                        bad_user = Bad_borrower.objects.get(user=self.user)
                        bad_user.ending_date = today+datetime.timedelta(weeks=101)

                    else :
                        bad_user = Bad_borrower.objects.create(user=self.user)
                    bad_user.save()
        
        super().save(*args, **kwargs)  # Call the "real" save() method.
        self.__original_returned = self.returned


    def __str__(self):
        return self.reference.name


def now_plus_2_year():
    return(timezone.timedelta(weeks=101) + timezone.now())

class Bad_borrower(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default="")
    ending_date = models.DateField(default=now_plus_2_year)

    def __str__(self):
        return self.user.email

    # override save method to delete subscription when we add a bad_borrower
    def save(self, *args, **kwargs):
        
        # check if the user had a subscription
        if Subscription.objects.filter(user__email=self.user.email).exists():
            Subscription.objects.get(user__email=self.user.email).delete()

        super().save(*args, **kwargs)  # Call the "real" save() method.
