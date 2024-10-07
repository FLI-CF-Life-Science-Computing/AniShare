"""
Admin module
"""
import copy
from django.contrib.auth.models import AbstractUser
from import_export.admin import ImportExportModelAdmin, ImportMixin, ExportMixin, ImportExportActionModelAdmin, ImportExportMixin
from import_export.widgets import ManyToManyWidget
from datetime import datetime, timedelta
from import_export import fields, resources 
from import_export.widgets import ForeignKeyWidget
from django.contrib import admin
from django import forms
from django.conf import settings
from rangefilter.filters import DateRangeFilterBuilder # , DateTimeRangeFilter
from .models import Animal, Person, Lab, Location, Organ, Change, Organtype, SacrificeIncidentToken, SearchRequestAnimal
from import_export.formats import base_formats
from django_admin_listfilter_dropdown.filters import DropdownFilter, RelatedDropdownFilter
from simple_history.admin import SimpleHistoryAdmin


admin.site.site_header = 'AniShare admin interface'
admin.site.site_title = 'AniShare'
admin.site.index_title = 'Welcome to AniShare'

class SCSV(base_formats.CSV):

	def get_title(self):
		return "scsv"

	def create_dataset(self, in_stream, **kwargs):
		kwargs['delimiter'] = ';'
		return super().create_dataset(in_stream, **kwargs)

