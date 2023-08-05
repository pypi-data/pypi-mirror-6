from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now

from signup.models import Validation

class Command(BaseCommand):
	help = 'Deletes expired user validation records'

	def handle(self, *args, **kwargs):
		activation_days = settings.SIGNUP_ACTIVATION_DAYS

		limit_time = now() - timedelta(days=activation_days)

		expired = Validation.objects.filter(created__lt=limit_time)
		for validation in expired:
			user = validation.user
			# cascade takes care of deleting validation
			user.delete()

