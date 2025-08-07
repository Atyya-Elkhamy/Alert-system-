from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import Alert, TriggeredAlert, Stock
from .serializers import AlertSerializer, TriggeredAlertSerializer, StockSerializer

class AlertListCreateView(generics.ListCreateAPIView):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AlertRetrieveDestroyView(generics.RetrieveDestroyAPIView):
    serializer_class = AlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Alert.objects.filter(user=self.request.user)

class TriggeredAlertListView(generics.ListAPIView):
    serializer_class = TriggeredAlertSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TriggeredAlert.objects.filter(alert__user=self.request.user)

class StockListView(generics.ListAPIView):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    permission_classes = [permissions.IsAuthenticated]