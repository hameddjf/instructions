from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.http import HttpResponseBadRequest, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.storage import default_storage
from django.views.generic.edit import FormView
from django.http import HttpResponse, Http404
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
import qrcode
import base64
import io

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from accounts.mixins import FieldsMixin, FormValidMixin, AuthAccInsrtInsMixin
from .forms import InstructionForm, InsChangeForm, CreateTagForm
from .models import Instruction, Attachment, Tag
from django.views import View


class CreateTagsView(LoginRequiredMixin, FormView):
    form_class = CreateTagForm
    template_name = "instructions/create_tags.html"
    success_url = reverse_lazy("create_tags")

    def form_valid(self, form):
        # بررسی تگ تکراری
        name = form.cleaned_data["name"]
        if Tag.objects.filter(name=name).exists():
            messages.error(self.request, "تگ تکراری است و نمی‌توانید آن را اضافه کنید.")
            return super().form_invalid(form)
        else:
            form.save()
            messages.success(
                self.request, "تگ '{}' با موفقیت به لیست اضافه شد.".format(name)
            )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        return context

    """
    Delete a tag by its primary key.

    Parameters:
        request (HttpRequest): The HTTP request object.
        pk (int): The primary key of the tag to be deleted.

    Returns:
        HttpResponse or JsonResponse: If the tag is successfully deleted, a redirect response is returned.
                                      If the tag is not found, a JSON response with an error message is returned.
    """


def delete_tag(request, pk):
    try:
        tag = Tag.objects.get(pk=pk)
        tag_name = tag.name
        tag.delete()
        messages.success(request, f"تگ '{tag_name}' با موفقیت حذف شد.")
        return redirect("create_tags")
    except Tag.DoesNotExist:
        messages.error(request, f"تگ '{tag_name}' یافت نشد.")
        return redirect("create_tags")


class InstructionRestoreView(View):
    def get(self, request, instruction_id):
        instruction = get_object_or_404(Instruction, id=instruction_id)
        instruction.is_active = True
        instruction.save()
        return redirect("self_instruction_list")


def increase_download(request, attachment_id):
    attachment = get_object_or_404(Attachment, id=attachment_id)
    attachment.increase_download_count()

    response = {
        "download_count": attachment.download_count,
        "file_url": attachment.file.url,
    }
    # print('download_count')

    return JsonResponse(response)


