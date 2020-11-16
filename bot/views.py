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
            # 明日の天気を取得
            # content_t = soup.find(id='yjw_pinpoint_tomorrow').find_all('td')
            info = []

            for each in content[1:]:
                info.append(each.get_text().strip('\n'))
                
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

            message = {
                "type": "flex",
                "altText": "目的地の時間帯天気",
                "contents": {
                    "type": "bubble",
                    "direction": "ltr",
                    "header": {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                            {
                                "type": "text",
                                "text": "目的地の今日の天気",
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

            return message

            # # 現在時刻を取得
            # dt_now = datetime.datetime.now()

            # # 0:00～2:59
            # if 0 < dt_now.hour < 3:
            #     return message_3
            # # 3:00～5:59
            # else if 3 <= dt_now.hour < 6:
            #     return message_6
            # # 6:00～8:59
            # else if 6 <= dt_now.hour < 9:
            #     return message_9
            # # 9:00～11:59
            # else if 9 <= dt_now.hour < 12:
            #     return message_12
            # # 12:00～14:59
            # else if 12 <= dt_now.hour < 15:
            #     return message_15
            # # 15:00～17:59
            # else if 15 <= dt_now.hour < 18:
            #     return message_18
            # # 18:00～20:59
            # else if 18 <= dt_now.hour < 21:
            #     return message_21
            # # 21:00～23:59
            # else if 21 <= dt_now.hour <= 23:
            #     return message_23

        info = get_weather_from_location(text)
        result = FlexSendMessage.new_from_json_dict(info)
        line_bot_api.reply_message(
            event.reply_token,
            messages=result
        )