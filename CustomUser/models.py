from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

# Custom user manager
class PSUCustomUserManager(BaseUserManager):
    def create_user(self, username, password=None):
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(psu_uuid=username)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        user = self.create_user(username,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


# Create your models here.
class PSUCustomUser(AbstractBaseUser):
    psu_uuid = models.CharField(unique=True, max_length=36, db_index=True)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = PSUCustomUserManager()

    USERNAME_FIELD = 'psu_uuid'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        # For this case we return email. Could also be User.first_name User.last_name if you have these fields
        return self.psu_uuid

    def get_short_name(self):
        # For this case we return email. Could also be User.first_name if you have this field
        return self.psu_uuid

    def __unicode__(self):
        return self.psu_uuid

    def has_perm(self, perm, obj=None):
        # Handle whether the user has a specific permission?"
        return True

    def has_module_perms(self, app_label):
        # Handle whether the user has permissions to view the app `app_label`?"
        return True

    @property
    def is_staff(self):
        # Handle whether the user is a member of staff?"
        return self.is_admin