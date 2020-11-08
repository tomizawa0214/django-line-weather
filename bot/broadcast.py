from django.template.loader import render_to_string
from linebot import LineBotApi
from linebot.models import TextSendMessage
import os
import requests


CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

r = requests.get('https://weather.tsukumijima.net/api/forecast/city/100010')
r_data = r.json()
d = r_data['forecasts']
maebashi = d[1]['image']['title']
h_temperature = d[1]['temperature']['max']['celsius']
l_temperature = d[1]['temperature']['min']['celsius']
rainy_percent_0 = d[1]['chanceOfRain']['00-06']
rainy_percent_6 = d[1]['chanceOfRain']['06-12']
rainy_percent_12 = d[1]['chanceOfRain']['12-18']
rainy_percent_18 = d[1]['chanceOfRain']['18-24']

context = {
    'r': r,
    'r_data': r_data,
    'd': d,
    'maebashi': maebashi,
    'h_temperature': h_temperature,
    'l_temperature': l_temperature,
    'rainy_percent_0': rainy_percent_0,
    'rainy_percent_6': rainy_percent_6,
    'rainy_percent_12': rainy_percent_12,
    'rainy_percent_18': rainy_percent_18
}

result = render_to_string('blog/text_template/weather.txt', context)
messages = TextSendMessage(text=result)
line_bot_api.broadcast(messages=messages)