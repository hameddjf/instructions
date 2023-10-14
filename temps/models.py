from django.db import models
from django.conf import settings


class Device(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='temps_devices',
        null=True,
        blank=True,
        default=None
    )

    version = models.FloatField(null=True)
    fw_version = models.CharField(max_length=100)

    sensor_count = models.IntegerField()

    serial = models.CharField(max_length=100, unique=True)
    pcb = models.CharField(max_length=100)
    cid = models.IntegerField()
    lot = models.CharField(max_length=100)
    zone = models.FloatField()

    measurement_delay = models.IntegerField()
    moving_avg = models.IntegerField()

    user_alarm_config = models.IntegerField()
    user_clock_config = models.IntegerField()
    alarm_indication = models.IntegerField()

    temp_unit = models.CharField(max_length=10)

    report_history_length = models.IntegerField()
    det_report = models.IntegerField()
    use_ext_devices = models.IntegerField()

    test_res = models.IntegerField()
    test_ts = models.DateTimeField()

    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class DeviceInformation(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='device_information')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_devices',
        null=True,
        blank=True,
        default=None
    )
    province = models.CharField(max_length=100, default='مشهد', blank=True, null=True)
    city = models.CharField(max_length=100, default='مشهد', blank=True, null=True)
    health_center = models.CharField(max_length=100, default='مشهد', blank=True, null=True)
    village = models.CharField(max_length=100, default='مشهد', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DeviceAlarm(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    t_al0 = models.FloatField(default=0.0)
    t_al_time0 = models.IntegerField(default=0)
    t_al1 = models.FloatField(default=0.0)
    t_al_time1 = models.IntegerField(default=0)


class Sensor(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sensors')
    timeout = models.IntegerField()
    offset = models.FloatField()


class Report(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    date = models.DateField()
    min_temp = models.FloatField()
    min_temp_time = models.TimeField()
    max_temp = models.FloatField()
    max_temp_time = models.TimeField()
    avg_temp = models.FloatField()
    alarm0_time = models.IntegerField()
    alarm1_time = models.IntegerField()
    timeout_time = models.IntegerField()
    events = models.IntegerField()
    checked_am_time = models.TimeField(null=True, blank=True)
    checked_pm_time = models.TimeField(null=True, blank=True)
    fault = models.PositiveIntegerField(null=True, blank=True, default=0)


class Certification(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE)
    version = models.FloatField()
    lot = models.CharField(max_length=100)
    issuer = models.CharField(max_length=100)
    valid_from = models.DateTimeField()
    owner = models.CharField(max_length=100)
    public_key = models.TextField()


class Signature(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    cert_signature = models.CharField(max_length=100)
    data_signature = models.CharField(max_length=100)
