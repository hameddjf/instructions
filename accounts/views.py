from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import Http404
from django.db.models import Q
from django import forms
import random
import string

from django.views import View
from .forms import (
    BehvarzCreationForm,
    BehvarzChangeForm,
    ExpertCreationForm,
    ManagerCreationForm,
    ExpertChangeForm,
    ManagerChangeForm,
    CityCreateForm,
    HealthCenterForm,
    VillageForm,
    SecurityQuestionForm,
)
from .models import Province, City, HealthCenter, Village, CustomUser
from .mixins import FieldsProfileMixin


@login_required
def change_password(request, pk):
    # استفاده از پارامتر pk در کد ویو
    user = get_object_or_404(CustomUser, pk=pk)

    if request.method == "POST":
        old_password = request.POST["old_password"]
        new_password1 = request.POST["new_password1"]
        new_password2 = request.POST["new_password2"]

        # بررسی صحت رمز قدیمی با استفاده از user
        if not user.check_password(old_password):
            messages.error(request, "رمز قدیمی نادرست است.")
            return redirect("changePass", pk=pk)

        # بررسی تطابق رمزهای جدید
        if new_password1 != new_password2:
            messages.error(request, "رمزهای جدید با هم مطابقت ندارند.")
            return redirect("changePass", pk=pk)

        # تغییر رمز عبور
        user.set_password(new_password1)
        user.save()

        # ورود مجدد پس از تغییر رمز
        user = authenticate(username=user.username, password=new_password1)
        login(request, user)

        messages.success(request, "رمز عبور با موفقیت تغییر یافت.")
        return redirect("changePass", pk=pk)

    return render(request, "registration/changePass.html", {"user": user})


class PassRecoveryView(View):
    model = CustomUser

    def get(self, request):
        form = SecurityQuestionForm()
        return render(request, "registration/recoveryPass.html", {"form": form})

    def post(self, request):
        secu_q_selected = request.POST.get("security_q")
        secu_answer = request.POST.get("security_key")
        cellphone_answer = request.POST.get("cell_phone")
        username = request.POST.get("username")

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return render(
                request,
                "registration/recoveryPass.html",
                {"error": "نام کاربری معتبر نیست."},
            )

        form = SecurityQuestionForm()  # تعیین اولیه متغیر form

        if (
            user.security_q == secu_q_selected
            and user.security_key == secu_answer
            and str(user.cell_phone) == cellphone_answer
        ):
            new_password = "".join(random.choices(string.digits, k=3))
            user.password = make_password(new_password)
            user.save()

            # تعیین متغیر form در صورت موفقیت آمیز بودن شرط if
            form.fields["new_password"] = forms.CharField(
                widget=forms.TextInput(attrs={"readonly": "readonly"}),
                initial=new_password,
            )
            return render(
                request,
                "registration/recoveryPass.html",
                {"form": form, "success": "رمزعبور جدید"},
            )

        return render(
            request,
            "registration/recoveryPass.html",
            {"form": form, "error": "داده‌های وارد شده صحیح نمی‌باشند."},
        )


class UserIncompleteRegisterView(ListView):
    model = CustomUser
    fields = "__all__"
    template_name = "accounts/incomplete_user.html"
    context_object_name = "user"

    def get_queryset(self):
        # کوئری‌ستی بسازید که لیست کاربران ناقص را برگرداند
        queryset = CustomUser.objects.filter(first_name="")
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # لیست کاربران ناقص را به context اضافه کنید
        incomplete_users = self.get_queryset()
        context["incomplete_users"] = incomplete_users

        return context


class ProfileView(FieldsProfileMixin, UpdateView):
    model = CustomUser
    template_name = "accounts/profile.html"
    context_object_name = "user"

    def get_object(self):
        return CustomUser.objects.get(pk=self.request.user.pk)

    def get_success_url(self):
        return reverse("profile", args=[self.request.user.pk])

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "ویرایش با موفقیت انجام شد.")
        return response

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            messages.error(
                self.request, f"خطا در ویرایش اطلاعات {field}: {', '.join(errors)}"
            )
        return super().form_invalid(form)


