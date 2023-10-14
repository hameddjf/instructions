import csv
from django.views.generic import View
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import UploadCSVForm


class YourCSVUploadView(FormView):
    template_name = "examples/upload_csv.html"
    form_class = UploadCSVForm
    success_url = reverse_lazy(
        "upload_csv"
    )  # مسیری که به آن هدایت می‌شوید پس از آپلود موفق

    def form_valid(self, form):
        uploaded_file = self.request.FILES["csv_file"]  # دریافت فایل آپلود شده
        content = uploaded_file.read().decode("utf-8")  # خواندن محتوا و تبدیل به رشته
        # تقسیم محتوا بر اساس خطوط و ایجاد لیست
        rows = content.split("\n")
        print(rows)
        data = {}

        # for line in lines:
        #     if line.startswith("Hist:"):
        #         in_hist = True
        #     elif in_hist:
        #         if line.strip().startswith("Date:"):
        #             date = line.split(":")[1].strip()
        #         elif line.strip().startswith("Min T:"):
        #             min_t = line.split(":")[1].strip()
        #         elif line.strip().startswith("Max T:"):
        #             max_t = line.split(":")[1].strip()
        #         elif line.strip().startswith("Avrg T:"):
        #             avrg_t = line.split(":")[1].strip()
        #         elif line.strip().startswith("Alarm:"):
        #             in_alarm = True
        #         elif in_alarm:
        # ویژگی‌های دیگر را هم به همین ترتیب پردازش کنید

        # ارسال داده‌ها به تمپلیت
        return render(self.request, "examples/display_data.html", {"data": data})


# class YourCSVUploadView(View):
#     def read_csv_file(self, file_path):
#         with open(file_path, 'r') as csvfile:
#             csv_reader = csv.reader(csvfile)
#             data = list(csv_reader)
#         return data