class AnimalResource(resources.ModelResource): # für den Import. Hier werden die Felder festgelegt, die importiert werden können

    animal_type = fields.Field(attribute='animal_type', column_name='Animal type') 
    responsible_person = fields.Field(
        column_name='Responsible',
        attribute='responsible_person',
        widget=ForeignKeyWidget(Person, 'name'))
    responsible_person2 = fields.Field(
        column_name='Responsible2',
        attribute='responsible_person2',
        widget=ForeignKeyWidget(Person, 'name'))
    lab_id = fields.Field(attribute='lab_id', column_name='Lab ID')
    database_id = fields.Field(attribute='database_id', column_name='ID')
    day_of_birth = fields.Field(attribute='day_of_birth', column_name='DOB')
    genetic_background = fields.Field(attribute='genetic_background', column_name='Background')
    line = fields.Field(attribute='line', column_name='Line / Strain (Name)')
    sex = fields.Field(attribute='sex', column_name='Sex')
    location = fields.Field(
        column_name='Building',
        attribute='location',
        widget=ForeignKeyWidget(Location, 'name'))
    mutations1 = fields.Field(attribute='mutations1',column_name='Mutation 1')
    mutations2 = fields.Field(attribute='mutations2',column_name='Mutation 2')
    mutations3 = fields.Field(attribute='mutations3',column_name='Mutation 3')
    mutations4 = fields.Field(attribute='mutations4',column_name='Mutation 4')
    grade1 = fields.Field(attribute='grade1',column_name='Grade 1')
    grade2 = fields.Field(attribute='grade2',column_name='Grade 2')
    grade3 = fields.Field(attribute='grade3',column_name='Grade 3')
    grade4 = fields.Field(attribute='grade4',column_name='Grade 4')
    licence_number = fields.Field(attribute='licence_number', column_name='License number')
    available_to = fields.Field(attribute='available_to', column_name='Available to')
    available_from = fields.Field(attribute='available_from', column_name='Available from')
    amount = fields.Field(attribute='amount', column_name='Amount')
    comment = fields.Field(attribute='comment', column_name='Comment')
    class Meta:
        model = Animal
        fields = ('lab_id','animal_type', 'amount', 'database_id','day_of_birth',
        'line','sex','location','mutations1', 'mutations2','mutations3', 'mutations4','grade1', 'grade2','grade3', 'grade4','licence_number',
        'responsible_person','responsible_person2','available_from','available_to','comment','genetic_background',)
        export_order = ('animal_type', 'amount', 'lab_id','database_id','sex','day_of_birth',
        'line','location','mutations1','grade1', 'grade2','grade3', 'grade4','licence_number',
        'responsible_person','available_from','available_to','comment',)
    def get_instance(self, instance_loader, row):
        try:
            params = {}
            for key in instance_loader.resource.get_import_id_fields():
                field = instance_loader.resource.fields[key]
                params[field.attribute] = field.clean(row)
            return self.get_queryset().get(**params)
        except Exception:
            return None 

    def import_obj(self, instance, row, dry_run): # Damit werden die Mutationen in ein Feld zusammengefasst
        super(AnimalResource, self).import_obj( instance, row, dry_run)
        
        """try:
            responsible = ""
            responsible = row['Responsible']   
            if (responsible !=""):
                rperson = Person.objects.get(responsible)
                if rperson == None:
                    new_person = Person()
                    new_person.name = dataset.responsible
                    new_person.email = "@leibniz-fli.de"
                    new_person.responsible_for_lab = Lab.objects.get(name="False")
                    new_person.save()
                    ADMIN_EMAIL = getattr(settings, "ADMIN_EMAIL", None)
                    send_mail("AniShare neue Person", 'Neue Person in AniShare {}'.format(new_person.name), ADMIN_EMAIL, [ADMIN_EMAIL])
        except: 
            messages.add_message(request, messages.ERROR,'Responsible person is unknown. Please check if there is a coloumn with the header Responsible')
         """   
        try:
            if (row['Grade 4'] != None):
                instance.mutations = "%s %s; %s %s; %s %s; %s %s" % (row['Mutation 1'], row['Grade 1'], row['Mutation 2'], row['Grade 2'], row['Mutation 3'], row['Grade 3'], row['Mutation 4'], row['Grade 4'])
                instance.grade1 = row['Grade 1']
                instance.grade2 = row['Grade 2']
                instance.grade3 = row['Grade 3']
                instance.grade4 = row['Grade 4']
            elif (row['Grade 3'] != None):   
                instance.mutations = "%s %s; %s %s; %s %s" % (row['Mutation 1'], row['Grade 1'], row['Mutation 2'], row['Grade 2'], row['Mutation 3'], row['Grade 3'])
                instance.grade1 = row['Grade 1']
                instance.grade2 = row['Grade 2']
                instance.grade3 = row['Grade 3']
            elif (row['Grade 2'] != None):   
                instance.mutations = "%s %s; %s %s" % (row['Mutation 1'], row['Grade 1'], row['Mutation 2'], row['Grade 2'])
                instance.grade1 = row['Grade 1']
                instance.grade2 = row['Grade 2']
            elif (row['Grade 1'] != None): 
                instance.mutations = "%s %s" % (row['Mutation 1'], row['Grade 1'])
                instance.grade1 = row['Grade 1']
            else:
                instance.mutations = ""
        except:  
            try:
                if (row['Grade 3'] != None):   
                    instance.mutations = "%s %s; %s %s; %s %s" % (row['Mutation 1'], row['Grade 1'], row['Mutation 2'], row['Grade 2'], row['Mutation 3'], row['Grade 3'])
                    instance.grade1 = row['Grade 1']
                    instance.grade2 = row['Grade 2']
                    instance.grade3 = row['Grade 3']
                elif (row['Grade 2'] != None):   
                    instance.mutations = "%s %s; %s %s" % (row['Mutation 1'], row['Grade 1'], row['Mutation 2'], row['Grade 2'])
                    instance.grade1 = row['Grade 1']
                    instance.grade2 = row['Grade 2']
                elif (row['Grade 1'] != None): 
                    instance.mutations = "%s %s" % (row['Mutation 1'], row['Grade 1'])
                    instance.grade1 = row['Grade 1']
                else:
                    instance.mutations = ""
            except:
                try:
                    if (row['Grade 2'] != None):   
                        instance.mutations = "%s %s;\n %s %s" % (row['Mutation 1'], row['Grade 1'], row['Mutation 2'], row['Grade 2'])
                        instance.grade1 = row['Grade 1']
                        instance.grade2 = row['Grade 2']
                    elif (row['Grade 1'] != None): 
                        instance.mutations = "%s %s" % (row['Mutation 1'], row['Grade 1'])
                        instance.grade1 = row['Grade 1']
                    else:
                        instance.mutations = ""
                except:
                    try:
                        if (row['Grade 1'] != None): 
                            instance.mutations = "%s %s" % (row['Mutation 1'], row['Grade 1'])
                            instance.grade1 = row['Grade 1']
                        else:
                            instance.mutations = ""
                    except:
                        instance.mutations =""

