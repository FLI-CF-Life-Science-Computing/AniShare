"""
This file describes all the models in the database.
"""
from datetime import datetime
from django.urls import reverse
from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from simple_history.models import HistoricalRecords
from django_currentuser.middleware import (get_current_user, get_current_authenticated_user)
from django_currentuser.db.models import CurrentUserField


class Lab(models.Model):
    """
    Labs are only defined by a name and are referenced by
    Person(s) which are responsible (contact) person for this lab
    """
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name + ' Lab'
    def responsible_person(self):
        """
        Retrieve only the person(s) which are responsible for this lab.
        """
        persons = Person.objects.filter(responsible_for_lab=self)
        return ', '.join(i.name for i in persons)

class Person(models.Model):
    """
    The responsible (contact) person for each lab.
    This person gets an email when an animal is being claimed.
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    responsible_for_lab = models.ForeignKey(Lab, on_delete=models.CASCADE, default=1)
    def __str__(self):
        return self.name + ' (' + str(self.responsible_for_lab) + ')'

class Institution(models.Model):
    """
    Institution from which the animal/organ is offered
    """
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Location(models.Model):
    """
    Location of animals. Eg. animal house, fish facilities etc.
    """
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Change(models.Model):
    """
    Model for documentation all changes to anishare
    """
    change_type = models.CharField(max_length=100, choices=(
        ('new', 'new'),
        ('adaption', 'adaption'),
        ('bugfix', 'bugfix'),
        ('deletion', 'deletion'),
    ), default="adaption")
    version = models.CharField(max_length=200,)
    entry_date = models.DateField(null=False, auto_now_add=True)
    short_text = models.CharField(max_length=400,)
    description = models.TextField(blank=True, null=True,)
    image = models.ImageField(null=True, blank=True, upload_to='images/')
    
    """def __str__(self):
        return "{} {} {}, {} id:{} [{}]".format
        (self.version, self.change_type, self.short_text, self.description, self.pk, self.entry_date)
