from django.contrib import admin
from .models import * 

admin.site.register(Alert)
admin.site.register(TriggeredAlert)
admin.site.register(Stock)