class AnimalExportResource(resources.ModelResource): # für den Export. Hier werden die Felder festgelegt, die exportiert werden können

    animal_type = fields.Field(attribute='animal_type', column_name='Animal type') 
    responsible_person = fields.Field(
        column_name='Responsible',
        attribute='responsible_person',
        widget=ForeignKeyWidget(Person, 'name'))
    responsible_person2 = fields.Field(
        column_name='Responsible2',
        attribute='responsible_person2',
        widget=ForeignKeyWidget(Person, 'name'))
    lab_id = fields.Field(attribute='lab_id', column_name='Lab ID')
    database_id = fields.Field(attribute='database_id', column_name='ID')
    day_of_birth = fields.Field(attribute='day_of_birth', column_name='DOB')
    genetic_background = fields.Field(attribute='genetic_background', column_name='Background')
    line = fields.Field(attribute='line', column_name='Line / Strain (Name)')
    sex = fields.Field(attribute='sex', column_name='Sex')
    location = fields.Field(
        column_name='Building',
        attribute='location',
        widget=ForeignKeyWidget(Location, 'name'))
    grade1 = fields.Field(attribute='grade1',column_name='Grade 1')
    grade2 = fields.Field(attribute='grade2',column_name='Grade 2')
    grade3 = fields.Field(attribute='grade3',column_name='Grade 3')
    grade4 = fields.Field(attribute='grade4',column_name='Grade 4')
    licence_number = fields.Field(attribute='licence_number', column_name='License number')
    available_to = fields.Field(attribute='available_to', column_name='Available to')
    available_from = fields.Field(attribute='available_from', column_name='Available from')
    amount = fields.Field(attribute='amount', column_name='Amount')
    comment = fields.Field(attribute='comment', column_name='Comment')
    class Meta:
        model = Animal
        fields = ('lab_id','animal_type', 'amount', 'database_id','day_of_birth',
        'line','sex','location','mutations','grade1', 'grade2','grade3', 'grade4','licence_number',
        'responsible_person','responsible_person2','available_from','available_to','comment','genetic_background','creation_date','new_owner')
        export_order = ('animal_type', 'amount', 'lab_id','database_id','sex','day_of_birth',
        'line','location','mutations','genetic_background','grade1', 'grade2','grade3', 'grade4','licence_number',
        'responsible_person','responsible_person2','available_from','available_to','comment','new_owner','creation_date',)
    

