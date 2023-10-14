from django.http import Http404
from django.shortcuts import get_object_or_404

from instructions.models import Instruction


class AuthAccDelInsMixin:
    def dispatch(self, request, pk, *args, **kwargs):
        instruction = get_object_or_404(Instruction, id=pk)
        if instruction.user == request.user or request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404("شما به این صفحه دسترسی ندارید.")


class AuthAccInsrtInsMixin:
    def dispatch(self, request, pk, *args, **kwargs):
        instruction = get_object_or_404(Instruction, id=pk)
        if (
            instruction.user == request.user
            and instruction.status == "drf"
            or request.user.is_superuser
        ):
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404("شما به این صفحه دسترسی ندارید.")


# ذخیره فرم با توجه به نوع کاربر
class FormValidMixin:
    def form_valid(self, form):
        if self.request.user.is_superuser:
            form.save()
        elif self.request.user.user_type == "manager":
            self.obj = form.save(commit=False)
            self.obj.user = self.request.user
        elif self.request.user.user_type == "expert":
            self.obj = form.save(commit=False)
            self.obj.user = self.request.user
        return super().form_valid(form)


class FieldsProfileMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            self.fields = [
                "first_name",
                "last_name",
                "birthday",
                "gender",
                "education",
                "cell_phone",
                "photo",
                "security_q",
                "security_key",
            ]
        elif request.user.user_type == "manager":
            self.fields = [
                "first_name",
                "last_name",
                "birthday",
                "gender",
                "education",
                "cell_phone",
                "photo",
                "security_q",
                "security_key",
            ]
        elif request.user.user_type == "expert":
            self.fields = [
                "first_name",
                "last_name",
                "birthday",
                "gender",
                "education",
                "cell_phone",
                "photo",
                "security_q",
                "security_key",
            ]
        elif request.user.user_type == "behvarz":
            self.fields = [
                "first_name",
                "last_name",
                "birthday",
                "gender",
                "education",
                "cell_phone",
                "photo",
                "security_q",
                "security_key",
            ]
        else:
            raise Http404("شما به این صفحه دسترسی ندارید.")
        return super().dispatch(request, *args, **kwargs)


# دسترسی به فیلدها برای ایجاد محتوا برای هر کاربر
class FieldsMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            self.fields = [
                "type",
                "number",
                "title",
                "description",
                "for_behvarz",
                "for_expert",
                "status",
            ]
        elif request.user.user_type == "manager":
            self.fields = [
                "type",
                "number",
                "title",
                "description",
                "for_behvarz",
                "for_expert",
                "status",
            ]
        elif request.user.user_type == "expert":
            self.fields = [
                "type",
                "number",
                "title",
                "description",
                "for_behvarz",
                "for_expert",
                "status",
            ]
        # elif request.user.is_behvarz:
        #     return super().dispatch(request, *args, **kwargs)
        else:
            raise Http404("شما به این صفحه دسترسی ندارید.")
        return super().dispatch(request, *args, **kwargs)
