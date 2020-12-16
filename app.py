# encoding: utf-8
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)

app = Flask(__name__)

# you can replace by load env file
handler = WebhookHandler('90408a879e1c898bab4b38655daefc7f') 
line_bot_api = LineBotApi('v/8TFiGUMJ4Xf6XnwOSznFR69IGMhYTeOF8fL9dTjJIdxVItTtMvonoyvZYbfaF86PD5v+O5ScKnrgi2Whu2WuVVHbZtJqfsn2CaqX3o0KZ1pkEp8LYoLtg0i42v1JmoQqlSVFgJvrQgG3cD+bsfeQdB04t89/1O/w1cDnyilFU=') 


@app.route('/')
def index():
    return "<p>Hello World!</p>"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# ========== handle user message ==========
@handler.add(MessageEvent, message=TextMessage)  
def handle_text_message(event):
    # message from user                  
    msg = event.message.text
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=msg))


    


import os
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=os.environ['PORT'])
    