class InsDetailView(DetailView):
    model = Instruction
    template_name = "instructions/ins_detail.html"
    context_object_name = "instruction"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("instruction_attach")

    # def increase_download(self, request, attachment_id):
    #     attachment = Attachment.objects.get(id=attachment_id)
    #     attachment.increase_download_count()
    #     return redirect(attachment.file.url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instruction = self.get_object()

        # Create QR code for each uploaded file
        attachments = instruction.instruction_attach.all()
        qr_codes = []
        attachment_download_counts = []

        for attachment in attachments:
            if attachment.file and default_storage.exists(attachment.file.name):
                file_url = self.request.build_absolute_uri(attachment.file.url)
                qr = qrcode.QRCode(version=1, box_size=3, border=3)
                qr.add_data(file_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                img_buffer = io.BytesIO()
                img.save(img_buffer, format="PNG")
                img_data = base64.b64encode(img_buffer.getvalue())
                qr_codes.append(img_data.decode("utf-8"))

                attachment_download_counts.append(attachment.download_count)

        context["qr_codes"] = qr_codes
        context["attachments"] = attachments
        context["attachment_download_counts"] = attachment_download_counts
        tags = instruction.tags.all()
        context["tags"] = tags

        return context


def ins_delete(request, pk):
    instruction = get_object_or_404(Instruction, id=pk)
    if request.method == "POST":
        instruction.is_active = False
        instruction.save()
        return redirect("instruction_list")
    return render(request, "instructions/ins_delete.html", {"instruction": instruction})


class InsUpdateView(LoginRequiredMixin, UpdateView):
    model = Instruction
    form_class = InsChangeForm
    template_name = "instructions/ins_update.html"
    success_url = reverse_lazy("self_instruction_list")

    # context_object_name = 'instruction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instruction = self.get_object()
        context["attachments"] = instruction.instruction_attach.all()
        return context

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.user = self.object.user
            if (
                not form.cleaned_data["for_behvarz"]
                and not form.cleaned_data["for_expert"]
            ):
                messages.error(
                    self.request, "حداقل یکی از موارد بهورز یا کارشناس را انتخاب کنید."
                )
                return super().form_invalid(form)

            # Save the form
            instance = form.save(commit=False)

            # Delete selected attachments
            attachments_get = self.request.POST.getlist("selected_attachments")
            print("Selected attachments:", attachments_get)
            print("Instance:", instance)
            attachments_to_delete = Attachment.objects.filter(
                id__in=attachments_get, ins_attach=instance
            )
            print("Attachments to delete:", attachments_to_delete)
            for attachment in attachments_to_delete:
                # Delete the file from storage
                file_path = attachment.file.path
                print("File path:", file_path)
                default_storage.delete(file_path)
                # Delete the attachment
                attachment.delete()

            # Handle uploaded files
            uploaded_files = self.request.FILES.getlist(
                "attachment"
            )  # نام فیلد مربوط به آپلود فایل را وارد کنید
            for uploaded_file in uploaded_files:
                attachment = Attachment(file=uploaded_file, ins_attach=instance)
                attachment.save()

            instance.save()

        messages.success(self.request, "محتوا با موفقیت ارسال شد.")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(
                    self.request, f"خطا در فیلد {form.fields[field].label}: {error}"
                )
        return self.render_to_response(
            self.get_context_data(
                form=form,
            )
        )


class InsCreateView(LoginRequiredMixin, FieldsMixin, FormValidMixin, CreateView):
    model = Instruction
    template_name = "instructions/ins_create.html"
    success_url = reverse_lazy("self_instruction_list")

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.user = self.request.user
            if (
                not form.cleaned_data["for_behvarz"]
                and not form.cleaned_data["for_expert"]
            ):
                messages.error(
                    self.request, "حداقل یکی از موارد بهورز یا کارشناس را انتخاب کنید."
                )
                return super().form_invalid(form)

            # Save instruction
            form.save(commit=False)
            form.save()

            # Get selected tag names from the form
            selected_tags = [
                tag.rstrip(",") for tag in self.request.POST.getlist("selected_tags")
            ]

            # Add existing tags to the instruction
            for tag_name in selected_tags:
                try:
                    tag = Tag.objects.get(name=tag_name)
                    form.instance.tags.add(tag)
                except Tag.DoesNotExist:
                    messages.error(
                        self.request, f'Tag with name "{tag_name}" does not exist.'
                    )

            attachments = self.request.FILES.getlist("attachment")
            for attachment in attachments:
                Attachment.objects.create(ins_attach=form.instance, file=attachment)

            form.save()

            messages.success(self.request, "محتوا با موفقیت ارسال شد.")
            return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(
                    self.request, f"خطا در فیلد {form.fields[field].label}: {error}"
                )
        return self.render_to_response(self.get_context_data(form=form))


def get_suggested_tags(request):
    query = request.GET.get("query", "")
    tags = Tag.objects.filter(name__icontains=query)[
        :10
    ]  # فرض کنید تگ‌ها در مدل Tag ذخیره شده‌اند.
    suggestions = [{"name": tag.name, "id": tag.id} for tag in tags]
    return JsonResponse({"suggestions": suggestions})


class SelfInsListView(LoginRequiredMixin, ListView):
    model = Instruction
    template_name = "instructions/self_ins_list.html"
    context_object_name = "instructions"
    paginate_by = 20

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user_id = self.request.user.id
            return Instruction.objects.filter(user_id=user_id).order_by(
                "-datetime_created"
            )
        return Instruction.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["last_visited"] = self.request.session.get("last_visited")
        self.request.session["last_visited"] = timezone.now().isoformat()
        context["ins_count"] = self.get_queryset().count()

        return context

    @property
    def download_counts(self):
        if not hasattr(self, "_download_counts"):
            self._download_counts = {
                instruction.id: instruction.download_count
                for instruction in self.object_list
            }
        return self._download_counts


from .utils import perform_search


class InsListView(LoginRequiredMixin, ListView):
    model = Instruction
    template_name = "instructions/ins_list.html"
    context_object_name = "instructions"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.distinct()

        # Apply search filters
        search_query = self.request.GET.get("q")
        tag_filter = self.request.GET.get("tag")
        type_filter = self.request.GET.get("type")
        start_date_filter = self.request.GET.get("start_date")
        end_date_filter = self.request.GET.get("end_date")
        status_filter = self.request.GET.get("status")

        queryset = perform_search(
            queryset,
            search_query,
            tag_filter,
            type_filter,
            start_date_filter,
            end_date_filter,
            status_filter,
            include_deleted=True,
        )

        # Prefetch related instruction_attach and calculate download counts
        queryset = queryset.prefetch_related("instruction_attach")
        download_counts = {
            instruction.id: instruction.instruction_attach.count()
            for instruction in queryset
        }

        # Add download_counts to context
        self.download_counts = download_counts

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add download_counts to context
        context["download_counts"] = self.download_counts

        # Add type_choices to context
        form = InstructionForm()
        context["type_choices"] = form.fields["type"].choices

        # Add Tags to context
        context["tags"] = Tag.objects.all()

        # Add Count Installations to context
        context["ins_count"] = self.get_queryset().count()

        return context


class InstructionDownloadView(View):
    def get(self, request, instruction_id):
        instruction = get_object_or_404(Instruction, id=instruction_id)

        # Increment the download count for the instruction
        instruction.increment_download_count()

        # Get the attachment related to the instruction (assuming only one attachment per instruction)
        attachment = instruction.instruction_attach.first()

        if attachment:
            # Generate the response with the file
            file_path = attachment.file.path
            with open(file_path, "rb") as file:
                response = HttpResponse(
                    file.read(), content_type="application/octet-stream"
                )
                response[
                    "Content-Disposition"
                ] = f'attachment; filename="{attachment.file_name}"'
                return response
        else:
            return HttpResponse("فایل ضمیمه وجود ندارد.")


class InsListViewDeleted(ListView):
    model = Instruction
    template_name = "instructions/ins_list_deleted.html"
    context_object_name = "instructions"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.distinct()

        # Apply search filters
        search_query = self.request.GET.get("q")
        tag_filter = self.request.GET.get("tag")
        type_filter = self.request.GET.get("type")
        start_date_filter = self.request.GET.get("start_date")
        end_date_filter = self.request.GET.get("end_date")
        status_filter = self.request.GET.get("status")

        queryset = perform_search(
            queryset,
            search_query,
            tag_filter,
            type_filter,
            start_date_filter,
            end_date_filter,
            status_filter,
            include_deleted=True,
        )
        return queryset.filter(is_active=False)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ins_count"] = self.get_queryset().count()
        return context
