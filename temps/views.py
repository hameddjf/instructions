from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.http import Http404
from django.utils.timezone import make_aware
from django.http import JsonResponse
import json
from django.db.models import Q

from datetime import datetime, timedelta

from .models import Device, Report
from accounts.models import CustomUser
from .forms import UploadFileForm, DateRangeForm
from .regex import (
    extract_device_data,
    extract_device_info_data,
    extract_sensor_data,
    extract_alarm_data,
    extract_report_data,
    extract_cert_data,
    extract_sig_data
)

from jalali_date import datetime2jalali
from sklearn.linear_model import LinearRegression
import numpy as np

from .meachin_learning import predict_faulty


def regression_view(request, device_id):
    try:
        reports = Report.objects.filter(device_id=device_id)
        min_temp = [report.min_temp for report in reports]
        max_temp = [report.max_temp for report in reports]

        # اجرای تحلیل رگرسیون
        X = np.array(min_temp).reshape(-1, 1)
        y = np.array(max_temp)

        model = LinearRegression()
        model.fit(X, y)

        # پیش‌بینی نقص برای یک مقدار دما خاص (برای مثال 25 درجه)
        prediction = model.predict(np.array([[25]]))[0]

    except Report.DoesNotExist:
        prediction = None

    context = {
        'prediction': prediction
    }
    return render(request, 'temps/regression.html', context)


class BaseDeviceReportView(View):

    def get_device(self, device_id):
        try:
            return Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            raise Http404

    def get_reports(self, device):
        return Report.objects.filter(device=device, date__gte=datetime.now() - timedelta(days=60))[:60]

    def get_chart_data(self, reports):
        jalali_dates = [datetime2jalali(datetime.combine(report.date, report.max_temp_time)).strftime('%Y-%m-%d') for
                        report in reports]
        max_temps = [report.max_temp for report in reports]
        min_temps = [report.min_temp for report in reports]
        avrg_temps = [report.avg_temp for report in reports]

        return {
            'dates': json.dumps(jalali_dates),
            'max_temps': json.dumps(max_temps),
            'min_temps': json.dumps(min_temps),
            'avrg_temps': json.dumps(avrg_temps),
        }

    def get_context_data(self, **kwargs):
        device_id = kwargs.get('device_id')
        device = self.get_device(device_id)
        reports = self.get_reports(device)
        chart_data = self.get_chart_data(reports)

        return {
            'device': device,
            **chart_data
        }

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, 'temps/draw_temp.html', context)

    def post(self, request, *args, **kwargs):
        device_id = kwargs.get('device_id')
        device = self.get_device(device_id)
        reports = self.get_reports(device)
        chart_data = self.get_chart_data(reports)

        # استخراج اطلاعات برای نمودار
        dates = chart_data['dates']
        max_temps = chart_data['max_temps']
        min_temps = chart_data['min_temps']
        avrg_temps = chart_data['avrg_temps']

        return render(request, 'chart_template.html', {
            'dates': dates,
            'max_temps': max_temps,
            'min_temps': min_temps,
            'avrg_temps': avrg_temps,
        })


class DeviceListView(LoginRequiredMixin, ListView):
    model = Device
    template_name = 'temps/device_list.html'
    context_object_name = 'devices'

    def get_queryset(self):
        # اگر کاربر سوپر یوزر باشد، تمام دستگاه‌ها را نمایش بده
        if self.request.user.is_superuser:
            return Device.objects.annotate(
                last_data_date=Max('report__date')
            )
        # اگر کاربر بهورز باشد، تنها دستگاه‌هایی که توسط خودش ثبت شده را نمایش بده
        elif self.request.user.user_type == 'behvarz':
            return Device.objects.filter(user=self.request.user).annotate(
                last_data_date=Max('report__date')
            )
        # اگر کاربر کارشناس باشد، دستگاه‌هایی که خودش ثبت کرده و دستگاه‌هایی که زیر مجموعه روستاهای تحت پوشش او هستند را نمایش بده
        elif self.request.user.user_type == 'expert':
            return Device.objects.filter(
                Q(user=self.request.user) | Q(user__village__health_center=self.request.user.health_center)
            ).annotate(
                last_data_date=Max('report__date')
            )
            # اگر کاربر مدیر باشد، دستگاه‌هایی که خودش ثبت کرده و دستگاه‌هایی که زیر مجموعه روستاهای تحت پوشش او یا زیر مجموعه مراکز بهداشتی او هستند را نمایش بده
        elif self.request.user.user_type == 'manager':
            return Device.objects.filter(
                Q(user=self.request.user) |
                # Q(user__village__health_center=self.request.user.health_center) |
                Q(user__health_center__city=self.request.user.city)
            ).annotate(
                last_data_date=Max('report__date')
            )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = CustomUser.objects.all()  # اینجا تمام کاربران را بگیرید
        return context


