from django.contrib.auth.signals import user_logged_in
from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    firstname = models.CharField(max_length=255, verbose_name=_('firstname'))
    lastname = models.CharField(max_length=255, verbose_name=_('lastname'))

    def primary_address(self):
        found = None
        adresses = self.saved_adresses()
        for address in adresses:
            if address.is_main:
                found = address

        if found or len(adresses) == 0:
            return found

        return adresses[0]


    def saved_adresses(self):
        return self.adresses.filter(temporary=False)

    def __unicode__(self):
        return '%s %s <%s>' % (self.firstname, self.lastname, self.user.email)




def create_user_profile(user, **kwargs):

    try:
        user.get_profile()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=user)

user_logged_in.connect(create_user_profile, sender=User)

