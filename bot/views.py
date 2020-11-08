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
    LocationMessage
)
from bs4 import BeautifulSoup
import requests
import os
import re


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
            content = soup.find(id='yjw_pinpoint_today').find_all('td')
            info = []

            for each in content[1:]:
                info.append(each.get_text().strip('\n'))

            # 時間
            time = info[:8]
            # 天気
            weather = info[9:17]
            # 気温
            temperature = info[18:26]
            # 上の3つの情報を合わせる
            weather_info = [(time[i], weather[i], temperature[i]) for i in range(8)]

            result_info = [('{0[0]}　{0[1]} {0[2]}°C'.format(weather_info[i])) for i in range(8)]
            today_weather = '\n'.join(result_info)

            # 表記変更
            today_weather = today_weather\
                .replace('0時', '00:00～')\
                .replace('3時', '03:00～')\
                .replace('6時', '06:00～')\
                .replace('9時', '09:00～')\
                .replace('12時', '12:00～')\
                .replace('15時', '15:00～')\
                .replace('18時', '18:00～')\
                .replace('21時', '21:00～')\
                .replace('晴れ', '☀')\
                .replace('曇り', '☁')\
                .replace('雨', '🌧')\
                .replace('大雨', '☔')\
                .replace('暴風雨', '☔🌀')\
                .replace('雪', '❄')\
                .replace('大雪', '☃')\
                .replace('暴風雪', '☃🌀')

            context = {
                'original_location': original_location,
                'today_weather': today_weather,
                'location_url': location_url,
            }

            result = render_to_string('blog/text_template/today_weather.txt', context)

            return result

        result = get_weather_from_location(text)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=result)
        )