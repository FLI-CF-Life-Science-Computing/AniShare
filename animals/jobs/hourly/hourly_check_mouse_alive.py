from django_extensions.management.jobs import HourlyJob


class Job(HourlyJob):
    help = ""


    def execute(self):
        from django.core import management
        from ...models import Animal, MouseAll, PupAll
        from django.core.mail import EmailMultiAlternatives, send_mail
        from datetime import datetime, timedelta
        from django.conf import settings
        from django.core.signing import Signer
        from django.core.mail import EmailMultiAlternatives, send_mail
        from django.template.loader import render_to_string
        from django.core.mail import EmailMessage
        from django.conf import settings
        import logging
        import sys

        mousedb = 'mousedb'
        logger = logging.getLogger('myscriptlogger')
        TIMEDIFF = getattr(settings, "TIMEDIFF", 2)
        try:
            animallist = Animal.objects.filter(new_owner__isnull =True).filter(available_from__lte = datetime.now().date()).filter(available_to__gte = datetime.now().date()).order_by('available_to')
            for animouse in animallist: # for all animals that are available now
                if animouse.mouse_id: # if mouse_id is present
                    if MouseAll.objects.using(mousedb).filter(id=animouse.mouse_id).filter(state='live').exists(): # if mouse is alive
                        continue
                    else:
                        animouse.available_to = datetime.now().date() - timedelta(days=1)
                        animouse.comment = '{}\n{}: Mouse is no longer alive or at the institute'.format(animouse.comment, datetime.now())
                        animouse.save()
                        logger.debug('{}: Mouse {} is no longer alive.'.format(datetime.now(),animouse.mouse_id))
                if animouse.pup_id: # if pup_id is present
                    if PupAll.objects.using(mousedb).filter(id=animouse.pup_id).filter(state='live').exists(): # if mouse is alive
                        continue
                    else:
                        if MouseAll.objects.using(mousedb).filter(eartag=animouse.database_id).filter(state='live').exists():
                            continue
                        else:
                            animouse.available_to = datetime.now().date()
                            animouse.comment = '{}\n{}: Pup is no longer alive or at the institute'.format(animouse.comment, datetime.now())
                            animouse.save()
                            logger.debug('{}:Pup {} is no longer alive.'.format(datetime.now(),animouse.pup_id))

        except BaseException as e:  
            logger.error('{}: AniShare Scriptfehler hourly_check_check_mouse_alive.py: Fehler {} in Zeile {}'.format(datetime.now(),e, sys.exc_info()[2].tb_lineno)) 
            ADMIN_EMAIL = getattr(settings, "ADMIN_EMAIL", None)
            send_mail("AniShare Importscriptfehler hourly_check_status_incidents.py", 'Fehler {} in Zeile {}'.format(e,sys.exc_info()[2].tb_lineno), ADMIN_EMAIL, [ADMIN_EMAIL])
            
        management.call_command("clearsessions")