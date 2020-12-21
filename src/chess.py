import os
from PIL import Image

# COLOR
WHITE = 0
BLACK = 1

# PIECE
PAWN = 1
ROOK = 2
KNIGHT = 3
BISHOP = 4
QUEEN = 5
KING = 6

#GAME STATUS
IDLE = 2
W_TURN = 0
B_TURN = 1

#MOVE STATUS
NORMAL = 0
CASTLE_LEFT = 1
CASTLE_RIGHT = 2
PROMOTION = 3
PAWN_DOBULE_MOVE = 4
EN_PASSANT = 5

class Game:
    def __init__(self):
        self.status = IDLE
        self.round = 0
        self.board = []
        self.pgn = []
        self.en_passant_flag = None
        for i in range(0, 8):
            self.board.append([0,0,0,0,0,0,0,0])

    def is_idle(self):
        return self.status == IDLE

    def set_up_board(self):
        # set black
        self.board[0][0] = {'color': BLACK, 'kind': ROOK, 'move': 0}
        self.board[0][1] = {'color': BLACK, 'kind': KNIGHT, 'move': 0}
        self.board[0][2] = {'color': BLACK, 'kind': BISHOP, 'move': 0}
        self.board[0][3] = {'color': BLACK, 'kind': QUEEN, 'move': 0}
        self.board[0][4] = {'color': BLACK, 'kind': KING, 'move': 0}
        self.board[0][5] = {'color': BLACK, 'kind': BISHOP, 'move': 0}
        self.board[0][6] = {'color': BLACK, 'kind': KNIGHT, 'move': 0}
        self.board[0][7] = {'color': BLACK, 'kind': ROOK, 'move': 0}
        for i in range(0, 8):
            self.board[1][i] = {'color': BLACK, 'kind': PAWN, 'move': 0, 'en_passant': False}
        
        #set white
        self.board[7][0] = {'color': WHITE, 'kind': ROOK, 'move': 0}
        self.board[7][1] = {'color': WHITE, 'kind': KNIGHT, 'move': 0}
        self.board[7][2] = {'color': WHITE, 'kind': BISHOP, 'move': 0}
        self.board[7][3] = {'color': WHITE, 'kind': QUEEN, 'move': 0}
        self.board[7][4] = {'color': WHITE, 'kind': KING, 'move': 0}
        self.board[7][5] = {'color': WHITE, 'kind': BISHOP, 'move': 0}
        self.board[7][6] = {'color': WHITE, 'kind': KNIGHT, 'move': 0}
        self.board[7][7] = {'color': WHITE, 'kind': ROOK, 'move': 0}
        for i in range(0, 8):
            self.board[6][i] = {'color': WHITE, 'kind': PAWN, 'move': 0, 'en_passant': False}
        
        self.status = W_TURN
        self.round = 1
        self.pgn = []
    
    def draw(self, user_id, fname):
        sprite_path = os.getcwd() + '/sprites/'
        board_img = Image.open(sprite_path + 'board.png').convert('RGBA')
        result_img = Image.new('RGBA', board_img.size, (0, 0, 0, 0))
        result_img.paste(board_img,(0,0))

        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j] == 0:
                    continue
                pic_id = self.board[i][j]['color'] * 6 + self.board[i][j]['kind']
                piece_img = Image.open(sprite_path + str(pic_id) + '.png').convert('RGBA')
                pos = (30 + j * 50, 30 + i * 50, 80 + j * 50, 80 + i * 50)
                result_img.paste(piece_img, pos, piece_img)

        if not os.path.exists(os.getcwd() + '/' + user_id):
            os.mkdir(os.getcwd() + '/' + user_id)
        result_img_path = os.getcwd() + '/' + user_id + '/' + fname + '.png'
        result_img.save(result_img_path)

    def is_legal_notation(self, text):
        if len(text) == 3:
            if (text == 'o-o'):
                return (1)
            else:
                return False
        elif len(text) == 4:
            if ord(text[0]) < ord('a') or ord(text[0]) > ord('h'):
                return False
            if ord(text[1]) < ord('1') or ord(text[1]) > ord('8'):
                return False
            if ord(text[2]) < ord('a') or ord(text[2]) > ord('h'):
                return False
            if ord(text[3]) < ord('1') or ord(text[3]) > ord('8'):
                return False
            return (ord(text[0]) - ord('a'), ord(text[1]) - ord('0'), ord(text[2]) - ord('a'), ord(text[3]) - ord('0'))
        elif len(text) == 5:
            if (text == 'o-o-o'):
                return (2)
            else:
                return False
        elif len(text) == 6:
            if ord(text[0]) < ord('a') or ord(text[0]) > ord('h'):
                return False
            if ord(text[1]) < ord('1') or ord(text[1]) > ord('8'):
                return False
            if ord(text[2]) < ord('a') or ord(text[2]) > ord('h'):
                return False
            if ord(text[3]) < ord('1') or ord(text[3]) > ord('8'):
                return False
            if text[4] != '=':
                return False
            if text[5] == 'b' or text[5] == 'n' or text[5] == 'r' or text[5] == 'q':
                return (ord(text[0]) - ord('a'), ord(text[1]) - ord('0'), ord(text[2]) - ord('a'), ord(text[3]) - ord('0'), text[5])
            return False
        else:
            return False

    def show(self):
        for i in range(0, 8):
            for j in range(0, 8):
                if self.board[i][j] == 0:
                    print('0', end = ' '),
                else:
                    print(self.board[i][j]['kind'], end = ' '),
            print()

    def is_legal_move(self, notation):
        # castling
        if type(notation) is int:
            if notation == 1:
                s = self.test_right_castle()
                if s != None:
                    return (s, CASTLE_RIGHT)
            elif notation == 2:
                s = self.test_left_castle()
                if s != None:
                    return (s, CASTLE_LEFT)
            return False

        j = notation[0]
        i = 8 - notation[1]
        d_j = notation[2]
        d_i = 8 - notation[3]
        piece = self.board[i][j]
        
        # promotion
        if len(notation) == 5:
            if piece == 0 or piece['color'] != self.status or piece['kind'] != PAWN:
                return False
            piece2 = self.board[d_i][d_j]
            if piece2 != 0 and piece2['color'] == piece['color']:
                return False

            src = (i, j)
            dest = (d_i, d_j)
            stat = self.test_pawn(src, dest)
            if stat == None:
                return False

            if piece['color'] == WHITE and d_i == 0:
                return (src, dest, PROMOTION, notation[4])
            elif piece['color'] == BLACK and d_i == 7:
                return (src, dest, PROMOTION, notation[4])
            return False
             
        # normal notation
        elif len(notation) == 4:
            if piece == 0 or piece['color'] != self.status:
                return False
            piece2 = self.board[d_i][d_j]
            if piece2 != 0 and piece2['color'] == piece['color']:
                return False
         
            src = (i, j)
            dest = (d_i, d_j)
            # convert coordination
            stat = None
            if piece['kind'] == PAWN:
                stat = self.test_pawn(src, dest)
                if stat != None and piece['color'] == WHITE and d_i == 0:
                    return (src, dest, PROMOTION, 'q')
                elif stat != None and piece['color'] == BLACK and d_i == 7:
                    return (src, dest, PROMOTION, 'q')                
            elif piece['kind'] == ROOK:
                stat = self.test_rook(src, dest)
            elif piece['kind'] == KNIGHT:
                stat = self.test_knight(src, dest)
            elif piece['kind'] == BISHOP:
                stat = self.test_bishop(src, dest)
            elif piece['kind'] == QUEEN:
                stat = self.test_queen(src, dest)
            elif piece['kind'] == KING:
                stat = self.test_king(src, dest)

            if stat != None:
                return (src, dest, stat)


        return False

    def test_pawn(self, src, dest):
        i1 = src[0]
        j1 = src[1]
        i2 = dest[0]
        j2 = dest[1]
        piece1 = self.board[i1][j1]
        piece2 = self.board[i2][j2]
        # move forward
        if piece1['color'] == WHITE:
            if j1 == j2:
                if piece2 != 0:
                    return None
                if i1 - i2 == 1:
                    return NORMAL
                if i1 - i2 == 2 and piece1['move'] == 0 and self.board[i1 - 1][j1] == 0:
                    return PAWN_DOBULE_MOVE
                return None
            if i1 - i2 == 1 and abs(j1 - j2) == 1:
                if piece2 != 0 and piece2['color'] == BLACK:
                    return NORMAL
                passant = self.board[i1][j2]
                if passant != 0 and passant['kind'] == PAWN and passant['en_passant'] == True:
                    return EN_PASSANT
        elif piece1['color'] == BLACK:
            if j1 == j2:
                if piece2 != 0:
                    return None
                if i2 - i1 == 1:
                    return NORMAL
                if i2 - i1 == 2 and piece1['move'] == 0 and self.board[i2 - 1][j1] == 0:
                    return PAWN_DOBULE_MOVE
                return None
            if i2 - i1 == 1 and abs(j2 - j1) == 1:
                if piece2 != 0 and piece2['color'] == WHITE:
                    return NORMAL
                passant = self.board[i1][j2]
                if passant != 0 and passant['kind'] == PAWN and passant['en_passant'] == True:
                    return EN_PASSANT
        return None

    def test_rook(self, src, dest):
        i1 = src[0]
        j1 = src[1]
        i2 = dest[0]
        j2 = dest[1]

        if (i1 == i2):
            if j2 < j1:
                i = j1 - 1
                while i > j2:
                    if self.board[i1][i] != 0:
                        return None
                    i -= 1
                return NORMAL
            elif j2 > j1:
                i = j1 + 1
                while i < j2:
                    if self.board[i1][i] != 0:
                        return None
                    i += 1
                return NORMAL                
        elif (j1 == j2):
            if i2 < i1:
                i = i1 - 1
                while i > i2:
                    if self.board[i][j1] != 0:
                        return None
                    i -= 1
                return NORMAL
            if i2 > i1:
                i = i1 + 1
                while i < i2:
                    if self.board[i][j1] != 0:
                        return None
                    i += 1
                return NORMAL
        return None
            
    def test_knight(self, src, dest):
        i1 = src[0]
        j1 = src[1]
        i2 = dest[0]
        j2 = dest[1]

        if i2 - i1 == 2:
            if j2 - j1 == 1 or j2 - j1 == -1:
                return NORMAL
        elif i2 - i1 == 1:
            if j2 - j1 == 2 or j2 - j1 == -2:
                return NORMAL            
        elif i2 - i1 == -1:
            if j2 - j1 == 2 or j2 - j1 == -2:
                return NORMAL            
        elif i2 - i1 == -2:
            if j2 - j1 == 1 or j2 - j1 == -1:
                return NORMAL
        return None
    
    def test_bishop(self, src, dest):
        i1 = src[0]
        j1 = src[1]
        i2 = dest[0]
        j2 = dest[1]

        if abs(i1 - i2) != abs(j1 - j2):
            return None
        istep = 1
        jstep = 1
        if i2 < i1:
            istep = -1
        if j2 < j1:
            jstep = -1
        i = i1 + istep
        j = j1 + jstep
        while i != i2:
            if self.board[i][j] != 0:
                return None
            i += istep
            j += jstep
        return NORMAL

    def test_queen(self, src, dest):
        i1 = src[0]
        j1 = src[1]
        i2 = dest[0]
        j2 = dest[1]

        if abs(i1 - i2) == abs(j1 - j2):
            return self.test_bishop(src, dest)
        if i1 == i2 or j1 == j2:
            return self.test_rook(src, dest)
        return None

    def test_king(self, src, dest):
        i1 = src[0]
        j1 = src[1]
        i2 = dest[0]
        j2 = dest[1]

        if abs(i1 - i2) <= 1 and abs(j1 - j2) <= 1:
            return NORMAL

    def test_right_castle(self):
        if self.status == W_TURN:
            if self.board[7][7] != 0 and self.board[7][7]['move'] == 0 and \
            self.board[7][4] != 0 and self.board[7][4]['move'] == 0 and \
            self.board[7][5] == 0 and self.board[7][6] == 0:
                return 7
        elif self.status == B_TURN:
            if self.board[0][7] != 0 and self.board[0][7]['move'] == 0 and \
            self.board[0][4] != 0 and self.board[0][4]['move'] == 0 and \
            self.board[0][5] == 0 and self.board[0][6] == 0:
                return 0
        return None

    def test_left_castle(self):
        if self.status == W_TURN:
            if self.board[7][0] != 0 and self.board[7][0]['move'] == 0 and \
            self.board[7][4] != 0 and self.board[7][4]['move'] == 0 and \
            self.board[7][1] == 0 and self.board[7][2] == 0 and self.board[7][3] == 0:
                return 7
        elif self.status == B_TURN:
            if self.board[0][0] != 0 and self.board[0][0]['move'] == 0 and \
            self.board[0][4] != 0 and self.board[0][4]['move'] == 0 and \
            self.board[0][1] == 0 and self.board[0][2] == 0 and self.board[0][3] == 0:
                return 0
        return None

    def move(self, m):
        if self.status == W_TURN:
            self.status = B_TURN
        else:
            self.round += 1
            self.status = W_TURN
        
        if len(m) == 2:
            if m[1] == CASTLE_LEFT:
                self.board[m[0]][2] = self.board[m[0]][4]
                self.board[m[0]][4] = 0
                self.board[m[0]][3] = self.board[m[0]][0]
                self.board[m[0]][0] = 0
            elif m[1] == CASTLE_RIGHT:
                self.board[m[0]][6] = self.board[m[0]][4]
                self.board[m[0]][4] = 0
                self.board[m[0]][5] = self.board[m[0]][7]
                self.board[m[0]][7] = 0
            
            if self.en_passant_flag != None:
                self.board[self.en_passant_flag[0]][self.en_passant_flag[1]]['en_passant'] = False
                self.en_passant_flag = None
            return
        
        i1 = m[0][0]
        j1 = m[0][1]
        i2 = m[1][0]
        j2 = m[1][1]
        stat = m[2]

        if stat == EN_PASSANT:
            self.board[i1][j1]['move'] += 1
            self.board[i2][j2] = self.board[i1][j1]
            self.board[i1][j1] = 0
            self.board[i1][j2] = 0
            self.en_passant_flag = None
            return
        if self.en_passant_flag != None:
            self.board[self.en_passant_flag[0]][self.en_passant_flag[1]]['en_passant'] = False
            self.en_passant_flag = None
        if stat == NORMAL:
            self.board[i1][j1]['move'] += 1
            self.board[i2][j2] = self.board[i1][j1]
            self.board[i1][j1] = 0
        elif stat == PAWN_DOBULE_MOVE:
            self.board[i1][j1]['en_passant'] = True
            self.board[i1][j1]['move'] += 1
            self.board[i2][j2] = self.board[i1][j1]
            self.en_passant_flag = (i2, j2)
            self.board[i1][j1] = 0
        elif stat == PROMOTION:
            mov = self.board[i1][j1]['move'] + 1
            col = self.board[i1][j1]['color']
            if m[3] == 'b':
                self.board[i2][j2] = {'color': col, 'kind': BISHOP, 'move': mov}
            elif m[3] == 'n':
                self.board[i2][j2] = {'color': col, 'kind': KNIGHT, 'move': mov}
            elif m[3] == 'r':
                self.board[i2][j2] = {'color': col, 'kind': ROOK, 'move': mov}
            elif m[3] == 'q':
                self.board[i2][j2] = {'color': col, 'kind': QUEEN, 'move': mov}
            print(self.board[i2][j2])
            self.board[i1][j1] = 0
        return
            