import itertools
import random
import copy #need this module to make a deepcopy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"
    
    #need these two more functions to make operations on sentence
    def __repr__(self):
        return f"{self.cells} = {self.count}\n"
    def __sub__(self, other):
        return Sentence(self.cells - other.cells, self.count - other.count)

    def known_mines(self):
        if self.count == len(self.cells):
            return self.cells
        return None

    def known_safes(self):
        if self.count == 0:
            return self.cells
        return None

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []
        
        self.MINE_COUNT = 8

    def mark_mine(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
            
    # Helper to remove duplicates
    def remove_duplicates(self, duplicates):
        unique_list = []
        for number in duplicates:
            if number not in unique_list:
                unique_list.append(number)
        return unique_list
    
    # Helper to cells nearby
    def get_nearby_cells(self, cell):
        cells = []
        for x in range(cell[0] - 1, cell[0] + 2):
            for y in range(cell[1] - 1, cell[1] + 2):
                if x not in range(0,8) or y not in range(0, 8): continue
                if (x,y) != cell: cells.append( (x, y) )
        return cells

    def add_knowledge(self, cell, count):
        self.moves_made.add(cell)

        self.mark_safe(cell)

        free_neighbours = [x for x in self.get_nearby_cells(cell) if x not in self.moves_made]

        sentence = Sentence(free_neighbours, count)

        additional_sentences = []
        for key,knowledge in enumerate(self.knowledge):
            if sentence.cells.issubset(knowledge.cells):
                additional_sentences.append(knowledge - sentence)

            elif sentence.cells.issuperset(knowledge.cells):
                additional_sentences.append(sentence - knowledge)

        for additional in additional_sentences:
            if additional not in self.knowledge:
                self.knowledge.append(additional)

        self.knowledge.append(sentence)

        self.knowledge = self.remove_duplicates(self.knowledge)

        new_knowledge = copy.deepcopy(self.knowledge)

        for sentence in new_knowledge:
            if sentence.known_mines():
                new_knowledge.remove(sentence)
                for mine in sentence.known_mines():
                    self.mark_mine(mine)

            if sentence.known_safes():
                new_knowledge.remove(sentence)
                for safe in sentence.known_safes():
                    self.mark_safe(safe)

        self.knowledge = new_knowledge
        

    def make_safe_move(self):
        safe_moves = list(self.safes - self.moves_made)
        if safe_moves:
            return safe_moves[0]
        return None

    def make_random_move(self):
        all_cells = set((int(x / self.width), x % self.height) for x in range(self.width * self.height))
        possible = list(all_cells - self.moves_made - self.mines)
        if len(self.mines) < self.MINE_COUNT:
            return random.choice(possible)
        return None
