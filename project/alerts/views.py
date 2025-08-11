from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from .models import Alert, TriggeredAlert, Stock
from .serializers import AlertSerializer, TriggeredAlertSerializer, StockSerializer


class AlertListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        alerts = Alert.objects.filter(user=request.user)
        serializer = AlertSerializer(alerts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AlertSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AlertRetrieveDestroyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        return Alert.objects.filter(user=user, pk=pk).first()

    def get(self, request, pk):
        alert = self.get_object(pk, request.user)
        if not alert:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AlertSerializer(alert)
        return Response(serializer.data)

    def delete(self, request, pk):
        alert = self.get_object(pk, request.user)
        if not alert:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        alert.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TriggeredAlertListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        triggered_alerts = TriggeredAlert.objects.filter(alert__user=request.user)
        serializer = TriggeredAlertSerializer(triggered_alerts, many=True)
        return Response(serializer.data)


class StockListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        stocks = Stock.objects.all()
        serializer = StockSerializer(stocks, many=True)
        return Response(serializer.data)
