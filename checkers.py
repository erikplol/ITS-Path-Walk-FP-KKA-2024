import pygame
import sys
import copy

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
GOLD = (255, 223, 0)
BLUE = (0, 0, 255)  # For highlighting valid moves

# Game settings
FPS = 60

class Piece:
    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = SQUARE_SIZE // 2 - self.PADDING
        pygame.draw.circle(win, BLACK, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)

        if self.king:
            self.draw_crown(win)

    def draw_crown(self, win):
        crown_color = GOLD
        pygame.draw.polygon(win, crown_color, [
            (self.x - 10, self.y - 15),
            (self.x, self.y - 25),
            (self.x + 10, self.y - 15),
            (self.x + 5, self.y - 5),
            (self.x - 5, self.y - 5)
        ])

    def move(self, row, col):
        self.row = row
        self.col = col
        self.calc_pos()

class Board:
    def __init__(self):
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        self.create_board()

    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    self.board[row].append(0)
                else:
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0)

    def draw(self, win):
        win.fill(BLACK)
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 != 0:
                    pygame.draw.rect(win, GREY, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
        
        for row in self.board:
            for piece in row:
                if piece != 0:
                    piece.draw(win)

    def move(self, piece, row, col):
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        if row == 0 or row == ROWS - 1:
            piece.make_king()

    def get_piece(self, row, col):
        return self.board[row][col]

    def remove(self, pieces):
        for piece in pieces:
            self.board[piece.row][piece.col] = 0

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def evaluate(self):
        return self.white_left - self.red_left + (self.white_kings * 0.5 - self.red_kings * 0.5)

    def get_valid_moves(self, piece):
        moves = {}
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED or piece.king:
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))

        if piece.color == WHITE or piece.king:
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

        return moves

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if left < 0:
                break

            current = self.board[r][left]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, left)] = last + skipped
                else:
                    moves[(r, left)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            left -= 1

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        moves = {}
        last = []
        for r in range(start, stop, step):
            if right >= COLS:
                break

            current = self.board[r][right]
            if current == 0:
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=last))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=last))
                break
            elif current.color == color:
                break
            else:
                last = [current]

            right += 1

        return moves

    def winner(self):
        if self.red_left <= 0:
            return WHITE
        elif self.white_left <= 0:
            return RED
        return None

class CheckersGame:
    def __init__(self, win):
        self.board = Board()  # Initialize the Board
        self.turn = RED
        self.selected_piece = None
        self.valid_moves = {}
        self.win = win
        self.game_over = False  # New attribute to track game-over state

    def update(self):
            self.board.draw(self.win)
            self.draw_valid_moves(self.valid_moves)
            
            # Check for game-over
            winner = self.board.winner()
            if winner:
                self.display_winner(winner)
                self.game_over = True  # Set game over state
            pygame.display.update()

    def display_winner(self, winner):
        font = pygame.font.Font(None, 74)
        text = font.render("Game Over! " + ("White" if winner == WHITE else "Red") + " Wins!", True, BLUE)
        self.win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        pygame.display.update()
        pygame.time.delay(3000)

    def reset(self):
        self.__init__(self.win)

    def select(self, row, col):
        if self.game_over:  # Prevent actions after game over
            return False
        piece = self.board.get_piece(row, col)
        if self.selected_piece:
            if (row, col) in self.valid_moves:
                self.move(row, col)
            else:
                self.selected_piece = None
                self.valid_moves = {}
                self.select(row, col)
        elif piece != 0 and piece.color == self.turn:
            self.selected_piece = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True
        return False

    def move(self, row, col):
        piece = self.selected_piece
        if piece and (row, col) in self.valid_moves:
            self.board.move(piece, row, col)
            captured = self.valid_moves[(row, col)]
            if captured:
                self.board.remove(captured)
            self.change_turn()
        self.selected_piece = None
        self.valid_moves = {}

    def ai_move(self):
        if not self.game_over:  # Only move if the game is not over
            _, new_board = self.minimax(self.board, 3, WHITE)  # Depth 3
            self.board = new_board
            self.change_turn()

    def draw_valid_moves(self, moves):
        for move in moves:
            row, col = move
            pygame.draw.circle(self.win, BLUE, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), 15)

    def change_turn(self):
        self.turn = WHITE if self.turn == RED else RED

    def ai_move(self):
        _, new_board = self.minimax(self.board, 3, WHITE)  # Depth 3
        self.board = new_board
        self.change_turn()

    def minimax(self, board, depth, max_player):
        if depth == 0 or board.winner() is not None:
            return board.evaluate(), board

        if max_player:
            max_eval = float('-inf')
            best_move = None
            for move in self.get_all_moves(board, WHITE):
                evaluation = self.minimax(move, depth - 1, False)[0]
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = None
            for move in self.get_all_moves(board, RED):
                evaluation = self.minimax(move, depth - 1, True)[0]
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = move
            return min_eval, best_move

    def get_all_moves(self, board, color):
        moves = []
        for piece in board.get_all_pieces(color):
            valid_moves = board.get_valid_moves(piece)
            for move, skip in valid_moves.items():
                temp_board = copy.deepcopy(board)
                temp_piece = temp_board.get_piece(piece.row, piece.col)
                temp_board.move(temp_piece, move[0], move[1])
                if skip:
                    temp_board.remove(skip)
                moves.append(temp_board)
        return moves

def main():
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Checkers Game with AI")
    clock = pygame.time.Clock()
    game = CheckersGame(win)

    run = True
    while run:
        clock.tick(FPS)

        if game.turn == WHITE and not game.game_over:  # AI turn only if game is not over
            game.ai_move()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.turn == RED and not game.game_over:  # Player's turn only if game is not over
                    pos = pygame.mouse.get_pos()
                    row, col = pos[1] // SQUARE_SIZE, pos[0] // SQUARE_SIZE
                    game.select(row, col)

        game.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()