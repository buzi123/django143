from django.db import models

# Create your models here.
# models.py

from django.db import models

class DeviceData(models.Model):
    temperature = models.IntegerField()
    humidity = models.IntegerField()
    led_status = models.BooleanField(default=False)
    timestamp = models.DateTimeField()

    # 返回包含温度、湿度、LED状态和时间戳的字符串
    def __str__(self):
        return f"Temperature: {self.temperature}, Humidity: {self.humidity}, LED: {self.led_status}, Timestamp: {self.timestamp}"
