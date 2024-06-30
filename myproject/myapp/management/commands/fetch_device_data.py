# 发送http请求到OneNet API获取设备数据，并解析返回的数据并存储到数据库中

from django.core.management.base import BaseCommand
from myapp.models import DeviceData
import requests
from datetime import datetime

class Command(BaseCommand):
    # 这是一个Django管理命令，用于从OneNet获取设备数据并存储到数据库
    help = 'Fetch device data from OneNet and store in database'
    
    def handle(self, *args, **kwargs):
        # 处理命令逻辑的主要方法

        url = "https://iot-api.heclouds.com/thingmodel/query-device-property"

        headers = {
            "Accept": "application/json, text/plain, */*",
            "authorization": "version=2018-10-31&res=products%2FnbZ3NLyFVT%2Fdevices%2Fesp8266&et=2034247827&method=sha1&sign=2cCGbfShvYthdBVesnXfPpBpWis%3D"
        }

        params = {
            "product_id": "nbZ3NLyFVT",
            "device_name": "esp8266"
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            try:
                response_data = response.json()
                print("Response data:", response_data)

                if response_data['code'] == 0:
                    humi_data = next(item for item in response_data['data'] if item['identifier'] == 'humi')
                    temp_data = next(item for item in response_data['data'] if item['identifier'] == 'temp')
                    led_data = next(item for item in response_data['data'] if item['identifier'] == 'led')

                    humidity = int(humi_data['value'])
                    temperature = int(temp_data['value'])
                    led_status = led_data['value'].lower() == 'true'
                    timestamp = datetime.fromtimestamp(humi_data['time'] / 1000.0)

                    DeviceData.objects.create(
                        temperature=temperature,
                        humidity=humidity,
                        led_status=led_status,
                        timestamp=timestamp
                    )
                    self.stdout.write(self.style.SUCCESS('成功获取并存储了一次设备数据'))
                else:
                    self.stdout.write(self.style.ERROR('请求失败,OneNet API返回错误信息'))
            except requests.exceptions.JSONDecodeError:
                print("错误：无法解码 JSON 响应")
        else:
            print(f"请求失败，显示状态码： {response.status_code}")