from django.template.loader import render_to_string
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage
import os
import requests
import datetime
import locale


CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

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
                    "color": "#457703FF",
                    "align": "center",
                    "contents": []
                }
            ]
        },
        "hero": {
            "type": "image",
            "url": maebashi,
            "size": "lg",
            "aspectRatio": "20:13",
            "aspectMode": "fit",
            "action": {
                "type": "uri",
                "label": "Action",
                "uri": "https://linecorp.com/"
            }
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "気温",
                    "weight": "bold",
                    "contents": []
                },
                {
                    "type": "separator",
                    "margin": "xs"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "flex": 1,
                    "paddingBottom": "10px",
                    "contents": [
                        {
                            "type": "text",
                            "text": "hello, world",
                            "contents": [
                                {
                                    "type": "span",
                                    "text": "最高　"
                                },
                                {
                                    "type": "span",
                                    "text": str(h_temperature) + "℃",
                                    "size": "xl",
                                    "color": "#FF0000"
                                }
                            ]
                        },
                        {
                            "type": "text",
                            "text": "hello, world",
                            "contents": [
                                {
                                    "type": "span",
                                    "text": "最低　"
                                },
                                {
                                    "type": "span",
                                    "text": str(l_temperature) + "℃",
                                    "size": "xl",
                                    "color": "#0096FF"
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "text",
                    "text": "降水確率",
                    "weight": "bold",
                    "margin": "xxl",
                    "contents": []
                },
                {
                    "type": "separator",
                    "margin": "xs"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "flex": 2,
                    "contents": [
                        {
                            "type": "text",
                            "text": "0:00 - 6:00",
                            "flex": 1,
                            "gravity": "center",
                            "contents": []
                        },
                        {
                            "type": "text",
                            "text": rainy_percent_0,
                            "size": "xl",
                            "flex": 2,
                            "align": "end",
                            "gravity": "center",
                            "offsetEnd": "70px",
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
                            "text": "6:00 - 12:00",
                            "gravity": "center",
                            "contents": []
                        },
                        {
                            "type": "text",
                            "text": rainy_percent_6,
                            "size": "xl",
                            "align": "end",
                            "offsetEnd": "70px",
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
                            "text": "12:00 - 18:00",
                            "gravity": "center",
                            "contents": []
                        },
                        {
                            "type": "text",
                            "text": rainy_percent_12,
                            "size": "xl",
                            "align": "end",
                            "offsetEnd": "70px",
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
                            "text": "18:00 - 24:00",
                            "gravity": "center",
                            "contents": []
                        },
                        {
                            "type": "text",
                            "text": rainy_percent_18,
                            "size": "xl",
                            "align": "end",
                            "offsetEnd": "70px",
                            "contents": []
                        }
                    ]
                }
            ]
        }
    }
}

result = FlexSendMessage.new_from_json_dict(info)
line_bot_api.broadcast(messages=result)