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

result = '-----前橋市の明日の天気-----\n'\
    + str(maebashi) \
    + '--------------------\n' \
    + '▼気温\n' 
    + '最高  ' + str(h_temperature) + '℃\n' \
    + '最低　' + str(l_temperature } + '℃\n' \
    + '--------------------\n' \
    + '▼降水確率\n' \
    + '00:00～06:00　' + str(rainy_percent_0) + '\n' \
    + '06:00～12:00　' + str(rainy_percent_6) + '\n' \
    + '12:00～18:00　' + str(rainy_percent_12) + '\n' \
    + '18:00～24:00　' + str(rainy_percent_18)

messages = TextSendMessage(text=result)
line_bot_api.broadcast(messages=messages)