class OrganResource(resources.ModelResource): # für den Import. Hier werden die Felder festgelegt, die importiert werden können

    animal_type = fields.Field(attribute='animal_type', column_name='Animal type') 
    organ_type = fields.Field(attribute='organ_type', column_name='Organ used', widget=ManyToManyWidget(Organtype,separator=',',field='name'))
    responsible_person = fields.Field(
        column_name='Responsible',
        attribute='responsible_person',
        widget=ForeignKeyWidget(Person, 'name'))
    responsible_person2 = fields.Field(
        column_name='Responsible2',
        attribute='responsible_person2',
        widget=ForeignKeyWidget(Person, 'name'))
    lab_id = fields.Field(attribute='lab_id', column_name='Lab ID')
    genetic_background = fields.Field(attribute='genetic_background', column_name='Background')
    database_id = fields.Field(attribute='database_id', column_name='ID')
    killing_person = fields.Field(attribute='killing_person', column_name='Euthanasia performed by')
    day_of_birth = fields.Field(attribute='day_of_birth', column_name='DOB')
    day_of_death = fields.Field(attribute='day_of_death', column_name='Sacrifice date')
    method_of_killing = fields.Field(attribute='method_of_killing', column_name='Sacrifice method')
    line = fields.Field(attribute='line', column_name='Line / Strain (Name)')
    sex = fields.Field(attribute='sex', column_name='Sex')
    comment = fields.Field(attribute='comment', column_name='Comment')
    location = fields.Field(
        column_name='Building',
        attribute='location',
        widget=ForeignKeyWidget(Location, 'name'))
    mutations1 = fields.Field(attribute='mutations1',column_name='Mutation 1')
    mutations2 = fields.Field(attribute='mutations2',column_name='Mutation 2')
    mutations3 = fields.Field(attribute='mutations3',column_name='Mutation 3')
    mutations4 = fields.Field(attribute='mutations4',column_name='Mutation 4')
    licence_number = fields.Field(attribute='licence_number', column_name='License number')
    class Meta:
        model = Organ
        fields = ('lab_id','animal_type','organ_type', 'database_id','killing_person','day_of_birth','day_of_death','method_of_killing'
        'line','sex','location','mutations1', 'mutations2','mutations3', 'mutations4','licence_number',
        'responsible_person','responsible_person2','comment',)
    def get_instance(self, instance_loader, row):
        try:
            params = {}
            for key in instance_loader.resource.get_import_id_fields():
                field = instance_loader.resource.fields[key]
                params[field.attribute] = field.clean(row)
            return self.get_queryset().get(**params)
        except Exception:
            return None
    
    def import_obj(self, instance, row, dry_run): # Damit werden die Mutationen in ein Feld zusammengefasst
        super(OrganResource, self).import_obj( instance, row, dry_run)
        try:
            instance.mutations = "%s %s %s %s" % (row['Mutation 1'], row['Mutation 2'], row['Mutation 3'], row['Mutation 4'])
        except:  
            try:
                instance.mutations = "%s %s %s" % (row['Mutation 1'], row['Mutation 2'], row['Mutation 3'])
            except:
                try:
                    instance.mutations = "%s %s" % (row['Mutation 1'], row['Mutation 2'])
                except:
                    try:
                        instance.mutations = "%s" % (row['Mutation 1'])
                    except:
                        instance.mutations =""


class AnimalForm(forms.ModelForm):
    """
    Form for animal editing in admin
    """
    class Meta:
        model = Animal
        SYNC_WITH_OTHER_SYSTEMS = getattr(settings, "SYNC_WITH_OTHER_SYSTEMS", None)
        if SYNC_WITH_OTHER_SYSTEMS:            
            fields = ('amount', 'animal_type', 'fish_specie','day_of_birth',
                    'available_from', 'available_to', 'sex', 'database_id',
                    'lab_id', 'line', 'location', 'responsible_person', 'responsible_person2',
                    'licence_number', 'genetic_background','mutations','medical_condition', 'comment', 'new_owner',  'licence_paragraph11',)
        else:
            fields = ('amount', 'animal_type', 'fish_specie','day_of_birth',
                    'available_from', 'available_to', 'sex', 'database_id',
                    'lab_id', 'line', 'location', 'responsible_person', 'responsible_person2',
                    'licence_number', 'genetic_background','mutations','medical_condition','comment', 'new_owner','licence_paragraph11',)
    def clean(self):
        available_from = self.cleaned_data.get('available_from')
        available_to = self.cleaned_data.get('available_to')
        day_of_birth = self.cleaned_data.get('day_of_birth')
#        self.author =  request.user
        try:
            if available_from > available_to:
                raise forms.ValidationError("Dates are incorrect")
            if day_of_birth and (
                    (datetime.now().date() -  day_of_birth) <=
                    timedelta(days=settings.MAX_AGE_PUPS)):
                if ((not 'new_owner' in self.changed_data) and (available_to - available_from <= timedelta(days=settings.MIN_SHARE_DURATION_PUPS))):
                    raise forms.ValidationError(
                        "Minimum share duration for pups must be {} days!".format(
                            settings.MIN_SHARE_DURATION_PUPS))
            elif ((not 'new_owner' in self.changed_data) and (available_to - available_from <= timedelta(days=settings.MIN_SHARE_DURATION))):
                raise forms.ValidationError(
                    "Minimum share duration must be {} days!".format(settings.MIN_SHARE_DURATION))
            return self.cleaned_data
        except:
            raise forms.ValidationError("Dates are incorrect. Please use the calendar function")
        

@admin.register(Change)
class ChangeAdmin(admin.ModelAdmin):
    """
    ChangeAdmin for Change model
    """
    list_display = ('version', 'short_text', 'description',)
    search_fields = ('version',)
    ordering = ('version', )


