from django.template.loader import render_to_string
from linebot import LineBotApi
from linebot.models import TextSendMessage, FlexSendMessage
import os
import requests
import datetime
import locale
from bs4 import BeautifulSoup


CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

r = requests.get('https://weather.tsukumijima.net/api/forecast/city/100010')
r_data = r.json()
d = r_data['forecasts']
maebashi = d[1]['image']['url']
maebashi_weather = d[1]['image']['title']
h_temperature = d[1]['temperature']['max']['celsius']
l_temperature = d[1]['temperature']['min']['celsius']
rainy_percent_0 = d[1]['chanceOfRain']['T00-06']
rainy_percent_6 = d[1]['chanceOfRain']['T06-12']
rainy_percent_12 = d[1]['chanceOfRain']['T12-18']
rainy_percent_18 = d[1]['chanceOfRain']['T18-24']

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

# # 明日の天気を取得
# r = requests.get("https://weather.yahoo.co.jp/weather/jp/10/4210/10202.html")
# soup = BeautifulSoup(r.text, 'html.parser')
# content = soup.find(id='yjw_pinpoint_tomorrow').find_all('td')
# info = [each.get_text().strip('\n') for each in content[1:]]

# # 絵文字変換
# for i in range(9, 17):
#     info[i] = info[i]\
#         .replace('晴れ', '☀')\
#         .replace('曇り', '☁')\
#         .replace('雨', '🌧')\
#         .replace('大雨', '☔')\
#         .replace('暴風雨', '☔🌀')\
#         .replace('雪', '❄')\
#         .replace('大雪', '☃')\
#         .replace('暴風雪', '☃🌀')

