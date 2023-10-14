from datetime import datetime
from django.utils import timezone
import re

from accounts.models import CustomUser
from .models import *

# ----------------------------------------------------------extract device information's----------------------

from django.shortcuts import get_object_or_404
from .models import Device


def extract_device_data(file_content, username):
    pattern_device = r"Device:\s+(?P<Device>\w+\-\w+\s+\w+\-\w+\s+\d+)\s+" \
                     "Vers:\s+(?P<Vers>\d+\.\d+)\s+" \
                     "Fw Vers:\s+(?P<Fw_vers>\d+\.\d+\w+\d+\w+)\s+" \
                     "Sensor:\s+(?P<Sensor>\d+)\s+" \
                     "Conf:\s+" \
                     "Serial:\s+(?P<Serial>\d+)\s+" \
                     "PCB:\s+(?P<PCB>\w+\d+)\s+" \
                     "CID:\s+(?P<CID>\d+)\s+" \
                     "Lot:\s+(?P<Lot>\d+\_\d+_\d+)\s+" \
                     "Zone:\s+(?P<Zone>\d+\.\d+)\s+" \
                     "Measurement delay:\s+(?P<Measurement_delay>\d+)\s+" \
                     "Moving Avrg:\s+(?P<Moving_Avrg>\d+)\s+" \
                     "User Alarm Config:\s+(?P<User_Alarm_Config>\d+)\s+" \
                     "User Clock Config:\s+(?P<Use_clock_Config>\d+)\s+" \
                     "Alarm Indication:\s(?P<Alarm_Indication>\d+)\s+" \
                     "Temp unit:\s(?P<Temp_unit>\w)"

    device_serial_match = re.search(r'Serial:\s+(?P<Serial>\d+)', file_content)

    if not device_serial_match:
        return None

    device_serial = device_serial_match.group('Serial')
    existing_device = Device.objects.filter(serial=device_serial).first()

    if not existing_device:
        # اگر دستگاه با این شماره سریال در دیتابیس وجود نداشته باشد، دستگاه جدید را ایجاد کنید و ذخیره کنید.
        existing_device = Device()

    match = re.search(pattern_device, file_content)
    print(match.group())

    if match:
        existing_device.user = CustomUser.objects.get(username=username)
        existing_device.version = match.group('Vers')
        existing_device.fw_version = match.group('Fw_vers')
        existing_device.sensor_count = int(match.group('Sensor'))
        existing_device.serial = match.group('Serial')
        existing_device.pcb = match.group('PCB')
        existing_device.cid = int(match.group('CID'))
        existing_device.lot = match.group('Lot')
        existing_device.zone = float(match.group('Zone'))
        existing_device.measurement_delay = int(match.group('Measurement_delay'))
        existing_device.moving_avg = int(match.group('Moving_Avrg'))
        existing_device.user_alarm_config = int(match.group('User_Alarm_Config'))
        existing_device.user_clock_config = int(match.group('Use_clock_Config'))
        existing_device.alarm_indication = int(match.group('Alarm_Indication'))
        existing_device.temp_unit = match.group('Temp_unit')
        existing_device.report_history_length = int(search_in_text(file_content, r'Report history length:\s+(\d+)'))
        existing_device.det_report = int(search_in_text(file_content, r'Det Report:\s+(\d+)'))
        existing_device.use_ext_devices = int(search_in_text(file_content, r'Use ext devices:\s+(\d+)'))
        existing_device.test_res = int(search_in_text(file_content, r'Test Res:\s+(\d+)'))
        test_ts_str = search_in_text(file_content, r"Test TS:\s+(?P<Test_TS>\d+\-\d+\-\d+\s+\d+\:\d+)")
        existing_device.test_ts = timezone.make_aware(datetime.strptime(test_ts_str, '%Y-%m-%d %H:%M'))

        existing_device.save()
    else:
        existing_device = Device()
        existing_device.user = CustomUser.objects.get(username=username)
        existing_device.version = match.group('Vers')
        existing_device.fw_version = match.group('Fw_vers')
        existing_device.sensor_count = int(match.group('Sensor'))
        existing_device.serial = match.group('Serial')
        existing_device.pcb = match.group('PCB')
        existing_device.cid = int(match.group('CID'))
        existing_device.lot = match.group('Lot')
        existing_device.zone = float(match.group('Zone'))
        existing_device.measurement_delay = int(match.group('Measurement_delay'))
        existing_device.moving_avg = int(match.group('Moving_Avrg'))
        existing_device.user_alarm_config = int(match.group('User_Alarm_Config'))
        existing_device.user_clock_config = int(match.group('Use_clock_Config'))
        existing_device.alarm_indication = int(match.group('Alarm_Indication'))
        existing_device.temp_unit = match.group('Temp_unit')
        existing_device.report_history_length = int(search_in_text(file_content, r'Report history length:\s+(\d+)'))
        existing_device.det_report = int(search_in_text(file_content, r'Det Report:\s+(\d+)'))
        existing_device.use_ext_devices = int(search_in_text(file_content, r'Use ext devices:\s+(\d+)'))
        existing_device.test_res = int(search_in_text(file_content, r'Test Res:\s+(\d+)'))
        test_ts_str = search_in_text(file_content, r"Test TS:\s+(?P<Test_TS>\d+\-\d+\-\d+\s+\d+\:\d+)")
        existing_device.test_ts = timezone.make_aware(datetime.strptime(test_ts_str, '%Y-%m-%d %H:%M'))
        existing_device.save()

    return existing_device