class DeviceReportsDetailView(LoginRequiredMixin, FormView):
    template_name = 'temps/display_Temp_Tbl.html'

    def get(self, request, device_id):
        print(request.POST)
        device = Device.objects.get(id=device_id)
        reports = device.report_set.all().order_by('-date')  # بازیابی همه گزارش‌های مرتبط با این دستگاه

        context = {'device': device, 'reports': reports}
        return render(request, self.template_name, context)


class UploadTextView(LoginRequiredMixin, View):
    def get(self, request):
        form = UploadFileForm()
        context = {
            'form': form,
        }
        return render(request, 'temps/uploadTemp.html', context)

    def post(self, request):
        username = request.user.username
        file_content = request.FILES['text_file'].read().decode('utf-8')

        # ----------------------------------------------------------extract device information's----------------------
        # device_data = extract_device_data(file_content)
        device = extract_device_data(file_content, username).save()
        # ----------------------------------------------------------extract device information's----------------------
        # device_data = extract_device_data(file_content)
        device_info = extract_device_info_data(file_content, username).save()
        # --------------------------------------------استخراج داده های Sensor-----------------------------------------
        # sensor_data = extract_sensor_data(file_content)
        sensor = extract_sensor_data(file_content).save()
        # --------------------------------------------Extract DeviceAlarm data -----------------------------------------
        # alarm_data = extract_alarm_data(file_content)
        alarm = extract_alarm_data(file_content).save()
        # --------------------------------استخراج داده های Report------------------------------------------------------
        report = extract_report_data(file_content).save()
        # -------------------------استخراج داده های Certification------------------------------------------------------
        cert = extract_cert_data(file_content).save()
        # ---------------------------استخراج داده های Signature------------------------------------------------------
        sign = extract_sig_data(file_content).save()

        context = {
            'device': device,
            'device_info': device_info,
            'sensor': sensor,
            'alarm': alarm,
            'report': report,
            'cert': cert,
            'sign': sign
        }
        return render(request, 'temps/uploadTemp.html', context)

