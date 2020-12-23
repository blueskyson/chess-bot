from transitions.extensions import GraphMachine
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction
from utils import send_text_message, send_image_message, push_text_message, push_image_message
from datetime import datetime
import board, ai, pieces
import os

domain = os.getenv('DOMAIN', None)
# domain = 'https://720b24cd008d.ngrok.io'

class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.board = None
        self.machine = GraphMachine(model=self, **machine_configs)
        self.history = []
        self.round = 1

    def is_going_to_resign(self, event):
        text = event.message.text.lower()
        if text != 'resign':
            return False
        user_id = event.source.user_id
        if self.board.status == board.WHITE:
            push_text_message(user_id, "Black Win!")
        else:
            push_text_message(user_id, "White Win!")
        self.board.remove(user_id)
        self.board = None
        return True
    
    def undo(self, event):
        text = event.message.text.lower()        
        if text != 'undo':
            return False

        if len(self.history) < 2:
            push_text_message(event.source.user_id, 'Could not undo.')
            return True
        self.history.pop()
        self.board = self.history[len(self.history) - 1]
        return True

    def undo2(self, event):
        text = event.message.text.lower()        
        if text != 'undo':
            return False
        if len(self.history) < 2:
            push_text_message(event.source.user_id, 'Could not undo.')
            return True
        self.history.pop()
        self.history.pop()
        self.board = self.history[len(self.history) - 1]
        self.round -= 1
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
        self.history.append(board.Board.clone(self.board))
        return True
    
    def on_enter_botplayblack(self, event):
        stamp = str(datetime.now().timestamp())
        user_id = event.source.user_id

        self.board.draw(user_id, stamp)
        board_info = 'Round ' + str(self.round) + ', black\'s turn.'
        self.round += 1

        push_text_message(user_id, board_info)
        push_image_message(user_id, domain + '/' + user_id + '/' + stamp)
        if self.board.is_win(pieces.Piece.WHITE):
            push_text_message(user_id, 'White win!')
            self.board.remove(user_id)
            self.go_back(event)
            return

        if self.board.is_check(pieces.Piece.BLACK):
            push_text_message(user_id, 'Check!')
        self.advance(event)
    
    def is_going_to_botmove(self, event):
        if self.board.status == board.BLACK:
            ai_move = ai.AI.get_ai_move(self.board, [], board.WHITE)
        else:
            ai_move = ai.AI.get_ai_move(self.board, [], board.BLACK)
        self.board.perform_move(ai_move)
        self.history.append(board.Board.clone(self.board))
        return True
    
    def is_going_to_userplaywhite(self, event):
        text = event.message.text.lower()
        if text == 'play' or text == 'play white':
            self.board = board.Board.new()
            self.board.status = board.WHITE
            self.history = []
            self.history.append(board.Board.clone(self.board))
            self.round = 1
            return True
        return False

    def on_enter_userplaywhite(self, event):
        stamp = str(datetime.now().timestamp())
        user_id = event.source.user_id
        self.board.draw(user_id, stamp)
        board_info = 'Round ' + str(self.round) + ', white\'s turn.'
        push_text_message(user_id, board_info)
        push_image_message(user_id, domain + '/' + user_id + '/' + stamp)
        
        if self.board.is_win(pieces.Piece.BLACK):
            push_text_message(user_id, 'Black win!')
            self.board.remove(user_id)
            self.go_back(event)
            return

        if self.board.is_check(pieces.Piece.WHITE):
            push_text_message(user_id, 'Check!')

    def on_enter_userplayblack(self, event):
        stamp = str(datetime.now().timestamp())
        user_id = event.source.user_id
        self.board.draw(user_id, stamp)
        board_info = 'Round ' + str(self.round) + ', black\'s turn.'
        push_text_message(user_id, board_info)
        push_image_message(user_id, domain + '/' + user_id + '/' + stamp)
        self.round += 1
            
        if self.board.is_win(pieces.Piece.WHITE):
            push_text_message(user_id, 'White win!')
            self.board.remove(user_id)
            self.go_back(event)
            return
        if self.board.is_check(pieces.Piece.BLACK):
            push_text_message(user_id, 'Check!')
    
    def is_going_to_userplayblack(self, event):
        text = event.message.text.lower()
        if text == 'play black':
            self.board = board.Board.new()
            self.board.status = board.BLACK
            self.history = []
            self.history.append(board.Board.clone(self.board))
            self.round = 1
            return True
        return False

    def on_enter_botplaywhite(self, event):
        stamp = str(datetime.now().timestamp())
        user_id = event.source.user_id
        self.board.draw(user_id, stamp)
        board_info = 'Round ' + str(self.round) + ', white\'s turn.'
        push_text_message(user_id, board_info)
        push_image_message(user_id, domain + '/' + user_id + '/' + stamp)
        
        if self.board.is_win(pieces.Piece.BLACK):
            push_text_message(user_id, 'Black win!')
            self.board.remove(user_id)
            self.go_back(event)
            return
        if self.board.is_check(pieces.Piece.WHITE):
            push_text_message(user_id, 'Check!')
        self.advance(event)
    
    def is_going_to_userplayself(self, event):
        text = event.message.text.lower()
        if text == 'play self':
            self.board = board.Board.new()
            self.history = []
            self.history.append(board.Board.clone(self.board))
            self.round = 1
            return True
        return False
    
    def on_enter_userplayself(self, event):
        stamp = str(datetime.now().timestamp())
        user_id = event.source.user_id
        self.board.draw(user_id, stamp)
        self.round = int(len(self.history) / 2) + 1
        if len(self.history) % 2 == 1:
            board_info = 'Round ' + str(self.round) + ', white\'s turn.'
            push_text_message(user_id, board_info)
            push_image_message(user_id, domain + '/' + user_id + '/' + stamp)
            
            if self.board.is_win(pieces.Piece.BLACK):
                push_text_message(user_id, 'BLACK win!')
                self.board.remove(user_id)
                self.go_back(event)
                return
            if self.board.is_check(pieces.Piece.WHITE):
                push_text_message(user_id, 'Check!')           
        else:
            board_info = 'Round ' + str(self.round) + ', black\'s turn.'
            push_text_message(user_id, board_info)
            push_image_message(user_id, domain + '/' + user_id + '/' + stamp)
            
            if self.board.is_win(pieces.Piece.WHITE):
                push_text_message(user_id, 'White win!')
                self.board.remove(user_id)
                self.go_back(event)
                return            
            if self.board.is_check(pieces.Piece.BLACK):
                push_text_message(user_id, 'Check!')



    def is_going_to_moveself(self, event):
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
        self.history.append(board.Board.clone(self.board))
        return True
        