class ManagerUpdateView(UpdateView):
    model = CustomUser
    form_class = ManagerChangeForm
    template_name = "accounts/update_manager.html"
    success_url = reverse_lazy("manager_list")
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        provinces = Province.objects.all()
        cities = City.objects.all()

        default_province_id = self.object.province.id if self.object.province else ""
        default_city_id = self.object.city.id if self.object.city else ""

        context.update(
            {
                "provinces": provinces,
                "cities": cities,
                "default_province_id": default_province_id,
                "default_city_id": default_city_id,
            }
        )
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        province_id = self.request.POST.get("province")
        city_id = self.request.POST.get("city")
        if province_id:
            self.object.province = Province.objects.get(id=province_id)
        if city_id:
            self.object.city = City.objects.get(id=city_id)
        self.object.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        # Get the error messages as a list of strings
        error_messages = []
        for field, errors in form.errors.as_data().items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

        # Add the error messages to the context
        context = self.get_context_data()
        context["error_messages"] = error_messages

        # Return the response with the form and error messages
        return self.render_to_response(context=context, form=form)


class ManagerDeleteView(DeleteView):
    model = CustomUser
    template_name = "accounts/delete_manager.html"
    success_url = reverse_lazy("manager_list")
    context_object_name = "username"


class ManagerListView(ListView):
    model = CustomUser
    template_name = "accounts/list_manager.html"
    context_object_name = "manager_list"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user_type="manager")
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(username__icontains=query)
            )
        return queryset


class ManagerRegisterView(CreateView):
    def get(self, request):
        provinces = Province.objects.all()
        cities = City.objects.all()

        form = ManagerCreationForm()

        default_province_id = request.GET.get("province", "")
        default_city_id = request.GET.get("city", "")

        return render(
            request,
            "accounts/register_manager.html",
            {
                "form": form,
                "provinces": provinces,
                "cities": cities,
                "default_province_id": default_province_id,
                "default_city_id": default_city_id,
            },
        )

    def post(self, request):
        provinces = Province.objects.all()
        cities = City.objects.all()

        form = ManagerCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = "manager"
            user.save()
            # manager = Manager(
            #     user=user,
            # )
            # manager.save()
            return redirect("manager_list")

        default_province_id = request.GET.get("province", "")
        default_city_id = request.GET.get("city", "")

        return render(
            request,
            "accounts/register_manager.html",
            {
                "form": form,
                "provinces": provinces,
                "cities": cities,
                "default_province_id": default_province_id,
                "default_city_id": default_city_id,
            },
        )


# کلاس های مرتبط با کارشناسان    ---------------------------------------------------------
class ExpertUpdateView(UpdateView):
    model = CustomUser
    form_class = ExpertChangeForm
    template_name = "accounts/update_expert.html"
    success_url = reverse_lazy("expert_list")
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        provinces = Province.objects.all()
        cities = City.objects.all()
        health_centers = HealthCenter.objects.all()

        default_province_id = self.object.province.id if self.object.province else ""
        default_city_id = self.object.city.id if self.object.city else ""
        default_health_center_id = (
            self.object.health_center.id if self.object.health_center else ""
        )

        context.update(
            {
                "provinces": provinces,
                "cities": cities,
                "health_centers": health_centers,
                "default_province_id": default_province_id,
                "default_city_id": default_city_id,
                "default_health_center_id": default_health_center_id,
            }
        )
        return context

    def form_valid(self, form):
        self.object = form.save()
        province_id = self.request.POST.get("province")
        city_id = self.request.POST.get("city")
        health_center_id = self.request.POST.get("health_center")
        if province_id:
            self.object.province = Province.objects.get(id=province_id)
        if city_id:
            self.object.city = City.objects.get(id=city_id)
        if health_center_id:
            self.object.health_center = HealthCenter.objects.get(id=health_center_id)

        return super().form_valid(form)

    def form_invalid(self, form):
        # Get the error messages as a list of strings
        error_messages = []
        for field, errors in form.errors.as_data().items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

        # Add the error messages to the context
        context = self.get_context_data()
        context["error_messages"] = error_messages

        # Return the response with the form and error messages
        return self.render_to_response(context=context, form=form)


class ExpertDeleteView(DeleteView):
    model = CustomUser
    template_name = "accounts/delete_expert.html"
    success_url = reverse_lazy("expert_list")
    context_object_name = "username"


