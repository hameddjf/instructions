from django.urls import path
from . import views

urlpatterns = [
    path('detailTickets/<int:pk>/', views.TicketDetailView.as_view(), name='detail_ticket'),

    path('listTickets/<int:pk>/', views.UserTicketListView.as_view(), name='list_tickets'),
    path('createTickets/', views.BaseView.as_view(), name='create_tickets'),
]
