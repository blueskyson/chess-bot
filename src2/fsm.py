from transitions.extensions import GraphMachine
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction
from utils import send_text_message, send_image_message, push_text_message, push_image_message
from datetime import datetime
import board, ai, pieces

domain = 'https://a0ecf7fbb9e1.ngrok.io'

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.board = None
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_userplay(self, event):
        text = event.message.text.lower()
        if text == 'play':
            self.board = board.Board.new()
            return True
        return False

    def is_going_to_resign(self, event):
        text = event.message.text.lower()
        if text != 'resign':
            return False
        user_id = event.source.user_id
        if self.board.status == board.WHITE:
            push_text_message(user_id, "Black Win!")
        else:
            push_text_message(user_id, "White Win!")
        return True
        
    def is_going_to_move(self, event):
        text = event.message.text.lower()
        mv = self.board.is_legal_notation(text)
        if mv == False:
            push_text_message(event.source.user_id, 'Invalid notation, type \'help\' to get notation guide.')
            return False
        stat = self.board.is_legal_move(mv, self.board.status)
        print('stat: ', stat)
        if stat == False:
            push_text_message(event.source.user_id, 'Illegal move.')
            return False
        self.board.user_perform_move(mv, stat)
        return True
    
    def on_enter_botplayblack(self, event):
        stamp = str(datetime.now().timestamp())
        user_id = event.source.user_id

        self.board.draw(user_id, stamp)
        board_info = 'Round ' + str(self.board.round) + ', black\'s turn.'
        self.board.round += 1

        push_text_message(user_id, board_info)
        push_image_message(user_id, domain + '/' + user_id + '/' + stamp)
        self.advance(event)
    
    def is_going_to_botmove(self, event):
        if self.board.status == board.BLACK:
            ai_move = ai.AI.get_ai_move(self.board, [], board.WHITE)
        else:
            ai_move = ai.AI.get_ai_move(self.board, [], board.BLACK)
        self.board.perform_move(ai_move)
        return True
    
    def is_going_to_userplaywhite(self, event):
        text = event.message.text.lower()
        if text == 'play' or text == 'play white':
            self.board = board.Board.new()
            self.board.status = board.WHITE
            return True
        return False

    def on_enter_userplaywhite(self, event):
        stamp = str(datetime.now().timestamp())
        user_id = event.source.user_id
        self.board.draw(user_id, stamp)
        board_info = 'Round ' + str(self.board.round) + ', white\'s turn.'
        push_text_message(user_id, board_info)
        push_image_message(user_id, domain + '/' + user_id + '/' + stamp)

    def on_enter_userplayblack(self, event):
        stamp = str(datetime.now().timestamp())
        user_id = event.source.user_id
        self.board.draw(user_id, stamp)
        board_info = 'Round ' + str(self.board.round) + ', black\'s turn.'
        push_text_message(user_id, board_info)
        push_image_message(user_id, domain + '/' + user_id + '/' + stamp)
        self.board.round += 1
    
    def is_going_to_userplayblack(self, event):
        text = event.message.text.lower()
        if text == 'play black':
            self.board = board.Board.new()
            self.board.status = board.BLACK
            return True
        return False

    def on_enter_botplaywhite(self, event):
        stamp = str(datetime.now().timestamp())
        user_id = event.source.user_id
        self.board.draw(user_id, stamp)
        board_info = 'Round ' + str(self.board.round) + ', white\'s turn.'
        push_text_message(user_id, board_info)
        push_image_message(user_id, domain + '/' + user_id + '/' + stamp)
        self.advance(event)