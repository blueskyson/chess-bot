from __future__ import unicode_literals

import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort, send_file
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine, domain
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
                states=["user", "botplayblack", "userplaywhite", "userplayblack", "botplaywhite"],
                transitions=[
                    {
                        "trigger": "advance",
                        "source": "user",
                        "dest": "userplaywhite",
                        "conditions": "is_going_to_userplaywhite"                        
                    },
                    {
                        "trigger": "advance",
                        "source": "user",
                        "dest": "botplaywhite",
                        "conditions": "is_going_to_userplayblack"                        
                    },
                    {
                        "trigger": "advance",
                        "source": ["userplaywhite", "userplayblack"],
                        "dest": "user",
                        "conditions": "is_going_to_resign"
                    },
                    {
                        "trigger": "advance",
                        "source": "userplaywhite",
                        "dest": "botplayblack",
                        "conditions": "is_going_to_move"                        
                    },
                    {
                        "trigger": "advance",
                        "source": "botplaywhite",
                        "dest": "userplayblack",
                        "conditions": "is_going_to_botmove"                        
                    },
                    {
                        "trigger": "advance",
                        "source": "botplayblack",
                        "dest": "userplaywhite",
                        "conditions": "is_going_to_botmove"
                    },
                    {
                        "trigger": "advance",
                        "source": "userplayblack",
                        "dest": "botplaywhite",
                        "conditions": "is_going_to_move"
                    },
                    {
                        "trigger": "go_back",
                        "source": ["user", "botplayblack", "userplaywhite"],
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
    img_path = os.getcwd() + '/fsm.png'
    machine[user_id].get_graph().draw(img_path, prog='dot', format='png')
    return send_file(img_path, mimetype='image/png')

@app.route('/<user_id>/<stamp>', methods=['GET'])
def show_board(user_id, stamp):
    img_path = os.getcwd() + '/' + user_id + '/' + stamp + '.png'
    return send_file(img_path, mimetype='image/png')

if __name__ == "__main__":
    http_port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=http_port)
