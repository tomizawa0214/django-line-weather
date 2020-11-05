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
)
import datetime
import requests
import pprint
import os


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
    @handler.add(MessageEvent, message=TextMessage)
    # def handle_message(event):
    #     dt = datetime.datetime.now()
    #     if dt.hour == 14:
    #         line_bot_api.reply_message(
    #             event.reply_token,
    #             [
    #                 TextSendMessage(text='位置情報を教えてください。'),
    #                 TextSendMessage(text='https://line.me/R/nv/location/')
    #             ]
    #         )

    def handle_message(event):
        r = requests.get('https://weather.tsukumijima.net/api/forecast/city/100010')
        r_data = r.json()
        d = r_data['forecasts']
        maebashi = d[1]['image']['title']
        emoji = 0x1000AA
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
            'emoji': emoji,
            'h_temperature': h_temperature,
            'l_temperature': l_temperature,
            'rainy_percent_0': rainy_percent_0,
            'rainy_percent_6': rainy_percent_6,
            'rainy_percent_12': rainy_percent_12,
            'rainy_percent_18': rainy_percent_18
        }

        # dt = datetime.datetime.now()
        # if dt.hour == 14:
        text = event.message.text
        if '天気' in text: 
            result = render_to_string('blog/text_template/weather.txt', context)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=result)
            )

    # @handler.add(MessageEvent, message=LocationMessage)
    # def handle_location(event):
    #     text = event.message.address

    #     result = sc.get_weather_from_location(text)
    #     line_bot_api.reply_message(
    #         event.reply_token,
    #         TextSendMessage(text=result)
    #     )