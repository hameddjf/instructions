from django.views import View
from django.shortcuts import render, redirect
from .models import Email
from .forms import EmailForm


class EmailCreateView(View):
    model = Email
    form_class = EmailForm
    template_name = "emails/email.html"

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            email = form.save(commit=False)
            email.sender = request.user
            email.save()
            return redirect("home")
        return render(request, self.template_name, {"form": form})
