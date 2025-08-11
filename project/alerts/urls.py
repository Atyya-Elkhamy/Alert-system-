from django.urls import path
from .views import *

urlpatterns = [
    path("alerts/", AlertListCreateView.as_view(), name="alert-list-create"),
    path("alerts/<int:pk>/", AlertRetrieveDestroyView.as_view(), name="alert-detail-delete"),
    path("alerts/triggered/", TriggeredAlertListView.as_view(), name="triggered-alert-list"),
    path("stocks/", StockListView.as_view(), name="stock-list"),
]
