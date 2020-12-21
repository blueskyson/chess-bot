import os

from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage, TemplateSendMessage, ImageCarouselColumn, ImageCarouselTemplate, URITemplateAction, ButtonsTemplate, MessageTemplateAction, ImageSendMessage
# from olami import Olami

channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))
    return "OK"

def send_carousel_message(reply_token, col):
    line_bot_api = LineBotApi(channel_access_token)
    message = TemplateSendMessage(
        alt_text = 'Carousel template',
        template = ImageCarouselTemplate(columns = col)
    )
    line_bot_api.reply_message(reply_token, message)
    return "OK"

def send_button_message(reply_token, title, text, btn, url):
    line_bot_api = LineBotApi(channel_access_token)
    message = TemplateSendMessage(
        alt_text='button template',
        template = ButtonsTemplate(
            title = title,
            text = text,
            thumbnail_image_url = url,
            actions = btn
        )
    )
    line_bot_api.reply_message(reply_token, message)
    return "OK"

def send_image_message(reply_token, url):
    line_bot_api = LineBotApi(channel_access_token)
    message = ImageSendMessage(
        original_content_url = url,
        preview_image_url = url
    )
    line_bot_api.reply_message(reply_token, message)
    return "OK"

def send_text_and_image_message(reply_token, text, url):
    line_bot_api = LineBotApi(channel_access_token)
    txt_message = TextSendMessage(text=text)
    img_message = ImageSendMessage(
        original_content_url = url,
        preview_image_url = url
    )
    line_bot_api.reply_message(reply_token, [txt_message, img_message])
    return "OK"

def push_text_message(user_id, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.push_message(user_id, TextSendMessage(text=text))
    return "OK"

def push_image_message(user_id, url):
    line_bot_api = LineBotApi(channel_access_token)
    message = ImageSendMessage(
        original_content_url = url,
        preview_image_url = url
    )
    line_bot_api.push_message(user_id, message)
    return "OK"

def push_2texts_and_image_massage(user_id, text1, text2, url):
    line_bot_api = LineBotApi(channel_access_token)
    txt_message1 = TextSendMessage(text=text1)
    txt_message2 = TextSendMessage(text=text2)
    img_message = ImageSendMessage(
        original_content_url = url,
        preview_image_url = url
    )
    line_bot_api.push_message(user_id, [txt_message1, txt_message2, img_message])
    return "OK"