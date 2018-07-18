from django.contrib import admin
from .models import *

# Register your models here.
class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'tier', 'charge_id', 'created_at', 'modified_at', 'user')


admin.site.register(PlanCharge, PlanAdmin)