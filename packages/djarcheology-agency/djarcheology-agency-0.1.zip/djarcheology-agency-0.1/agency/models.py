from django.db import models
from django.db.models import Q
from polymorphic import PolymorphicModel
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from localflavor.us.models import PhoneNumberField

AGENCY_CONTENTTYPE_CHOICES = ContentType.objects.filter(app_label='agency')

class Agent(PolymorphicModel):

    class Meta:
        verbose_name = 'Agent'
        verbose_name_plural = 'Agents'
        db_table = 'agency_agent'


class Person(Agent):
    first_name = models.CharField(max_length=200, null=True, blank=True)
    middle_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        verbose_name = 'Person'
        verbose_name_plural = 'People'
        db_table = 'agency_person'

    def __unicode__(self):
        name = "%s, %s" % (self.last_name, self.first_name)
        return name


class Organization(Agent):
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        db_table = 'agency_organization'

    def __unicode__(self):
        return self.name


class Affiliation(models.Model):
    person = models.ForeignKey(Person, null=True, blank=True)
    organization = models.ForeignKey(Organization, null=True, blank=True)

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = 'Affiliation'
        verbose_name_plural = 'Affiliations'
        db_table = 'agency_affiliation'


class Address(models.Model):

    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'


class PhoneNumber(models.Model):
    agent_type = models.ForeignKey(ContentType, limit_choices_to=AGENCY_CONTENTTYPE_CHOICES, null=True, blank=True)
    agent_id = models.IntegerField(null=True, blank=True)
    agent = generic.GenericForeignKey('agent_type', 'agent_id')

    phone_number = PhoneNumberField()
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Phone Number'
        verbose_name_plural = 'Phone Numbers'