@admin.register(Organtype)
class OrgantypeAdmin(admin.ModelAdmin):
    """
    ModelAdmin for Organ types
    """
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name', )

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    """
    ModelAdmin for Person model
    """
    list_display = ('name', 'email', 'responsible_for_lab')
    search_fields = ('name', 'email', 'responsible_for_lab__name')
    ordering = ('name', )

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """
    ModelAdmin for Location model
    """
    list_display = ('name',)
    search_fields = ('name',)

def clear_claim(modeladmin, request, queryset):
    """
    Convenience Function to delete a claim from several selected animals
    """
    queryset.update(new_owner='')
    clear_claim.short_description = "Clear 'new_owner' from selected animals"

def copy_animal(modeladmin, request, queryset):
    """
    Copy an instance of an animal so similar entries can be easily created.
    """
    for animal in queryset:
        animal_copy = copy.copy(animal) # (2) django copy object
        animal_copy.id = None   # (3) set 'id' to None to create new object
        animal_copy.save()    # initial save

    copy_animal.short_description = "Make a Copy of an entry"


class AnimalHelmholtzResource(resources.ModelResource): # für den Import. Hier werden die Felder festgelegt, die importiert werden können

    animal_type = 'mouse'
    responsible_person = fields.Field(
        column_name='Responsible',
        attribute='responsible_person',
        widget=ForeignKeyWidget(Person, 'name'))
    lab_id = fields.Field(attribute='lab_id', column_name='ear')
    database_id = fields.Field(attribute='database_id', column_name='mouse_id')
    day_of_birth = fields.Field(attribute='day_of_birth', column_name='born')
    genetic_background = fields.Field(attribute='genotype', column_name='genotype')
    line = fields.Field(attribute='line', column_name='line')
    sex = fields.Field(attribute='sex', column_name='sex')
    location = fields.Field(
        column_name='room/rack',
        attribute='location',
        widget=ForeignKeyWidget(Location, 'name'))
    licence_number = ''
    amount = 1
    comment = fields.Field(attribute='comment', column_name='Comment')
    class Meta:
        model = Animal
        fields = ('lab_id','animal_type', 'amount', 'database_id','day_of_birth','line','sex','location','licence_number','comment','genetic_background')
    def get_instance(self, instance_loader, row):
        try:
            params = {}
            for key in instance_loader.resource.get_import_id_fields():
                field = instance_loader.resource.fields[key]
                params[field.attribute] = field.clean(row)
            return self.get_queryset().get(**params)
        except Exception:
            return None 

    def before_import_row(self, row, **kwargs):
        row['available_from'] = datetime.today()   

    def before_import(self, dataset, dry_run, *args, **kwargs):
        for data in dataset.dict:
            data['available_from'] = datetime.today()    
            data['available_to'] =   datetime.today() + timedelta(days=14) 
        return super(AnimalHelmholtzResource, self).before_import(dataset, dry_run, *args, **kwargs)


@admin.register(Animal)
#class AnimalAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
class AnimalAdmin(ImportExportMixin, admin.ModelAdmin):
    """
    ModelAdmin for Animal model
    """
    resource_class = AnimalHelmholtzResource
    list_display = ('id','animal_type','database_id', 'lab_id','sex', 'entry_date', 'day_of_birth', 'age',  'available_from',
                    'available_to', 'line', 'mutations', 'location', 'licence_number',
                    'responsible_persons', 'new_owner',)
    list_display_links = ('id','animal_type','sex','entry_date', 'day_of_birth', 'age',
                          'available_from', 'available_to', 'line', 'mutations', 'database_id',
                          'location', 'licence_number', 'lab_id','responsible_persons',
                          'new_owner')
    search_fields = ('id','animal_type', 'fish_specie', 'sex', 'database_id', 'lab_id', 'day_of_birth',
                     'line', 'mutations', 'genetic_background', 'location__name', 'new_owner', 'licence_number',
                     'available_from', 'available_to', 'responsible_person__name',
                     'responsible_person__email', 'added_by__email',)
    autocomplete_fields = ['responsible_person','responsible_person2']
    list_filter = ('animal_type','fish_specie','sex', ('responsible_person__responsible_for_lab',RelatedDropdownFilter),('line', DropdownFilter),('genetic_background', DropdownFilter),
                   ('day_of_birth', DateRangeFilterBuilder()),
                   'location', ('licence_number', DropdownFilter), ('new_owner', DropdownFilter), 'added_by')
    radio_fields = {'sex':admin.HORIZONTAL}
    readonly_fields = ('creation_date', 'modification_date')
    form = AnimalForm
    save_as = True
    save_on_top = True
    actions = [clear_claim, copy_animal]
    def age(self, obj):
        """Show the age in the admin as 'Age (w)' instead of 'age'"""
        return obj.age()
    age.short_description = 'Age (w)'
