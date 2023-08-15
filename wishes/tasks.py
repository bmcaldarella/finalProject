import schedule
import time
from datetime import timedelta
from django.utils import timezone
from .models import Create_vote

def close_expired_votes():
    now = timezone.now()
    expired_votes = Create_vote.objects.filter(status='open', timestamp__lt=now - timedelta(days=models.F('duration_days')))
    for vote in expired_votes:
        vote.close_vote()

# Ejecutar la tarea cada hora
schedule.every().hour.do(close_expired_votes)

while True:
    schedule.run_pending()
    time.sleep(1)
