from django.views.generic import TemplateView
import requests
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

import urllib.parse

from accounts.models import CustomUser
from instructions.models import Instruction


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_count = CustomUser.objects.count()
        instruction_count = Instruction.objects.filter(is_active=True).count()
        # دریافت اطلاعات کاربران به تفکیک behvarz، expert و manager از مدل User
        behvarz_users = CustomUser.objects.filter(user_type="behvarz").count
        expert_users = CustomUser.objects.filter(user_type="expert").count
        manager_users = CustomUser.objects.filter(user_type="manager").count

        context = {
            "user_count": user_count,
            "instruction_count": instruction_count,
            "behvarz": behvarz_users,
            "expert": expert_users,
            "manager": manager_users,
        }
        return context

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #
    #     # دریافت شهر کاربر
    #     user = self.request.user
    #     city = user.city
    #
    #     # دریافت اطلاعات آب و هوا برای شهر کاربر
    #     api_key = settings.OPENWEATHERMAP_API_KEY
    #     url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
    #     response = requests.get(url)
    #     data = response.json()
    #
    #     # تبدیل دما از کلوین به سانتیگراد و گرد کردن به یک رقم اعشار
    #     temperature = round(data['main']['temp'] - 273.15, 1)
    #
    #     # دریافت اطلاعات پیش بینی آب و هوا برای شهر کاربر
    #     forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}'
    #     forecast_response = requests.get(forecast_url)
    #     forecast_data = forecast_response.json()
    #
    #     # بازگرداندن اطلاعات هواشناسی و پیش بینی برای هفته آینده
    #     context['weather'] = {
    #         'city': data['name'],
    #         'description': data['weather'][0]['description'],
    #         'temperature': temperature,
    #         'humidity': data['main']['humidity'],
    #         'icon': data['weather'][0]['icon'],
    #         'forecast': []
    #     }
    #
    #     for item in forecast_data['list']:
    #         date_time = item['dt_txt']
    #         date = date_time.split(' ')[0]
    #         time = date_time.split(' ')[1]
    #         if time == '12:00:00':
    #             temperature = round(item['main']['temp'] - 273.15, 1)
    #             context['weather']['forecast'].append({
    #                 'date': date,
    #                 'description': item['weather'][0]['description'],
    #                 'temperature': temperature,
    #                 'humidity': item['main']['humidity'],
    #                 'icon': item['weather'][0]['icon']
    #             })
    #
    #     return context
