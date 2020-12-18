from transitions.extensions import GraphMachine
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction
from utils import send_text_message, send_image_message
from datetime import datetime

# domain = 'https://7a11edb09d53.ngrok.io'
domain = 'https://lincc-linebot.herokuapp.com'

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_play(self, event):
        text = event.message.text
        return text.lower() == "play"
    def on_enter_play(self, event):
        stamp = str(datetime.now().timestamp())
        send_image_message(event.reply_token, domain + '/show-board/' + stamp)

    def move(self, event):
        text = event.message.text
        return True