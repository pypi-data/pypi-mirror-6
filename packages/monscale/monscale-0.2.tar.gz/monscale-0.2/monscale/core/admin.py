from django.contrib import admin
from models import *

class ScaleActionAdmin(admin.ModelAdmin):
    pass
admin.site.register(ScaleAction, ScaleActionAdmin)

class ThresholdAdmin(admin.ModelAdmin):
    pass
admin.site.register(Threshold, ThresholdAdmin)

class MonitoredServiceAdmin(admin.ModelAdmin):
    pass
admin.site.register(MonitoredService, MonitoredServiceAdmin)

class AlarmIndicatorAdmin(admin.ModelAdmin):
    pass
admin.site.register(AlarmIndicator, AlarmIndicatorAdmin)

