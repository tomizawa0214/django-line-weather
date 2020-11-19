from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.template.loader import render_to_string
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent,
    TextMessage,
    TextSendMessage,
    FlexSendMessage,
    LocationMessage
)
from bs4 import BeautifulSoup
import requests
import os
import re
import datetime


CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

class CallbackView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse('OK')

    def post(self, request, *args, **kwargs):
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseBadRequest()
        except LineBotApiError as e:
            print(e)
            return HttpResponseServerError()

        return HttpResponse('OK')

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CallbackView, self).dispatch(*args, **kwargs)

    @staticmethod
    @handler.add(MessageEvent, message=LocationMessage)
    def handle_location(event):
        text = event.message.address

        # 位置情報からその日の天気を返す
        def get_weather_from_location(original_location):
            # 住所の中から郵便番号を抽出する
            location = re.findall('\d{3}-\d{4}', original_location)
            # 1回目のスクレイピングでは住所を検索し、候補から取ってくる
            url = "https://weather.yahoo.co.jp/weather/search/?p=" + location[0]
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
            content = soup.find(class_="serch-table")
            # 2回目のスクレイピングで用いるURLを得る
            location_url = "http:" + content.find('a').get('href')
            r = requests.get(location_url)
            soup = BeautifulSoup(r.text, 'html.parser')
            # 今日の天気を取得
            content = soup.find(id='yjw_pinpoint_today').find_all('td')
            info = [each.get_text().strip('\n') for each in content[1:]]
            # 明日の天気を取得
            content_t = soup.find(id='yjw_pinpoint_tomorrow').find_all('td')
            info_t = [each.get_text().strip('\n') for each in content_t[1:]]
                
            # 絵文字変換
            for i in range(9, 17):
                info[i] = info[i]\
                    .replace('晴れ', '☀')\
                    .replace('曇り', '☁')\
                    .replace('雨', '🌧')\
                    .replace('大雨', '☔')\
                    .replace('暴風雨', '☔🌀')\
                    .replace('雪', '❄')\
                    .replace('大雪', '☃')\
                    .replace('暴風雪', '☃🌀')

            for j in range(9, 17):
                info_t[j] = info[j]\
                    .replace('晴れ', '☀')\
                    .replace('曇り', '☁')\
                    .replace('雨', '🌧')\
                    .replace('大雨', '☔')\
                    .replace('暴風雨', '☔🌀')\
                    .replace('雪', '❄')\
                    .replace('大雪', '☃')\
                    .replace('暴風雪', '☃🌀')

            # 現在時刻を取得
            dt = datetime.datetime.now()

            # 0:00～2:59
            if 0 < dt.hour < 3:
                message_3 = {
                    "type": "flex",
                    "altText": "目的地の時間帯天気をお知らせします！",
                    "contents": {
                        "type": "bubble",
                        "direction": "ltr",
                        "header": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地の時間帯天気",
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#1DCD00",
                                    "align": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "none",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "0:00～",
                                            "flex": 1,
                                            "align": "start",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[9],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[18]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "margin": "xs",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "3:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[10],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[19]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "6:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[11],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[20]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "9:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[12],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[21]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "12:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[13],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[22]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "15:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[14],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[23]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "18:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[15],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[24]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "21:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[16],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[25]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地",
                                    "weight": "bold",
                                    "size": "xs",
                                    "align": "start",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "separator",
                                    "margin": "xs"
                                },
                                {
                                    "type": "text",
                                    "text": original_location,
                                    "size": "xxs",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": "引用：Yahoo!天気",
                                    "size": "xxs",
                                    "margin": "xxl",
                                    "contents": []
                                }
                            ]
                        }
                    }
                }
                return message_3

            # 3:00～5:59
            elif 3 <= dt.hour < 6:
                message_6 = {
                    "type": "flex",
                    "altText": "目的地の時間帯天気をお知らせします！",
                    "contents": {
                        "type": "bubble",
                        "direction": "ltr",
                        "header": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地の時間帯天気",
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#1DCD00",
                                    "align": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "none",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "3:00～",
                                            "flex": 1,
                                            "align": "start",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[10],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[19]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "margin": "xs",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "6:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[11],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[20]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "9:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[12],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[21]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "12:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[13],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[22]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "15:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[14],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[23]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "18:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[15],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[24]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "21:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[16],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[25]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "24:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[9],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[18]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地",
                                    "weight": "bold",
                                    "size": "xs",
                                    "align": "start",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "separator",
                                    "margin": "xs"
                                },
                                {
                                    "type": "text",
                                    "text": original_location,
                                    "size": "xxs",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": "引用：Yahoo!天気",
                                    "size": "xxs",
                                    "margin": "xxl",
                                    "contents": []
                                }
                            ]
                        }
                    }
                }
                return message_6

            # 6:00～8:59
            elif 6 <= dt.hour < 9:
                message_9 = {
                    "type": "flex",
                    "altText": "目的地の時間帯天気をお知らせします！",
                    "contents": {
                        "type": "bubble",
                        "direction": "ltr",
                        "header": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地の時間帯天気",
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#1DCD00",
                                    "align": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "none",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "6:00～",
                                            "flex": 1,
                                            "align": "start",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[11],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[20]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "margin": "xs",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "9:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[12],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[21]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "12:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[13],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[22]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "15:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[14],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[23]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "18:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[15],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[24]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "21:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[16],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[25]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "24:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[9],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[18]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌3:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[10],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[19]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地",
                                    "weight": "bold",
                                    "size": "xs",
                                    "align": "start",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "separator",
                                    "margin": "xs"
                                },
                                {
                                    "type": "text",
                                    "text": original_location,
                                    "size": "xxs",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": "引用：Yahoo!天気",
                                    "size": "xxs",
                                    "margin": "xxl",
                                    "contents": []
                                }
                            ]
                        }
                    }
                }
                return message_9

            # 9:00～11:59
            elif 9 <= dt.hour < 12:
                message_12 = {
                    "type": "flex",
                    "altText": "目的地の時間帯天気をお知らせします！",
                    "contents": {
                        "type": "bubble",
                        "direction": "ltr",
                        "header": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地の時間帯天気",
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#1DCD00",
                                    "align": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "none",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "9:00～",
                                            "flex": 1,
                                            "align": "start",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[12],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[21]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "margin": "xs",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "12:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[13],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[22]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "15:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[14],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[23]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "18:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[15],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[24]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "21:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[16],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[25]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "24:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[9],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[18]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌3:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[10],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[19]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌6:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[11],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[20]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地",
                                    "weight": "bold",
                                    "size": "xs",
                                    "align": "start",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "separator",
                                    "margin": "xs"
                                },
                                {
                                    "type": "text",
                                    "text": original_location,
                                    "size": "xxs",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": "引用：Yahoo!天気",
                                    "size": "xxs",
                                    "margin": "xxl",
                                    "contents": []
                                }
                            ]
                        }
                    }
                }
                return message_12

            # 12:00～14:59
            elif 12 <= dt.hour < 15:
                message_15 = {
                    "type": "flex",
                    "altText": "目的地の時間帯天気をお知らせします！",
                    "contents": {
                        "type": "bubble",
                        "direction": "ltr",
                        "header": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地の時間帯天気",
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#1DCD00",
                                    "align": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "none",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "12:00～",
                                            "flex": 1,
                                            "align": "start",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[13],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[22]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "margin": "xs",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "15:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[14],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[23]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "18:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[15],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[24]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "21:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[16],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[25]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "24:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[9],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[18]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌3:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[10],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[18]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌6:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[11],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[20]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌9:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[12],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[21]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地",
                                    "weight": "bold",
                                    "size": "xs",
                                    "align": "start",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "separator",
                                    "margin": "xs"
                                },
                                {
                                    "type": "text",
                                    "text": original_location,
                                    "size": "xxs",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": "引用：Yahoo!天気",
                                    "size": "xxs",
                                    "margin": "xxl",
                                    "contents": []
                                }
                            ]
                        }
                    }
                }
                return message_15

            # 15:00～17:59
            elif 15 <= dt.hour < 18:
                message_18 = {
                    "type": "flex",
                    "altText": "目的地の時間帯天気をお知らせします！",
                    "contents": {
                        "type": "bubble",
                        "direction": "ltr",
                        "header": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地の時間帯天気",
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#1DCD00",
                                    "align": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "none",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "15:00～",
                                            "flex": 1,
                                            "align": "start",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[14],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[23]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "margin": "xs",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "18:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[15],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[24]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "21:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[16],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[25]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "24:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[9],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[18]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌3:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[10],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[19]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌6:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[11],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[20]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌9:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[14],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[23]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌12:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[13],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[22]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地",
                                    "weight": "bold",
                                    "size": "xs",
                                    "align": "start",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "separator",
                                    "margin": "xs"
                                },
                                {
                                    "type": "text",
                                    "text": original_location,
                                    "size": "xxs",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": "引用：Yahoo!天気",
                                    "size": "xxs",
                                    "margin": "xxl",
                                    "contents": []
                                }
                            ]
                        }
                    }
                }
                return message_18

            # 18:00～20:59
            elif 18 <= dt.hour < 21:
                message_21 = {
                    "type": "flex",
                    "altText": "目的地の時間帯天気をお知らせします！",
                    "contents": {
                        "type": "bubble",
                        "direction": "ltr",
                        "header": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地の時間帯天気",
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#1DCD00",
                                    "align": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "none",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "18:00～",
                                            "flex": 1,
                                            "align": "start",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[15],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[24]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "margin": "xs",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "21:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[16],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[25]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "24:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[9],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[18]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌3:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[10],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[19]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌6:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[11],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[20]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌9:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[12],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[21]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌12:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[13],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[22]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌15:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[14],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[23]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地",
                                    "weight": "bold",
                                    "size": "xs",
                                    "align": "start",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "separator",
                                    "margin": "xs"
                                },
                                {
                                    "type": "text",
                                    "text": original_location,
                                    "size": "xxs",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": "引用：Yahoo!天気",
                                    "size": "xxs",
                                    "margin": "xxl",
                                    "contents": []
                                }
                            ]
                        }
                    }
                }
                return message_21

            # 21:00～23:59
            elif 21 <= dt.hour <= 23:
                message_23 = {
                    "type": "flex",
                    "altText": "目的地の時間帯天気をお知らせします！",
                    "contents": {
                        "type": "bubble",
                        "direction": "ltr",
                        "header": {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地の時間帯天気",
                                    "weight": "bold",
                                    "size": "xl",
                                    "color": "#1DCD00",
                                    "align": "center",
                                    "contents": []
                                }
                            ]
                        },
                        "body": {
                            "type": "box",
                            "layout": "vertical",
                            "spacing": "none",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "21:00～",
                                            "flex": 1,
                                            "align": "start",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info[16],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info[25]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "margin": "xs",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "24:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[9],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[18]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌3:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[10],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[19]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌6:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[11],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[20]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌9:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[12],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[21]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌12:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[13],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[22]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌15:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[14],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[23]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "horizontal",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "翌18:00～",
                                            "gravity": "center",
                                            "contents": []
                                        },
                                        {
                                            "type": "box",
                                            "layout": "horizontal",
                                            "contents": [
                                                {
                                                    "type": "text",
                                                    "text": info_t[15],
                                                    "size": "xl",
                                                    "contents": []
                                                },
                                                {
                                                    "type": "text",
                                                    "text": str(info_t[24]) + "℃",
                                                    "weight": "bold",
                                                    "size": "lg",
                                                    "align": "end",
                                                    "gravity": "center",
                                                    "contents": []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        "footer": {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": "目的地",
                                    "weight": "bold",
                                    "size": "xs",
                                    "align": "start",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "separator",
                                    "margin": "xs"
                                },
                                {
                                    "type": "text",
                                    "text": original_location,
                                    "size": "xxs",
                                    "margin": "md",
                                    "contents": []
                                },
                                {
                                    "type": "text",
                                    "text": "引用：Yahoo!天気",
                                    "size": "xxs",
                                    "margin": "xxl",
                                    "contents": []
                                }
                            ]
                        }
                    }
                }
                return message_23

        weather = get_weather_from_location(text)
        result = FlexSendMessage.new_from_json_dict(weather)
        line_bot_api.reply_message(
            event.reply_token,
            messages=result
        )