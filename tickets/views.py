from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views.generic import ListView
from django.core.mail import send_mail
from django.contrib import messages
from django.views import View

from .models import Ticket, Comment, Attachment
from .forms import CommentForm, TicketForm


class TicketDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        ticket = get_object_or_404(Ticket, id=pk)
        comments = Comment.objects.filter(ticket=ticket)
        comment_form = CommentForm()
        admin_user = get_user_model().objects.filter(is_staff=True).first()

        if request.user.is_superuser:
            ticket.read_by_superuser = False
        else:
            ticket.read_by_user = False

        ticket.save()

        attachments = ticket.attachments.all()

        return render(request, 'tickets/ticket_detail.html',
                      {
                          'ticket': ticket,
                          'comments': comments,
                          'comment_form': comment_form,
                          'admin_user': admin_user,
                          'attachments': attachments,
                      })

    def post(self, request, pk):
        ticket = get_object_or_404(Ticket, id=pk)
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            if ticket.status == 'open':
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.user = request.user
                comment.save()

                new_status = request.POST.get('status')
                if request.user.is_superuser:
                    ticket.status = new_status
                    ticket.read_by_user = True
                    ticket.read_by_superuser = False
                else:
                    ticket.status = 'open'
                    ticket.read_by_user = False
                    ticket.read_by_superuser = True
                ticket.save()

        return HttpResponseRedirect(reverse('detail_ticket', args=[pk]))


def send_admin_notification(ticket):
    # پیاده‌سازی تابع ارسال اطلاعیه به ادمین، به عنوان مثال ارسال ایمیل
    subject = 'New Ticket Submission'
    message = f'A new ticket has been submitted with the title: {ticket.title}'
    from_email = 'hamze_Nasirii@yahoo.com'
    to_email = 'amir_hamze64@yahoo.com'
    send_mail(subject, message, from_email, [to_email])


class BaseView(LoginRequiredMixin, FormView):
    template_name = 'tickets/ticket_form.html'
    form_class = TicketForm
    success_url = reverse_lazy('create_tickets')

    def form_valid(self, form):
        ticket = form.save(commit=False)
        ticket.status = 'open'
        ticket.user = self.request.user
        ticket.read_by_user = 'True'
        ticket.save()

        attachments = self.request.FILES.getlist('attachment')
        for attachment in attachments:
            Attachment.objects.create(ticket=ticket, file=attachment)

        messages.success(self.request, 'تیکت با موفقیت ارسال شد.')
        return super().form_valid(form)

    def form_invalid(self, form):
        field_errors = form.errors.items()
        error_message = "Form submission failed. Please check the form for errors."
        return self.render_to_response(
            self.get_context_data(form=form, field_errors=field_errors, error_message=error_message)
        )


class UserTicketListView(ListView):
    model = Ticket
    template_name = 'tickets/user_ticket_list.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Ticket.objects.filter(status='open')
        else:
            return Ticket.objects.filter(user=self.request.user)

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #
    #
    #     return context