def extract_device_info_data(file_content, username):
    Info_serial = re.search(r'Serial:\s+(?P<Serial>\d+)', file_content).group('Serial')
    device = Device.objects.filter(serial=Info_serial).first()
    existing_deviceInfo = DeviceInformation.objects.filter(device=device).first()

    user = CustomUser.objects.get(username=username)

    if not existing_deviceInfo:
        existing_deviceInfo = DeviceInformation()
        existing_deviceInfo.device = device

    if existing_deviceInfo:
        existing_deviceInfo.user = user
        # existing_deviceInfo.province = user.province.name
        # existing_deviceInfo.city = user.city.name
        # health_center = user.health_center.first()
        # existing_deviceInfo.health_center = health_center.name
        # existing_deviceInfo.village = user.village.name
        existing_deviceInfo.save()
    else:
        existing_deviceInfo.device = device
        existing_deviceInfo.user = user
        # existing_deviceInfo.province = user.province.name
        # existing_deviceInfo.city = user.city.name
        # existing_deviceInfo.health_center = user.health_center.name
        # existing_deviceInfo.village = user.village.name
        existing_deviceInfo.save()

    return existing_deviceInfo


# --------------------------------------------استخراج داده های Sensor-----------------------------------------
def extract_sensor_data(file_content):
    sensor_pattern = r'Int Sensor:\s+Timeout:\s+(?P<Timeout>\d+),\s+' \
                     r'Offset:\s+(?P<Offset>[+-]\d+\.\d+)'

    match = re.search(sensor_pattern, file_content)

    sens_serial = re.search(r'Serial:\s+(?P<Serial>\d+)', file_content).group('Serial')
    print("sens serial:", sens_serial)
    device = Device.objects.filter(serial=sens_serial).first()
    existing_sensor = Sensor.objects.filter(device=device).first()
    print("sensor", existing_sensor)

    if not existing_sensor:
        existing_sensor = Sensor()
        existing_sensor.device = device

    if existing_sensor:
        existing_sensor.timeout = match.group('Timeout')
        existing_sensor.offset = match.group('Offset')
        print("existing_sensor timeout:", existing_sensor.timeout)
        print("existing_sensor offset", existing_sensor.offset)
        existing_sensor.save()
    else:
        existing_sensor.timeout = match.group('Timeout')
        existing_sensor.offset = match.group('Offset')
        print("existing_sensor timeout:", existing_sensor.timeout)
        print("existing_sensor offset", existing_sensor.offset)
        existing_sensor.save()

    return existing_sensor

    # --------------------------------------------Extract DeviceAlarm data -----------------------------------------


