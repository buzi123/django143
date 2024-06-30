from django.shortcuts import render
from django.http import JsonResponse
import json
import requests
from django.http import HttpResponseRedirect
from .models import DeviceData  # 导入设备数据模型

def get_device_status():
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
            temperature = None
            humidity = None
            led_status = None

            for item in response_data.get('data', []):
                if item['identifier'] == 'temp':
                    temperature = int(item['value'])
                elif item['identifier'] == 'humi':
                    humidity = int(item['value'])
                elif item['identifier'] == 'led':
                    led_status = item['value'].lower() == 'false'

            return temperature, humidity, led_status
        except requests.exceptions.JSONDecodeError:
            return None, None, None
    else:
        return None, None, None

# 因为云平台不会发送正确的返回信息，已经弃用
# def toggle_led(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         led_status = data.get('led')

#         url = "https://iot-api.heclouds.com/thingmodel/set-device-property"
#         authorization = "version=2018-10-31&res=products%2FnbZ3NLyFVT%2Fdevices%2Fesp8266&et=2034247827&method=sha1&sign=2cCGbfShvYthdBVesnXfPpBpWis%3D"
#         headers = {
#             "Accept": "application/json, text/plain, */*",
#             "Content-Type": "application/json",
#             "Authorization": authorization
#         }
#         body = {
#             "product_id": "nbZ3NLyFVT",
#             "device_name": "esp8266",
#             "params": {
#                 "led": led_status
#             }
#         }
#         response = requests.post(url, headers=headers, json=body)
        
#         return JsonResponse({
#             'status': response.status_code,
#             'message': response.text,
#         })

#     return JsonResponse({'error': 'Invalid request'}, status=400)

from myapp.management.commands.fetch_device_data import Command
def device_status(request):
    # 获取并更新最新的设备数据

    # 定义变量 fetch_data 并将 Command 类的 handle 方法赋值给它
    fetch_data = Command().handle
    # 调用 fetch_data 函数
    fetch_data()
    # 这里我们实例化了fetch_device_data命令的 Command 类。
    # Command().handle 是管理命令的主要执行函数，调用它时，程序会执行你在 fetch_device_data.py 中定义的逻辑，
    # 去 OneNet API 获取最新的设备数据并存储到数据库中。
    # 每次访问这个视图时，都会执行该函数，从而更新最新的数据。
    # 获取最新的数据记录
    latest_device_data = DeviceData.objects.latest('timestamp')

    return render(request, 'myapp/device_status.html', {
        'temperature': latest_device_data.temperature,
        'humidity': latest_device_data.humidity,
        'led_status': latest_device_data.led_status,
        'latest_update_message': "最新一次更新时间：" + latest_device_data.timestamp.strftime("%Y-%m-%d %H:%M:%S")
    })
    # 使用 Django 的 render 函数来渲染 device_status.html 模板，并传递获取的最新数据。
def control_led(request, state):
    url = "https://iot-api.heclouds.com/thingmodel/set-device-property"
    headers = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Authorization": "version=2018-10-31&res=products%2FnbZ3NLyFVT%2Fdevices%2Fesp8266&et=2034247827&method=sha1&sign=2cCGbfShvYthdBVesnXfPpBpWis%3D"
    }
    body = {
    "product_id": "nbZ3NLyFVT",
    "device_name": "esp8266",
    "params": {
        "led": None  
    }
    }
    # 设置LED灯状态
    body["params"]["led"] = state == "true"

    # 发送POST请求
    requests.post(url, headers=headers, json=body)

    # 重定向到设备状态页面
    return HttpResponseRedirect('/myapp/status/')
    # 请求完成后，函数重定向用户到设备状态页面，HttpResponseRedirect 是 Django 提供的一个快捷方法，
    # 用于生成一个 HTTP 302 重定向响应。


def latest_data_view(request):
    latest_data = DeviceData.objects.order_by('-timestamp')[:100]  # 获取最新的100条数据
    context = {'latest_data': latest_data}
    return render(request, 'myapp/latest_data.html', context)