#    def formfield_for_foreignkey(self, db_field, request, **kwargs):
#        if db_field.name == 'author':
#            kwargs['queryset'] = get_user_model().objects.filter(username=request.user.username)
#        return super(AnimalAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.added_by = request.user
        super().save_model(request, obj, form, change)
    def get_import_formats(self):
        formats = (
                  base_formats.XLSX,
                  base_formats.XLS,
                  base_formats.ODS,
                  base_formats.CSV,
                  SCSV,)
        return [f for f in formats if f().can_export()]
    def get_export_resource_class(self):
        return AnimalExportResource



@admin.register(Organ)
class OrganAdmin(ImportExportModelAdmin):
#class OrganAdmin(ImportMixin, admin.ModelAdmin):
    """
    ModelAdmin for Organ model
    """
    resource_class = OrganResource
    filter_horizontal = ('organ_type',)
    list_display = ('id','animal_type','get_organtypes', 'entry_date', 'day_of_birth',
                    'day_of_death', 'age', 'method_of_killing', 'killing_person', 'line','genetic_background',
                    'sex', 'location','lab_id', 'licence_number', 'responsible_persons', 'added_by')
    list_display_links = ('id', 'animal_type','get_organtypes', 'entry_date', 'day_of_birth',
                          'day_of_death', 'age', 'method_of_killing', 'killing_person', 'line',
                          'sex', 'location','lab_id', 'licence_number', 'responsible_persons', 'added_by')
    search_fields = ('id', 'animal_type', 'entry_date', 'day_of_birth',
                     'day_of_death','method_of_killing', 'killing_person', 'line','genetic_background','lab_id'
                     'sex', 'location__name', 'licence_number', 'responsible_person__name', 'added_by__username')
    autocomplete_fields = ['responsible_person']
    list_filter = (('sex', DropdownFilter),'animal_type','method_of_killing','killing_person','line','genetic_background',
                   ('day_of_birth', DateRangeFilterBuilder()), ('day_of_death', DateRangeFilterBuilder()),
                   'responsible_person__responsible_for_lab',
                   'location', 'licence_number', 'added_by',)
    radio_fields = {'sex':admin.HORIZONTAL}
    readonly_fields = ('added_by', 'creation_date', 'modification_date')
    save_as = True
    save_on_top = True
#    form = OrganForm
    actions = [clear_claim, copy_animal]

    def age(self, obj):
        """Show the age in the admin as 'Age (w)' instead of 'age'"""
        return obj.age()
    age.short_description = 'Age (w)'

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set added_by during the first save.
            obj.added_by = request.user
        super().save_model(request, obj, form, change)
    def get_import_formats(self):
        formats = (base_formats.XLSX,
                  base_formats.XLS,
                  base_formats.ODS,
                  base_formats.CSV,
                  SCSV,)
        return [f for f in formats if f().can_export()]

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    """
    ModelAdmin for Lab model
    """
    list_display = ('name', 'responsible_person')
    search_fields = ('name',)

@admin.register(SacrificeIncidentToken)
class SacrificeIncidentToken(admin.ModelAdmin):
    list_display = ('initiator', 'incidentid','urltoken','created','confirmed')
    search_fields = ('initiator', 'incidentid','urltoken','created','confirmed')

@admin.register(SearchRequestAnimal)
class SearchRequestAnimal(admin.ModelAdmin):
    list_display = ('user', 'animal_type','sex','wild_type','active_from','active_until')
    search_fields = ('user', 'animal_type','sex','wild_type')
    pass

