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
import chess

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
# domain = 'https://a80b49743215.ngrok.io'
domain = 'https://lincc-linebot.herokuapp.com'

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

machine = {}

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
        if event.source.user_id not in machine:
            machine[event.source.user_id] = TocMachine(
                states=["user", "play", "move"],
                transitions=[
                    {
                        "trigger": "advance",
                        "source": "user",
                        "dest": "play",
                        "conditions": "is_going_to_play"
                    },
                    {
                        "trigger": "advance",
                        "source": "play",
                        "dest": "play",
                        "conditions": "is_going_to_move"
                    },
                    {
                        "trigger": "go_back",
                        "source": ["user", "play"],
                        "dest": "user"
                    }
                ],
                initial="user",
                auto_transitions=False,
                show_conditions=True,
            )

        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        txt = event.message.text
        print(f'\nUser: {event.source.user_id} FSM STATE: {machine[event.source.user_id].state}')
        # print(f'REQUEST BODY: \n{request.get_json()}')
        
        # general states
        if txt == 'fsm':
            return send_image_message(event.reply_token, domain + '/show-fsm/' + event.source.user_id)
        if txt == 'help':
            return send_text_message(event.reply_token, texts.HELP)
        response = machine[event.source.user_id].advance(event)
        if response == False:
            if machine[event.source.user_id].state == 'play':
                if txt == 'play':
                    send_text_message(event.reply_token, 'You are already in a game!')
            elif machine[event.source.user_id].state == 'user':
                if txt == 'resign' or txt == 'draw' or txt == 'undo':
                    send_text_message(event.reply_token, 'Invalid request, you are not in a game!')
    return 'OK'

@app.route('/show-fsm/<user_id>', methods=['GET'])
def show_fsm(user_id):
    machine[user_id].get_graph().draw('fsm.png', prog='dot', format='png')
    return send_file('fsm.png', mimetype='image/png')

@app.route('/<user_id>/<stamp>', methods=['GET'])
def show_board(user_id, stamp):
    img_path = os.getcwd() + '/' + user_id + '/' + stamp + '.png'
    return send_file(img_path, mimetype='image/png')

if __name__ == "__main__":
    http_port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=http_port)
