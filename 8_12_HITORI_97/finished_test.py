from main2 import Cell

def finished(self):
    # Empty matrix case
    if not self.cells:
        return True

    matrix = self.from_list_to_matrix()
    white_cells = [cell for cell in self.cells if not cell.selected]
    
    # Check white cell connectivity
    if not self.check_white_connections():
        return False

    # No additional marking of cells in the finished check
    for cell in white_cells:
        cell.circled = False

    return True


def test_finished_empty_matrix(self):
    self.board_game.cells = []
    self.assertTrue(self.board_game.finished())
def test_finished_all_white_cells_connected(self):
    self.board_game.size = 3
    self.board_game.cells = [
        Cell((0, 0), 1, 30), Cell((30, 0), 2, 30), Cell((60, 0), 3, 30),
        Cell((0, 30), 4, 30), Cell((30, 30), 5, 30), Cell((60, 30), 6, 30),
        Cell((0, 60), 7, 30), Cell((30, 60), 8, 30), Cell((60, 60), 9, 30)
    ]
    # Set up a scenario where all white cells are connected
    self.board_game.cells[0].selected = True  # Black cell
    self.board_game.cells[8].selected = True  # Black cell

    result = self.board_game.finished()
    
    self.assertTrue(result)
    # Check that all white cells are not circled
    for cell in self.board_game.cells[1:8]:
        self.assertFalse(cell.circled)



def test_finished_with_isolated_white_cells(self):
    self.board_game.size = 3
    self.board_game.cells = [
        Cell((0, 0), 1, 10), Cell((10, 0), 2, 10), Cell((20, 0), 3, 10),
        Cell((0, 10), 4, 10), Cell((10, 10), 5, 10), Cell((20, 10), 6, 10),
        Cell((0, 20), 7, 10), Cell((10, 20), 8, 10), Cell((20, 20), 9, 10)
    ]
    # Set up a scenario with isolated white cells
    self.board_game.cells[0].selected = True
    self.board_game.cells[2].selected = True
    self.board_game.cells[6].selected = True
    self.board_game.cells[8].selected = True

    result = self.board_game.finished()
    self.assertFalse(result, "Should return False when there are isolated white cells")

