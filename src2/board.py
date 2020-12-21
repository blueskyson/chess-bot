import pieces, ai
import os
from PIL import Image

# COLOR
WHITE = pieces.Piece.WHITE
BLACK = pieces.Piece.BLACK

# PIECE
PAWN = pieces.Pawn.PIECE_TYPE
ROOK = pieces.Rook.PIECE_TYPE
KNIGHT = pieces.Knight.PIECE_TYPE
BISHOP = pieces.Bishop.PIECE_TYPE
QUEEN = pieces.Queen.PIECE_TYPE
KING = pieces.King.PIECE_TYPE

#MOVE STATUS
CASTLE_LEFT = 1
CASTLE_RIGHT = 2
PROMOTION = 3
PAWN_DOBULE_MOVE = 4
EN_PASSANT = 5
NORMAL = 6

class Board:

    WIDTH = 8
    HEIGHT = 8

    def __init__(self, chesspieces, white_king_moved, black_king_moved):
        self.chesspieces = chesspieces
        self.white_king_moved = white_king_moved
        self.black_king_moved = black_king_moved
        self.round = 1
        self.status = WHITE

    @classmethod
    def clone(cls, chessboard):
        chesspieces = [[0 for x in range(Board.WIDTH)] for y in range(Board.HEIGHT)]
        for x in range(Board.WIDTH):
            for y in range(Board.HEIGHT):
                piece = chessboard.chesspieces[x][y]
                if (piece != 0):
                    chesspieces[x][y] = piece.clone()
        return cls(chesspieces, chessboard.white_king_moved, chessboard.black_king_moved)

    @classmethod
    def new(cls):
        chess_pieces = [[0 for x in range(Board.WIDTH)] for y in range(Board.HEIGHT)]
        # Create pawns.
        for x in range(Board.WIDTH):
            chess_pieces[x][Board.HEIGHT-2] = pieces.Pawn(x, Board.HEIGHT-2, pieces.Piece.WHITE)
            chess_pieces[x][1] = pieces.Pawn(x, 1, pieces.Piece.BLACK)

        # Create rooks.
        chess_pieces[0][Board.HEIGHT-1] = pieces.Rook(0, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[Board.WIDTH-1][Board.HEIGHT-1] = pieces.Rook(Board.WIDTH-1, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[0][0] = pieces.Rook(0, 0, pieces.Piece.BLACK)
        chess_pieces[Board.WIDTH-1][0] = pieces.Rook(Board.WIDTH-1, 0, pieces.Piece.BLACK)

        # Create Knights.
        chess_pieces[1][Board.HEIGHT-1] = pieces.Knight(1, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[Board.WIDTH-2][Board.HEIGHT-1] = pieces.Knight(Board.WIDTH-2, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[1][0] = pieces.Knight(1, 0, pieces.Piece.BLACK)
        chess_pieces[Board.WIDTH-2][0] = pieces.Knight(Board.WIDTH-2, 0, pieces.Piece.BLACK)

        # Create Bishops.
        chess_pieces[2][Board.HEIGHT-1] = pieces.Bishop(2, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[Board.WIDTH-3][Board.HEIGHT-1] = pieces.Bishop(Board.WIDTH-3, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[2][0] = pieces.Bishop(2, 0, pieces.Piece.BLACK)
        chess_pieces[Board.WIDTH-3][0] = pieces.Bishop(Board.WIDTH-3, 0, pieces.Piece.BLACK)

        # Create King & Queen.
        chess_pieces[4][Board.HEIGHT-1] = pieces.King(4, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[3][Board.HEIGHT-1] = pieces.Queen(3, Board.HEIGHT-1, pieces.Piece.WHITE)
        chess_pieces[4][0] = pieces.King(4, 0, pieces.Piece.BLACK)
        chess_pieces[3][0] = pieces.Queen(3, 0, pieces.Piece.BLACK)

        return cls(chess_pieces, False, False)

    def get_possible_moves(self, color):
        moves = []
        for x in range(Board.WIDTH):
            for y in range(Board.HEIGHT):
                piece = self.chesspieces[x][y]
                if (piece != 0):
                    if (piece.color == color):
                        moves += piece.get_possible_moves(self)

        return moves

    def perform_move(self, move):
        piece = self.chesspieces[move.xfrom][move.yfrom]
        piece.move += 1
        piece.x = move.xto
        piece.y = move.yto
        self.chesspieces[move.xto][move.yto] = piece
        self.chesspieces[move.xfrom][move.yfrom] = 0

        if (piece.piece_type == pieces.Pawn.PIECE_TYPE):
            if (piece.y == 0 or piece.y == Board.HEIGHT-1):
                self.chesspieces[piece.x][piece.y] = pieces.Queen(piece.x, piece.y, piece.color)

        if (move.castling_move):
            if (move.xto < move.xfrom):
                rook = self.chesspieces[move.xfrom][0]
                rook.x = 2
                self.chesspieces[2][0] = rook
                self.chesspieces[0][0] = 0
            if (move.xto > move.xfrom):
                rook = self.chesspieces[move.xfrom][Board.HEIGHT-1]
                rook.x = Board.WIDTH-4
                self.chesspieces[Board.WIDTH-4][Board.HEIGHT-1] = rook
                self.chesspieces[move.xfrom][Board.HEIGHT-1] = 0

        if (piece.piece_type == pieces.King.PIECE_TYPE):
            if (piece.color == pieces.Piece.WHITE):
                self.white_king_moved = True
            else:
                self.black_king_moved = True

    def user_perform_move(self, move, status):
        if status == CASTLE_LEFT:
            yy = 0
            if self.status == WHITE:
                yy = 7
            self.chesspieces[0][yy].x = 3
            self.chesspieces[3][yy] = self.chesspieces[0][yy]
            self.chesspieces[0][yy] = 0
            self.chesspieces[4][yy].x = 2
            self.chesspieces[2][yy] = self.chesspieces[4][7]
            self.chesspieces[4][yy] = 0
            return
        if status == CASTLE_RIGHT:
            yy = 0
            if self.status == WHITE:
                yy = 7
            self.chesspieces[7][yy].x = 3
            self.chesspieces[5][yy] = self.chesspieces[7][yy]
            self.chesspieces[7][yy] = 0
            self.chesspieces[4][yy].x = 6
            self.chesspieces[6][yy] = self.chesspieces[4][7]
            self.chesspieces[4][yy] = 0
            return        
            
        piece = self.chesspieces[move.xfrom][move.yfrom]
        piece.move += 1
        piece.x = move.xto
        piece.y = move.yto
        if status == PROMOTION:
            if move.xto > 0:
                self.chesspieces[move.xto][move.yto] = pieces.Queen(move.xto, move.yto, piece.color)
                self.chesspieces[move.xfrom][move.yfrom] = 0
                return
            move.xto += 10
            border = 7
            if piece.color == WHITE:
                border = 0
            if move.yto == 'b':
                self.chesspieces[move.xto][border] = pieces.Bishop(move.xto, border, piece.color)
            elif move.yto == 'n':
                self.chesspieces[move.xto][border] = pieces.Knight(move.xto, border, piece.color)
            elif move.yto == 'r':
                self.chesspieces[move.xto][border] = pieces.Rook(move.xto, border, piece.color)
            elif move.yto == 'q':
                self.chesspieces[move.xto][border] = pieces.Queen(move.xto, border, piece.color)
            self.chesspieces[move.xfrom][move.yfrom] = 0
            return

        if status == PAWN_DOBULE_MOVE:
            piece.en_passant = True
        elif status == EN_PASSANT:
            self.chesspieces[move.xto][move.yfrom] = 0
        self.chesspieces[move.xto][move.yto] = piece
        self.chesspieces[move.xfrom][move.yfrom] = 0
            

    # Returns if the given color is checked.
    def is_check(self, color):
        other_color = pieces.Piece.WHITE
        if (color == pieces.Piece.WHITE):
            other_color = pieces.Piece.BLACK

        for move in self.get_possible_moves(other_color):
            copy = Board.clone(self)
            copy.perform_move(move)

            king_found = False
            for x in range(Board.WIDTH):
                for y in range(Board.HEIGHT):
                    piece = copy.chesspieces[x][y]
                    if (piece != 0):
                        if (piece.color == color and piece.piece_type == pieces.King.PIECE_TYPE):
                            king_found = True

            if (not king_found):
                return True

        return False

    # Returns piece at given position or 0 if: No piece or out of bounds.
    def get_piece(self, x, y):
        if (not self.in_bounds(x, y)):
            return 0

        return self.chesspieces[x][y]

    def in_bounds(self, x, y):
        return (x >= 0 and y >= 0 and x < Board.WIDTH and y < Board.HEIGHT)

    def to_string(self):
        string =  "    A  B  C  D  E  F  G  H\n"
        string += "    -----------------------\n"
        for y in range(Board.HEIGHT):
            string += str(8 - y) + " | "
            for x in range(Board.WIDTH):
                piece = self.chesspieces[x][y]
                if (piece != 0):
                    string += piece.to_string()
                else:
                    string += ".. "
            string += "\n"
        return string + "\n"

# --- add by me ---

    def draw(self, user_id, fname):
        sprite_path = os.getcwd() + '/sprites/'
        board_img = Image.open(sprite_path + 'board.png').convert('RGBA')
        result_img = Image.new('RGBA', board_img.size, (0, 0, 0, 0))
        result_img.paste(board_img,(0,0))
        offset = {'0':0, '1':1}

        for y in range(Board.HEIGHT):
            for x in range(Board.WIDTH):
                piece = self.chesspieces[x][y]
                if piece == 0:
                    continue

                pic_id = offset[piece.color] * 6 + int(piece.piece_type)
                piece_img = Image.open(sprite_path + str(pic_id) + '.png').convert('RGBA')
                pos = (30 + x * 50, 30 + y * 50, 80 + x * 50, 80 + y * 50)
                result_img.paste(piece_img, pos, piece_img)
        
        if not os.path.exists(os.getcwd() + '/' + user_id):
            os.mkdir(os.getcwd() + '/' + user_id)
        result_img_path = os.getcwd() + '/' + user_id + '/' + fname + '.png'
        result_img.save(result_img_path)

    def letter_to_xpos(letter):
        letter = letter.upper()
        if letter == 'A':
            return 0
        if letter == 'B':
            return 1
        if letter == 'C':
            return 2
        if letter == 'D':
            return 3
        if letter == 'E':
            return 4
        if letter == 'F':
            return 5
        if letter == 'G':
            return 6
        if letter == 'H':
            return 7
        raise ValueError("Invalid letter.")
    
    def is_legal_notation(self, text):
        if len(text) == 3:
            if (text == 'o-o'):
                return ai.Move(-1, -1, -1, 0, True)
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
            return ai.Move(ord(text[0]) - ord('a'), 8 - ord(text[1]) + ord('0'), ord(text[2]) - ord('a'), 8 - ord(text[3]) + ord('0'), False)
        elif len(text) == 5:
            if (text == 'o-o-o'):
                return ai.Move(-1, -1, -1, 1, True)
            else:
                return False
        elif len(text) == 6:
            if ord(text[0]) < ord('a') or ord(text[0]) > ord('h'):
                return False
            if ord(text[1]) < ord('1') or ord(text[1]) > ord('8'):
                return False
            if ord(text[2]) < ord('a') or ord(text[2]) > ord('h'):
                return Falsesrc[0]
            if ord(text[3]) < ord('1') or ord(text[3]) > ord('8'):
                return False
            if text[4] != '=':
                return False
            if text[5] == 'b' or text[5] == 'n' or text[5] == 'r' or text[5] == 'q':
                return ai.Move(ord(text[0]) - ord('a'), 8 - ord(text[1]) + ord('0'), ord(text[2]) - ord('a') - 10, text[5], False)
            return False
        else:
            return False
    
    def is_legal_move(self, move, color):
        # castling
        if move.castling_move == True:
            if move.yto == 0:
                s = self.test_right_castle(color)
                if s != None:
                    return CASTLE_RIGHT
            elif move.yto == 1:
                s = self.test_left_castle(color)
                if s != None:
                    return CASTLE_LEFT
        print(move.xfrom, move.yfrom, move.xto, move.yto)        
        piece = self.chesspieces[move.xfrom][move.yfrom]
        piece2 = self.chesspieces[move.xto][move.yto]
        if piece == 0 or piece.color != color:
            return False
        if piece2 != 0 and piece2.color == color:
            return False

        # promotion
        if move.xto < 0:
            if piece != PAWN:
                return False
            stat = self.test_pawn(move)
            if stat == None:
                return False

            if piece.color == WHITE and move.yfrom == 1:
                return PROMOTION
            elif piece.color == BLACK and move.yfrom == 6:
                return PROMOTION
            return False

        # normal notation
        else:
            stat = None
            if piece.piece_type == PAWN:
                stat = self.test_pawn(move)
                if stat != None and piece.color == WHITE and move.yto == 0:
                    return PROMOTION
                elif stat != None and piece.color == BLACK and move.yto == 7:
                    return PROMOTION
            elif piece.piece_type == ROOK:
                stat = self.test_rook(move)
            elif piece.piece_type == KNIGHT:
                stat = self.test_knight(move)
            elif piece.piece_type == BISHOP:
                stat = self.test_bishop(move)
            elif piece.piece_type == QUEEN:
                stat = self.test_queen(move)
            elif piece.piece_type == KING:
                stat = self.test_king(move)
            
            if stat != None:
                return stat
        return False

    def test_pawn(self, move):
        xfrom = move.xfrom
        yfrom = move.yfrom
        xto = move.xto
        yto = move.yto
        piece1 = self.chesspieces[xfrom][yfrom]
        piece2 = self.chesspieces[xto][yto]
        # move forward
        if piece1.color == WHITE:
            if xfrom == xto:
                if piece2 != 0:
                    return None
                if yfrom - yto == 1:
                    return NORMAL
                if yfrom - yto == 2 and piece1.move == 0 and self.chesspieces[xfrom][yfrom - 1] == 0:
                    return PAWN_DOBULE_MOVE
                return None
            if yfrom - yto == 1 and abs(xfrom - xto) == 1:
                if piece2 != 0 and piece2.color == BLACK:
                    return NORMAL
                passant = self.chesspieces[xto][yfrom]
                if passant != 0 and passant.piece_type == PAWN and passant.en_passant == True:
                    return EN_PASSANT
        if piece1.color == BLACK:
            if xfrom == xto:
                if piece2 != 0:
                    return None
                if yfrom - yto == -1:
                    return NORMAL
                if yfrom - yto == -2 and piece1.move == 0 and self.chesspieces[xfrom][yfrom + 1] == 0:
                    return PAWN_DOBULE_MOVE
                return None
            if yfrom - yto == -1 and abs(xfrom - xto) == 1:
                if piece2 != 0 and piece2.color == WHITE:
                    return NORMAL
                passant = self.chesspieces[xto][yfrom]
                if passant != 0 and passant.piece_type == PAWN and passant.en_passant == True:
                    return EN_PASSANT
        return None

    def test_rook(self, move):
        xfrom = move.xfrom
        yfrom = move.yfrom
        xto = move.xto
        yto = move.yto
        piece1 = self.chesspieces[xfrom][yfrom]
        piece2 = self.chesspieces[xto][yto]

        if (yfrom == yto):
            if xto < xfrom:
                i = xfrom - 1
                while i > xto:
                    if self.chesspieces[i][yfrom] != 0:
                        return None
                    i -= 1
                return NORMAL
            elif xto > xfrom:
                i = xfrom + 1
                while i < xto:
                    if self.chesspieces[i][yfrom] != 0:
                        return None
                    i += 1
                return NORMAL                
        elif (xfrom == xto):
            if yto < yfrom:
                i = yfrom - 1
                while i > yto:
                    if self.chesspieces[xfrom][i] != 0:
                        return None
                    i -= 1
                return NORMAL
            if yto > yfrom:
                i = yfrom + 1
                while i < yto:
                    if self.chesspieces[xfrom][i] != 0:
                        return None
                    i += 1
                return NORMAL
        return None
    
    def test_knight(self, move):
        i1 = move.yfrom
        j1 = move.xfrom
        i2 = move.yto
        j2 = move.xto

        if abs(i2 - i1) == 2:
            if abs(j2 - j1) == 1:
                return NORMAL
        elif abs(i2 - i1) == 1:
            if abs(j2 - j1) == 2:
                return NORMAL            
        return None

    def test_bishop(self, move):
        i1 = move.yfrom
        j1 = move.xfrom
        i2 = move.yto
        j2 = move.xto

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
            if self.chesspieces[j][i] != 0:
                return None
            i += istep
            j += jstep
        return NORMAL

    def test_queen(self, move):
        i1 = move.yfrom
        j1 = move.xfrom
        i2 = move.yto
        j2 = move.xto

        if abs(i1 - i2) == abs(j1 - j2):
            return self.test_bishop(move)
        if i1 == i2 or j1 == j2:
            return self.test_rook(move)
        return None

    def test_king(self, move):
        if abs(move.xfrom - move.xto) <= 1 and abs(move.yfrom - move.yto) <= 1:
            return NORMAL
        return None

    def test_right_castle(self, color):
        if color == WHITE:
            if self.chesspieces[7][7] != 0 and self.chesspieces[7][7].move == 0 and \
            self.chesspieces[7][4] != 0 and self.chesspieces[7][4].move == 0 and \
            self.chesspieces[7][5] == 0 and self.chesspieces[7][6] == 0:
                return 7
        elif color == BLACK:
            if self.chesspieces[7][0] != 0 and self.chesspieces[7][0].move == 0 and \
            self.chesspieces[0][4] != 0 and self.chesspieces[0][4].move == 0 and \
            self.chesspieces[0][5] == 0 and self.chesspieces[0][6] == 0:
                return 0
        return None

    def test_left_castle(self, color):
        if color == WHITE:
            if self.chesspieces[7][0] != 0 and self.chesspieces[7][0].move == 0 and \
            self.chesspieces[7][4] != 0 and self.chesspieces[7][4].move == 0 and \
            self.chesspieces[7][1] == 0 and self.chesspieces[7][2] == 0 and self.chesspieces[7][3] == 0:
                return 7
        elif color == BLACK:
            if self.chesspieces[0][0] != 0 and self.chesspieces[0][0].move == 0 and \
            self.chesspieces[0][4] != 0 and self.chesspieces[0][4].move == 0 and \
            self.chesspieces[0][1] == 0 and self.chesspieces[0][2] == 0 and self.chesspieces[0][3] == 0:
                return 0
        return None
    