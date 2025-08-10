from rest_framework import serializers
from .models import Alert, TriggeredAlert, Stock
from accounts.models import User

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'symbol', 'name', 'price']
        read_only_fields = ['id', 'price'] 

class AlertSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    stock_id = serializers.PrimaryKeyRelatedField(
        queryset=Stock.objects.all(),
        source='stock',
        write_only=True,
        help_text="ID of the stock to monitor"
    )
    
    class Meta:
        model = Alert
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'stock']
        extra_kwargs = {
            'threshold': {'required': False},
            'duration': {'required': False},
        }
    
    def validate(self, data):
        """
        Validate that the correct fields are provided based on alert type
        """
        alert_type = data.get('alert_type')
        
        if alert_type == 'PRICE' and 'threshold' not in data:
            raise serializers.ValidationError(
                "Threshold is required for price alerts"
            )
            
        if alert_type == 'DURATION' and 'duration' not in data:
            raise serializers.ValidationError(
                "Duration is required for duration alerts"
            )
            
        return data

class TriggeredAlertSerializer(serializers.ModelSerializer):
    alert = AlertSerializer(read_only=True)
    
    class Meta:
        model = TriggeredAlert
        fields = '__all__'
        read_only_fields = ['id', 'triggered_at']