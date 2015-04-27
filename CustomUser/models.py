from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


# Custom user manager
class PSUCustomUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(username=username)

        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(
            username,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


# Create your models here.
class PSUCustomUser(AbstractBaseUser):
    username = models.CharField(unique=True, max_length=36, db_index=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = PSUCustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "PSU User"
        verbose_name_plural = "PSU Users"

    def get_full_name(self):
        # For this case we return email. Could also be User.first_name User.last_name if you have these fields
        return self.username

    def get_short_name(self):
        # For this case we return email. Could also be User.first_name if you have this field
        return self.username

    def __unicode__(self):
        return self.username

    @staticmethod
    def has_perm(perm, obj=None):
        # Handle whether the user has a specific permission?"
        return True

    @staticmethod
    def has_module_perms(app_label):
        # Handle whether the user has permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        # Handle whether the user is a member of staff?"
        return self.is_admin

    def set_password(self, raw_password):
        # Passwords are not stored in user objects, auth is done in API calls
        self.set_unusable_password()