# class UploadTextView(LoginRequiredMixin, View):
#     def get(self, request):
#         form = UploadFileForm()
#         return render(request, 'temps/uploadTemp.html', {'form': form})
#
#     def post(self, request):
#
#         file_content = request.FILES['text_file'].read().decode('utf-8')
#
#         # ----------------------------------------------------------extract device information's----------------------
#
#         pattern_device = "Device:\s+(?P<Device>\w+\-\w+\s+\w+\-\w+\s+\d+)\s+" \
#                          "Vers:\s+(?P<Vers>\d+\.\d+)\s+" \
#                          "Fw Vers:\s+(?P<Fw_vers>\d+\.\d+\w+\d+\w+)\s+" \
#                          "Sensor:\s+(?P<Sensor>\d+)\s+" \
#                          "Conf:\s+" \
#                          "Serial:\s+(?P<Serial>\d+)\s+" \
#                          "PCB:\s+(?P<PCB>\w+\d+)\s+" \
#                          "CID:\s+(?P<CID>\d+)\s+" \
#                          "Lot:\s+(?P<Lot>\d+\_\d+_\d+)\s+" \
#                          "Zone:\s+(?P<Zone>\d+\.\d+)\s+" \
#                          "Measurement delay:\s+(?P<Measurement_delay>\d+)\s+" \
#                          "Moving Avrg:\s+(?P<Moving_Avrg>\d+)\s+" \
#                          "User Alarm Config:\s+(?P<User_Alarm_Config>\d+)\s+" \
#                          "User Clock Config:\s+(?P<Use_clock_Config>\d+)\s+" \
#                          "Alarm Indication:\s(?P<Alarm_Indication>\d+)\s+" \
#                          "Temp unit:\s(?P<Temp_unit>\w)"
#
#         serial = search_in_text(file_content, r'Serial:\s+(?P<Serial>\d+)')
#
#         existing_device = Device.objects.filter(serial=serial).first()
#         device = Device()
#
#         for m in re.findall(pattern_device, file_content):
#             # device.device_name = m[0]
#             version = m[1]
#             fw_version = m[2]
#             sensor_count = m[3]
#             pcb = m[5]
#             cid = m[6]
#             lot = m[7]
#             zone = m[8]
#             measurement_delay = m[9]
#             moving_avg = m[10]
#             user_alarm_config = m[11]
#             user_clock_config = m[12]
#             alarm_indication = m[13]
#             temp_unit = m[14]
#             report_history_length = int(search_in_text(file_content, r'Report history length:\s+(\d+)'))
#             det_report = int(search_in_text(file_content, r'Det Report:\s+(\d+)'))
#             use_ext_devices = int(search_in_text(file_content, r'Use ext devices:\s+(\d+)'))
#             #
#             test_res = int(search_in_text(file_content, r'Test Res:\s+(\d+)'))
#             test_ts_str = search_in_text(file_content, r"Test TS:\s+(?P<Test_TS>\d+\-\d+\-\d+\s+\d+\:\d+)")
#             test_ts = timezone.make_aware(datetime.strptime(test_ts_str, '%Y-%m-%d %H:%M'))
#             test_ts = test_ts
#
#         if existing_device:
#             existing_device.version = version
#             existing_device.fw_version = fw_version
#             existing_device.sensor_count = sensor_count
#             existing_device.pcb = pcb
#             existing_device.cid = cid
#             existing_device.lot = lot
#             existing_device.zone = zone
#             existing_device.measurement_delay = measurement_delay
#             existing_device.moving_avg = moving_avg
#             existing_device.user_alarm_config = user_alarm_config
#             existing_device.user_clock_config = user_clock_config
#             existing_device.alarm_indication = alarm_indication
#             existing_device.temp_unit = temp_unit
#             existing_device.report_history_length = report_history_length
#             existing_device.det_report = det_report
#             existing_device.use_ext_devices = use_ext_devices
#             existing_device.test_res = test_res
#             existing_device.test_ts = test_ts
#             existing_device.save()
#         else:
#             for m in re.findall(pattern_device, file_content):
#                 # device.device_name = m[0]
#                 device.version = m[1]
#                 device.fw_version = m[2]
#                 device.sensor_count = m[3]
#                 device.serial = m[4]
#                 print("register new device:", device.serial)
#                 device.pcb = m[5]
#                 device.cid = m[6]
#                 device.lot = m[7]
#                 device.zone = m[8]
#                 device.measurement_delay = m[9]
#                 device.moving_avg = m[10]
#                 device.user_alarm_config = m[11]
#                 device.user_clock_config = m[12]
#                 device.alarm_indication = m[13]
#                 device.temp_unit = m[14]
#                 device.report_history_length = int(search_in_text(file_content, r'Report history length:\s+(\d+)'))
#                 device.det_report = int(search_in_text(file_content, r'Det Report:\s+(\d+)'))
#                 device.use_ext_devices = int(search_in_text(file_content, r'Use ext devices:\s+(\d+)'))
#
#                 device.test_res = int(search_in_text(file_content, r'Test Res:\s+(\d+)'))
#                 test_ts_str = search_in_text(file_content, r"Test TS:\s+(?P<Test_TS>\d+\-\d+\-\d+\s+\d+\:\d+)")
#                 test_ts = timezone.make_aware(datetime.strptime(test_ts_str, '%Y-%m-%d %H:%M'))
#                 device.test_ts = test_ts
#                 device.save()
#         # --------------------------------------------استخراج داده های Sensor-----------------------------------------
#
#         sensor_pattern = r'Int Sensor:\s+Timeout:\s+(?P<Timeout>\d+),\s+' \
#                          r'Offset:\s+(?P<Offset>[+-]\d+\.\d+)'
#
#         for m in re.findall(sensor_pattern, file_content):
#             timeout = int(m[0])
#             offset = float(m[1])
#
#         sens_serial = re.search(r'Serial:\s+(?P<Serial>\d+)', file_content).group('Serial')
#         print("sens serial:", sens_serial)
#         id = Device.objects.filter(serial=sens_serial).first()
#         existing_sensor = Sensor.objects.filter(device=id).first()
#         print("sensor", existing_sensor)
#
#         sensor = Sensor()
#
#         if existing_sensor:
#             existing_sensor.timeout = timeout
#             existing_sensor.offset = offset
#             print("existing_sensor timeout:", existing_sensor.timeout)
#             print("existing_sensor offset", existing_sensor.offset)
#             existing_sensor.save()
#         else:
#             for m in re.findall(sensor_pattern, file_content):
#                 sensor.device = device
#                 sensor.timeout = m[0]
#                 sensor.offset = m[1]
#                 print("new sensor timeout:", sensor.timeout)
#                 print("new sensor offset:", sensor.offset)
#                 sensor.save()
#
#         # --------------------------------------------Extract DeviceAlarm data -----------------------------------------
#
#         alarm_pattern = r"Alarm:\s+0:\s+T AL:\s+(?P<Temp_AL_0>[+-]\d+\.\d+)\,\s+" \
#                         r"t AL:\s+(?P<time_AL_0>\d+)\s+1:\s+" \
#                         r"T AL:\s+(?P<Temp_AL_1>[+-]\d+\.\d+)\,\s+" \
#                         r"t AL:\s+(?P<time_AL_1>\d+)"
#
#         for m in re.findall(alarm_pattern, file_content):
#             t_al0 = m[0]
#             t_al_time0 = m[1]
#             t_al1 = m[2]
#             t_al_time1 = m[3]
#
#         alarm_serial = re.search(r'Serial:\s+(?P<Serial>\d+)', file_content).group('Serial')
#         device = Device.objects.filter(serial=alarm_serial).first()
#         existing_alarm = DeviceAlarm.objects.filter(device=device).first()
#         print("alarm exist:", existing_alarm)
#
#         alarm = DeviceAlarm()
#
#         if existing_alarm:
#             existing_alarm.t_al0 = t_al0
#             existing_alarm.t_al_time0 = t_al_time0
#             existing_alarm.t_al1 = t_al1
#             existing_alarm.t_al_time1 = t_al_time1
#             print("update device alarm", existing_alarm.t_al0)
#             existing_alarm.save()
#         else:
#             alarm.device = device
#             alarm.t_al0 = t_al0
#             alarm.t_al_time0 = t_al_time0
#             alarm.t_al1 = t_al1
#             alarm.t_al_time1 = t_al_time1
#             print("new device alarm:", alarm.t_al0)
#             alarm.save()
#
#             # --------------------------------استخراج داده های Report------------------------------------------------------
#         report_pattern = r"Date:\s+(?P<DATE>\d+\-\d+\-\d+)\s+" \
#                          "Min T:\s+(?P<Min_T>[+-]?\d+\.\d+)\,\s+" \
#                          "TS Min T:\s+(?P<TS_Min_T>\d+\:\d+)\s+" \
#                          "Max T:\s+(?P<Max_T>[+-]\d+\.\d+)\,\s+" \
#                          "TS Max T:\s+(?P<TS_Max_T>\d+\:\d+)\s+" \
#                          "Avrg T:\s+(?P<Avrg_T>[+-]\d+\.\d+)\s+" \
#                          "Alarm:\s+\d:\s+t Acc:\s+(?P<t_Acc_0>\d+)\s+\d\:\s+" \
#                          "t Acc:\s+(?P<t_Acc_1>\d+)\s+Int Sensor timeout:\s+" \
#                          "t AccST:\s+(?P<t_AccST>\d+)\s+" \
#                          "Events:\s+(?P<Events>\d+)"
#
#         report_serial = re.search(r'Serial:\s+(?P<Serial>\d+)', file_content).group('Serial')
#         device = Device.objects.filter(serial=report_serial).first()
#         device.save()
#
#         if device:
#             existing_report = Report.objects.filter(device=device)
#             if existing_report:
#                 for report in existing_report:
#                     print("Old Date:", report.date.strftime("%Y-%m-%d"))  # نمایش تاریخ به فرمت YYYY-MM-DD
#                 for m in re.findall(report_pattern, file_content):
#                     report_date = m[0]
#                     if not existing_report.filter(date=report_date).exists():
#                         report = Report()
#                         report.device = device
#                         report.date = report_date
#                         report.min_temp = m[1]
#                         report.min_temp_time = m[2]
#                         report.max_temp = m[3]
#                         report.max_temp_time = m[4]
#                         report.avg_temp = m[5]
#                         report.alarm0_time = m[6]
#                         report.alarm1_time = m[7]
#                         report.timeout_time = m[8]
#                         report.events = m[9]
#                         print("re new report:", report.date)
#                         report.save()
#             else:
#                 for m in re.findall(report_pattern, file_content):
#                     report = Report()
#                     report.device = device
#                     report.date = m[0]
#                     report.min_temp = m[1]
#                     report.min_temp_time = m[2]
#                     report.max_temp = m[3]
#                     report.max_temp_time = m[4]
#                     report.avg_temp = m[5]
#                     report.alarm0_time = m[6]
#                     report.alarm1_time = m[7]
#                     report.timeout_time = m[8]
#                     report.events = m[9]
#                     print("new report:", report.date)
#                     report.save()
#         else:
#             print("دستگاهی با شماره سریال مورد نظر یافت نشد.")
#
#         # -------------------------استخراج داده های Certification------------------------------------------------------
#         cert_pattern = r"Cert:\s+Vers:\s+(?P<Vers>\d+\.\d+)\s+" \
#                        r"Lot:\s+(?P<Lot>\d+\_\d+\_\d+)\s+" \
#                        r"Issuer:\s+(?P<Issuer>\w+\s+\W+\s+\w+\W+\w+)\s+" \
#                        r"Valid from:\s+(?P<Valid_from>\d+\-\d+\-\d+\s+\d+\:\d+)\s+" \
#                        r"Owner:\s+(?P<Owner>\w+\s+\W+\s+\w+\W+\w+)\s+" \
#                        r"Public Key:\s+(?P<Public_Key>\w+)"
#
#         for m in re.findall(cert_pattern, file_content):
#             version = m[0]
#             lot = m[1]
#             issuer = m[2]
#             valid_from = m[3]
#             owner = m[4]
#             public_key = m[5]
#
#         cert_serial = re.search(r'Serial:\s+(?P<Serial>\d+)', file_content).group('Serial')
#         device = Device.objects.filter(serial=cert_serial).first()
#         device.save()
#         existing_cert = Certification.objects.filter(device=device).first()
#
#         cert = Certification()
#
#         if existing_cert:
#             existing_cert.version = version
#             existing_cert.lot = lot
#             existing_cert.issuer = issuer
#             existing_cert.valid_from = valid_from
#             existing_cert.owner = owner
#             existing_cert.public_key = public_key
#             existing_cert.save()
#         else:
#             cert.device = device
#             cert.version = version
#             cert.lot = lot
#             cert.issuer = issuer
#             cert.valid_from = valid_from
#             cert.owner = owner
#             cert.public_key = public_key
#             cert.save()
#
#         # ---------------------------استخراج داده های Signature------------------------------------------------------
#         sig_pattern = r"Sig Cert:\s+(?P<Sig_Cert>\w+)\s+" \
#                       r"Sig:\s+(?P<Sig>\w+)"
#
#         for m in re.findall(sig_pattern, file_content):
#             sig_cert = m[0]
#             sig = m[1]
#
#         sig_serial = re.search(r'Serial:\s+(?P<Serial>\d+)', file_content).group('Serial')
#         device = Device.objects.filter(serial=sig_serial).first()
#         existing_sig = Signature.objects.filter(device=device).first()
#
#         signature = Signature()
#
#         if existing_sig:
#             existing_sig.cert_signature = sig_cert
#             existing_sig.data_signature = sig
#             existing_sig.save()
#         else:
#             signature.device = device
#             signature.cert_signature = sig_cert
#             signature.data_signature = sig
#             signature.save()
#
#         context = {'device': device}
#         return render(request, 'temps/uploadTemp.html', context)
