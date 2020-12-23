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

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
domain = os.getenv('DOMAIN', None)

HELP = '- Show this information: help\n'\
       '- Start game as white: play\n'\
       '- Pick the colors: play white/black\n'\
       '- Play with yourself: play self\n'\
       '- Make a move: use Long Algebraic Notation\n'\
       'e2e4 moves a piece from e2 to e4\n'\
       'b1d2 moves a piece from b1 to d2\n'\
       'O-O-O or O-O to castle\n'\
       'Pawns are promoted to queen by default, or you can use e7e8=r to promote to rook. There are b (bishop), n (knight), r (rook), q (queen) choices\n'\
       '- Request undo of last move: undo\n'\
       '- Resign: resign\n'\
       '- Show current state: fsm'\

# '- Show all game PGNs: pgns\n'\
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)
if domain is None:
    print('Specify domain as environment variable.')
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
                states=["user", "botplayblack", "userplaywhite", "userplayblack", "botplaywhite", "userplayself"],
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
                        "source": ["userplaywhite", "userplayblack", "userplayself"],
                        "dest": "user",
                        "conditions": "is_going_to_resign"
                    },
                    {
                        "trigger": "advance",
                        "source": "userplaywhite",
                        "dest": "userplaywhite",
                        "conditions": "undo2"
                    },
                    {
                        "trigger": "advance",
                        "source": "userplayblack",
                        "dest": "userplayblack",
                        "conditions": "undo2"
                    },
                    {
                        "trigger": "advance",
                        "source": "userplayself",
                        "dest": "userplayself",
                        "conditions": "undo"
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
                        "trigger": "advance",
                        "source": "user",
                        "dest": "userplayself",
                        "conditions": "is_going_to_userplayself" 
                    },
                    {
                        "trigger": "advance",
                        "source": "userplayself",
                        "dest": "userplayself",
                        "conditions": "is_going_to_moveself" 
                    },
                    {
                        "trigger": "go_back",
                        "source": ["user", "botplayblack", "userplaywhite", "userplayblack", "botplaywhite", "userplayself"],
                        "dest": "user"
                    },
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
            return send_text_message(event.reply_token, HELP)
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
    machine[user_id].get_graph().draw(img_path)
    if os.path.isfile(img_path):
        return send_file(img_path, mimetype='image/png')
    return send_file(os.getcwd() + '/notfound.png', mimetype='image/png')

@app.route('/<user_id>/<stamp>', methods=['GET'])
def show_board(user_id, stamp):
    img_path = os.getcwd() + '/' + user_id + '/' + stamp + '.png'
    return send_file(img_path, mimetype='image/png')

if __name__ == "__main__":
    http_port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=http_port)
