from django_extensions.management.jobs import HourlyJob


class Job(HourlyJob):
    help = ""

    def execute(self):
        from django.core import management
        from ...models import FishTeamName, Fish, Animal
        from django.contrib.auth.models import User
        from django.core.mail import EmailMultiAlternatives, send_mail
        from datetime import datetime, timedelta
        from django.conf import settings
        import logging
        import sys
        import requests

        fishdb = 'fishdb_test'
        logger = logging.getLogger('myscriptlogger')
        ADMIN_EMAIL = getattr(settings, "ADMIN_EMAIL", None)
        TIMEDIFF = getattr(settings, "TIMEDIFF", 2)
        TICKATLAB_TEAM_AVAILABLE_ANIMALS = getattr(settings, "TICKATLAB_TEAM_AVAILABLE_ANIMALS", '')
        if TICKATLAB_TEAM_AVAILABLE_ANIMALS == '':
            logger.debug('TICKATLAB_TEAM_AVAILABLE_ANIMALS is not set in local_settings.py')
            send_mail("AniShare Importscriptfehler hourly_check_status_tickatlab_testsystem.py", 'TICKATLAB_TEAM_AVAILABLE_ANIMALS is not set in local_settings.py', ADMIN_EMAIL, [ADMIN_EMAIL])
            return
        try:
            fishteam = FishTeamName.objects.using(fishdb).get(name=TICKATLAB_TEAM_AVAILABLE_ANIMALS)
            if fishteam is None:
                logger.debug('TICKATLAB_TEAM_AVAILABLE_ANIMALS {} not found in FishTeamName'.format(TICKATLAB_TEAM_AVAILABLE_ANIMALS))
                send_mail("AniShare Importscriptfehler hourly_check_status_tickatlab_testsystem.py", 'TICKATLAB_TEAM_AVAILABLE_ANIMALS {} not found in FishTeamName'.format(TICKATLAB_TEAM_AVAILABLE_ANIMALS), ADMIN_EMAIL, [ADMIN_EMAIL])
                return
            fishlist_tickatlab = Fish.objects.using(fishdb).all().filter(teamid=fishteam.id).order_by('id')
            fishids_tickatlab = [fish.id for fish in fishlist_tickatlab]
            animals = Animal.objects.filter(animal_type='fish').filter(available_to__lt=datetime.now().date())
            for fish in animals:
                if fish.fish_id in fishids_tickatlab:
                    continue
                else:
                    logger.debug('Fish {} is no longer available in Tickatlab, setting available_to to today'.format(fish.fish_id))
                    fish.available_to = datetime.now().date()
                    fish.save()   

        except BaseException as e: 
            management.call_command("clearsessions")
            ADMIN_EMAIL = getattr(settings, "ADMIN_EMAIL", None)
            send_mail("AniShare Importscriptfehler hourly_check_status_tickatlab_testsystem.py", 'Fehler {} in Zeile {}'.format(e,sys.exc_info()[2].tb_lineno), ADMIN_EMAIL, [ADMIN_EMAIL])
        management.call_command("clearsessions")
