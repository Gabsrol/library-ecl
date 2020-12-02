from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


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

#la classe ouvrage
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



class Subscription(models.Model):
    beginning_date = models.DateField(default=timezone.now())
    ending_date = models.DateField(default=(datetime.timedelta(weeks=52)+timezone.now()))
    #A priori le one-to-one accepte le one-to-zero : un client peut avoir un abonnement / un abonnement est forcément lié à un client
    user = models.OneToOneField(User, on_delete=models.CASCADE, default="")

    def __str__(self):
        return self.user.email



class Loan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="")
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE, default="")
    beginning_date = models.DateField()
    ending_date = models.DateField()
    returned = models.BooleanField(default = False)

    def __str__(self):
        return self.reference.name



class Bad_borrower(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default="")
    ending_date = models.DateField(default=datetime.timedelta(weeks=101)+timezone.now())

    def __str__(self):
        return self.user.email

    # override save method to delete subscription when we add a bad_borrower
    def save(self, *args, **kwargs):
        
        # check if the user had a subscription
        if Subscription.objects.filter(user__email=self.user.email).exists():
            Subscription.objects.get(user__email=self.user.email).delete()

        super().save(*args, **kwargs)  # Call the "real" save() method.