# message = {
#     "type": "flex",
#     "altText": "高崎市の明日の天気をお知らせします！",
#     "contents": {
#         "type": "bubble",
#         "direction": "ltr",
#         "header": {
#             "type": "box",
#             "layout": "horizontal",
#             "contents": [
#                 {
#                     "type": "text",
#                     "text": "明日の高崎市の天気",
#                     "weight": "bold",
#                     "size": "xl",
#                     "color": "#1DCD00",
#                     "align": "center",
#                     "contents": []
#                 }
#             ]
#         },
#         "body": {
#             "type": "box",
#             "layout": "vertical",
#             "spacing": "none",
#             "contents": [
#                 {
#                     "type": "box",
#                     "layout": "horizontal",
#                     "contents": [
#                         {
#                             "type": "text",
#                             "text": "0:00～",
#                             "flex": 1,
#                             "align": "start",
#                             "gravity": "center",
#                             "contents": []
#                         },
#                         {
#                             "type": "box",
#                             "layout": "horizontal",
#                             "contents": [
#                                 {
#                                     "type": "text",
#                                     "text": info[9],
#                                     "size": "xl",
#                                     "contents": []
#                                 },
#                                 {
#                                     "type": "text",
#                                     "text": str(info[18]) + "℃",
#                                     "weight": "bold",
#                                     "size": "lg",
#                                     "align": "end",
#                                     "gravity": "center",
#                                     "contents": []
#                                 }
#                             ]
#                         }
#                     ]
#                 },
#                 {
#                     "type": "box",
#                     "layout": "horizontal",
#                     "margin": "xs",
#                     "contents": [
#                         {
#                             "type": "text",
#                             "text": "3:00～",
#                             "gravity": "center",
#                             "contents": []
#                         },
#                         {
#                             "type": "box",
#                             "layout": "horizontal",
#                             "contents": [
#                                 {
#                                     "type": "text",
#                                     "text": info[10],
#                                     "size": "xl",
#                                     "contents": []
#                                 },
#                                 {
#                                     "type": "text",
#                                     "text": str(info[19]) + "℃",
#                                     "weight": "bold",
#                                     "size": "lg",
#                                     "align": "end",
#                                     "gravity": "center",
#                                     "contents": []
#                                 }
#                             ]
#                         }
#                     ]
#                 },
#                 {
#                     "type": "box",
#                     "layout": "horizontal",
#                     "contents": [
#                         {
#                             "type": "text",
#                             "text": "6:00～",
#                             "gravity": "center",
#                             "contents": []
#                         },
#                         {
#                             "type": "box",
#                             "layout": "horizontal",
#                             "contents": [
#                                 {
#                                     "type": "text",
#                                     "text": info[11],
#                                     "size": "xl",
#                                     "contents": []
#                                 },
#                                 {
#                                     "type": "text",
#                                     "text": str(info[20]) + "℃",
#                                     "weight": "bold",
#                                     "size": "lg",
#                                     "align": "end",
#                                     "gravity": "center",
#                                     "contents": []
#                                 }
#                             ]
#                         }
#                     ]
#                 },
#                 {
#                     "type": "box",
#                     "layout": "horizontal",
#                     "contents": [
#                         {
#                             "type": "text",
#                             "text": "9:00～",
#                             "gravity": "center",
#                             "contents": []
#                         },
#                         {
#                             "type": "box",
#                             "layout": "horizontal",
#                             "contents": [
#                                 {
#                                     "type": "text",
#                                     "text": info[12],
#                                     "size": "xl",
#                                     "contents": []
#                                 },
#                                 {
#                                     "type": "text",
#                                     "text": str(info[21]) + "℃",
#                                     "weight": "bold",
#                                     "size": "lg",
#                                     "align": "end",
#                                     "gravity": "center",
#                                     "contents": []
#                                 }
#                             ]
#                         }
#                     ]
#                 },
#                 {
#                     "type": "box",
#                     "layout": "horizontal",
#                     "contents": [
#                         {
#                             "type": "text",
#                             "text": "12:00～",
#                             "gravity": "center",
#                             "contents": []
#                         },
#                         {
#                             "type": "box",
#                             "layout": "horizontal",
#                             "contents": [
#                                 {
#                                     "type": "text",
#                                     "text": info[13],
#                                     "size": "xl",
#                                     "contents": []
#                                 },
#                                 {
#                                     "type": "text",
#                                     "text": str(info[22]) + "℃",
#                                     "weight": "bold",
#                                     "size": "lg",
#                                     "align": "end",
#                                     "gravity": "center",
#                                     "contents": []
#                                 }
#                             ]
#                         }
#                     ]
#                 },
#                 {
#                     "type": "box",
#                     "layout": "horizontal",
#                     "contents": [
#                         {
#                             "type": "text",
#                             "text": "15:00～",
#                             "gravity": "center",
#                             "contents": []
#                         },
#                         {
#                             "type": "box",
#                             "layout": "horizontal",
#                             "contents": [
#                                 {
#                                     "type": "text",
#                                     "text": info[14],
#                                     "size": "xl",
#                                     "contents": []
#                                 },
#                                 {
#                                     "type": "text",
#                                     "text": str(info[23]) + "℃",
#                                     "weight": "bold",
#                                     "size": "lg",
#                                     "align": "end",
#                                     "gravity": "center",
#                                     "contents": []
#                                 }
#                             ]
#                         }
#                     ]
#                 },
#                 {
#                     "type": "box",
#                     "layout": "horizontal",
#                     "contents": [
#                         {
#                             "type": "text",
#                             "text": "18:00～",
#                             "gravity": "center",
#                             "contents": []
#                         },
#                         {
#                             "type": "box",
#                             "layout": "horizontal",
#                             "contents": [
#                                 {
#                                     "type": "text",
#                                     "text": info[15],
#                                     "size": "xl",
#                                     "contents": []
#                                 },
#                                 {
#                                     "type": "text",
#                                     "text": str(info[24]) + "℃",
#                                     "weight": "bold",
#                                     "size": "lg",
#                                     "align": "end",
#                                     "gravity": "center",
#                                     "contents": []
#                                 }
#                             ]
#                         }
#                     ]
#                 },
#                 {
#                     "type": "box",
#                     "layout": "horizontal",
#                     "contents": [
#                         {
#                             "type": "text",
#                             "text": "21:00～",
#                             "gravity": "center",
#                             "contents": []
#                         },
#                         {
#                             "type": "box",
#                             "layout": "horizontal",
#                             "contents": [
#                                 {
#                                     "type": "text",
#                                     "text": info[16],
#                                     "size": "xl",
#                                     "contents": []
#                                 },
#                                 {
#                                     "type": "text",
#                                     "text": str(info[25]) + "℃",
#                                     "weight": "bold",
#                                     "size": "lg",
#                                     "align": "end",
#                                     "gravity": "center",
#                                     "contents": []
#                                 }
#                             ]
#                         }
#                     ]
#                 }
#             ]
#         },
#         "footer": {
#             "type": "box",
#             "layout": "vertical",
#             "contents": [
#                 {
#                     "type": "text",
#                     "text": "引用：Yahoo!天気",
#                     "size": "xxs",
#                     "margin": "xxl",
#                     "contents": []
#                 }
#             ]
#         }
#     }
# }

# result = FlexSendMessage.new_from_json_dict(message)
result = FlexSendMessage.new_from_json_dict(info)
line_bot_api.broadcast(messages=result)