"""

    def get_absolute_url(self):
        """
        Get absolute url for this model. Important to link from the admin.
        """
        return "/changehistory/?id=%i" % self.pk


class Animal(models.Model):
    """
    Main model containing the animals.
    """
    amount = models.PositiveIntegerField(default=1, 
                                         help_text="How many fishs? (eg. fish in tank). If animal = mouse only one is possible")
    animal_type = models.CharField(max_length=100, choices=(
        ('fish', 'Fish'),
        ('mouse', 'Mouse'),
        ('pup', 'Pup'),
    ),
                                   default='mouse')
    database_id = models.CharField(max_length=200, null=True, blank=True, help_text="ID of animal in eg. PYRAT")
    fish_id = models.CharField(max_length=200, null=True, blank=True, help_text="DB ID of fish in tickatlab")
    mouse_id = models.CharField(max_length=200, null=True, blank=True, help_text="DB ID of mouse in PyRat")
    pup_id = models.CharField(max_length=200, null=True, blank=True, help_text="DB ID of pup in PyRat")
    lab_id = models.CharField(max_length=200, null=True, blank=True, help_text="ID of lab in eg. PYRAT")
    creation_date = models.DateTimeField(null=False, auto_now_add=True)
    modification_date = models.DateTimeField(null=False, auto_now=True)
    entry_date = models.DateField(null=False, auto_now_add=True)
    day_of_birth = models.DateField()
    fish_specie = models.CharField(max_length=20, null=True, blank=True, choices=(('n', 'Nothobranchius'), ('z', 'Zebrafish')),) 
    genetic_background = models.CharField(max_length=200,blank=True, null=True)
    line = models.CharField(max_length=200, help_text="genetic trait of animal")
    sex = models.CharField(max_length=2, choices=(('m', 'male'), ('f', 'female'), ('u', 'unknown')),
                           help_text='Select "unknown" if multiple animals.')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True, help_text="The institut where the animal is located")
    location = models.ForeignKey(Location, on_delete=models.CASCADE,
                                 help_text='Where is the animal housed?')
    mutations = models.TextField(blank=True, null=True,
                                 help_text="Describe the mutations with the grade of this line in as much detail as possible")
    grade = models.CharField(max_length=200, null=True, blank=True, help_text="")
    cage = models.CharField(null=True, blank=True,max_length=200, help_text="cage where the animal is located")
    medical_condition = models.CharField(max_length=1024, null=True, blank=True, help_text="Describe the medical health of the animal")
    """grade1 = models.CharField(max_length=10, null=True, choices=(
        ('+/+', '+/+'),
        ('+/0', '+/0'),
        ('-/+', '-/+'),
        ('-/-', '-/-'),
        ('-/0', '-/0'),
        ('0/fl', '0/fl'),
        ('fl/+', 'fl/+'),
        ('fl/-', 'fl/-'),
        ('fl/fl', 'fl/fl'),
        ('fl/tg', 'fl/tg'),
        ('ki/+', 'ki/+'),
        ('ki/fl', 'ki/fl'),
        ('ki/ki', 'ki/ki'),
        ('ko/+', 'ko/+'),
        ('ko/0', 'ko/0'),
        ('ko/ko', 'ko/ko'),
        ('tg/+', 'tg/+'),
        ('tg/?', 'tg/?'),
        ('tg/tg', 'tg/tg'),
        ('tki/+', 'tki/+'),
        ('tki/tki', 'tki/tki'),
        ('W41/+', 'W41/+'),
        ('W41/W41', 'W41/W41'),
        ('Wv/+', 'Wv/+'),
        ('Wv/Wv', 'Wv/Wv'),
        ('y/-', 'y/-'),
        ),help_text='Grade 1',)"""
    grade1 = models.CharField(max_length=10,blank=True, null=True,help_text='Grade 1')
    grade2 = models.CharField(max_length=10,blank=True, null=True,help_text='Grade 2')
    grade3 = models.CharField(max_length=10,blank=True, null=True ,help_text='Grade 3')
    grade4 = models.CharField(max_length=10,blank=True, null=True ,help_text='Grade 4')
    licence_paragraph11 = models.BooleanField(default=False,null=False, blank=False, verbose_name='§11 License') 
    licence_number = models.CharField(max_length=200, verbose_name='License number')
    responsible_person = models.ForeignKey(Person, related_name='rperson', on_delete=models.CASCADE, help_text='Person who is responsible in the lab for dealing with the animals')
    responsible_person2 = models.ForeignKey(Person, related_name='rperson2', null=True, blank=True, on_delete=models.CASCADE, 
                                            help_text='Second person who is responsible in the lab for dealing with the animals', verbose_name = "Second responsible person")
    #responsible_person = models.ManyToManyField(Person, related_name='Responsible_person', help_text='Person who is responsible in the lab for dealing with the animals')
    available_from = models.DateField()
    available_to = models.DateField() # default=datetime.today() + timedelta(days=15))
    comment = models.TextField(blank=True, null=True,
                               help_text='Comments, such as individual organs to be offered')
    new_owner = models.CharField(max_length=200, blank=True,
                                 help_text='Person claiming this animal for themselves') # turn into foreignkey to auth_users?
    added_by = models.ForeignKey(User, unique=False, on_delete=models.CASCADE, null=True)
    pyrat_incidentid = models.CharField(max_length=20, null=True, blank=True)
    #sync_with_other_sharing_system = models.BooleanField(default=False,null=False, blank=False) # If true the object can be syncronised with an other sharing platform 
    history = HistoricalRecords()

    def validate_amount(value):
        if (self.animal_type != 'fish' and value != 1):
            raise ValidationError('Only one mouse is possible')

    def clean(self):
        animal_type = self.animal_type
        amount = self.amount
        if (animal_type != 'fish' and amount != 1):
            raise ValidationError('Only one mouse is possible')

    def background(self):
        if self.genetic_background is None:
            return ("")
        else:
            return(self.genetic_background)

    def responsible_persons(self):
        if str(self.responsible_person2) != "None":
            return (str(self.responsible_person) + str(" ") +str(self.responsible_person2))
        return (self.responsible_person)

    def age(self):
        """
        Return the age of the animal, calculated by the difference to either
        the current date or the available_to date
        """
#        return int((self.entry_date - self.day_of_birth).days / 7)
        now = datetime.today().date()
        if now < self.available_to:
            return int((now - self.day_of_birth).days / 7)
        return int((self.available_to - self.day_of_birth).days / 7)

    def available(self):
        """
        Returns True if the animal is still available
        """
        today = datetime.now().date()
        return (self.available_from <= today) and (today <= self.available_to)

    def get_absolute_url(self):
        """
        Get absolute url for this model. Important to link from the admin.
        """
        return reverse('animals:claim', kwargs={'primary_key': self.pk})

    def __str__(self):
        return "{} {} {}, {} id:{} [{}]".format(
            self.amount, self.get_sex_display(), self.animal_type, self.line, self.pk, self.day_of_birth)

    def description(self):
        """
        Return description of this model
        """
        return "id:{}, lab_id:{}, available:{}-{}, location:{}, mutations:{}".format(
            self.database_id, self.lab_id, self.available_from,
            self.available_to, self.location, "".join(self.mutations))

class Organtype(models.Model):
    """
    Model containing the organ types
    """
    """ name = models.CharField(max_length=100, choices=(
        ('bladder', 'bladder'),
        ('bone marrow', 'bone marrow'),
        ('brain', 'brain'),
        ('genitals', 'genitals'),
        ('heart', 'heart'),
        ('intestine', 'intestine'),
        ('kidney', 'kidney'),
        ('liver', 'liver'),
        ('lungs', 'lungs'),
        ('spleen', 'spleen'),
        ('stomach', 'stomach'),
        ('other', 'other'),
        ),help_text='Organ type which is not available',)"""
    name = models.CharField(max_length=100,)
    class Meta:
        verbose_name = "presets for used organs"
        verbose_name_plural = "Organs used"
    def __str__(self):
        return self.name

class FishRole(models.Model):
    roleid= models.IntegerField(db_column='ROLEID',)
    userid = models.IntegerField(db_column='USERID',)

    class Meta:
        managed = False
        db_table = 'VUSERROLES'

class FishTeam(models.Model):
    teamid = models.IntegerField(db_column='TEAMID',)
    userid = models.IntegerField(db_column='USERID',)

    class Meta:
        managed = False
        db_table = 'VTEAM'

class FishPeople(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    login = models.CharField(db_column='LOGIN', max_length=255)
    firstname = models.CharField(db_column='FIRSTNAME', max_length=255)
    lastname = models.CharField(db_column='LASTNAME', max_length=255)
    mainteamid = models.IntegerField(db_column='MAINTEAMID')

    class Meta:
        managed = False
        db_table = 'VPERSON'

class Fish(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    animalnumber = models.CharField(db_column='ANIMALNUMBER', max_length=255, help_text="Anima-ID")
    identifier1 = models.CharField(db_column='IDENTIFIER1', max_length=255)
    identifier2 = models.CharField(db_column='IDENTIFIER2', max_length=255)
    identifier3 = models.CharField(db_column='IDENTIFIER3', max_length=255)
    identifier4 = models.CharField(db_column='IDENTIFIER4', max_length=255)
    #sex = models.IntegerField(db_column='SEX')
    sex = models.CharField(db_column='SEX', max_length=2, choices=(('1', 'male'), ('2', 'female'), ('0', 'unknown')),
                           help_text='Select "unknown" if multiple animals.')
    quantity = models.IntegerField(db_column='QUANTITY')
    dob = models.DateField(db_column='DOB')
    notes = models.CharField(db_column='NOTES', max_length=4000)
    responsible = models.CharField(db_column='RESPONSIBLE', max_length=512)
    responsible_email = models.CharField(db_column='RESPONSIBLE_EMAIL', max_length=512)
    location = models.CharField(db_column='LOCATION', max_length=4000)
    license = models.CharField(db_column='LICENSE', max_length=255)
    strain = models.CharField(db_column='STRAIN', max_length=255)
    teamid = models.CharField(db_column='TEAMID', max_length=255)
    teamname = models.CharField(db_column='TEAMNAME', max_length=255)
    mutation = models.CharField(db_column='MUTATION', max_length=511)
    tag = models.CharField(db_column='TAGS', max_length=1000)
    specie = models.IntegerField(db_column='SPECIESID', choices=(('40291147', 'Nothobranchius'), ('40291120', 'Zebrafish')),
                           help_text='Fish specie')

    def concatidentifier(self):
        if (self.identifier1 != ""):
            return(self.animalnumber+"//"+self.identifier1)
            #return(self.animalnumber)
        else:
            return(self.animalnumber)

    def age(self):
        """
        Return the age of the animal, calculated by the difference to either
        the current date or the available_to date
        """
        now = datetime.today().date()
        return int((now - self.dob).days / 7)

    class Meta:
        managed = False
        db_table = 'FISHS_ALIVE'

class PyratUser(models.Model):
    id = models.IntegerField(db_column='USERID', primary_key=True)
    username = models.CharField(db_column='USERNAME', max_length=255)
    firstname = models.CharField(db_column='FIRSTNAME', max_length=255)
    lastname = models.CharField(db_column='LASTNAME', max_length=255)
    #usernum = models.IntegerField(db_column='locallevel')
    locallevel = models.IntegerField(db_column='locallevel')
    email = models.CharField(db_column='EMAIL', max_length=255)

    class Meta:
        managed = False
        db_table = 'v_user'

class MouseMutation(models.Model):
    class Meta:
        managed = False
        db_table = 'v_mutation'
        unique_together = (('animalid', 'pupid'),)
    animalid          = models.IntegerField(db_column='animalid',primary_key=True)
    pupid             = models.IntegerField(db_column='pupid')
    mutation_name     = models.CharField(db_column='mutation_name', max_length=255)
    grade_name        = models.CharField(db_column='grade_name', max_length=255)
    

class PyratProject(models.Model):
    id      = models.IntegerField(db_column='id', primary_key=True)
    name    = models.CharField(db_column='name', max_length=100)
    status  = models.CharField(db_column='status', max_length=10, choices=(('active', 'active'), ('inactive', 'inactive')))
    class Meta:
        managed = False
        db_table = 'project'
        
class Mouse(models.Model):
    id      = models.IntegerField(db_column='animalid', primary_key=True)
    eartag  = models.CharField(db_column='eartag', max_length=255)
    sex = models.CharField(db_column='sex', max_length=2, choices=(('m', 'male'), ('f', 'female'), ('u', 'unknown')),
                           help_text='Select "unknown" if multiple animals.')
    dob = models.DateField(db_column='dateborn')
    #notes = models.CharField(db_column='NOTES', max_length=4000)
    responsible = models.CharField(db_column='fullname', max_length=512)
    #responsible_firstname = models.CharField(db_column='firstname', max_length=512)
    #responsible_lastname = models.CharField(db_column='lastname', max_length=512)
    responsible_email = models.CharField(db_column='email', max_length=512)
    location = models.CharField(db_column='building', max_length=4000)
    licence = models.CharField(db_column='licence', max_length=255)
    strain = models.CharField(db_column='strain', max_length=255)
    labid = models.CharField(db_column='labid', max_length=255)
    genetic_bg = models.CharField(db_column='genetic_bg', max_length=255)
    owner_id = models.IntegerField(db_column='owner_id',)
    owner = models.CharField(db_column='owner', max_length=255)
    mutation = models.CharField(db_column='mutation', max_length=512)
    project = models.CharField(db_column='projectname', max_length=512)
    medical_condition = models.CharField(db_column='medical_condition', max_length=1024)

    def age(self):
        """
        Return the age of the animal, calculated by the difference to either
        the current date or the available_to date
        """
        now = datetime.today().date()
        return int((now - self.dob).days / 7)

    class Meta:
        managed = False
        db_table = 'v_animal'

class MouseAll(models.Model):
    id      = models.IntegerField(db_column='animalid', primary_key=True)
    eartag  = models.CharField(db_column='eartag', max_length=255)
    sex = models.CharField(db_column='sex', max_length=2, choices=(('m', 'male'), ('f', 'female'), ('u', 'unknown')),
                           help_text='Select "unknown" if multiple animals.')
    dob = models.DateField(db_column='dateborn')
    #notes = models.CharField(db_column='NOTES', max_length=4000)
    responsible = models.CharField(db_column='fullname', max_length=512)
    #responsible_firstname = models.CharField(db_column='firstname', max_length=512)
    #responsible_lastname = models.CharField(db_column='lastname', max_length=512)
    responsible_email = models.CharField(db_column='email', max_length=512)
    location = models.CharField(db_column='building', max_length=4000)
    licence = models.CharField(db_column='licence', max_length=255)
    strain = models.CharField(db_column='strain', max_length=255)
    labid = models.CharField(db_column='labid', max_length=255)
    genetic_bg = models.CharField(db_column='genetic_bg', max_length=255)
    owner_id = models.IntegerField(db_column='owner_id',)
    owner = models.CharField(db_column='owner', max_length=255)
    mutation = models.CharField(db_column='mutation', max_length=512)
    project = models.CharField(db_column='projectname', max_length=512)

    def age(self):
        """
        Return the age of the animal, calculated by the difference to either
        the current date or the available_to date
        """
        now = datetime.today().date()
        return int((now - self.dob).days / 7)

    class Meta:
        managed = False
        db_table = 'v_animal_full'


class Pup(models.Model):
    id      = models.IntegerField(db_column='id', primary_key=True)
    eartag  = models.CharField(db_column='eartag', max_length=255)
    sex = models.CharField(db_column='sex', max_length=2, choices=(('m', 'male'), ('f', 'female'), ('?', 'unknown')),
                           help_text='Select "unknown" if multiple animals.')
    dob = models.DateField(db_column='dateborn')
    responsible = models.CharField(db_column='fullname', max_length=512)
    responsible_email = models.CharField(db_column='email', max_length=512)
    location = models.CharField(db_column='building', max_length=4000)
    licence = models.CharField(db_column='licence', max_length=255)
    strain = models.CharField(db_column='strain', max_length=255)
    labid = models.CharField(db_column='labid', max_length=255)
    genetic_bg = models.CharField(db_column='genetic_bg', max_length=255)
    owner_id = models.IntegerField(db_column='owner_id',)
    owner = models.CharField(db_column='owner', max_length=255)
    mutation = models.CharField(db_column='mutation', max_length=512)
    project = models.CharField(db_column='projectname', max_length=512)
    medical_condition = models.CharField(db_column='medical_condition', max_length=1024)

    def age(self):
        """
        Return the age of the animal, calculated by the difference to either
        the current date or the available_to date
        """
        now = datetime.today().date()
        return int((now - self.dob).days / 7)

    class Meta:
        managed = False
        db_table = 'v_pup'


class PyratUserPermission(models.Model):
    id = models.IntegerField(db_column='id', primary_key=True)
    userid = models.IntegerField(db_column='userid')
    aliasid = models.IntegerField(db_column='aliasid')
    uid = models.IntegerField(db_column='uid',)
    usernum = models.CharField(db_column='levelid', max_length=255)

    class Meta:
        managed = False
        db_table = 'v_permission'



class FishMutation(models.Model):
    id          = models.IntegerField(db_column='ID', primary_key=True)
    description = models.CharField(db_column='DESCRIPTION', max_length=255)
    genotype    = models.CharField(db_column='GENOTYPE', max_length=255)
    referenceid = models.CharField(db_column='REFERENCEID', max_length=255)
    class Meta:
        managed = False
        db_table = 'VGENETICMODIFICATIONASSIGNMENT'

class Organ(models.Model):
    """
    Model containing the organs
    """
    """amount = models.PositiveIntegerField(default=1,
                                         help_text="How many organs?")"""
    animal_type = models.CharField(max_length=100, choices=(
        ('fish', 'fish'),
        ('mouse', 'mouse'),
        ('unknown', 'unknown'),
        ),
                                   default='mouse')
    sex = models.CharField(max_length=2, choices=(('m', 'male'), ('f', 'female'), ('u', 'unknown')),
                           help_text='Select "unknown" if multiple animals.')
    organ_type = models.ManyToManyField(Organtype, related_name='Organ_used', verbose_name='presets for used organs')
    day_of_birth = models.DateField()
    day_of_death = models.DateField()
    method_of_killing = models.CharField(null=True, blank=True,verbose_name='Sacrifice method', max_length=100, choices=(
        ('CO2', 'CO2'),
        ('cervicale dislocation', 'cervicale dislocation'),
        ('decapitation', 'decapitation'),
        ('blood withdrawl', 'blood withdrawl'),
        ('finale heart punction', 'finale heart punction'),
        ('overdose anaesthetics', 'overdose anaesthetic'),
        ('other', 'other'),
        ),)
    killing_person = models.EmailField(verbose_name='Euthanasia performed by',null=True, blank=True, help_text='Email address of the person who performe euthanasia. Leave it empty if it is the address of the responsible person')
    database_id = models.CharField(max_length=200, help_text="ID of animal in eg. PYRAT")
    lab_id = models.CharField(max_length=200, null=True, blank=True, help_text="ID of lab in eg. PYRAT")
    entry_date = models.DateField(null=False, auto_now_add=True)
    line = models.CharField(max_length=200, help_text="genetic trait of animal")
    genetic_background = models.CharField(max_length=200, blank=True, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True, help_text="Institution from which the organ is offered")
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, help_text='Where is the animal housed?')
    licence_number = models.CharField(max_length=200, blank=True, verbose_name='License number')
    responsible_person = models.ForeignKey(Person, related_name='rperson_organ', on_delete=models.CASCADE, default=0,
                                           help_text='Person who is responsible in the lab for dealing with the animals')
    responsible_person2 = models.ForeignKey(Person,  related_name='rperson2_organ', null=True, blank=True, on_delete=models.CASCADE, 
                                            help_text='Second person who is responsible in the lab for dealing with the animals', verbose_name = "Second responsible person")
    mutations = models.TextField(blank=True, null=True, help_text="Describe the mutations of this line in as much detail as possible")
    comment = models.TextField(blank=True, null=True,
                               help_text='Comments, such as individual organs to be offered')
#    new_owner = models.CharField(max_length=200, blank=True,
#                                 help_text='Person claiming this animal for themselves') # turn into foreignkey to auth_users?
    creation_date = models.DateTimeField(null=False, auto_now_add=True)
    modification_date = models.DateTimeField(null=False, auto_now=True)
    #sync_with_other_sharing_system = models.BooleanField(default=False,null=False, blank=False) # If true the object can be syncronised with an other sharing platform 
    added_by = models.ForeignKey(User, unique=False, on_delete=models.CASCADE, null=True)

    def get_organtypes(self):
        """Get all organ types which are used"""
        return ",\n".join([ot.name for ot in self.organ_type.all()])
    get_organtypes.short_description ='ORGAN TYPE (used)'

    def background(self):
        if self.genetic_background is None:
            return ("")
        else:
            return(self.genetic_background)

    def responsible_persons(self):
        if str(self.responsible_person2) != "None":
            return (str(self.responsible_person) + str(" ") +str(self.responsible_person2))
        return (self.responsible_person)

    def age(self):
        """
        Return the age of the animal, at the time of death
        """
        return int((self.day_of_death - self.day_of_birth).days / 7)

    def available(self):
        """
        Returns True if the animal is still available
        """
        today = datetime.now().date()
        return self.day_of_death >= today

    def get_absolute_url(self):
        """
        Get absolute url for this model. Important to link from the admin.
        """
        return reverse('claim_organ', kwargs={'primary_key': self.pk})

    def __str__(self):
        return " {} {}, {} id:{} [{}]".format(
            self.get_sex_display(), self.animal_type, self.line, self.pk, self.day_of_birth)

    def description(self):
        """
        Return description of this model
        """
        return "id:{}, lab_id:{}, available:{}-{}, location:{}, mutations:{}".format(
            self.database_id, self.lab_id, self.day_of_birth,
            self.day_of_death, self.location, "".join(self.mutations))

@receiver(post_save, sender=Organ) # check if killing_person (mail address) is given. If not save the mail address of the responsible person as killing_person 
def update_killing_person(sender, instance, created, **kwargs):
    if (instance.killing_person == None):
        instance.killing_person = instance.responsible_person.email
        instance.save()

# class ClaimOrgan(forms.Form):
#    organUsed=forms.ModelMultipleChoiceField(queryset=Organtype.objects.all(),widget=forms.CheckboxSelectMultiple())

class WIncident(models.Model):
    incidentid = models.AutoField(db_column='id', primary_key=True)
    incidentclass =  models.IntegerField(db_column='class_id', blank=True, null=True)
    #incidentclass = models.ForeignKey('WIncidentclass', models.DO_NOTHING, db_column='incidentclass', blank=True, null=True)
    initiator = models.ForeignKey('PyratUser', models.DO_NOTHING, blank=True, null=True,db_column='initiator_id')
    owner = models.ForeignKey('PyratUser', models.DO_NOTHING, blank=True, null=True, related_name='ownerpyrat', db_column='owner_id')
    responsible= models.ForeignKey('PyratUser', models.DO_NOTHING, blank=True, null=True, related_name='responsiblepyrat', db_column='responsible_id')
    incidentdescription = models.TextField(db_column='description')
    opendate = models.DateTimeField(db_column='open_date')
    closedate = models.DateTimeField(blank=True, null=True, db_column='close_date')
    priority = models.IntegerField(blank=True, null=True, db_column='priority_id')
    #priority = models.ForeignKey('WIncidentpriorities', models.DO_NOTHING, db_column='priority')
    status = models.IntegerField(blank=True, null=True, db_column='status_id') 
    #status = models.ForeignKey('WIncidentstatus', models.DO_NOTHING, db_column='status')
    duedate = models.DateTimeField(blank=True, null=True, db_column='due_date')
    sacrifice_reason = models.IntegerField(blank=True, null=True, db_column='sacrifice_reason_id') 
    sacrifice_method = models.IntegerField(blank=True, null=True, db_column='sacrifice_method_id') 
    licence = models.IntegerField(blank=True, null=True, db_column='licence_id')
    classification = models.IntegerField(blank=True, null=True, db_column='classification_id')
    #severity_level = models.IntegerField(blank=True, null=True, db_column='severity_level_id')
    
    wr_building = models.IntegerField(blank=True, null=True, db_column='wr_building_id')
    wr_area = models.IntegerField(blank=True, null=True, db_column='wr_area_id')
    wr_room = models.IntegerField(blank=True, null=True, db_column='wr_room_id')
    wr_rack = models.IntegerField(blank=True, null=True, db_column='wr_rack_id')
    """
    behavior = models.ForeignKey('WIncidentBehavior', models.DO_NOTHING, blank=True, null=True)
    """
    approved = models.IntegerField(db_column='approved')
    """
    strain = models.ForeignKey('Strain', models.DO_NOTHING, blank=True, null=True)
    procedure = models.ForeignKey('Procedures', models.DO_NOTHING, blank=True, null=True)
    building = models.ForeignKey('LocationBuildings', models.DO_NOTHING, blank=True, null=True)
    area = models.ForeignKey('LocationAreas', models.DO_NOTHING, blank=True, null=True)
    room = models.ForeignKey('LocationRooms', models.DO_NOTHING, blank=True, null=True)
    rack = models.ForeignKey('Rack', models.DO_NOTHING, blank=True, null=True)
    licence = models.ForeignKey('Licence2', models.DO_NOTHING, blank=True, null=True)
    classification = models.ForeignKey('Classification', models.DO_NOTHING, blank=True, null=True)
    new_owner = models.ForeignKey('Localuser', models.DO_NOTHING, blank=True, null=True)
    new_responsible = models.ForeignKey('Localuser', models.DO_NOTHING, blank=True, null=True)
    """
    change_responsible = models.IntegerField(blank=True, null=True,db_column='export_responsible_id')
    generation = models.CharField(max_length=10, blank=True, null=True,db_column='breeding_generation')

    class Meta:
        managed = False
        db_table = 'v_incident'

class WIncident_write(models.Model):
    incidentid = models.AutoField(db_column='id', primary_key=True)
    incidentclass =  models.IntegerField(db_column='class_id', blank=True, null=True)
    #incidentclass = models.ForeignKey('WIncidentclass', models.DO_NOTHING, db_column='incidentclass', blank=True, null=True)
    #initiator = models.ForeignKey('PyratUser', models.DO_NOTHING, blank=True, null=True,db_column='initiator_id')
    initiator = models.IntegerField(blank=True, null=True,db_column='initiator_id')
    owner = models.IntegerField(db_column='owner_id', blank=True, null=True)
    #owner = models.ForeignKey('PyratUser', models.DO_NOTHING, blank=True, null=True, related_name='ownerpyrat_write', db_column='owner_id')
    responsible = models.IntegerField(db_column='responsible_id', blank=True, null=True)
    #responsible= models.ForeignKey('PyratUser', models.DO_NOTHING, blank=True, null=True, related_name='responsiblepyrat_write', db_column='responsible_id')
    incidentdescription = models.TextField(db_column='description')
    opendate = models.DateTimeField(db_column='open_date', auto_now_add=True)
    closedate = models.DateTimeField(blank=True, null=True, db_column='close_date')
    priority = models.IntegerField(blank=True, null=True, db_column='priority_id')
    #priority = models.ForeignKey('WIncidentpriorities', models.DO_NOTHING, db_column='priority')
    status = models.IntegerField(blank=True, null=True, db_column='status_id') 
    #status = models.ForeignKey('WIncidentstatus', models.DO_NOTHING, db_column='status')
    duedate = models.DateTimeField(blank=True, null=True, db_column='due_date')
    sacrifice_reason = models.IntegerField(blank=True, null=True, db_column='sacrifice_reason_id') 
    licence = models.IntegerField(blank=True, null=True, db_column='licence_id')
    classification = models.IntegerField(blank=True, null=True, db_column='classification_id')
    #severity_level = models.IntegerField(blank=True, null=True, db_column='severity_level_id')
    sacrifice_method = models.IntegerField(blank=True, null=True, db_column='sacrifice_method_id') 
    behavior = models.IntegerField(blank=True, null=True, db_column='behavior_id') 
    last_modified = models.DateTimeField(null=False, db_column='last_modified')
    
    wr_building = models.IntegerField(blank=True, null=True, db_column='wr_building_id')
    wr_area = models.IntegerField(blank=True, null=True, db_column='wr_area_id')
    wr_room = models.IntegerField(blank=True, null=True, db_column='wr_room_id')
    wr_rack = models.IntegerField(blank=True, null=True, db_column='wr_rack_id')
    """
    behavior = models.ForeignKey('WIncidentBehavior', models.DO_NOTHING, blank=True, null=True)
    """
    approved = models.IntegerField(db_column='approved')
    """
    strain = models.ForeignKey('Strain', models.DO_NOTHING, blank=True, null=True)
    procedure = models.ForeignKey('Procedures', models.DO_NOTHING, blank=True, null=True)
    building = models.ForeignKey('LocationBuildings', models.DO_NOTHING, blank=True, null=True)
    area = models.ForeignKey('LocationAreas', models.DO_NOTHING, blank=True, null=True)
    room = models.ForeignKey('LocationRooms', models.DO_NOTHING, blank=True, null=True)
    rack = models.ForeignKey('Rack', models.DO_NOTHING, blank=True, null=True)
    licence = models.ForeignKey('Licence2', models.DO_NOTHING, blank=True, null=True)
    classification = models.ForeignKey('Classification', models.DO_NOTHING, blank=True, null=True)
    new_owner = models.ForeignKey('Localuser', models.DO_NOTHING, blank=True, null=True)
    new_responsible = models.ForeignKey('Localuser', models.DO_NOTHING, blank=True, null=True)
    """
    change_responsible = models.IntegerField(blank=True, null=True,db_column='export_responsible_id')
    generation = models.CharField(max_length=10, blank=True, null=True,db_column='breeding_generation')

    class Meta:
        managed = False
        db_table = 'work_request'

class WIncidentAnimals(models.Model):
    id          = models.IntegerField(db_column='id', primary_key=True)
    #animalid = models.ForeignKey('Mouse', models.DO_NOTHING, db_column='animalid', blank=True, null=True)
    #incidentid = models.ForeignKey('WIncident', models.DO_NOTHING, db_column='incidentid', blank=True, null=True)
    animalid    = models.IntegerField(blank=False, null=False, db_column='animal_id')
    incidentid  = models.IntegerField(blank=False, null=False, db_column='work_request_id')

    class Meta:
        managed = False
        db_table = 'work_request_animal_ref'

class WIncidentPups(models.Model):
    id          = models.IntegerField(db_column='id', primary_key=True)
    pupid       = models.IntegerField(blank=False, null=False, db_column='pup_id')
    incidentid  = models.IntegerField(blank=False, null=False, db_column='work_request_id')

    class Meta:
        managed = False
        db_table = 'work_request_pup_ref'


#class WIncidentcomment(models.Model):
#    incidentid      = models.ForeignKey('WIncident', models.DO_NOTHING, db_column='work_request_id', blank=True, null=True)
#    comment         = models.TextField()
#    commentdate     = models.DateTimeField(null=False, auto_now_add=True)
#
#    class Meta:
#        managed = False
#        db_table = 'comment_work_request_ref'

class Comment(models.Model):
    id              = models.AutoField(db_column='id', primary_key=True)
    creator_id      = models.ForeignKey('PyratUser', models.DO_NOTHING, db_column='creator_id', blank=True, null=True)
    created         = models.DateTimeField(null=False, auto_now_add=True)
    origin          = models.CharField(max_length=20, blank=False, null=False, default='work_request',db_column='origin')
    visible         = models.SmallIntegerField(blank=False, null=False, default=1,db_column='visible')
    content         = models.TextField()
    reply_pending   = models.SmallIntegerField(blank=False, null=False, default=0,db_column='reply_pending')

    class Meta:
        managed = False
        db_table = 'comment'

class Comment_work_request_ref(models.Model):
    comment_id      = models.IntegerField(primary_key=True, db_column='comment_id')
    work_request_id = models.IntegerField(db_column='work_request_id', blank=False, null=False)
    
    class Meta:
        managed = False
        db_table = 'comment_work_request_ref'


class WIncidentanimals_write(models.Model):
    id              = models.AutoField(db_column='id', primary_key=True)
    incidentid      = models.ForeignKey('WIncident_write', models.DO_NOTHING, db_column='work_request_id', blank=True, null=True)
    animalid        = models.IntegerField(db_column='animalid',blank=False, null=False)
    perform_status  = models.CharField(max_length=20, blank=False, null=False,db_column='perform_status')

    class Meta:
        managed = False
        db_table = 'work_request_animal_ref'

class WIncidentpups_write(models.Model):
    id              = models.AutoField(db_column='id', primary_key=True)
    incidentid      = models.ForeignKey('WIncident_write', models.DO_NOTHING, db_column='work_request_id', blank=True, null=True)
    pupid           = models.IntegerField(db_column='pup_id',blank=False, null=False)
    perform_status  = models.CharField(max_length=20, blank=False, null=False,db_column='perform_status')

    class Meta:
        managed = False
        db_table = 'work_request_pup_ref'


class Cached_work_request_subject_location(models.Model):
    work_request_id     = models.AutoField(db_column='work_request_id', primary_key=True)
    building_id         = models.IntegerField(db_column='building_id', blank=True, null=True)
    area_id             = models.IntegerField(db_column='area_id', blank=True, null=True)
    room_id             = models.IntegerField(db_column='room_id', blank=True, null=True)
    rack_id             = models.IntegerField(db_column='rack_id', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cached_work_request_subject_location'

class SacrificeIncidentToken(models.Model):
    initiator   = models.CharField(max_length=50, blank=False, null=False)
    incidentid  = models.IntegerField(blank=False, null=False) # AddToAniShare Incident ID
    urltoken    = models.CharField(max_length=100, blank=False, null=False)
    created     = models.DateTimeField(null=False, auto_now_add=True)
    confirmed   = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.initiator

class SearchRequestAnimal(models.Model):
    user            = CurrentUserField()
    animal_type = models.CharField(max_length=100, choices=(
        ('fish', 'Fish'),
        ('mouse', 'Mouse'),
        ('pup', 'Pup'),
    ),default='mouse')
    fish_specie     = models.CharField(max_length=20, null=True, blank=True, choices=(('n', 'Nothobranchius'), ('z', 'Zebrafish')))
    sex             = models.CharField(max_length=2, null=True, blank=True, choices=(('m', 'male'), ('f', 'female'), ('u', 'unknown')))
    active_from     = models.DateField(null=False,blank=False, help_text="You will informed about matching entries starting this date")
    active_until    = models.DateField(null=False, blank=False, help_text="You will informed about matching entries until this date")
    wild_type       = models.BooleanField(default=True,null=False, blank=False)
    found_animals   = models.ManyToManyField(Animal, related_name='animal_found')
    age_min         = models.IntegerField(blank=True, null=True)
    age_max         = models.IntegerField(blank=True, null=True)