class ExpertListView(ListView):
    model = CustomUser
    template_name = "accounts/list_expert.html"
    context_object_name = "expert_list"

    def get_queryset(self):
        user_city = self.request.user.city
        is_superuser = self.request.user.is_superuser
        queryset = CustomUser.objects.filter(user_type="expert")

        if user_city:
            queryset = queryset.filter(city=user_city)
        elif is_superuser:
            # اگر کاربر جاری یک superuser است، همه کارشناسان را نمایش دهید
            pass
        else:
            # اگر هیچ یک از شرایط بالا نتطابق نکنند، لیست خالی برگردانید
            return queryset.none()

        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(username__icontains=query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context["expert_list"]:
            context["message"] = "موردی یافت نشد."
        return context


class ExpertRegisterView(CreateView):
    def get(self, request):
        provinces = Province.objects.all()
        cities = City.objects.all()
        health_centers = HealthCenter.objects.all()

        manager = CustomUser.objects.get(username=request.user.username)
        manager_province_id = manager.province_id
        manager_city_id = manager.city_id

        form = ExpertCreationForm()
        form.fields["user_type"].widget = forms.HiddenInput()

        if request.user.user_type == "manager":
            default_province_id = manager_province_id
            default_city_id = manager_city_id
        else:
            default_province_id = request.GET.get("province", "")
            default_city_id = request.GET.get("city", "")

        default_health_center_id = request.GET.get("health_center", "")

        return render(
            request,
            "accounts/register_expert.html",
            {
                "form": form,
                "provinces": provinces,
                "cities": cities,
                "health_centers": health_centers,
                "default_province_id": default_province_id,
                "default_city_id": default_city_id,
                "default_health_center_id": default_health_center_id,
            },
        )

    def post(self, request):
        provinces = Province.objects.all()
        cities = City.objects.all()
        health_centers = HealthCenter.objects.all()

        manager = CustomUser.objects.get(username=request.user.username)
        manager_province = manager.province
        manager_city = manager.city

        form = ExpertCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            user.province = manager_province
            user.city = manager_city
            user.user_type = "expert"

            user.save()
            messages.success(request, "عملیات با موفقیت انجام شد.")
            return redirect("expert_list")
        else:
            field_errors = form.errors.as_data()
            for field, errors in field_errors.items():
                error_messages = []
                for error in errors:
                    error_messages.append(str(error))
                messages.error(
                    request, f'خطا در فیلد {field}: {"، ".join(error_messages)}'
                )

        default_province_id = request.GET.get("province", "")
        default_city_id = request.GET.get("city", "")
        default_health_center_id = request.GET.get("health_center", "")

        return render(
            request,
            "accounts/register_expert.html",
            {
                "form": form,
                "provinces": provinces,
                "cities": cities,
                "health_centers": health_centers,
                "default_province_id": default_province_id,
                "default_city_id": default_city_id,
                "default_health_center_id": default_health_center_id,
            },
        )


# کلاس های مرتبط با بهورزان    ---------------------------------------------------------
class BehvarzUpdateView(UpdateView):
    model = CustomUser
    form_class = BehvarzChangeForm
    template_name = "accounts/update_behvarz.html"
    success_url = reverse_lazy("behvarz_list")
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        provinces = Province.objects.all()
        cities = City.objects.all()
        health_centers = HealthCenter.objects.all()
        villages = Village.objects.all()

        default_province_id = self.object.province.id if self.object.province else ""
        default_city_id = self.object.city.id if self.object.city else ""
        default_health_center_id = (
            self.object.health_center.id if self.object.health_center else ""
        )
        default_village_name = self.object.village.name if self.object.village else ""

        context.update(
            {
                "provinces": provinces,
                "cities": cities,
                "health_centers": health_centers,
                "villages": villages,
                "default_province_id": default_province_id,
                "default_city_id": default_city_id,
                "default_health_center_id": default_health_center_id,
                "default_village_name": default_village_name,
            }
        )
        return context

    def form_valid(self, form):
        self.object = form.save()
        province_id = self.request.POST.get("province")
        city_id = self.request.POST.get("city")
        health_center_id = self.request.POST.get("health_center")
        village_id = self.request.POST.get("village")
        if province_id:
            self.object.province = Province.objects.get(id=province_id)
        if city_id:
            self.object.city = City.objects.get(id=city_id)
        if health_center_id:
            self.object.health_center = HealthCenter.objects.get(id=health_center_id)
        if village_id:
            self.object.village = Village.objects.get(id=village_id)

        return super().form_valid(form)

    def form_invalid(self, form):
        # Get the error messages as a list of strings
        error_messages = []
        for field, errors in form.errors.as_data().items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

        # Add the error messages to the context
        context = self.get_context_data()
        context["error_messages"] = error_messages

        # Return the response with the form and error messages
        return self.render_to_response(context=context, form=form)


class BehvarzDeleteView(DeleteView):
    model = CustomUser
    template_name = "accounts/delete_behvarz.html"
    success_url = reverse_lazy("behvarz_list")
    context_object_name = "username"


class BehvarzRegisterView(CreateView):
    def get(self, request):
        provinces = Province.objects.all()
        cities = City.objects.all()
        health_centers = HealthCenter.objects.all()
        villages = Village.objects.all()

        manager = CustomUser.objects.get(username=request.user.username)
        manager_province_id = manager.province_id
        manager_city_id = manager.city_id

        form = BehvarzCreationForm()
        form.fields["user_type"].widget = forms.HiddenInput()

        if request.user.user_type == "manager":
            default_province_id = manager_province_id
            default_city_id = manager_city_id
        else:
            default_province_id = request.GET.get("province", "")
            default_city_id = request.GET.get("city", "")

        # default_city_id = request.GET.get('city', '')
        default_health_center_id = request.GET.get("health_center", "")

        return render(
            request,
            "accounts/register_behvarz.html",
            {
                "form": form,
                "provinces": provinces,
                "cities": cities,
                "health_centers": health_centers,
                "villages": villages,
                "default_province_id": default_province_id,
                "default_city_id": default_city_id,
                "default_health_center_id": default_health_center_id,
            },
        )

    def post(self, request):
        provinces = Province.objects.all()
        cities = City.objects.all()
        health_centers = HealthCenter.objects.all()
        villages = Village.objects.all()

        manager = CustomUser.objects.get(username=request.user.username)
        manager_province = manager.province
        manager_city = manager.city

        form = BehvarzCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            user.province = manager_province
            user.city = manager_city
            user.save()
            # behvarz = Behvarz(
            #     user=user,
            #     date_employee=form.cleaned_data['date_employee'],
            #     education=form.cleaned_data['education'],
            # )
            # behvarz.save()
            messages.success(request, "عملیات با موفقیت انجام شد.")
            return redirect("behvarz_list")
        else:
            field_errors = form.errors.as_data()
            for field, errors in field_errors.items():
                error_messages = []
                for error in errors:
                    error_messages.append(str(error))
                messages.error(
                    request, f'خطا در فیلد {field}: {"، ".join(error_messages)}'
                )

        default_province_id = request.GET.get("province", "")
        default_city_id = request.GET.get("city", "")
        default_health_center_id = request.GET.get("health_center", "")

        return render(
            request,
            "accounts/register_behvarz.html",
            {
                "form": form,
                "provinces": provinces,
                "cities": cities,
                "health_centers": health_centers,
                "villages": villages,
                "default_province_id": default_province_id,
                "default_city_id": default_city_id,
                "default_health_center_id": default_health_center_id,
            },
        )


class BehvarzListView(ListView):
    model = CustomUser
    template_name = "accounts/list_behvarz.html"
    context_object_name = "behvarz_list"

    def get_queryset(self):
        user_hc = self.request.user.health_center
        user_city = self.request.user.city
        is_superuser = self.request.user.is_superuser
        queryset = CustomUser.objects.filter(user_type="behvarz")

        if self.request.user.user_type != "behvarz":
            if user_hc:
                queryset = queryset.filter(health_center=user_hc)
            elif user_city:
                queryset = queryset.filter(city=user_city)

            if is_superuser:
                queryset = CustomUser.objects.filter(user_type="behvarz")

            query = self.request.GET.get("q")
            if query:
                queryset = queryset.filter(
                    Q(first_name__icontains=query)
                    | Q(last_name__icontains=query)
                    | Q(username__icontains=query)
                )
            return queryset
        else:
            raise Http404("شما به این صفحه دسترسی ندارید.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context["behvarz_list"]:
            context["message"] = "موردی یافت نشد."
        return context


# class BehvarzListView(ListView):
#     model = Behvarz
#     template_name = 'accounts/list_behvarz.html'
#     context_object_name = 'behvarz_list'
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         query = self.request.GET.get('q')
#         if query:
#             queryset = queryset.filter(user__first_name__icontains=query) | queryset.filter(
#                 user__last_name__icontains=query) | queryset.filter(user__username__icontains=query)
#         return queryset


class VillageUpdateView(LoginRequiredMixin, UpdateView):
    model = Village
    fields = ["name"]
    template_name = "accounts/village_edit.html"
    context_object_name = "village"

    def form_valid(self, form):
        response = super().form_valid(form)
        health_center_id = self.object.health_center.id
        return HttpResponseRedirect(
            reverse_lazy("village_add_list", kwargs={"pk": health_center_id})
        )

    def get_success_url(self):
        if "HTTP_REFERER" in self.request.META:
            return self.request.META["HTTP_REFERER"]
        else:
            return reverse_lazy(
                "village_add_list", kwargs={"pk": self.object.health_center.id}
            )


class VillageDeleteView(LoginRequiredMixin, DeleteView):
    model = Village
    context_object_name = "village"
    template_name = "accounts/village_delete.html"
    context_object_name = "village"

    def delete(self, request, *args, **kwargs):
        messages.success(request, f'روستای " " با موفقیت حذف شد. ')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        healthcenter_id = self.object.healthcenter.id
        return reverse("village_add_list", kwargs={"pk": healthcenter_id})


@login_required()
@require_http_methods(["GET", "POST"])
def village_add_list_view(request, pk):
    health_center = HealthCenter.objects.get(id=pk)
    village = Village.objects.filter(health_center=health_center).order_by("-id")

    if request.method == "POST":
        form = VillageForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            if Village.objects.filter(
                name=name, health_center=health_center.id
            ).exists():
                messages.warning(request, f" این روستا قبلا برای این مرکز ثبت شده است.")
            else:
                new_village = Village.objects.create(
                    name=name, health_center=health_center
                )
                new_village.save()
                messages.success(request, f'روستای "{name}" با موفقیت ثبت شد. ')
                return HttpResponseRedirect(
                    reverse("village_add_list", args=[health_center.id])
                )
        else:
            form = VillageForm()
            messages.warning(request, f"فرم معتبر نیست. لطفا مجددا تلاش کنید. ")

    else:
        form = VillageForm()

    if not village:
        messages.info(request, f"هنوز روستایی برای این مرکز تعریف نشده است.")

    context = {"village": village, "healthcenter": health_center, "form": form}
    return render(request, "accounts/village_add_list.html", context)


class HealthCenterUpdateView(LoginRequiredMixin, UpdateView):
    model = HealthCenter
    fields = ["name"]
    template_name = "accounts/hc_edit.html"
    context_object_name = "health_center"

    def form_valid(self, form):
        # response = super().form_valid(form)
        city_id = self.object.city.id
        return HttpResponseRedirect(reverse_lazy("hc_add_list", kwargs={"pk": city_id}))

    def get_success_url(self):
        if "HTTP_REFERER" in self.request.META:
            return self.request.META["HTTP_REFERER"]
        else:
            return reverse_lazy("hc_add_list", kwargs={"pk": self.object.city.id})


class HealthCenterDeleteView(LoginRequiredMixin, DeleteView):
    model = HealthCenter
    context_object_name = "health_center"
    template_name = "accounts/hc_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(request, f'نام " " با موفقیت حذف شد. ')
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        city_id = self.object.city.id
        return reverse("hc_add_list", kwargs={"pk": city_id})


@login_required()
@require_http_methods(["GET", "POST"])
def healthcenteraddview(request, pk):
    city = City.objects.get(id=pk)
    health_center = HealthCenter.objects.filter(city=city).order_by("-id")

    if request.method == "POST":
        form = HealthCenterForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            if HealthCenter.objects.filter(name=name, city=city.id).exists():
                messages.warning(
                    request, f'نام "{{name}}" قبلاً برای این شهر وارد شده است.'
                )
            else:
                new_health_center = HealthCenter.objects.create(name=name, city=city)
                new_health_center.save()
                messages.success(request, f'نام "{name}" برای این شهر ثبت شد.')
                return HttpResponseRedirect(reverse("hc_add_list", args=[city.id]))
        else:
            form = HealthCenterForm()
            messages.warning(request, "فرم معتبر نیست. لطفاً مجدداً تلاش کنید.")

    else:  # درخواست با متد GET انجام شده است
        form = HealthCenterForm()

    if not health_center:
        messages.info(request, "برای این شهر هنوز نام مرکز ثبت نشده است.")

    context = {"healthcenter": health_center, "city": city, "form": form}
    return render(request, "accounts/hc_add_list.html", context)


class CityUpdateView(LoginRequiredMixin, UpdateView):
    model = City
    template_name = "accounts/city_edit.html"
    fields = ["name"]
    context_object_name = "city"

    def form_valid(self, form):
        # response = super().form_valid(form)
        province_id = self.object.province.id
        return HttpResponseRedirect(
            reverse_lazy("city_add_list", kwargs={"pk": province_id})
        )

    def get_success_url(self):
        if "HTTP_REFERER" in self.request.META:
            return self.request.META["HTTP_REFERER"]
        else:
            return reverse_lazy("city_add_list", kwargs={"pk": self.object.province.id})


@login_required()
def province_city(request, pk):
    province = Province.objects.get(id=pk)
    cities = City.objects.filter(province=province).order_by("-id")

    if request.method == "POST":
        form = CityCreateForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            if City.objects.filter(name=name, province=province.id).exists():
                messages.warning(request, "نام این شهر قبلا وارد شده است.")
            else:
                new_city = City.objects.create(name=name, province=province)
                new_city.save()
                messages.success(request, "نام شهر به درستی وارد شده است.")
                return HttpResponseRedirect(
                    reverse("city_add_list", args=[province.id])
                )
    else:
        form = CityCreateForm()

    if not cities:
        messages.info(request, "برای این استان شهری ثبت نشده است.")

    context = {"cities": cities, "provinces": province, "form": form}
    return render(request, "accounts/city_add_list.html", context)


class CityDeleteView(LoginRequiredMixin, DeleteView):
    model = City
    context_object_name = "city"
    template_name = "accounts/city_delete.html"

    def delete(self, request, *args, **kwargs):
        messages.success(request, "نام شهر با موفقیت حذف شد.")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        province_id = self.object.province.id
        return reverse("city_add_list", kwargs={"pk": province_id})


class ProvinceUpdateView(LoginRequiredMixin, UpdateView):
    model = Province
    template_name = "accounts/province_edit.html"
    fields = ["name"]
    context_object_name = "province"

    def get_success_url(self):
        return reverse("province_add_list")


class ProvinceDeleteView(LoginRequiredMixin, DeleteView):
    model = Province
    success_url = reverse_lazy("province_add_list")
    context_object_name = "province"
    template_name = "accounts/province_delete.html"


class ProvinceAddView(LoginRequiredMixin, CreateView, ListView):
    model = Province
    template_name = "accounts/province_add_list.html"
    context_object_name = "provinces"
    fields = ["name"]
    success_url = reverse_lazy("province_add_list")

    def form_invalid(self, form):
        messages.error(self.request, "نام استان تکراری است.")
        return super().form_invalid(form)

    def form_valid(self, form):
        if Province.objects.filter(name=form.cleaned_data["name"]).exists():
            # form.add_error('name', 'نام شهرستان تکراری است.')
            # messages.error(self.request, 'نام شهرستان تکراری است.')
            return super().form_invalid(form)
        messages.success(self.request, "شهرستان با موفقیت اضافه شد.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("province_add_list")


class PLacesTableView(ListView):
    template_name = "accounts/places_table.html"

    def get_context_data(self, **kwargs):
        context = {}
        provinces = Province.objects.all()

        # جمع‌آوری اطلاعات استان‌ها و شهرها
        province_city_data = []
        for province in provinces:
            cities = City.objects.filter(province=province)
            city_names = [city.name for city in cities]
            province_city_data.append(
                {"province_name": province.name, "city_names": city_names}
            )

        # جمع‌آوری اطلاعات مراکز و روستاها
        city_center_data = []
        for city in City.objects.all():
            health_centers = HealthCenter.objects.filter(city=city)
            health_center_names = [hc.name for hc in health_centers]
            villages = Village.objects.filter(health_center__in=health_centers)
            village_names = [village.name for village in villages]
            city_center_data.append(
                {
                    "city_name": city.name,
                    "health_center_names": health_center_names,
                    "village_names": village_names,
                }
            )

        context["province_city_data"] = province_city_data
        context["city_center_data"] = city_center_data

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)
