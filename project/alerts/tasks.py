import requests
from alerts.celery import shared_task
from django.conf import settings
from .models import Stock

@shared_task
def fetch_stock_prices():
    API_KEY = settings.STOCK_API_KEY
    SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'FB', 'NVDA', 'PYPL', 'ADBE', 'NFLX']
    
    for symbol in SYMBOLS:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
        response = requests.get(url)
        data = response.json()
        
        if 'price' in data:
            price = float(data['price'])
            # Update or create stock
            stock, created = Stock.objects.update_or_create(
                symbol=symbol,
                defaults={'price': price}
            )
            # Check alerts for this stock
            check_alerts_for_stock.delay(stock.id)
    
    return "Stock prices updated successfully"

@shared_task
def check_alerts_for_stock(stock_id):
    from .models import Stock, Alert, TriggeredAlert
    from django.utils import timezone
    from datetime import timedelta
    
    stock = Stock.objects.get(id=stock_id)
    active_alerts = Alert.objects.filter(stock=stock, is_active=True)
    
    for alert in active_alerts:
        if alert.alert_type == 'PRICE':
            if stock.price >= alert.threshold:
                TriggeredAlert.objects.create(
                    alert=alert,
                    price=stock.price
                )
                # Send notification
                send_alert_notification.delay(alert.user.id, f"{stock.symbol} reached {stock.price}")
        
        elif alert.alert_type == 'DURATION':
            # Check if price has been below threshold for specified duration
            pass

@shared_task
def send_alert_notification(user_id, message):
    from accounts.models import User
    from django.core.mail import send_mail
    from django.conf import settings
    
    user = User.objects.get(id=user_id)
    send_mail(
        'Stock Alert Notification',
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )