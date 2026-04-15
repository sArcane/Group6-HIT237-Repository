from django.contrib import admin
from .models import Species, Location, Recording, AnomalyFlag

admin.site.register(Species)
admin.site.register(Location)
admin.site.register(Recording)
admin.site.register(AnomalyFlag)