def extract_alarm_data(file_content):
    alarm_pattern = r"Alarm:\s+0:\s+T AL:\s+(?P<Temp_AL_0>[+-]\d+\.\d+)\,\s+" \
                    r"t AL:\s+(?P<time_AL_0>\d+)\s+1:\s+" \
                    r"T AL:\s+(?P<Temp_AL_1>[+-]\d+\.\d+)\,\s+" \
                    r"t AL:\s+(?P<time_AL_1>\d+)"

    match = re.search(alarm_pattern, file_content)

    alarm_serial = re.search(r'Serial:\s+(?P<Serial>\d+)', file_content).group('Serial')
    device = Device.objects.filter(serial=alarm_serial).first()
    existing_alarm = DeviceAlarm.objects.filter(device=device).first()
    print("alarm exist:", existing_alarm)
    if not existing_alarm:
        existing_alarm = DeviceAlarm()
        existing_alarm.device = device

    if existing_alarm:
        existing_alarm.t_al0 = match.group('Temp_AL_0')
        existing_alarm.t_al_time0 = match.group('time_AL_0')
        existing_alarm.t_al1 = match.group('Temp_AL_1')
        existing_alarm.t_al_time1 = match.group('time_AL_1')
        print("update device alarm", existing_alarm.t_al0)
        existing_alarm.save()
    else:
        existing_alarm.t_al0 = match.group('Temp_AL_0')
        existing_alarm.t_al_time0 = match.group('time_AL_0')
        existing_alarm.t_al1 = match.group('Temp_AL_1')
        existing_alarm.t_al_time1 = match.group('time_AL_1')
        print("new device alarm:", existing_alarm.t_al0)
        existing_alarm.save()

    return existing_alarm

    # --------------------------------استخراج داده های Report------------------------------------------------------


def extract_report_data(file_content):
    report_pattern = r"Date:\s+(?P<DATE>\d+\-\d+\-\d+)\s+" \
                     "Min T:\s+(?P<Min_T>[+-]?\d+\.\d+)\,\s+" \
                     "TS Min T:\s+(?P<TS_Min_T>\d+\:\d+)\s+" \
                     "Max T:\s+(?P<Max_T>[+-]\d+\.\d+)\,\s+" \
                     "TS Max T:\s+(?P<TS_Max_T>\d+\:\d+)\s+" \
                     "Avrg T:\s+(?P<Avrg_T>[+-]\d+\.\d+)\s+" \
                     "Alarm:\s+\d:\s+t Acc:\s+(?P<t_Acc_0>\d+)\s+\d\:\s+" \
                     "t Acc:\s+(?P<t_Acc_1>\d+)\s+Int Sensor timeout:\s+" \
                     "t AccST:\s+(?P<t_AccST>\d+)\s+" \
                     "Events:\s+(?P<Events>\d+)"

    report_serial = re.search(r'Serial:\s+(?P<Serial>\d+)', file_content).group('Serial')
    device = Device.objects.filter(serial=report_serial).first()
    device.save()

    if device:
        existing_report = Report.objects.filter(device=device)
        if existing_report:
            for report in existing_report:
                print("Old Date:", report.date.strftime("%Y-%m-%d"))  # نمایش تاریخ به فرمت YYYY-MM-DD
            for m in re.findall(report_pattern, file_content):
                report_date = m[0]
                if not existing_report.filter(date=report_date).exists():
                    report = Report()
                    report.device = device
                    report.date = report_date
                    report.min_temp = m[1]
                    report.min_temp_time = m[2]
                    report.max_temp = m[3]
                    report.max_temp_time = m[4]
                    report.avg_temp = m[5]
                    if float(m[3]) >= 8 or float(m[1]) <= 0:
                        report.fault = 0
                    else:
                        report.fault = 1
                    report.alarm0_time = m[6]
                    report.alarm1_time = m[7]
                    report.timeout_time = m[8]
                    report.events = m[9]
                    print("re new report:", report.date)
                    report.save()
        else:
            for m in re.findall(report_pattern, file_content):
                report = Report()
                report.device = device
                report.date = m[0]
                report.min_temp = m[1]
                report.min_temp_time = m[2]
                report.max_temp = m[3]
                report.max_temp_time = m[4]
                report.avg_temp = m[5]
                if float(m[3]) >= 8 or float(m[1]) <= 0:
                    report.fault = 0
                else:
                    report.fault = 1
                report.alarm0_time = m[6]
                report.alarm1_time = m[7]
                report.timeout_time = m[8]
                report.events = m[9]
                print("new report:", report.date)
                report.save()
    else:
        print("دستگاهی با شماره سریال مورد نظر یافت نشد.")

    return report

    # -------------------------استخراج داده های Certification------------------------------------------------------


