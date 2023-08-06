from django.contrib import admin
from models import Agent, Person, Organization

admin.site.register(Agent, admin.ModelAdmin)
admin.site.register(Person, admin.ModelAdmin)
admin.site.register(Organization, admin.ModelAdmin)

