import requests
from celery import shared_task
from django.conf import settings
from .models import Stock

@shared_task
def fetch_stock_prices():
    API_KEY = settings.STOCK_API_KEY
    SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'FB', 'NVDA', 'PYPL', 'ADBE', 'NFLX']
    
    for symbol in SYMBOLS:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'price' in data:
                price = float(data['price'])
                stock, _ = Stock.objects.update_or_create(
                    symbol=symbol,
                    defaults={'price': price}
                )
                check_alerts_for_stock.delay(stock.id)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

    return "Stock prices updated successfully"

@shared_task
def check_alerts_for_stock(stock_id):
    from .models import Stock, Alert, TriggeredAlert
    from django.utils import timezone

    try:
        stock = Stock.objects.get(id=stock_id)
        active_alerts = Alert.objects.filter(stock=stock, is_active=True)

        for alert in active_alerts:
            if alert.alert_type == 'PRICE' and stock.price >= alert.threshold:
                TriggeredAlert.objects.create(alert=alert, price=stock.price)
                send_alert_notification.delay(alert.user.id, f"{stock.symbol} reached {stock.price}")
    except Exception as e:
        print(f"Error checking alerts for stock {stock_id}: {e}")

@shared_task
def send_alert_notification(user_id, message):
    from accounts.models import User
    from django.core.mail import send_mail

    try:
        user = User.objects.get(id=user_id)
        send_mail(
            'Stock Alert Notification',
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Failed to send email: {e}")
