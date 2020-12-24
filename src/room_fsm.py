from transitions.extensions import GraphMachine
from linebot.models import ImageCarouselColumn, URITemplateAction, MessageTemplateAction
from utils import send_text_message, send_image_message, push_text_message, push_image_message
from datetime import datetime
import board, ai, pieces
import os

domain = os.getenv('DOMAIN', None)

class RoomTocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.board = None
        self.machine = GraphMachine(model=self, **machine_configs)
        self.history = []
        self.user1 = None
        self.user2 = None
        self.undouser = None

    def on_enter_user():
        self.user1 = None
        self.user2 = None

    def is_going_to_userplaywhite(self, event):
        text = event.message.text.lower()
        if text == 'play' or text == 'play white':
            self.board = board.Board.new()
            self.history = []
            self.history.append(board.Board.clone(self.board))
            self.user1 = event.source.user_id
            return True
        return False

    def is_going_to_userplayblack(self, event):
        text = event.message.text.lower()
        if text == 'play black':
            self.board = board.Board.new()
            self.history = []
            self.history.append(board.Board.clone(self.board))
            self.user1 = event.source.user_id
            return True
        return False

    def on_enter_userplaywhite(self, event):
        stamp = str(datetime.now().timestamp())
        room_id = event.source.room_id
        self.board.draw(room_id, stamp)
        r = int((len(self.history) + 1) / 2)
        board_info = 'Round ' + str(r) + ', white\'s turn.'
        push_text_message(room_id, board_info)
        push_image_message(room_id, domain + '/' + room_id + '/' + stamp)
        
        if self.board.is_win(pieces.Piece.BLACK):
            push_text_message(room_id, 'Black win!')
            self.board.remove(room_id)
            self.go_back(event)
            return
        if self.board.is_check(pieces.Piece.WHITE):
            push_text_message(room_id, 'Check!')
    
    def on_enter_userplayblack(self, event):
        stamp = str(datetime.now().timestamp())
        room_id = event.source.room_id
        self.board.draw(room_id, stamp)
        r = int((len(self.history) + 1) / 2)
        board_info = 'Round ' + str(r) + ', black\'s turn.'
        push_text_message(room_id, board_info)
        push_image_message(room_id, domain + '/' + room_id + '/' + stamp)
            
        if self.board.is_win(pieces.Piece.WHITE):
            push_text_message(room_id, 'White win!')
            self.board.remove(room_id)
            self.go_back(event)
            return
        if self.board.is_check(pieces.Piece.BLACK):
            push_text_message(room_id, 'Check!')

    def is_going_to_resign(self, event):
        text = event.message.text.lower()
        if event.source.user_id != self.user1 or text != 'resign':
            return False
        room_id = event.source.room_id
        if len(self.history) % 2 == 1:
            push_text_message(room_id, "Black Win!")
        else:
            push_text_message(room_id, "White Win!")
        self.board.remove(room_id)
        self.board = None
        return True

    def undo2(self, event):
        text = event.message.text.lower()        
        if event.source.user_id != self.user1 or text != 'undo':
            return False
        if len(self.history) < 3:
            push_text_message(event.source.room_id, 'Could not undo.')
            return True
        self.history.pop()
        self.history.pop()
        self.board = self.history[len(self.history) - 1]
        return True
    
    def undo(self, event):
        text = event.message.text.lower()        
        if event.source.user_id != self.user1 or text != 'undo':
            return False

        if len(self.history) < 2:
            push_text_message(event.source.room_id, 'Could not undo.')
            return True
        self.history.pop()
        self.board = self.history[len(self.history) - 1]
        return True

    def is_going_to_move(self, event):
        if event.source.user_id != self.user1:
            return False
        text = event.message.text.lower()
        mv = self.board.is_legal_notation(text)
        if mv == False:
            push_text_message(event.source.room_id, 'Invalid notation, type \'help\' to get notation guide.')
            return False
        if len(self.history) % 2 == 1:
            stat = self.board.is_legal_move(mv, board.WHITE)
        else:
            stat = self.board.is_legal_move(mv, board.BLACK)            
        print('stat: ', stat)
        if stat == False:
            push_text_message(event.source.room_id, 'Illegal move.')
            return False
        self.board.user_perform_move(mv, stat)
        self.history.append(board.Board.clone(self.board))
        return True

    def is_going_to_botmove(self, event):
        if len(self.history) % 2 == 1:
            ai_move = ai.AI.get_ai_move(self.board, [], board.WHITE)
        else:
            ai_move = ai.AI.get_ai_move(self.board, [], board.BLACK)
        self.board.perform_move(ai_move)
        self.history.append(board.Board.clone(self.board))
        return True

    def is_going_to_userplayself(self, event):
        text = event.message.text.lower()
        if text == 'play self':
            self.board = board.Board.new()
            self.history = []
            self.history.append(board.Board.clone(self.board))
            self.user1 = event.source.user_id
            return True
        return False

    def on_enter_userplayself(self, event):
        stamp = str(datetime.now().timestamp())
        room_id = event.source.room_id
        self.board.draw(room_id, stamp)
        r = int((len(self.history) + 1) / 2)
        if len(self.history) % 2 == 1:
            board_info = 'Round ' + str(r) + ', white\'s turn.'
            push_text_message(room_id, board_info)
            push_image_message(room_id, domain + '/' + room_id + '/' + stamp)
            
            if self.board.is_win(pieces.Piece.BLACK):
                push_text_message(room_id, 'BLACK win!')
                self.board.remove(room_id)
                self.go_back(event)
                return
            if self.board.is_check(pieces.Piece.WHITE):
                push_text_message(room_id, 'Check!')           
        else:
            board_info = 'Round ' + str(r) + ', black\'s turn.'
            push_text_message(room_id, board_info)
            push_image_message(room_id, domain + '/' + room_id + '/' + stamp)
            
            if self.board.is_win(pieces.Piece.WHITE):
                push_text_message(room_id, 'White win!')
                self.board.remove(room_id)
                self.go_back(event)
                return            
            if self.board.is_check(pieces.Piece.BLACK):
                push_text_message(room_id, 'Check!')

    def is_going_to_moveself(self, event):
        text = event.message.text.lower()
        mv = self.board.is_legal_notation(text)
        if mv == False:
            push_text_message(event.source.room_id, 'Invalid notation, type \'help\' to get notation guide.')
            return False
        if len(self.history) % 2 == 1:
            stat = self.board.is_legal_move(mv, board.WHITE)
        else:
            stat = self.board.is_legal_move(mv, board.BLACK) 
        print('stat: ', stat)
        if stat == False:
            push_text_message(event.source.room_id, 'Illegal move.')
            return False
        self.board.user_perform_move(mv, stat)
        self.history.append(board.Board.clone(self.board))
        return True

    def on_enter_botplayblack(self, event):
        stamp = str(datetime.now().timestamp())
        room_id = event.source.room_id

        self.board.draw(room_id, stamp)
        r = int((len(self.history) + 1) / 2)
        board_info = 'Round ' + str(r) + ', black\'s turn.'

        push_text_message(room_id, board_info)
        push_image_message(room_id, domain + '/' + room_id + '/' + stamp)
        if self.board.is_win(pieces.Piece.WHITE):
            push_text_message(room_id, 'White win!')
            self.board.remove(room_id)
            self.go_back(event)
            return

        if self.board.is_check(pieces.Piece.BLACK):
            push_text_message(room_id, 'Check!')
        self.advance(event)

    def on_enter_botplaywhite(self, event):
        stamp = str(datetime.now().timestamp())
        room_id = event.source.room_id
        self.board.draw(room_id, stamp)
        r = int((len(self.history) + 1) / 2)
        board_info = 'Round ' + str(r) + ', white\'s turn.'
        push_text_message(room_id, board_info)
        push_image_message(room_id, domain + '/' + room_id + '/' + stamp)

        if self.board.is_win(pieces.Piece.BLACK):
            push_text_message(room_id, 'Black win!')
            self.board.remove(room_id)
            self.go_back(event)
            return
        if self.board.is_check(pieces.Piece.WHITE):
            push_text_message(room_id, 'Check!')
        self.advance(event)

    # 2p play

    def is_going_to_creategame(self, event):
        text = event.message.text.lower()
        if text == 'play 2p' or text == 'play 2p white':
            self.user1 = event.source.user_id
            self.user2 = None
            return True
        elif text == 'play 2p black':
            self.user2 = event.source.user_id
            self.user1 = None
            return True
        return False
    def is_going_to_cancel(self, event):
        text = event.message.text.lower()
        if text == 'cancel':
            if self.user1 == None and event.source.user_id == self.user2:
                push_text_message(event.source.room_id, 'Game canceled')
                return True
            if self.user2 == None and event.source.user_id == self.user1:
                push_text_message(event.source.room_id, 'Game canceled')
                return True
            push_text_message(event.source.room_id, 'Only One who creates the game can cancel.')
        return False

    def on_enter_creategame(self, event):
        push_text_message(event.source.room_id, 'Game created. Waiting for another player to join the game.')

    def is_going_to_2pplay(self, event):
        text = event.message.text.lower()
        if text == 'play accept':
            if self.user2 == None:
                self.user2 = event.source.user_id
            else:
                self.user1 = event.source.user_id
            self.board = board.Board.new()
            self.history = []
            self.history.append(board.Board.clone(self.board))
            return True
        return False

    def on_enter_2pplay(self, event):
        stamp = str(datetime.now().timestamp())
        room_id = event.source.room_id
        self.board.draw(room_id, stamp)
        r = int((len(self.history) + 1) / 2)
        if len(self.history) % 2 == 1:
            board_info = 'Round ' + str(r) + ', white\'s turn.'
            push_text_message(room_id, board_info)
            push_image_message(room_id, domain + '/' + room_id + '/' + stamp)
            
            if self.board.is_win(pieces.Piece.BLACK):
                push_text_message(room_id, 'BLACK win!')
                self.board.remove(room_id)
                self.go_back(event)
                return
            if self.board.is_check(pieces.Piece.WHITE):
                push_text_message(room_id, 'Check!')           
        else:
            board_info = 'Round ' + str(r) + ', black\'s turn.'
            push_text_message(room_id, board_info)
            push_image_message(room_id, domain + '/' + room_id + '/' + stamp)
            
            if self.board.is_win(pieces.Piece.WHITE):
                push_text_message(room_id, 'White win!')
                self.board.remove(room_id)
                self.go_back(event)
                return            
            if self.board.is_check(pieces.Piece.BLACK):
                push_text_message(room_id, 'Check!')

    def is_going_to_2pmove(self, event):
        if len(self.history) % 2 == 1:
            if event.source.user_id != self.user1:
                return False
        else:
            if event.source.user_id != self.user2:
                return False
        
        text = event.message.text.lower()
        mv = self.board.is_legal_notation(text)
        if mv == False:
            push_text_message(event.source.room_id, 'Invalid notation, type \'help\' to get notation guide.')
            return False
        if len(self.history) % 2 == 1:
            stat = self.board.is_legal_move(mv, board.WHITE)
        else:
            stat = self.board.is_legal_move(mv, board.BLACK)
        if stat == False:
            push_text_message(event.source.room_id, 'Illegal move.')
            return False
        self.board.user_perform_move(mv, stat)
        self.history.append(board.Board.clone(self.board))
        return True

    def is_going_to_requestundo(self, event):
        text = event.message.text.lower()
        if text == 'undo':
            if event.source.user_id == self.user1:
                self.undouser = self.user1
                push_text_message(event.source.room_id, 'Accept undo? (y/n)')
                return True
            elif event.source.user_id == self.user2:
                self.undouser = self.user2
                push_text_message(event.source.room_id, 'Accept undo? (y/n)')
                return True
        return False
    
    def is_going_to_replyundo(self, event):
        text = event.message.text.lower()
        if (self.undouser == self.user1 and event.source.user_id == self.user2)\
        or (self.undouser == self.user2 and event.source.user_id == self.user1):
            if text == 'n':
                push_text_message(event.source.room_id, 'Reject undo.')
            elif text == 'y':
                if len(self.history) < 2:
                    push_text_message(event.source.room_id, 'Could not undo.')
                else:
                    self.history.pop()
                    self.board = self.history[len(self.history) - 1]
            return True
        if text == 'n' or text == 'y':
            push_text_message(event.source.room_id, 'Only players can reply undo.')
        return False
        