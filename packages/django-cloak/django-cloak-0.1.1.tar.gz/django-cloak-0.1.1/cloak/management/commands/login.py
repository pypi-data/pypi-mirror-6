from __future__ import print_function
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model 
from django.core.signing import TimestampSigner
from django.core.urlresolvers import reverse
from django.core.exceptions import FieldError
from ...views import login

class Command(BaseCommand):
    args = '[USERNAME_FIELD value]'
    help = 'Login as a user using a temporary URL'

    def handle(self, *args, **options):
        """
        With no arguments, find the first user in the system with the is_admin
        flag set to true, or just the first user in the system period.

        With a single argument, look for the user with that value as the
        USERNAME_FIELD value.

        When a user is found, print out a URL slug you can paste into your
        browser to login as the user.
        """
        user_model = get_user_model()

        if len(args) == 0:
            # find the first admin user, or the first user ordered by PK
            try:
                user_model.objects.filter(is_admin=True).order_by("pk").first()
            except FieldError as e:
                # now just try to get first user ordered by pk 
                user = user_model.objects.all().order_by("pk").first()

            if user is None:
                raise CommandError("No users found!")

        elif len(args) == 1:
            # find the user with the USERNAME_FIELD equal to the command line
            # argument
            try:
                user = user_model.objects.get_by_natural_key(args[0])
            except user_model.DoesNotExist as e:
                raise CommandError("The user does not exist")
        else:
            raise CommandError("You passed me too many arguments")

        signer = TimestampSigner()
        signature = signer.sign(str(user.pk))

        print(reverse(login, args=(signature,)))
