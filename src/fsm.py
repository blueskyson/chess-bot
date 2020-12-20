from transitions.extensions import GraphMachine
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction
from utils import send_text_message, send_image_message, push_text_message, push_image_message
from datetime import datetime
import chess
from chess import Game

# domain = 'https://7a11edb09d53.ngrok.io'
domain = 'https://a80b49743215.ngrok.io'

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.game = Game()
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_play(self, event):
        text = event.message.text.lower()
        if text == 'play':
            self.game.set_up_board()
            return True
        return False

    def on_enter_play(self, event):
        stamp = str(datetime.now().timestamp())
        user_id = event.source.user_id

        self.game.draw(user_id, stamp)
        game_info = 'Round ' + str(self.game.round)
        if self.game.status == chess.W_TURN:
            game_info = game_info + ', white\'s turn.'
        elif self.game.status == chess.B_TURN:
            game_info = game_info + ', black\'s turn.'
    
        push_text_message(user_id, game_info)
        push_image_message(user_id, domain + '/' + user_id + '/' + stamp)

    def is_going_to_move(self, event):
        text = event.message.text.lower()
        notation = self.game.is_legal_notation(text)
        if notation == False:
            push_text_message(event.source.user_id, 'Invalid notation, type \'help\' to get notation guide.')
            return False
        m = self.game.is_legal_move(notation)
        if m == False:
            push_text_message(event.source.user_id, 'Illegal move.')
            return False
        self.game.move(m)
        return True
    
