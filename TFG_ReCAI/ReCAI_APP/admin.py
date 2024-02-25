from django.contrib import admin
from .models import PalabrasEncadenadas
from .models import EslabonCentral
from .models import RondaFinal

class EncadenadasAdmin(admin.ModelAdmin):
    list_display = ('tema', 'p1', 'p2', 'p3', 'p4', 'p5', 'p6')

class EslabonAdmin(admin.ModelAdmin):
    list_display = ('p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7')

class FinalAdmin(admin.ModelAdmin):
    list_display = ('p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7','p8', 'p9', 'p10', 'p11', 'p12', 'p13', 'final','pista') 

admin.site.register(PalabrasEncadenadas, EncadenadasAdmin)
admin.site.register(EslabonCentral, EslabonAdmin)
admin.site.register(RondaFinal, FinalAdmin)



