import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame
import sys
import copy
import random
import json

# Initialize Pygame
pygame.init()

# Base Constant Colors (UI elements, overlays, text)
SIDEBAR_BG = (46, 49, 49)          # Dark Grey
SIDEBAR_TEXT = (236, 240, 241)     # Off-white
HIGHLIGHT_VALID = (100, 200, 100, 120)  # Semi-transparent green for moves
TEXT_COLOR = (255, 255, 255)
PIECE_WHITE = (245, 245, 245)      # Light Grey/White
PIECE_WHITE_OUTLINE = (60, 60, 60)
PIECE_BLACK = (40, 40, 40)         # Charcoal
PIECE_BLACK_OUTLINE = (200, 200, 200)

# Window Configuration
SQUARE_SIZE = 70
BOARD_SIZE = 8 * SQUARE_SIZE
SIDEBAR_WIDTH = 220
WINDOW_WIDTH = BOARD_SIZE + SIDEBAR_WIDTH
WINDOW_HEIGHT = BOARD_SIZE

# Fonts
try:
    FONT_UI = pygame.font.SysFont("dejavusans", 15)
    FONT_UI_BOLD = pygame.font.SysFont("dejavusans", 15, bold=True)
    FONT_HEADER = pygame.font.SysFont("dejavusans", 22, bold=True)
except:
    FONT_UI = pygame.font.SysFont("arial", 15)
    FONT_UI_BOLD = pygame.font.SysFont("arial", 15, bold=True)
    FONT_HEADER = pygame.font.SysFont("arial", 22, bold=True)


def draw_arrow(screen, color_rgb, start, end, thickness=6, head_size=16, alpha=150):
    """Draws a beautiful semi-transparent vector arrow from start to end pixel coordinates."""
    import math
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    
    ux = dx / dist
    uy = dy / dist
    
    # Create a transparent surface for the arrow
    temp_surf = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
    color = (*color_rgb, alpha)
    
    # Shorten shaft slightly so it doesn't peak out of the head
    shortened_x2 = x2 - ux * head_size
    shortened_y2 = y2 - uy * head_size
    pygame.draw.line(temp_surf, color, (x1, y1), (shortened_x2, shortened_y2), thickness)
    
    # Arrowhead vertices
    bx = x2 - ux * head_size
    by = y2 - uy * head_size
    px = -uy
    py = ux
    
    pt1 = (x2, y2)
    pt2 = (bx + px * (head_size * 0.6), by + py * (head_size * 0.6))
    pt3 = (bx - px * (head_size * 0.6), by - py * (head_size * 0.6))
    
    pygame.draw.polygon(temp_surf, color, [pt1, pt2, pt3])
    screen.blit(temp_surf, (0, 0))


