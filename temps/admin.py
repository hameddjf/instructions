from django.contrib import admin

from .models import *


@admin.register(DeviceInformation)
class DeviceInformationAdmin(admin.ModelAdmin):
    list_display = ['device', 'user', 'created_at', 'updated_at']

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['user','serial', 'version', 'fw_version', 'sensor_count', 'pcb', 'cid', 'lot', 'zone', 'measurement_delay',
                    'updated_at', 'created_at']


@admin.register(DeviceAlarm)
class DeviceAlarmAdmin(admin.ModelAdmin):
    list_display = ['device', 't_al0', 't_al_time0', 't_al1', 't_al_time1']


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ['device', 'version', 'lot', 'issuer', 'valid_from', 'owner', 'public_key']


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ['device', 'timeout', 'offset']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['device', 'date', 'min_temp', 'min_temp_time', 'max_temp', 'max_temp_time', 'avg_temp','fault',
                    'alarm0_time', 'alarm1_time', 'timeout_time', 'events', 'checked_am_time', 'checked_pm_time']


@admin.register(Signature)
class SignatureAdmin(admin.ModelAdmin):
    list_display = ['device', 'cert_signature', 'data_signature']


from django.contrib import admin

# Register your models here.
