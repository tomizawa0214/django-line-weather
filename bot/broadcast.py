from django.template.loader import render_to_string
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage
import os
import requests


# CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
# line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
line_bot_api = LineBotApi("h9YGQlME9/AcSC/4o1Fwu3XJciHDE0rkkl/mXdORClMYCgwC90e4RhdePogIE4+gl/hw5StOvSO7/GoWQ5V/kJJc5o3/gs9L3TDxywcKPZwXB2CVM/e1G42yc6SjAxSm6Erar5TCVQeTEE8yaulhJgdB04t89/1O/w1cDnyilFU=")

r = requests.get('https://weather.tsukumijima.net/api/forecast/city/100010')
r_data = r.json()
d = r_data['forecasts']
maebashi = d[1]['image']['url']
maebashi_weather = d[1]['image']['title']
h_temperature = d[1]['temperature']['max']['celsius']
l_temperature = d[1]['temperature']['min']['celsius']
rainy_percent_0 = d[1]['chanceOfRain']['00-06']
rainy_percent_6 = d[1]['chanceOfRain']['06-12']
rainy_percent_12 = d[1]['chanceOfRain']['12-18']
rainy_percent_18 = d[1]['chanceOfRain']['18-24']

info = {
    "type": "flex",
    "altText": "明日の天気は、" + str(maebashi_weather),
    "contents": {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "horizontal",
            "contents": [
                {
                    "type": "text",
                    "text": "明日の前橋市の天気",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#457703",
                    "align": "center",
                    "gravity": "center",
                    "contents": []
                }
            ]
        },
        "hero": {
            "type": "image",
            "url": maebashi,
            "size": "md",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
                "type": "uri",
                "label": "Action",
                "uri": "https://linecorp.com/"
            }
        },
        "body": {
            "type": "box",
            "layout": "horizontal",
            "spacing": "md",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "flex": 1,
                    "contents": [
                        {
                            "type": "text",
                            "text": "気温",
                            "weight": "bold",
                            "flex": 1,
                            "align": "start",
                            "gravity": "center",
                            "contents": []
                        },
                        {
                            "type": "separator"
                        },
                        {
                            "type": "text",
                            "text": "最高　" + str(h_temperature) + "℃　/　最低　" + str(l_temperature) + "℃",
                            "flex": 1,
                            "gravity": "center",
                            "offsetTop": "5px",
                            "contents": []
                        },
                        {
                            "type": "text",
                            "text": "降水確率",
                            "weight": "bold",
                            "flex": 1,
                            "gravity": "bottom",
                            "margin": "xxl",
                            "contents": []
                        },
                        {
                            "type": "separator"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "paddingTop": "5px",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "0:00～6:00",
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": rainy_percent_0,
                                    "contents": []
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "6:00～12:00",
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": rainy_percent_6,
                                    "contents": []
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "12:00～18:00",
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": rainy_percent_12,
                                    "contents": []
                                }
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "18:00～24:00",
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": rainy_percent_18,
                                    "contents": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }
}

result = FlexSendMessage.new_from_json_dict(info)
line_bot_api.broadcast(messages=result)