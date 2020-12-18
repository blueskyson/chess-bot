# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from __future__ import unicode_literals

import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort, send_file
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message, send_image_message
import texts
app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

machine = TocMachine(
    states=["user", "playing"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "playing",
            "conditions": "start"
        },
        {
            "trigger": "advance",
            "source": "playing",
            "dest": "playing",
            "conditions": "move"
        },
        {
            "trigger": "go_back",
            "source": ["user", "init_game"],
            "dest": "user"
        }
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        
        print(f'\nFSM STATE: {machine.state}')
        # print(f'REQUEST BODY: \n{request.get_json()}')
        
        # general states
        if event.message.text.lower() == 'fsm':
            return send_image_message(event.reply_token, 'https://6d44374a6939.ngrok.io/show-fsm')
        
        response = machine.advance(event)
        if response == False:
            if machine.state == 'user':
                send_text_message(event.reply_token, 'hi')
            elif machine.state == 'init_game':
                send_text_message(event.reply_token, '幹')
    return 'OK'

@app.route('/show-fsm', methods=['GET'])
def show_fsm():
    machine.get_graph().draw('fsm.png', prog='dot', format='png')
    return send_file('fsm.png', mimetype='image/png')

if __name__ == "__main__":
    http_port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=http_port)