def extract_cert_data(file_content):
    cert_pattern = r"Cert:\s+Vers:\s+(?P<Vers>\d+\.\d+)\s+" \
                   r"Lot:\s+(?P<Lot>\d+\_\d+\_\d+)\s+" \
                   r"Issuer:\s+(?P<Issuer>\w+\s+\W+\s+\w+\W+\w+)\s+" \
                   r"Valid from:\s+(?P<Valid_from>\d+\-\d+\-\d+\s+\d+\:\d+)\s+" \
                   r"Owner:\s+(?P<Owner>\w+\s+\W+\s+\w+\W+\w+)\s+" \
                   r"Public Key:\s+(?P<Public_Key>\w+)"

    match = re.search(cert_pattern, file_content)

    cert_serial = re.search(r'Serial:\s+(?P<Serial>\d+)', file_content).group('Serial')
    device = Device.objects.filter(serial=cert_serial).first()
    existing_cert = Certification.objects.filter(device=device).first()

    if not existing_cert:
        existing_cert = Certification()
        existing_cert.device = device

    if existing_cert:
        existing_cert.version = match.group('Vers')
        existing_cert.lot = match.group('Lot')
        existing_cert.issuer = match.group('Issuer')
        existing_cert.valid_from = match.group('Valid_from')
        existing_cert.owner = match.group('Owner')
        existing_cert.public_key = match.group('Public_Key')
        existing_cert.save()
    else:
        version = match.group('Vers')
        existing_cert.version = version
        existing_cert.lot = match.group('Lot')
        existing_cert.issuer = match.group('Issuer')
        existing_cert.valid_from = match.group('Valid_from')
        existing_cert.owner = match.group('Owner')
        existing_cert.public_key = match.group('Public_Key')
        existing_cert.save()

    return existing_cert

    # ---------------------------استخراج داده های Signature------------------------------------------------------


def extract_sig_data(file_content):
    sig_pattern = r"Sig Cert:\s+(?P<Sig_Cert>\w+)\s+" \
                  r"Sig:\s+(?P<Sig>\w+)"

    match = re.search(sig_pattern, file_content)

    sig_serial = re.search(r'Serial:\s+(?P<Serial>\d+)', file_content).group('Serial')
    device = Device.objects.filter(serial=sig_serial).first()
    existing_sig = Signature.objects.filter(device=device).first()

    if not existing_sig:
        existing_sig = Signature()
        existing_sig.device = device

    if existing_sig:
        existing_sig.cert_signature = match.group('Sig_Cert')
        existing_sig.data_signature = match.group('Sig')
        existing_sig.save()
    else:
        existing_sig.cert_signature = match.group('Sig_Cert')
        existing_sig.data_signature = match.group('Sig')
        existing_sig.save()

    return existing_sig


def search_in_text(text, pattern):
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None
