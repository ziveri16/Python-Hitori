import math
import g2d
import random
import time 

class Cell:
    def __init__(self, pos: tuple, value: int, size: int):
        self.pos = pos
        self.value = value
        self.size = size
        self.selected = False
        self.circled = False
        self.closed = False
        self.valid = True
    
    #verifico se il clic del mouse si trova all'interno dell'area di un oggetto
    def check_mouse_click(self, mouse_pos: tuple) -> bool:
        x, y = self.pos
        return x < mouse_pos[0] < x + self.size and y < mouse_pos[1] < y + self.size
    
class BoardGame: #classe boardgame per gestire  le dinamiche del gioco
    def __init__(self):
        self.size = 5 #impostiamoa 5 in fase di inizializzazione per assicurarci che il gioco sia sempre giocabile(una matrice 15x15 verrà tagliata a 5x5)
        self.cells = []
        self.game_state = "menu" #modalità iniziale
        self.selected_mode = 0
        self.modes = ["easy", "medium", "hard", "veryhard", "superhard", "impossible"] 
        self.numbers = []
        self.game_state = "menu"  
        self.start_time = None  
        self.elapsed_time = 0  


    def load_csv(self): #funzioni per caricare gli esempi
        filenames = [
            "matrix/matrix_easy.csv",
            "matrix/matrix_medium.csv",
            "matrix/matrix_hard.csv",
            "matrix/matrix_veryhard.csv",
            "matrix/matrix_superhard.csv",
            "matrix/matrix_impossible.csv"
        ]
        try:
            with open(filenames[self.selected_mode]) as infile:
                self.numbers = []
                for line in infile:
                    self.numbers += [int(v) for v in line.strip().split(",")] #usiamo la manipolazione delle stringhe per ottenere i valori delle celle
            print(f"Loaded file: {filenames[self.selected_mode]} with {len(self.numbers)} numbers.")
            self.initialize_cells()
            self.game_state = "game"
        except FileNotFoundError:
            print(f"File {filenames[self.selected_mode]} not found.")

    def initialize_cells(self): #creiamo le celle 
        grid_size = int(math.sqrt(len(self.numbers)))  #la grandezza della griglia essendo tutte matrici quadrate sarà data dalla radice del totale
        self.size = grid_size
        self.cells = []

        canvas_size = 500 #grandezza del canvas
        border = 2 
        
        cell_size = int((canvas_size - 2 * border) // grid_size)

        x_offset = (canvas_size - (cell_size * grid_size)) // 2
        y_offset = (canvas_size - (cell_size * grid_size)) // 2
        
        numbers_index = 0
        for j in range(grid_size):
            for i in range(grid_size): 
                if numbers_index < len(self.numbers):
                    cell_x = i * cell_size + x_offset
                    cell_y = j * cell_size + y_offset #aggiungiamo alla lista di celle le celle generate in base al numero e alla grandezza del canvas
                    self.cells.append(Cell((cell_x, cell_y), self.numbers[numbers_index], cell_size)) #tenendo conto anche del gap tra le celle e i bordi
                    numbers_index += 1

    def get_cell_from_pos(self, pos: tuple): #metodo che data la posizioone del mouse restituisce la cella su cui si trovava il cursore quando è stato chiamato il click
        for cell in self.cells:
            if cell.check_mouse_click(pos):
                return cell
        return None

    def from_list_to_matrix(self):
        cells_matrix = []
        cells_duplicate = self.cells[:]
        for _ in range(self.size):
            temp = cells_duplicate[:self.size]
            cells_matrix.append(temp)
            for el in temp:
                cells_duplicate.remove(el)
        return cells_matrix

    def check_for_duplicate(self, cells):
        values = [cell.value for cell in cells if not cell.selected]
        return len(values) != len(set(values))

    def check_adiecent_cells(self, matrix, cell, color: bool):
        indexes_to_check = []
        verified_cells = []
        row_index, col_index = self.get_matrix_index_from_cell(cell)

        if -1 < row_index + 1 < len(matrix):
            indexes_to_check.append((row_index + 1, col_index))
        if -1 < row_index - 1 < len(matrix):
            indexes_to_check.append((row_index - 1, col_index))
        if -1 < col_index + 1 < len(matrix[0]):
            indexes_to_check.append((row_index, col_index + 1))
        if -1 < col_index - 1 < len(matrix[0]):
            indexes_to_check.append((row_index, col_index - 1))

        for el in indexes_to_check:
            if matrix[el[0]][el[1]].selected == color or color == None:
                verified_cells.append(matrix[el[0]][el[1]])
        
        return verified_cells

    def get_matrix_index_from_cell(self, cell):
        matrix = self.from_list_to_matrix()
        for i, row in enumerate(matrix):
            if cell in row:
                return (i, row.index(cell))
        return None

    def check_black_cells(self):
        matrix = self.from_list_to_matrix()
        any_invalid = False
        for row in matrix:
            for cell in row:
                if cell.selected:
                    adjacent_black_cells = self.check_adiecent_cells(matrix, cell, True)
                    if adjacent_black_cells:
                        cell.valid = False
                        any_invalid = True
                        for adj_cell in adjacent_black_cells:
                            adj_cell.valid = False
                    else:
                        cell.valid = True

        return not any_invalid

    def finished(self):
        matrix = self.from_list_to_matrix()
        white_cells = [el for row in matrix for el in row if not el.selected]
        
        connected_cells = []

        for cell in white_cells:
            adjacent_white_cells = self.check_adiecent_cells(matrix, cell, False)
            
            for el in adjacent_white_cells:
                if el not in connected_cells:
                    el.circled = False
                    connected_cells.append(el)

        for el in white_cells:
            if el not in connected_cells:
                el.circled = True

        return len(connected_cells) == len(white_cells)

    def check_for_win(self):
        matrix = self.from_list_to_matrix()
        columns = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
        
        for el in columns:
            if self.check_for_duplicate(el):
                return False
        
        for el in matrix:
            if self.check_for_duplicate(el):
                return False

        all_valid = all(cell.valid for cell in self.cells)
        white_connections_valid = self.finished()
        
        if all_valid and white_connections_valid:
            print("YOU WON!")
            self.game_state = "win"
            return True

        return False
    
    def check_for_circled_duplicates(self) -> bool:

        for row in self.from_list_to_matrix():
            circled_values = [el.value for el in row if el.circled]
            if len(circled_values) != len(set(circled_values)):
                return True
        

        matrix = self.from_list_to_matrix()
        columns = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
        for col in columns:
            circled_values = [el.value for el in col if el.circled]
            if len(circled_values) != len(set(circled_values)):
                return True
        
        return False

    def start_timer(self):
        if self.start_time is None: 
            self.start_time = time.time()

    def stop_timer(self):
        if self.start_time is not None:
            self.elapsed_time += time.time() - self.start_time
            self.start_time = None  

    def reset_timer(self):
        self.start_time = None
        self.elapsed_time = 0

    def get_elapsed_time(self):
        if self.start_time is not None:
           
            return self.elapsed_time + (time.time() - self.start_time)
        return self.elapsed_time
    
    def select_same_value_cells(self, clicked_cell):
        matrix = self.from_list_to_matrix()
        columns = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
        
        for el in columns[self.get_matrix_index_from_cell(clicked_cell)[1]]:
            if el.value == clicked_cell.value:
                el.selected = True

        for el in matrix[self.get_matrix_index_from_cell(clicked_cell)[0]]:
             if el.value == clicked_cell.value:
                el.selected = True
        
        clicked_cell.selected = False

    def undo_selection(self, cell):
        matrix = self.from_list_to_matrix()
        columns = [[row[i] for row in matrix] for i in range(len(matrix[0]))]
        
        for el in columns[self.get_matrix_index_from_cell(cell)[1]]:
            if el.value == cell.value:
                el.selected = False
        
        for el in matrix[self.get_matrix_index_from_cell(cell)[0]]:
            if el.value == cell.value:
                el.selected = False
        
        cell.selected = False

    def wrong(self) -> bool:     
        black_cells_valid = self.check_black_cells()
        print(f"check_black_cells: {black_cells_valid}")
        white_cells_connected = self.finished()
        print(f"finished (white cells connected): {white_cells_connected}")
        circled_duplicates = self.check_for_circled_duplicates()
        print(f"check_for_circled_duplicates: {circled_duplicates}")
        is_wrong = not black_cells_valid or not white_cells_connected or circled_duplicates
        print(f"Risultato 'wrong': {is_wrong}")
        
        return is_wrong
    
    def draw_gui(self):
        g2d.clear_canvas()
        g2d.set_color((5, 17, 3))
        g2d.draw_rect((0, 500), (500, 550))
        g2d.set_color((122, 255, 160))
        g2d.draw_line((10, 520), (490, 520), 3)
        current_mode = self.modes[self.selected_mode]
        g2d.set_color((122, 255, 160))
        g2d.draw_text(f"Game mode: {current_mode}", (100, 560), 20)
        
        elapsed = round(float(self.get_elapsed_time()), 2)
        g2d.set_color((122, 255, 160))
        g2d.draw_text(f"Time:", (340, 560), 20)
        g2d.draw_text(str(elapsed), (390, 560), 20)


class BoardGameGui:
    def __init__(self, game: BoardGame):
        self.game = game

    def tick(self):
        if self.game.game_state == "menu":
            self.draw_menu()
        elif self.game.game_state == "win":
            self.draw_win()
        else:
            self.update_game_screen()

    def draw_menu(self):
        g2d.set_color((5, 17, 3))
        g2d.draw_rect((0, 0), (500, 600))
        g2d.draw_image("img/HITORI.png", (100, 30))
        g2d.draw_image("img/start.png", (135, 130))
        pos_y = 230
        for i, mode in enumerate(self.game.modes):
            if i == self.game.selected_mode:
                g2d.set_color((122, 255, 160))
            else:
                g2d.set_color((255, 255, 255))
            g2d.draw_text(mode, (250, pos_y), 24)
            pos_y += 40

    # disegno la schermata della vittoria
    def draw_win(self):
        g2d.set_color((5, 17, 3))
        g2d.draw_rect((0, 0), (500, 500))
        g2d.draw_image("img/SOLVED.png", (0, 30))
        g2d.draw_image("img/made_by.png", (135, 170))
        g2d.draw_image("img/Lorenzo_Gervasoni.png", (25, 250))
        g2d.draw_image("img/and.png", (190, 325))
        g2d.draw_image("img/Marco_Ziveri.png", (80, 400))

    def update_game_screen(self):
        g2d.set_color((0, 0, 0))
        g2d.draw_rect((0, 0), (500, 500))
        for cell in self.game.cells:
            self.draw_cell(cell)

    # disegno la griglia delle celle
    def draw_cell(self, cell):
        grid_size = int(math.sqrt(len(self.game.numbers)))
        cell_size = int(500 // grid_size)

        g2d.set_color((255, 255, 255))
        g2d.draw_rect(cell.pos, (cell_size - 2, cell_size - 2))

        if cell.selected:
            g2d.set_color((0, 0, 0))
            if not cell.valid:
                g2d.set_color((120, 0, 0))
            g2d.draw_rect(cell.pos, (cell_size, cell_size))
        elif cell.closed:
            g2d.set_color((250, 120, 120))
            g2d.draw_rect(cell.pos, (cell_size, cell_size))

        if cell.circled:
            g2d.set_color((120, 120, 120))
            g2d.draw_circle((cell.pos[0] + cell_size // 2, cell.pos[1] + cell_size // 2), cell_size * 0.4)

        g2d.set_color((0, 0, 0) if not cell.selected else (255, 255, 255))
        g2d.draw_text(str(cell.value), 
                    (cell.pos[0] + cell_size // 2, cell.pos[1] + cell_size // 2), 
                    int(cell_size * 0.5))
        

def main():
    game = BoardGame()
    gui = BoardGameGui(game)
    
    g2d.init_canvas((500, 600))

    def game_tick():
        # se il game state è impostato a menu, uso le frecce per scorrere le modalità
        if game.game_state == "menu":
            if g2d.key_pressed("ArrowUp"):
                game.selected_mode = (game.selected_mode - 1) % len(game.modes)
            elif g2d.key_pressed("ArrowDown"):
                game.selected_mode = (game.selected_mode + 1) % len(game.modes)
            # premendo invio faccio partire il gioco
            if g2d.key_pressed("Enter"):
                game.load_csv()
                game.reset_timer()  
                game.start_timer() 
        # se il game state è impostato  a win, fermo il timer
        elif game.game_state == "win":
            game.stop_timer() 
            if g2d.key_pressed("Enter"):
                game.game_state = "menu"
        else:
            # se il game state è impostato a game, mostro il gioco con relativo timer e modalità sceltar
            game.check_for_win()
            game.check_black_cells()
            game.draw_gui()
            # se si clicca il tasto sinistro, annerisco la cella
            if g2d.mouse_clicked():
                clicked_cell = game.get_cell_from_pos(g2d.mouse_pos())
                if clicked_cell:
                    clicked_cell.selected = not clicked_cell.selected
                    if clicked_cell.circled:
                        clicked_cell.circled = False
            # se clicco il tasto destro, cerchio il numero
            if g2d.mouse_right_clicked():
                clicked_cell = game.get_cell_from_pos(g2d.mouse_pos())
                if clicked_cell:
                    if clicked_cell.selected:
                        for el in game.check_adiecent_cells(game.from_list_to_matrix(), clicked_cell, None):
                            if not el.selected:
                                el.circled = True
                    elif clicked_cell.circled:
                        clicked_cell.circled = not clicked_cell.circled
                        game.select_same_value_cells(clicked_cell)
                    else:
                        clicked_cell.circled = not clicked_cell.circled
            # attivo gli automatismi
            if g2d.key_released("h"): 
                
                matrix_copy = [row[:] for row in game.from_list_to_matrix()]

                
                changes_to_select = []
                changes_to_circle = []

                
                for row in matrix_copy:
                    for el in row:
                        if el.selected:
                            
                            changes_to_select.append(el)
                        elif el.circled:
                        
                            adj_cells = game.check_adiecent_cells(matrix_copy, el, None)
                            for adj_el in adj_cells:
                                if not adj_el.selected:
                                    changes_to_circle.append(adj_el)

            
                for el in changes_to_select:
                    el.circled = not el.circled 
                    game.select_same_value_cells(el)  

                for el in changes_to_circle:
                    el.circled = not el.circled 
            # con a provo a risolvere randomicamente il puzzle
            if g2d.key_released("a"):
                blank_cells = [el for row in game.from_list_to_matrix() for el in row if not el.selected and not el.circled]
                tried_cells = set()  

                while not game.check_for_win():
                    test_cell = random.choice(blank_cells)

                    game.select_same_value_cells(test_cell)
                    
                    if not game.wrong():
                        tried_cells.add(test_cell)
                    else:
                        game.undo_selection(test_cell)

                    blank_cells = [el for el in blank_cells if el not in tried_cells]

                    if not blank_cells:
                        break

        gui.tick()
    g2d.main_loop(game_tick)

if __name__ == "__main__":
    main()