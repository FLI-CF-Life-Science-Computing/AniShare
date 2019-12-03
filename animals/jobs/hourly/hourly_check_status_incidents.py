from django_extensions.management.jobs import HourlyJob


class Job(HourlyJob):
    help = ""

    def execute(self):
        from django.core import management
        from ...models import WIncident, WIncident_write, WIncidentAnimals, Animal, Mouse, WIncidentcomment, WIncidentPups, Pup, WIncidentanimals_write, WIncidentpups_write
        from ...models import SacrificeIncidentToken
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
        mousedb_write = 'mousedb_write'
        LINES_PROHIBIT_SACRIFICE = getattr(settings, "LINES_PROHIBIT_SACRIFICE", None)
        logger = logging.getLogger('myscriptlogger')
        TIMEDIFF = getattr(settings, "TIMEDIFF", 2)
        try:
            today = datetime.now().date()
            incidentlist = WIncident.objects.using(mousedb).all().filter(incidentclass=22).filter(status=5)
            for incident in incidentlist:
                skip = 0
                error = 0
                i = 0
                animallist = WIncidentAnimals.objects.using(mousedb).filter(incidentid = incident.incidentid)
                puplist = WIncidentPups.objects.using(mousedb).filter(incidentid = incident.incidentid)
                count_mice = animallist.count()
                count_pups = puplist.count()
                count_animals = count_mice + count_pups
                for pyratmouse in animallist:
                    i = i + 1
                    try:
                        animouseFilter = Animal.objects.filter(mouse_id=pyratmouse.animalid)
                        if len(animouseFilter) == 0: # Check if pup has been weaned
                            if Mouse.objects.using(mousedb).filter(id = pyratmouse.animalid).exists():
                                v_mouse = Mouse.objects.using(mousedb).get(id = pyratmouse.animalid)
                            else:
                                continue
                            if Animal.objects.filter(database_id=v_mouse.eartag).exists():
                                animouse = Animal.objects.get(database_id=v_mouse.eartag)
                                animouse.mouse_id = v_mouse.id
                                animouse.save() # Save new animal_id (id changed because pup is now an adult)
                                skip = 1 # with the next run the script will find the pup with the mouse_id
                            else:
                                continue
                        else:
                            animouse = Animal.objects.get(mouse_id=pyratmouse.animalid)
                        if (animouse.new_owner):
                            logger.debug('anipup.new_owner=1')
                            continue
                        if (animouse.available_to >= today):
                            skip = 1
                            break
                    except BaseException as e: 
                            error = 1
                            skip = 1
                            ADMIN_EMAIL = getattr(settings, "ADMIN_EMAIL", None)
                            send_mail("AniShare Check Status Error", 'Fehler {} bei der Statusüberprüfung des Auftrags {} (Maus) in Zeile {}'.format( e, incident.incidentid, sys.exc_info()[2].tb_lineno), ADMIN_EMAIL, [ADMIN_EMAIL])
                for pyratpup in puplist:
                    i = i + 1
                    try:
                        anipupFilter = Animal.objects.filter(pup_id=pyratpup.pupid)
                        if len(anipupFilter) == 0:
                            continue
                        anipup = Animal.objects.get(pup_id=pyratpup.pupid)
                        if (anipup.new_owner):
                            continue
                        if (anipup.available_to >= today):
                            skip = 1
                            break
                    except BaseException as e:  
                            error = 1
                            skip = 1
                            ADMIN_EMAIL = getattr(settings, "ADMIN_EMAIL", None)
                            send_mail("AniShare Check Status Error", 'Fehler {} bei der Statusüberprüfung des Auftrags {} (Pup) in Zeile {}'.format( e, incident.incidentid,sys.exc_info()[2].tb_lineno), ADMIN_EMAIL, [ADMIN_EMAIL])
                if (skip == 0 and i == count_animals):
                    incident_write = WIncident_write.objects.using(mousedb_write).get(incidentid=incident.incidentid)
                    incident_write.status = 1
                    incident_write.closedate = datetime.now()
                    incident_write.save(using=mousedb_write)
                    logger.debug('{}: Incident status {} has been changed to 1.'.format(datetime.now(), incident.incidentid))
                    new_comment = WIncidentcomment()
                    new_comment.incidentid = incident
                    new_comment.comment = 'AniShare: Request status changed to closed'
                    new_comment.save(using=mousedb_write) 
                    new_comment.commentdate = new_comment.commentdate + timedelta(hours=TIMEDIFF)
                    new_comment.save(using=mousedb_write)
                    """if incident.sacrifice_reason:

                        # save token and send to Add to AniShare initiator to create sacrifice request
                        new_sacrifice_incident_token            = SacrificeIncidentToken()
                        new_sacrifice_incident_token.initiator  = incident.initiator.username
                        new_sacrifice_incident_token.incidentid = incident.incidentid
                        signer = Signer()
                        new_sacrifice_incident_token.urltoken   = signer.sign("{}".format(incident.incidentid))
                        new_sacrifice_incident_token.save()
                        
                        # Send email to initiator to confirm sacrifice request
                        animallist = Animal.objects.filter(pyrat_incidentid = incident.incidentid)
                        i = 0
                        for animal in animallist:
                            if animal.new_owner:
                                animallist = animallist.exclude(pk=animal.pk)
                            if animal.line in LINES_PROHIBIT_SACRIFICE:
                                animallist = animallist.exclude(pk=animal.pk) 
                            i = i + 1
                        if len(animallist) > 0:
                            initiator_name = "{} {}".format(incident.initiator.firstname,incident.initiator.lastname)
                            sacrifice_link = "{}/{}/{}".format(settings.DOMAIN,"confirmsacrificerequest",new_sacrifice_incident_token.urltoken)
                            message = render_to_string('email_animals_sacrifice.html',{'animals':animallist, 'initiator':initiator_name, 'sacrifice_link':sacrifice_link})
                            subject = "Confirmation sacrifice request"
                            recipient = incident.initiator.email
                            msg = EmailMessage(subject, message, "tierschutz@leibniz-fli.de", [recipient])
                            msg.content_subtype = "html"
                            msg.send()"""
                 
        except BaseException as e:  
            logger.error('{}: AniShare Importscriptfehler hourly_check_status_incidents.py: Fehler {} in Zeile {}'.format(datetime.now(),e, sys.exc_info()[2].tb_lineno)) 
            ADMIN_EMAIL = getattr(settings, "ADMIN_EMAIL", None)
            send_mail("AniShare Importscriptfehler hourly_check_status_incidents.py", 'Fehler {} in Zeile {}'.format(e,sys.exc_info()[2].tb_lineno), ADMIN_EMAIL, [ADMIN_EMAIL])
        management.call_command("clearsessions")