class ChessGame:
    def __init__(self):
        self.game_mode = 'PvP'  # 'PvP', 'AI', or 'Train'
        self.theme = 'classic'  # Active theme: 'classic', 'modern', 'neon'
        self.feedback_message = None
        self.feedback_timer = 0.0
        
        # Available Themes definition
        self.themes = {
            'classic': {
                'name': 'Класична',
                'board_light': (240, 217, 181),      # Warm Cream
                'board_dark': (181, 136, 99),        # Warm Wood Brown
                'highlight_selected': (130, 151, 105), # Sage Green
                'highlight_last_move': (205, 210, 106) # Soft Yellow
            },
            'modern': {
                'name': 'Сучасна синя',
                'board_light': (234, 237, 243),      # Soft Ice Blue
                'board_dark': (112, 154, 191),       # Deep Ocean Blue
                'highlight_selected': (129, 236, 236), # Bright Aqua
                'highlight_last_move': (250, 177, 160) # Pastel Salmon
            },
            'neon': {
                'name': 'Неонова',
                'board_light': (45, 52, 54),         # Midnight Gray
                'board_dark': (0, 184, 148),         # Neon Mint Green
                'highlight_selected': (253, 203, 110), # Neon Gold
                'highlight_last_move': (224, 86, 253) # Neon Purple
            }
        }
        self.reset_game()

    def reset_game(self):
        # Initial Board State: 'w' = White, 'b' = Black
        # R = Rook, N = Knight, B = Bishop, Q = Queen, K = King, P = Pawn
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ]
        self.turn = 'w'
        self.selected_piece = None
        self.valid_moves = []
        self.last_move = None
        self.captured_pieces = {'w': [], 'b': []}
        self.game_over = False
        self.winner = None
        self.move_log = []
        self.promotion_pending = None

        # Castling Tracking
        self.king_moved = {'w': False, 'b': False}
        self.rook_moved = {
            'w': {'kingside': False, 'queenside': False},
            'b': {'kingside': False, 'queenside': False}
        }

        # Timers Tracking (10 minutes)
        self.time_limit = 600
        self.white_time = self.time_limit
        self.black_time = self.time_limit
        self.time_out_loss = False

        # En Passant Tracking
        self.en_passant_target = None
        self.next_en_passant_target = None

        # Training & Analysis indicators
        self.best_move_arrow = None
        self.current_eval = 0.0
        self.update_analysis()

    def set_feedback(self, text, duration=2.0):
        self.feedback_message = text
        self.feedback_timer = duration

    def save_game(self, filename="chess_save.json"):
        state = {
            'game_mode': self.game_mode,
            'theme': self.theme,
            'board': self.board,
            'turn': self.turn,
            'last_move': self.last_move,
            'captured_pieces': self.captured_pieces,
            'game_over': self.game_over,
            'winner': self.winner,
            'move_log': self.move_log,
            'promotion_pending': self.promotion_pending,
            'king_moved': self.king_moved,
            'rook_moved': self.rook_moved,
            'white_time': self.white_time,
            'black_time': self.black_time,
            'time_out_loss': self.time_out_loss,
            'en_passant_target': self.en_passant_target
        }
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(state, f)
            self.set_feedback("Збережено успішно!", 2.0)
            return True
        except Exception:
            self.set_feedback("Помилка збереження", 2.0)
            return False

    def load_game(self, filename="chess_save.json"):
        if not os.path.exists(filename):
            self.set_feedback("Немає збережень!", 2.0)
            return False
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.game_mode = state['game_mode']
            self.theme = state.get('theme', 'classic')
            self.board = state['board']
            self.turn = state['turn']
            
            lm = state['last_move']
            if lm:
                self.last_move = (tuple(lm[0]), tuple(lm[1]))
            else:
                self.last_move = None
                
            self.captured_pieces = state['captured_pieces']
            self.game_over = state['game_over']
            self.winner = state['winner']
            self.move_log = state['move_log']
            
            pp = state['promotion_pending']
            if pp:
                self.promotion_pending = (tuple(pp[0]), tuple(pp[1]))
            else:
                self.promotion_pending = None
                
            self.king_moved = state['king_moved']
            self.rook_moved = state['rook_moved']
            self.white_time = state['white_time']
            self.black_time = state['black_time']
            self.time_out_loss = state.get('time_out_loss', False)
            
            ep = state['en_passant_target']
            if ep:
                self.en_passant_target = tuple(ep)
            else:
                self.en_passant_target = None
                
            self.selected_piece = None
            self.valid_moves = []
            self.update_analysis()
            self.set_feedback("Завантажено!", 2.0)
            return True
        except Exception:
            self.set_feedback("Помилка файлу!", 2.0)
            return False

    def get_piece_at(self, r, c):
        if 0 <= r < 8 and 0 <= c < 8:
            return self.board[r][c]
        return None

    def find_king(self, board, color):
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece == f'{color}K':
                    return (r, c)
        return None

    def is_in_check(self, board, color):
        king_pos = self.find_king(board, color)
        if not king_pos:
            return False
        
        opponent_color = 'b' if color == 'w' else 'w'
        
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.startswith(opponent_color):
                    moves = self.get_raw_moves(board, r, c)
                    if king_pos in moves:
                        return True
        return False

    def is_square_under_attack(self, board, r, c, attacker_color):
        for ar in range(8):
            for ac in range(8):
                piece = board[ar][ac]
                if piece and piece.startswith(attacker_color):
                    if (r, c) in self.get_raw_moves(board, ar, ac):
                        return True
        return False

    def get_raw_moves(self, board, r, c):
        piece = board[r][c]
        if not piece:
            return []
        
        color = piece[0]
        ptype = piece[1]
        moves = []

        if ptype == 'P':  # Pawn Logic
            direction = -1 if color == 'w' else 1
            start_row = 6 if color == 'w' else 1
            
            # 1 Step forward
            if 0 <= r + direction < 8 and board[r + direction][c] is None:
                moves.append((r + direction, c))
                # 2 Steps forward from initial rank
                if r == start_row and board[r + 2 * direction][c] is None:
                    moves.append((r + 2 * direction, c))
            
            # Diagonal Captures & En Passant
            for dc in [-1, 1]:
                tc = c + dc
                tr = r + direction
                if 0 <= tr < 8 and 0 <= tc < 8:
                    target_piece = board[tr][tc]
                    if target_piece and target_piece[0] != color:
                        moves.append((tr, tc))
                    elif (tr, tc) == self.en_passant_target:
                        moves.append((tr, tc))

        elif ptype == 'R':  # Rook
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                tr, tc = r + dr, c + dc
                while 0 <= tr < 8 and 0 <= tc < 8:
                    target_piece = board[tr][tc]
                    if target_piece is None:
                        moves.append((tr, tc))
                    elif target_piece[0] != color:
                        moves.append((tr, tc))
                        break
                    else:
                        break
                    tr += dr
                    tc += dc

        elif ptype == 'B':  # Bishop
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                tr, tc = r + dr, c + dc
                while 0 <= tr < 8 and 0 <= tc < 8:
                    target_piece = board[tr][tc]
                    if target_piece is None:
                        moves.append((tr, tc))
                    elif target_piece[0] != color:
                        moves.append((tr, tc))
                        break
                    else:
                        break
                    tr += dr
                    tc += dc

        elif ptype == 'Q':  # Queen
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
            for dr, dc in directions:
                tr, tc = r + dr, c + dc
                while 0 <= tr < 8 and 0 <= tc < 8:
                    target_piece = board[tr][tc]
                    if target_piece is None:
                        moves.append((tr, tc))
                    elif target_piece[0] != color:
                        moves.append((tr, tc))
                        break
                    else:
                        break
                    tr += dr
                    tc += dc

        elif ptype == 'N':  # Knight
            jump_offsets = [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]
            for dr, dc in jump_offsets:
                tr, tc = r + dr, c + dc
                if 0 <= tr < 8 and 0 <= tc < 8:
                    target_piece = board[tr][tc]
                    if target_piece is None or target_piece[0] != color:
                        moves.append((tr, tc))

        elif ptype == 'K':  # King
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for dr, dc in directions:
                tr, tc = r + dr, c + dc
                if 0 <= tr < 8 and 0 <= tc < 8:
                    target_piece = board[tr][tc]
                    if target_piece is None or target_piece[0] != color:
                        moves.append((tr, tc))

        return moves

    def get_legal_moves(self, r, c, board=None, turn=None):
        """Get moves, filtering out those that put/keep the player's own king in check."""
        if board is None:
            board = self.board
        if turn is None:
            turn = self.turn

        piece = board[r][c]
        if not piece or piece[0] != turn:
            return []
        
        raw_moves = self.get_raw_moves(board, r, c)
        legal_moves = []
        
        for tr, tc in raw_moves:
            temp_board = copy.deepcopy(board)
            # Handle simulated En Passant capture removal
            if piece[1] == 'P' and (tr, tc) == self.en_passant_target:
                temp_board[r][tc] = None

            temp_board[tr][tc] = temp_board[r][c]
            temp_board[r][c] = None
            
            if not self.is_in_check(temp_board, turn):
                legal_moves.append((tr, tc))

        # Add Castling moves
        if piece[1] == 'K':
            color = piece[0]
            opp_color = 'b' if color == 'w' else 'w'
            row = 7 if color == 'w' else 0
            
            # Kingside castling
            if not self.king_moved[color] and not self.rook_moved[color]['kingside']:
                if board[row][5] is None and board[row][6] is None:
                    if not self.is_in_check(board, color):
                        if not self.is_square_under_attack(board, row, 5, opp_color) and \
                           not self.is_square_under_attack(board, row, 6, opp_color):
                            legal_moves.append((row, 6))
            
            # Queenside castling
            if not self.king_moved[color] and not self.rook_moved[color]['queenside']:
                if board[row][1] is None and board[row][2] is None and board[row][3] is None:
                    if not self.is_in_check(board, color):
                        if not self.is_square_under_attack(board, row, 3, opp_color) and \
                           not self.is_square_under_attack(board, row, 2, opp_color):
                            legal_moves.append((row, 2))
                
        return legal_moves

    def is_checkmate_or_stalemate(self):
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.startswith(self.turn):
                    if len(self.get_legal_moves(r, c)) > 0:
                        return False
        return True

    def make_move(self, start, end):
        start_r, start_c = start
        end_r, end_c = end
        
        moving_piece = self.board[start_r][start_c]
        target_piece = self.board[end_r][end_c]
        
        if moving_piece is None:
            return False

        # Reset next en-passant target
        self.next_en_passant_target = None

        # Check En Passant capture execution
        is_en_passant = False
        if moving_piece[1] == 'P' and (end_r, end_c) == self.en_passant_target:
            is_en_passant = True
            captured_pawn_color = 'b' if moving_piece[0] == 'w' else 'w'
            self.captured_pieces[captured_pawn_color].append('P')
            self.board[start_r][end_c] = None

        # Add capture to history
        if target_piece and not is_en_passant:
            self.captured_pieces[target_piece[0]].append(target_piece[1])

        # Track special Castling execution
        is_castle = False
        if moving_piece[1] == 'K' and abs(start_c - end_c) == 2:
            is_castle = True
            row = start_r
            if end_c == 6:  # Kingside
                self.board[row][6] = moving_piece
                self.board[row][5] = f"{moving_piece[0]}R"
                self.board[row][4] = None
                self.board[row][7] = None
            elif end_c == 2: # Queenside
                self.board[row][2] = moving_piece
                self.board[row][3] = f"{moving_piece[0]}R"
                self.board[row][4] = None
                self.board[row][0] = None

        if not is_castle:
            self.board[end_r][end_c] = moving_piece
            self.board[start_r][start_c] = None
        
        # Track if king or rook moved for Castling eligibility
        if moving_piece == 'wK':
            self.king_moved['w'] = True
        elif moving_piece == 'bK':
            self.king_moved['b'] = True
        elif moving_piece == 'wR':
            if start == (7, 7): self.rook_moved['w']['kingside'] = True
            elif start == (7, 0): self.rook_moved['w']['queenside'] = True
        elif moving_piece == 'bR':
            if start == (0, 7): self.rook_moved['b']['kingside'] = True
            elif start == (0, 0): self.rook_moved['b']['queenside'] = True

        # Check if pawn moved 2 squares for en-passant
        if moving_piece[1] == 'P' and abs(start_r - end_r) == 2:
            self.next_en_passant_target = ((start_r + end_r) // 2, start_c)

        # Pawn Promotion trigger check
        if moving_piece[1] == 'P' and (end_r == 0 or end_r == 7):
            if moving_piece[0] == 'b' and self.game_mode == 'AI':
                self.board[end_r][end_c] = 'bQ'
                self.move_log.append(f"{self.coords_to_notation(start, end)}=Q")
                self.finalize_turn(start, end)
            else:
                self.promotion_pending = (start, end)
                self.selected_piece = None
                self.valid_moves = []
        else:
            if is_castle:
                notation = "0-0" if end_c == 6 else "0-0-0"
                self.move_log.append(notation)
            else:
                notation = self.coords_to_notation(start, end)
                if is_en_passant:
                    notation += " e.p."
                self.move_log.append(notation)
            self.finalize_turn(start, end)
                
        return True

    def finalize_turn(self, start, end):
        self.last_move = (start, end)
        self.selected_piece = None
        self.valid_moves = []
        
        # Advance en passant target state
        self.en_passant_target = self.next_en_passant_target
        self.next_en_passant_target = None
        
        # Switch turn
        self.turn = 'b' if self.turn == 'w' else 'w'
        
        # Check game-over conditions
        if self.is_checkmate_or_stalemate():
            self.game_over = True
            if self.is_in_check(self.board, self.turn):
                self.winner = 'w' if self.turn == 'b' else 'b'
            else:
                self.winner = 'Draw'

        # Update Live Analysis after turn ends
        self.update_analysis()

    def coords_to_notation(self, start, end):
        files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        ranks = ['8', '7', '6', '5', '4', '3', '2', '1']
        return f"{files[start[1]]}{ranks[start[0]]}-{files[end[1]]}{ranks[end[0]]}"

    def make_ai_move(self):
        if self.game_over or self.promotion_pending:
            return False
        
        all_legal_moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.startswith('b'):
                    valid = self.get_legal_moves(r, c)
                    for tr, tc in valid:
                        all_legal_moves.append(((r, c), (tr, tc)))
                        
        if not all_legal_moves:
            return False
        
        piece_values = {'P': 10, 'N': 30, 'B': 30, 'R': 50, 'Q': 90, 'K': 900}
        
        best_move = None
        best_score = -1
        
        for start, end in all_legal_moves:
            moving_piece = self.board[start[0]][start[1]]
            target_piece = self.board[end[0]][end[1]]
            score = 0
            if target_piece:
                score = piece_values.get(target_piece[1], 10)
            elif moving_piece[1] == 'P' and end == self.en_passant_target:
                score = 10
            
            if score > best_score:
                best_score = score
                best_move = (start, end)
                
        if best_score == 0:
            best_move = random.choice(all_legal_moves)
            
        if best_move:
            self.make_move(best_move[0], best_move[1])
            return True
        return False

    # --- ADVANCED ANALYSIS ENGINE (TRAINING MODE) ---
    def evaluate_board(self, board):
        """Standard professional evaluation function using material values and positional tables."""
        piece_values = {'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000}
        
        pawn_table = [
            [0,  0,  0,  0,  0,  0,  0,  0],
            [50, 50, 50, 50, 50, 50, 50, 50],
            [10, 10, 20, 30, 30, 20, 10, 10],
            [5,  5, 10, 25, 25, 10,  5,  5],
            [0,  0,  0, 20, 20,  0,  0,  0],
            [5, -5,-10,  0,  0,-10, -5,  5],
            [5, 10, 10,-20,-20, 10, 10,  5],
            [0,  0,  0,  0,  0,  0,  0,  0]
        ]
        
        knight_table = [
            [-50,-40,-30,-30,-30,-30,-40,-50],
            [-40,-20,  0,  0,  0,  0,-20,-40],
            [-30,  0, 10, 15, 10, 10,  0,-30],
            [-30,  5, 15, 20, 20, 15,  5,-30],
            [-30,  0, 15, 20, 20, 15,  0,-30],
            [-30,  5, 10, 15, 15, 10,  5,-30],
            [-40,-20,  0,  5,  5,  0,-20,-40],
            [-50,-40,-30,-30,-30,-30,-40,-50]
        ]
        
        bishop_table = [
            [-20,-10,-10,-10,-10,-10,-10,-20],
            [-10,  0,  0,  0,  0,  0,  0,-10],
            [-10,  0,  5, 10, 10,  5,  0,-10],
            [-10,  5,  5, 10, 10,  5,  5,-10],
            [-10,  0, 10, 10, 10, 10,  0,-10],
            [-10, 10, 10, 10, 10, 10, 10,-10],
            [-10,  5,  0,  0,  0,  0,  5,-10],
            [-20,-10,-10,-10,-10,-10,-10,-20]
        ]
        
        score = 0
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece:
                    color = piece[0]
                    ptype = piece[1]
                    val = piece_values.get(ptype, 0)
                    
                    bonus = 0
                    if ptype == 'P':
                       bonus = pawn_table[r][c] if color == 'w' else pawn_table[7 - r][c]
                    elif ptype == 'N':
                       bonus = knight_table[r][c] if color == 'w' else knight_table[7 - r][c]
                    elif ptype == 'B':
                       bonus = bishop_table[r][c] if color == 'w' else bishop_table[7 - r][c]
                       
                    if color == 'w':
                        score += val + bonus
                    else:
                        score -= (val + bonus)
        return score / 100.0  # Centipawn format (e.g. +1.50)

    def is_checkmate_after_move(self, board, next_player):
        """Verifies if next_player has any legal response remaining (fast check)."""
        for r in range(8):
            for c in range(8):
                piece = board[r][c]
                if piece and piece.startswith(next_player):
                    valid = self.get_legal_moves(r, c, board=board, turn=next_player)
                    if valid:
                        return False
        return self.is_in_check(board, next_player)

    def apply_sim_move(self, board, start, end):
        """Mutates a simulated board object, resolving captures & special castling details."""
        sr, sc = start
        er, ec = end
        piece = board[sr][sc]
        
        if piece is None:
            return

        # En Passant capture simulation
        if piece[1] == 'P' and (er, ec) == self.en_passant_target:
            board[sr][ec] = None
            
        # Castling simulation
        if piece[1] == 'K' and abs(sc - ec) == 2:
            if ec == 6: # Kingside
                board[sr][6] = piece
                board[sr][5] = f"{piece[0]}R"
                board[sr][4] = None
                board[sr][7] = None
            elif ec == 2: # Queenside
                board[sr][2] = piece
                board[sr][3] = f"{piece[0]}R"
                board[sr][4] = None
                board[sr][0] = None
            return
            
        board[er][ec] = piece
        board[sr][sc] = None
        
        # Promotion simulation
        if piece[1] == 'P' and (er == 0 or er == 7):
            board[er][ec] = f"{piece[0]}Q"

    def compute_best_move(self):
        """Computes the best legal move for the current active side using 1-ply search with checkmate verification."""
        legal_moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and piece.startswith(self.turn):
                    valid = self.get_legal_moves(r, c)
                    for tr, tc in valid:
                        legal_moves.append(((r, c), (tr, tc)))
                        
        if not legal_moves:
            return None, 0.0
            
        best_move = None
        
        if self.turn == 'w':
            best_score = -99999.0
            for start, end in legal_moves:
                temp_board = copy.deepcopy(self.board)
                self.apply_sim_move(temp_board, start, end)
                
                if self.is_checkmate_after_move(temp_board, 'b'):
                    score = 9999.0
                else:
                    score = self.evaluate_board(temp_board)
                    
                if score > best_score:
                    best_score = score
                    best_move = (start, end)
            return best_move, best_score
        else:
            best_score = 99999.0
            for start, end in legal_moves:
                temp_board = copy.deepcopy(self.board)
                self.apply_sim_move(temp_board, start, end)
                
                if self.is_checkmate_after_move(temp_board, 'w'):
                    score = -9999.0
                else:
                    score = self.evaluate_board(temp_board)
                    
                if score < best_score:
                    best_score = score
                    best_move = (start, end)
            return best_move, best_score

    def update_analysis(self):
        """Triggers recalculation of the live board analysis metrics."""
        self.current_eval = self.evaluate_board(self.board)
        best_move, _ = self.compute_best_move()
        self.best_move_arrow = best_move


def draw_piece(screen, piece, cx, cy, size):
    """Draws custom minimalist vector icons for chess pieces."""
    color = PIECE_WHITE if piece[0] == 'w' else PIECE_BLACK
    outline_color = PIECE_WHITE_OUTLINE if piece[0] == 'w' else PIECE_BLACK_OUTLINE
    ptype = piece[1]
    
    def draw_outline_poly(pts):
        pygame.draw.polygon(screen, color, pts)
        pygame.draw.polygon(screen, outline_color, pts, 2)

    if ptype == 'P':  # Pawn
        pygame.draw.rect(screen, color, (cx - size * 0.2, cy + size * 0.15, size * 0.4, size * 0.1))
        pygame.draw.rect(screen, outline_color, (cx - size * 0.2, cy + size * 0.15, size * 0.4, size * 0.1), 1)
        draw_outline_poly([
            (cx - size * 0.15, cy + size * 0.15),
            (cx + size * 0.15, cy + size * 0.15),
            (cx + size * 0.05, cy - size * 0.05),
            (cx - size * 0.05, cy - size * 0.05)
        ])
        pygame.draw.circle(screen, color, (cx, cy - size * 0.12), int(size * 0.15))
        pygame.draw.circle(screen, outline_color, (cx, cy - size * 0.12), int(size * 0.15), 2)

    elif ptype == 'R':  # Rook
        pygame.draw.rect(screen, color, (cx - size * 0.25, cy + size * 0.18, size * 0.5, size * 0.08))
        pygame.draw.rect(screen, outline_color, (cx - size * 0.25, cy + size * 0.18, size * 0.5, size * 0.08), 1)
        draw_outline_poly([
            (cx - size * 0.2, cy + size * 0.18),
            (cx + size * 0.2, cy + size * 0.18),
            (cx + size * 0.2, cy - size * 0.15),
            (cx - size * 0.2, cy - size * 0.15)
        ])
        draw_outline_poly([
            (cx - size * 0.22, cy - size * 0.15),
            (cx + size * 0.22, cy - size * 0.15),
            (cx + size * 0.22, cy - size * 0.25),
            (cx + size * 0.12, cy - size * 0.25),
            (cx + size * 0.12, cy - size * 0.20),
            (cx + size * 0.04, cy - size * 0.20),
            (cx + size * 0.04, cy - size * 0.25),
            (cx - size * 0.04, cy - size * 0.25),
            (cx - size * 0.04, cy - size * 0.20),
            (cx - size * 0.12, cy - size * 0.20),
            (cx - size * 0.12, cy - size * 0.25),
            (cx - size * 0.22, cy - size * 0.25)
        ])

    elif ptype == 'B':  # Bishop
        pygame.draw.rect(screen, color, (cx - size * 0.22, cy + size * 0.18, size * 0.44, size * 0.08))
        pygame.draw.rect(screen, outline_color, (cx - size * 0.22, cy + size * 0.18, size * 0.44, size * 0.08), 1)
        pygame.draw.ellipse(screen, color, (cx - size * 0.18, cy - size * 0.18, size * 0.36, size * 0.36))
        pygame.draw.ellipse(screen, outline_color, (cx - size * 0.18, cy - size * 0.18, size * 0.36, size * 0.36), 2)
        pygame.draw.circle(screen, color, (cx, cy - size * 0.22), int(size * 0.05))
        pygame.draw.circle(screen, outline_color, (cx, cy - size * 0.22), int(size * 0.05), 1)
        pygame.draw.line(screen, outline_color, (cx - size * 0.05, cy - size * 0.1), (cx + size * 0.08, cy + size * 0.05), 2)

    elif ptype == 'N':  # Knight
        pygame.draw.rect(screen, color, (cx - size * 0.22, cy + size * 0.18, size * 0.44, size * 0.08))
        pygame.draw.rect(screen, outline_color, (cx - size * 0.22, cy + size * 0.18, size * 0.44, size * 0.08), 1)
        draw_outline_poly([
            (cx + size * 0.18, cy + size * 0.18),
            (cx - size * 0.18, cy + size * 0.18),
            (cx - size * 0.18, cy + size * 0.08),
            (cx - size * 0.10, cy - size * 0.05),
            (cx - size * 0.22, cy - size * 0.05),
            (cx - size * 0.24, cy - size * 0.15),
            (cx - size * 0.12, cy - size * 0.22),
            (cx + size * 0.05, cy - size * 0.22),
            (cx + size * 0.15, cy - size * 0.10),
            (cx + size * 0.18, cy + size * 0.05)
        ])
        eye_color = PIECE_BLACK if piece[0] == 'w' else PIECE_WHITE
        pygame.draw.circle(screen, eye_color, (cx - size * 0.1, cy - size * 0.14), 2)

    elif ptype == 'Q':  # Queen
        pygame.draw.rect(screen, color, (cx - size * 0.25, cy + size * 0.18, size * 0.5, size * 0.08))
        pygame.draw.rect(screen, outline_color, (cx - size * 0.25, cy + size * 0.18, size * 0.5, size * 0.08), 1)
        draw_outline_poly([
            (cx - size * 0.2, cy + size * 0.18),
            (cx + size * 0.2, cy + size * 0.18),
            (cx + size * 0.22, cy - size * 0.12),
            (cx + size * 0.12, cy - size * 0.02),
            (cx + size * 0.0, cy - size * 0.18),
            (cx - size * 0.12, cy - size * 0.02),
            (cx - size * 0.22, cy - size * 0.12)
        ])
        pygame.draw.circle(screen, color, (cx - size * 0.22, cy - size * 0.12), 3)
        pygame.draw.circle(screen, outline_color, (cx - size * 0.22, cy - size * 0.12), 3, 1)
        pygame.draw.circle(screen, color, (cx, cy - size * 0.18), 3)
        pygame.draw.circle(screen, outline_color, (cx, cy - size * 0.18), 3, 1)
        pygame.draw.circle(screen, color, (cx + size * 0.22, cy - size * 0.12), 3)
        pygame.draw.circle(screen, outline_color, (cx + size * 0.22, cy - size * 0.12), 3, 1)

    elif ptype == 'K':  # King
        pygame.draw.rect(screen, color, (cx - size * 0.25, cy + size * 0.18, size * 0.5, size * 0.08))
        pygame.draw.rect(screen, outline_color, (cx - size * 0.25, cy + size * 0.18, size * 0.5, size * 0.08), 1)
        draw_outline_poly([
            (cx - size * 0.22, cy + size * 0.18),
            (cx + size * 0.22, cy + size * 0.18),
            (cx + size * 0.22, cy - size * 0.15),
            (cx + size * 0.10, cy - size * 0.15),
            (cx + size * 0.12, cy - size * 0.05),
            (cx - size * 0.12, cy - size * 0.05),
            (cx - size * 0.10, cy - size * 0.15),
            (cx - size * 0.22, cy - size * 0.15)
        ])
        pygame.draw.rect(screen, color, (cx - 3, cy - size * 0.3, 6, 12))
        pygame.draw.rect(screen, outline_color, (cx - 3, cy - size * 0.3, 6, 12), 1)
        pygame.draw.rect(screen, color, (cx - 8, cy - size * 0.25, 16, 4))
        pygame.draw.rect(screen, outline_color, (cx - 8, cy - size * 0.25, 16, 4), 1)


def main():
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Chess Pygame v9 (Training & Analysis Mode)")
    clock = pygame.time.Clock()
    
    game = ChessGame()
    
    # UI Component rectangles on Sidebar (Adjusted for 3 modes layout)
    pvp_btn_rect = pygame.Rect(BOARD_SIZE + 15, 12, 90, 28)
    ai_btn_rect = pygame.Rect(BOARD_SIZE + 115, 12, 90, 28)
    train_btn_rect = pygame.Rect(BOARD_SIZE + 15, 45, SIDEBAR_WIDTH - 30, 28)
    
    # Dynamic theme selection cycle button
    theme_btn_rect = pygame.Rect(BOARD_SIZE + 15, 405, SIDEBAR_WIDTH - 30, 28)
    
    # Save & Load buttons
    save_btn_rect = pygame.Rect(BOARD_SIZE + 15, 440, 90, 28)
    load_btn_rect = pygame.Rect(BOARD_SIZE + 115, 440, 90, 28)
    
    restart_btn_rect = pygame.Rect(BOARD_SIZE + 20, WINDOW_HEIGHT - 55, SIDEBAR_WIDTH - 40, 36)

    ai_thinking_timer = 0  # Simulation delay for AI move
    dt = 0  # Delta time in seconds

    while True:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Update player timers (only if not in Training mode)
        if not game.game_over and not game.promotion_pending and game.game_mode != 'Train':
            if game.turn == 'w':
                game.white_time -= dt
                if game.white_time <= 0:
                    game.white_time = 0
                    game.game_over = True
                    game.time_out_loss = True
                    game.winner = 'b'
            else:
                game.black_time -= dt
                if game.black_time <= 0:
                    game.black_time = 0
                    game.game_over = True
                    game.time_out_loss = True
                    game.winner = 'w'

        # Decrease feedback message timer
        if game.feedback_timer > 0:
            game.feedback_timer -= dt

        # Handle AI Turn triggering (only in AI mode)
        if game.game_mode == 'AI' and game.turn == 'b' and not game.game_over and not game.promotion_pending:
            if ai_thinking_timer == 0:
                ai_thinking_timer = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - ai_thinking_timer > 600:  # 600 ms delay
                game.make_ai_move()
                ai_thinking_timer = 0

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                
                # A. Handle Promotion UI clicks specifically
                if game.promotion_pending:
                    for idx in range(4):
                        bx = 140 + idx * 70
                        by = 250
                        btn_rect = pygame.Rect(bx, by, 60, 60)
                        if btn_rect.collidepoint(x, y):
                            choices = ['Q', 'R', 'B', 'N']
                            chosen_type = choices[idx]
                            
                            # Complete the promotion process
                            start, end = game.promotion_pending
                            end_r, end_c = end
                            color = game.turn  # True current turn player
                            
                            game.board[end_r][end_c] = f"{color}{chosen_type}"
                            game.move_log.append(f"{game.coords_to_notation(start, end)}={chosen_type}")
                            
                            game.promotion_pending = None
                            game.finalize_turn(start, end)
                            break
                    continue  # Ignore board/sidebar actions during promotion popup

                # B. Normal Sidebar buttons checks
                if pvp_btn_rect.collidepoint(x, y) and game.game_mode != 'PvP':
                    game.game_mode = 'PvP'
                    game.reset_game()
                elif ai_btn_rect.collidepoint(x, y) and game.game_mode != 'AI':
                    game.game_mode = 'AI'
                    game.reset_game()
                elif train_btn_rect.collidepoint(x, y) and game.game_mode != 'Train':
                    game.game_mode = 'Train'
                    game.reset_game()
                elif theme_btn_rect.collidepoint(x, y):
                    # Cycle through available themes: classic -> modern -> neon -> classic
                    theme_order = ['classic', 'modern', 'neon']
                    curr_idx = theme_order.index(game.theme)
                    next_idx = (curr_idx + 1) % len(theme_order)
                    game.theme = theme_order[next_idx]
                    game.set_feedback(f"Тема: {game.themes[game.theme]['name']}", 1.5)
                elif save_btn_rect.collidepoint(x, y):
                    game.save_game()
                elif load_btn_rect.collidepoint(x, y):
                    game.load_game()
                    ai_thinking_timer = 0
                elif restart_btn_rect.collidepoint(x, y):
                    game.reset_game()
                    ai_thinking_timer = 0
                
                # C. Normal Board click checks
                elif x < BOARD_SIZE:
                    # Ignore player inputs during AI turn (Black's turn) or game over
                    if game.game_mode == 'AI' and game.turn == 'b':
                        continue
                    if game.game_over:
                        continue
                        
                    c = x // SQUARE_SIZE
                    r = y // SQUARE_SIZE
                    
                    piece = game.board[r][c]
                    # If a piece is already selected, and we click a valid move square
                    if game.selected_piece and (r, c) in game.valid_moves:
                        game.make_move(game.selected_piece, (r, c))
                    # If we click one of our own color pieces, select it
                    elif piece and piece[0] == game.turn:
                        game.selected_piece = (r, c)
                        game.valid_moves = game.get_legal_moves(r, c)
                    else:
                        # Deselect
                        game.selected_piece = None
                        game.valid_moves = []

        # --- EXTRACT CURRENT THEME COLORS ---
        current_theme_data = game.themes[game.theme]
        board_light = current_theme_data['board_light']
        board_dark = current_theme_data['board_dark']
        highlight_selected = current_theme_data['highlight_selected']
        highlight_last_move = current_theme_data['highlight_last_move']

        # --- DRAWING ---
        screen.fill(board_light)

        # 1. Draw Board Squares
        for r in range(8):
            for c in range(8):
                sq_color = board_light if (r + c) % 2 == 0 else board_dark
                pygame.draw.rect(screen, sq_color, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                
                # Highlight last move (start and end square)
                if game.last_move and ((r, c) == game.last_move[0] or (r, c) == game.last_move[1]):
                    pygame.draw.rect(screen, highlight_last_move, (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)

        # 2. Draw Move Highlights
        if game.selected_piece:
            sr, sc = game.selected_piece
            pygame.draw.rect(screen, highlight_selected, (sc * SQUARE_SIZE, sr * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            
            for vr, vc in game.valid_moves:
                pygame.draw.circle(screen, HIGHLIGHT_VALID, (vc * SQUARE_SIZE + SQUARE_SIZE // 2, vr * SQUARE_SIZE + SQUARE_SIZE // 2), int(SQUARE_SIZE * 0.15))

        # 3. Draw Pieces & Check highlights
        for r in range(8):
            for c in range(8):
                piece = game.board[r][c]
                if piece:
                    # Highlight king red if in check
                    if piece[1] == 'K' and game.is_in_check(game.board, piece[0]):
                        pygame.draw.rect(screen, (231, 76, 60), (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)
                    
                    cx = c * SQUARE_SIZE + SQUARE_SIZE // 2
                    cy = r * SQUARE_SIZE + SQUARE_SIZE // 2
                    draw_piece(screen, piece, cx, cy, SQUARE_SIZE)

        # Recommended move arrow has been removed by user request

        # Draw last move arrow to visually track the last move made (requested by user)
        if game.last_move and not game.promotion_pending:
            start_sq, end_sq = game.last_move
            cx1 = start_sq[1] * SQUARE_SIZE + SQUARE_SIZE // 2
            cy1 = start_sq[0] * SQUARE_SIZE + SQUARE_SIZE // 2
            cx2 = end_sq[1] * SQUARE_SIZE + SQUARE_SIZE // 2
            cy2 = end_sq[0] * SQUARE_SIZE + SQUARE_SIZE // 2
            
            # Use themed colors for the last move arrow (subtle, beautiful and semi-transparent)
            last_move_arrow_color = (241, 196, 15)  # Warm yellow for classic
            if game.theme == 'neon':
                last_move_arrow_color = (168, 115, 232)  # Soft Purple / Lavender
            elif game.theme == 'modern':
                last_move_arrow_color = (250, 177, 160)  # Pastel Salmon
                
            draw_arrow(screen, last_move_arrow_color, (cx1, cy1), (cx2, cy2), thickness=5, head_size=14, alpha=130)

        # 4. Draw Transparent Modal overlay if Promotion Pending
        if game.promotion_pending:
            overlay = pygame.Surface((BOARD_SIZE, BOARD_SIZE), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            modal_rect = pygame.Rect(125, 190, 310, 150)
            pygame.draw.rect(screen, (52, 73, 94), modal_rect, border_radius=10)
            pygame.draw.rect(screen, (236, 240, 241), modal_rect, width=3, border_radius=10)
            
            lbl_promo = FONT_UI_BOLD.render("Перетворення! Оберіть фігуру:", True, SIDEBAR_TEXT)
            screen.blit(lbl_promo, (140, 210))
            
            choices = ['Q', 'R', 'B', 'N']
            for idx, ptype in enumerate(choices):
                bx = 140 + idx * 70
                by = 250
                btn_rect = pygame.Rect(bx, by, 60, 60)
                if btn_rect.collidepoint(mouse_x, mouse_y):
                    pygame.draw.rect(screen, highlight_selected, btn_rect, border_radius=5)
                else:
                    pygame.draw.rect(screen, (44, 62, 80), btn_rect, border_radius=5)
                pygame.draw.rect(screen, (236, 240, 241), btn_rect, width=1, border_radius=5)
                
                draw_piece(screen, f"{game.turn}{ptype}", bx + 30, by + 30, 55)

        # 5. Draw Sidebar Panel (UI components)
        pygame.draw.rect(screen, SIDEBAR_BG, (BOARD_SIZE, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
        
        # --- GAME MODE SWITCHER BUTTONS ---
        # 1. PvP Button
        if game.game_mode == 'PvP':
            pygame.draw.rect(screen, highlight_selected, pvp_btn_rect, border_radius=5)
        else:
            pygame.draw.rect(screen, (52, 73, 94), pvp_btn_rect, border_radius=5)
            if pvp_btn_rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(screen, (72, 93, 114), pvp_btn_rect, border_radius=5)
        lbl_pvp = FONT_UI_BOLD.render("2 Гравці", True, SIDEBAR_TEXT)
        screen.blit(lbl_pvp, (BOARD_SIZE + 30, 18))

        # 2. AI Button
        if game.game_mode == 'AI':
            pygame.draw.rect(screen, highlight_selected, ai_btn_rect, border_radius=5)
        else:
            pygame.draw.rect(screen, (52, 73, 94), ai_btn_rect, border_radius=5)
            if ai_btn_rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(screen, (72, 93, 114), ai_btn_rect, border_radius=5)
        lbl_ai = FONT_UI_BOLD.render("Робот", True, SIDEBAR_TEXT)
        screen.blit(lbl_ai, (BOARD_SIZE + 137, 18))

        # 3. Training Mode Button
        if game.game_mode == 'Train':
            pygame.draw.rect(screen, highlight_selected, train_btn_rect, border_radius=5)
        else:
            pygame.draw.rect(screen, (52, 73, 94), train_btn_rect, border_radius=5)
            if train_btn_rect.collidepoint(mouse_x, mouse_y):
                pygame.draw.rect(screen, (72, 93, 114), train_btn_rect, border_radius=5)
        lbl_train = FONT_UI_BOLD.render("Тренування / Аналіз", True, SIDEBAR_TEXT)
        screen.blit(lbl_train, (BOARD_SIZE + 35, 51))
        
        # --- TURN INDICATOR BOX ---
        turn_box_y = 80
        pygame.draw.rect(screen, (52, 73, 94), (BOARD_SIZE + 15, turn_box_y, SIDEBAR_WIDTH - 30, 38), border_radius=5)
        
        if game.game_mode == 'AI' and game.turn == 'b' and not game.game_over:
            turn_text = "Думає..."
        else:
            turn_text = "Хід : Білі" if game.turn == 'w' else "Хід : Чорні"
            
        lbl_turn = FONT_UI_BOLD.render(turn_text, True, SIDEBAR_TEXT)
        screen.blit(lbl_turn, (BOARD_SIZE + 30, turn_box_y + 10))
        
        # Turn piece preview circle
        prev_cx = BOARD_SIZE + SIDEBAR_WIDTH - 45
        prev_cy = turn_box_y + 19
        draw_piece(screen, f"{game.turn}P", prev_cx, prev_cy, 32)

        # --- TIMERS OR EVALUATION BAR ---
        timers_box_y = 124
        
        if game.game_mode == 'Train':
            # Draw live board evaluation indicator instead of clock
            pygame.draw.rect(screen, (52, 73, 94), (BOARD_SIZE + 15, timers_box_y, SIDEBAR_WIDTH - 30, 38), border_radius=5)
            
            val_clamped = max(-8.0, min(8.0, game.current_eval))
            ratio = (val_clamped + 8.0) / 16.0  # Normalized to 0.0 - 1.0 scale
            
            bar_x = BOARD_SIZE + 20
            bar_y = timers_box_y + 6
            bar_w = SIDEBAR_WIDTH - 40
            bar_h = 7
            
            # Base black bar
            pygame.draw.rect(screen, (30, 30, 30), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
            # Overlay white portion
            white_w = int(bar_w * ratio)
            if white_w > 0:
                pygame.draw.rect(screen, (245, 245, 245), (bar_x + (bar_w - white_w), bar_y, white_w, bar_h), border_radius=3)
            # Draw equal midline (0.00)
            pygame.draw.line(screen, (231, 76, 60), (bar_x + bar_w // 2, bar_y - 2), (bar_x + bar_w // 2, bar_y + bar_h + 2), 1)
            
            # Evaluation Text
            eval_sign = "+" if game.current_eval > 0 else ""
            eval_text = f"Оцінка: {eval_sign}{game.current_eval:.2f}"
            if game.current_eval == 0.0:
                eval_text = "Оцінка: 0.00 (Рівно)"
                
            lbl_eval = FONT_UI.render(eval_text, True, SIDEBAR_TEXT)
            screen.blit(lbl_eval, (BOARD_SIZE + 25, timers_box_y + 18))
        else:
            # Draw standard Timers
            pygame.draw.rect(screen, (52, 73, 94), (BOARD_SIZE + 15, timers_box_y, SIDEBAR_WIDTH - 30, 38), border_radius=5)
            
            def format_time(seconds):
                secs = max(0, int(seconds))
                mins = secs // 60
                secs = secs % 60
                return f"{mins:02d}:{secs:02d}"

            white_time_str = format_time(game.white_time)
            black_time_str = format_time(game.black_time)

            lbl_w_timer = FONT_UI_BOLD.render(f"W: {white_time_str}", True, SIDEBAR_TEXT)
            lbl_b_timer = FONT_UI_BOLD.render(f"B: {black_time_str}", True, SIDEBAR_TEXT)

            screen.blit(lbl_w_timer, (BOARD_SIZE + 25, timers_box_y + 11))
            screen.blit(lbl_b_timer, (BOARD_SIZE + 120, timers_box_y + 11))

        # Game Over Banner or Active Status or Feedback Message
        if game.feedback_message and game.feedback_timer > 0:
            msg_color = (46, 204, 113) if "успішно" in game.feedback_message or "Завантажено" in game.feedback_message or "Тема" in game.feedback_message else (231, 76, 60)
            lbl_status = FONT_UI_BOLD.render(game.feedback_message, True, msg_color)
            screen.blit(lbl_status, (BOARD_SIZE + 20, 171))
        elif game.game_over:
            pygame.draw.rect(screen, (44, 62, 80), (BOARD_SIZE + 15, 160, SIDEBAR_WIDTH - 30, 45), border_radius=5)
            if game.time_out_loss:
                status_txt = "Час вичерпано!"
                status_sub = "Перемога Чорних!" if game.winner == 'b' else "Перемога Білих!"
            else:
                if game.winner == 'Draw':
                    status_txt = "Нічия (Пат)"
                    status_sub = "Гру завершено"
                else:
                    status_txt = "Мат!"
                    status_sub = "Перемога Білих!" if game.winner == 'w' else "Перемога Чорних!"
            
            lbl_status = FONT_UI_BOLD.render(status_txt, True, (241, 196, 15))
            screen.blit(lbl_status, (BOARD_SIZE + 25, 165))
            lbl_status_sub = FONT_UI.render(status_sub, True, SIDEBAR_TEXT)
            screen.blit(lbl_status_sub, (BOARD_SIZE + 25, 185))
        else:
            lbl_status = FONT_UI.render("Гра триває...", True, (149, 165, 166))
            screen.blit(lbl_status, (BOARD_SIZE + 20, 171))

        # Recent moves log list
        lbl_log_header = FONT_UI_BOLD.render("Останні ходи:", True, SIDEBAR_TEXT)
        screen.blit(lbl_log_header, (BOARD_SIZE + 20, 205))
        
        start_y = 225
        log_slice = game.move_log[-8:]
        for idx, move in enumerate(log_slice):
            move_num = len(game.move_log) - len(log_slice) + idx + 1
            prefix = f"{(move_num+1)//2}." if move_num % 2 != 0 else "   "
            lbl_move = FONT_UI.render(f"{prefix} {move}", True, (200, 200, 200))
            col_x = BOARD_SIZE + 20 if idx < 4 else BOARD_SIZE + 120
            row_y = start_y + (idx % 4) * 20
            screen.blit(lbl_move, (col_x, row_y))

        # Captured Pieces Box
        lbl_captures = FONT_UI_BOLD.render("Захоплені фігури:", True, SIDEBAR_TEXT)
        screen.blit(lbl_captures, (BOARD_SIZE + 20, 315))
        
        white_captures = game.captured_pieces['w']  # captured by black
        black_captures = game.captured_pieces['b']  # captured by white
        
        lbl_cap_w = FONT_UI.render("Білі:", True, (180, 180, 180))
        screen.blit(lbl_cap_w, (BOARD_SIZE + 20, 335))
        for idx, pt in enumerate(white_captures[-8:]):
            draw_piece(screen, f"w{pt}", BOARD_SIZE + 70 + idx * 16, 343, 22)
            
        lbl_cap_b = FONT_UI.render("Чорні:", True, (180, 180, 180))
        screen.blit(lbl_cap_b, (BOARD_SIZE + 20, 370))
        for idx, pt in enumerate(black_captures[-8:]):
            draw_piece(screen, f"b{pt}", BOARD_SIZE + 70 + idx * 16, 378, 22)

        # --- THEME SELECT BUTTON ---
        pygame.draw.rect(screen, (127, 140, 141), theme_btn_rect, border_radius=5)
        if theme_btn_rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, (149, 165, 166), theme_btn_rect, border_radius=5)
        lbl_theme_text = FONT_UI_BOLD.render(f"Тема: {current_theme_data['name']}", True, TEXT_COLOR)
        screen.blit(lbl_theme_text, (BOARD_SIZE + 25, 411))

        # --- SAVE / LOAD BUTTONS ---
        # 1. Save Button
        pygame.draw.rect(screen, (52, 152, 219), save_btn_rect, border_radius=5)
        if save_btn_rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, (41, 128, 185), save_btn_rect, border_radius=5)
        lbl_save = FONT_UI_BOLD.render("Зберегти", True, TEXT_COLOR)
        screen.blit(lbl_save, (BOARD_SIZE + 26, 446))

        # 2. Load Button
        pygame.draw.rect(screen, (39, 174, 96), load_btn_rect, border_radius=5)
        if load_btn_rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, (46, 204, 113), load_btn_rect, border_radius=5)
        lbl_load = FONT_UI_BOLD.render("Завантажити", True, TEXT_COLOR)
        screen.blit(lbl_load, (BOARD_SIZE + 121, 446))

        # Reset button
        pygame.draw.rect(screen, (192, 57, 43), restart_btn_rect, border_radius=5)
        if restart_btn_rect.collidepoint(mouse_x, mouse_y):
            pygame.draw.rect(screen, (231, 76, 60), restart_btn_rect, border_radius=5)
            
        lbl_restart = FONT_UI_BOLD.render("Скинути гру", True, TEXT_COLOR)
        screen.blit(lbl_restart, (BOARD_SIZE + 65, WINDOW_HEIGHT - 45))

        # Update display and tick clock
        pygame.display.flip()
        dt = clock.tick(30) / 1000.0


if __name__ == "__main__":
    main()
