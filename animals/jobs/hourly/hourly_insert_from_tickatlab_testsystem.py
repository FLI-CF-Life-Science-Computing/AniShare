from django_extensions.management.jobs import HourlyJob


class Job(HourlyJob):
    help = ""

    def execute(self):
        from django.core import management
        from ...models import FishTeamName, Fish, Animal, FishMutation, Location, Person, Lab, FishTagIndexRecord, FishTagRecord
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
            send_mail("AniShare Importscriptfehler hourly_insert_from_tickatlab_testsystem.py", 'TICKATLAB_TEAM_AVAILABLE_ANIMALS is not set in local_settings.py', ADMIN_EMAIL, [ADMIN_EMAIL])
            return
        try:
            # Get the tickatlab team from the tickatlab for offering fish in AniShare
            fishteam = FishTeamName.objects.using(fishdb).get(name=TICKATLAB_TEAM_AVAILABLE_ANIMALS)
            if fishteam is None:
                logger.debug('TICKATLAB_TEAM_AVAILABLE_ANIMALS {} not found in FishTeamName'.format(TICKATLAB_TEAM_AVAILABLE_ANIMALS))
                send_mail("AniShare Importscriptfehler hourly_insert_from_tickatlab_testsystem.py", 'TICKATLAB_TEAM_AVAILABLE_ANIMALS {} not found in FishTeamName'.format(TICKATLAB_TEAM_AVAILABLE_ANIMALS), ADMIN_EMAIL, [ADMIN_EMAIL])
                return
            # Get all fish from the tickatlab team and check if they are already in AniShare. If not, insert them into AniShare.
            fishlist = Fish.objects.using(fishdb).all().filter(teamid=fishteam.id).order_by('id')
            fishids = [fish.id for fish in fishlist] # Save only the fish ids
            imported_fish_list = Animal.objects.filter(animal_type='fish').filter(fish_id__in=fishids) # Get all fish that are already in AniShare
            imported_fish_ids = []
            for animal in imported_fish_list:
                #print('Fish {} is already in AniShare'.format(animal.fish_id))
                imported_fish_ids.append(int(animal.fish_id))
                if animal.available_to < datetime.now().date(): # If the fish is already in AniShare but not available anymore, set the available_to date to today + 365 days and add a comment to the animal.
                    info = 'Previous availability: from {} to {}'.format(animal.available_from,animal.available_to)
                    animal.comment = "{}\n{}".format(animal.comment, info)
                    animal.available_to = datetime.now().date() + timedelta(days=365)
                    animal.save()

            fish_ids_left = set(fishids) - set(imported_fish_ids) # Get the fish ids that are not yet in AniShare
            for fish_id in fish_ids_left:
                fish = Fish.objects.using(fishdb).get(id=fish_id)
                animal = Animal()
                animal.animal_type = 'fish'
                animal.fish_id = str(fish.id)
                if (fish.identifier1 != ""):
                    animal.database_id = fish.animalnumber+"//"+fish.identifier1
                else:
                    animal.database_id    = fish.animalnumber
                animal.lab_id         = animal.database_id
                animal.amount         = fish.quantity
                animal.available_from = datetime.now().date()
                animal.available_to = datetime.now().date() + timedelta(days=365)
                animal.licence_number = fish.license
                animal.day_of_birth   = fish.dob
                animal.comment        = fish.tag
                if fish.specie == 40291147:   # It is a Notobranchius
                    animal.fish_specie = 'n'
                elif fish.specie == 40291120:
                    animal.fish_specie = 'z' # It is a Zebra fish
                fishmutations          = FishMutation.objects.using(fishdb).filter(referenceid = fish.id)
                animal.mutations = ''
                for m in fishmutations:
                        animal.mutations  = animal.mutations + m.description + ' ' + m.genotype + '; '
                try:
                    animal.location       = Location.objects.get(name=fish.location)
                except Location.DoesNotExist:
                    new_location = Location()
                    new_location.name = fish.location
                    new_location.save()
                    animal.location       = Location.objects.get(name=fish.location)
                animal.line           = fish.strain
                try:        
                    animal.responsible_person = Person.objects.get(name=fish.responsible)
                except Person.DoesNotExist:
                    new_person = Person()
                    new_person.name = fish.responsible
                    new_person.email = fish.responsible_email
                    new_person.responsible_for_lab = Lab.objects.get(name="False")
                    new_person.save()
                    animal.responsible_person = Person.objects.get(name=fish.responsible)
                    send_mail("AniShare neue Person", 'Neue Person in AniShare {}'.format(new_person.name), ADMIN_EMAIL, [ADMIN_EMAIL])
                if (fish.sex == 1):
                    animal.sex = 'm'
                elif (fish.sex == 2):
                    animal.sex = 'f'
                elif (fish.sex == 0):
                    animal.sex = 'u'
                animal.save()

                new_tag_index_record = FishTagIndexRecord()
                new_tag_index_record.tag = 'anishare importiert '+datetime.now().strftime("%d.%m.%Y")
                new_tag_index_record.objectid = fish.id
                new_tag_index_record.typename = 'Atune.Data.Tickatlab.Breeding.Model.Animal'
                new_tag_index_record.color = 16777215
                new_tag_index_record.save(using=fishdb)



        except BaseException as e: 
            management.call_command("clearsessions")
            ADMIN_EMAIL = getattr(settings, "ADMIN_EMAIL", None)
            send_mail("AniShare Importscriptfehler hourly_insert_from_tickatlab_testsystem.py", 'Fehler {} in Zeile {}'.format(e,sys.exc_info()[2].tb_lineno), ADMIN_EMAIL, [ADMIN_EMAIL])
        management.call_command("clearsessions")
