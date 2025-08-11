import requests
from celery import shared_task
from django.conf import settings
from django.db import transaction
from .models import Stock, Alert, TriggeredAlert
from accounts.models import User
from accounts.views import send_plain_email


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
                auto_create_alerts_for_stock(stock)
                check_alerts_for_stock(stock.id)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
    return "Stock prices updated successfully"


def auto_create_alerts_for_stock(stock):
    threshold_price = round(stock.price * 1.05, 2)
    users = User.objects.filter(is_active=True)
    for user in users:
        if not Alert.objects.filter(user=user, stock=stock, is_active=True).exists():
            Alert.objects.create(
                user=user,
                stock=stock,
                alert_type='PRICE',
                threshold=threshold_price,
                is_active=True
            )
            print(f"Created alert for {user.email} on {stock.symbol} at {threshold_price}")


@shared_task
def check_alerts_for_stock(stock_id):
    try:
        stock = Stock.objects.get(id=stock_id)
        active_alerts = Alert.objects.filter(stock=stock, is_active=True)
        for alert in active_alerts:
            if alert.alert_type == 'PRICE' and stock.price >= alert.threshold:
                if not TriggeredAlert.objects.filter(alert=alert, price=stock.price).exists():
                    TriggeredAlert.objects.create(alert=alert, price=stock.price)
                    send_alert_notification.delay(
                        alert.user.id,
                        f"{stock.symbol} reached {stock.price} (threshold {alert.threshold})"
                    )
    except Exception as e:
        print(f"Error checking alerts for stock {stock_id}: {e}")


@shared_task
def send_alert_notification(user_id, message):
    try:
        user = User.objects.get(id=user_id)
        send_plain_email(user.email, 'Stock Alert Notification', message)
        print(f"Email sent to {user.email}")
    except Exception as e:
        print(f"Failed to send email: {e}")
