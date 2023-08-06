from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model 
from django.core.signing import TimestampSigner
from django.core.urlresolvers import reverse
from ...views import login

class Command(BaseCommand):
    args = 'USERNAME_FIELD value'
    help = 'Cloak yourself as a user using a URL'

    def handle(self, *args, **options):
        user_model = get_user_model()
        user = user_model.objects.get_by_natural_key(args[0])

        signer = TimestampSigner()
        signature = signer.sign(str(user.pk))

        print(reverse(login, args=(signature,)))
