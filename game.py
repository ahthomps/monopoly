"""
 *****************************************************************************
   FILE:  game.py

   AUTHOR: Alma Thompson

   ASSIGNMENT: Final Project - Monopoly

   DATE: 5/1/18

   DESCRIPTION: This program allows the user to play a two-player gamer of
                the classic board game Monopoly. Some rules have been adapted
                to better fit the coded version of the game.

 *****************************************************************************
"""

from cs110graphics import *
import random
import json


class GameManager(EventHandler):
    """This class manages almost all other classes in the game. The primary
       functions of this class is to start the Board and GamePieces classes,
       add the starting popup window, create players, and start and end
       turns."""

    # the constructor for the GameManager class:
    def __init__(self, win):

        # call the EventHandler parent class so that methods belonging to
        # that class are accessible:
        EventHandler.__init__(self)

        self._win = win

        # starts Board and GamePieces classes:
        self._board = Board(self._win)
        self._game_pieces = GamePieces(self._win, self)
        self._houses = Houses(self._win, self)

        # initializes the list of player tokens and starts the game opening
        # popup window:
        self._player_characters = []
        self._start_win = PopUpWin(self._win, None, self)
        self._start_win.start()

    def create_players(self):
        """This function creates two players that will play the Monopoly game.
           Players are created using the token choices made in the _start_win.
           The play_turn() function is called with _player1 playing first."""

        # makes players:
        self._player1 = Player(self._win, self._game_pieces,
                               self._player_characters[0],
                               self._board, 1)
        self._player2 = Player(self._win, self._game_pieces,
                               self._player_characters[1],
                               self._board, 2)
        self._all_players = [self._player1, self._player2]

        # starts first turn:
        self.play_turn(self._player1, self._player2)

    def play_turn(self, player, other):
        """This function performs all the components of a turn of Monopoly."""

        # _player is the active player for the turn and _other is the passive
        # player:
        self._player = player
        self._other = other

        # initializes the number of successive doubles rolled by the player for
        # this turn:
        self._roll_doubles = 0

        # displays whose turn it is, the player's money, and any properties
        # that the player may have:
        self._player.display_player_title()
        self._player.display_money()
        self._player.display_properties()

        # starts the BuyProperty, Spots, and Cards classes:
        self._buy_prop = BuyProperty(self._win, self._player, self._other,
                                     self)
        self._spots = Spots(self._win, self._player, self._buy_prop,
                            self._board, self)
        self._cards = Cards(self._win, self._player, self._other, self._board,
                            self)
        # creates the dice for game play and adds handlers to them:
        self._die1 = Die(self._win, (1075, 90))
        self._die2 = Die(self._win, (1125, 90))
        self._die1.add_handler(DieHandler(self._win, self._die1, self._die2,
                                          self._game_pieces, self._spots,
                                          self._player, self,
                                          self._roll_doubles))
        self._die2.add_handler(DieHandler(self._win, self._die2, self._die1,
                                          self._game_pieces, self._spots,
                                          self._player, self,
                                          self._roll_doubles))

    def add_end_turn_button(self):
        """This function adds an end turn button to the window."""

        # creates the body of the button:
        self._end_turn_button = Rectangle(self._win, 70, 40, (1155, 30))
        self._end_turn_button.set_depth(2)
        self._end_turn_button.set_fill_color('red')
        self._win.add(self._end_turn_button)

        # creates the text inside the button:
        self._end_turn_text = Text(self._win, 'END TURN', 8, (1155, 30))
        self._end_turn_text.set_depth(1)
        self._win.add(self._end_turn_text)

        # adds handlers to the body and text of the button:
        self._end_turn_button.add_handler(self)
        self._end_turn_text.add_handler(self)

        # initiates the player's ability to buy a house as False:
        self._can_buy_house = False
        # initiates the different sets of properties that a player has
        # complete:
        house_sets = []

        # looks through all the different property sets:
        for prop_set in self._player._prop_kinds:
            # checks if the player has all the deeds in the set:
            if (self._player._prop_kinds
                    [prop_set]['have']) == (self._player._prop_kinds
                                            [prop_set]['max']):
                # changes the player's ability to buy a house to True:
                self._can_buy_house = True
                # appends the name of the set that the player has a monopoly
                # on and adds it to house_sets
                house_sets.append(prop_set)

        # if the player has the ability to buy houses, calls the function
        # Houses.display_house_buttons:
        if self._can_buy_house:
            self._houses.display_house_buttons(house_sets)

    def remove_end_turn_button(self):
        """This function removes the end turn button from the window."""

        self._win.remove(self._end_turn_button)
        self._win.remove(self._end_turn_text)

    def handle_mouse_enter(self):
        """This function changes the button's body color to red when the player
           puts the mouse on the button."""

        self._end_turn_button.set_border_color('red')

    def handle_mouse_leave(self):
        """This function changes the button's body color to black when the
           player takes the mouse off the button."""

        self._end_turn_button.set_border_color('black')

    def handle_mouse_release(self):
        """This function ends the player's turn by removing player-specific
           information (buy house buttons, money, properties, and title), the
           dice, and the end turn button itself. It also starts a new turn with
           the players in the active and passive playing positions switching
           roles."""

        if self._can_buy_house:
            self._houses.remove_house_buttons()
        self._player.remove_money()
        self._player.remove_properties()
        self._player.remove_player_title()
        self._die1.remove_die()
        self._die1.remove_pips_from_win()
        self._die2.remove_die()
        self._die2.remove_pips_from_win()
        self.remove_end_turn_button()
        self.play_turn(self._other, self._player)


class Board(object):
    """This class creates the basic elements of the Monopoly board and contains
       general information about each space on the board."""

    # The constructor for the Board class:
    def __init__(self, win):

        self._win = win

        # creates game board and adds to window:
        board = Image(self._win, 'board.jpg', 700, 700, (350, 350))
        board.set_depth(10)
        self._win.add(board)

        # creates piggy bank to display player's money and adds to window:
        pig_bank = Image(self._win, 'pig_bank.png', 180, 150, (1100, 200))
        pig_bank.set_depth(2)
        self._win.add(pig_bank)

        # creates a window called "POTENTIAL PROPERTY" where players will
        # choose whether or not to buy a property and adds it to window:
        choice_win = Rectangle(self._win, 280, 240, (850, 160))
        choice_win.set_depth(10)
        self._win.add(choice_win)
        choice_win_text = Text(self._win, 'POTENTIAL PROPERTY', 15, (850, 55))
        choice_win_text.set_depth(9)
        self._win.add(choice_win_text)

        # creates a window called "YOUR PROPERTIES" where any properties that
        # a player owns will be displayed and adds it to window:
        display_win = Rectangle(self._win, 420, 390, (920, 490))
        display_win.set_depth(30)
        self._win.add(display_win)
        display_win_text = Text(self._win, 'YOUR PROPERTIES', 18, (920, 315))
        display_win_text.set_depth(29)
        self._win.add(display_win_text)

        # lists all the coordinates that correspond to each space on the board,
        # keys in the dictionary are in accordance to the spot's number:
        self._locations = {1: (650, 650), 2: (580, 660), 3: (525, 660),
                           4: (465, 660), 5: (410, 660), 6: (350, 660),
                           7: (290, 660), 8: (235, 660), 9: (180, 660),
                           10: (120, 660), 11: (50, 685), 12: (40, 580),
                           13: (40, 525), 14: (40, 465), 15: (40, 410),
                           16: (40, 350), 17: (40, 290), 18: (40, 235),
                           19: (40, 180), 20: (40, 120), 21: (50, 50),
                           22: (120, 40), 23: (180, 40), 24: (235, 40),
                           25: (290, 40), 26: (350, 40), 27: (410, 40),
                           28: (465, 40), 29: (525, 40), 30: (580, 40),
                           31: (650, 50), 32: (660, 120), 33: (660, 180),
                           34: (660, 235), 35: (660, 290), 36: (660, 350),
                           37: (660, 410), 38: (660, 465), 39: (660, 525),
                           40: (660, 580), 41: (60, 640)}

        # loads a dictionary from the file 'dicts.json' - the dictionary
        # includes information about each spot (type of spot - deed, chance,
        # Go to Jail, etc; prices; rent; etc.), dictionary keys correspond to
        # the keys of _locations:
        with open('dicts.json', 'r') as infile:
            self._properties = json.load(infile)


class GamePieces(EventHandler):
    """This class creates the players' game tokens."""

    # the constructor for the GamePieces class:
    def __init__(self, win, game):

        # call the EventHandler parent class so that methods belonging to
        # that class are accessible:
        EventHandler.__init__(self)

        self._win = win
        self._game = game

        # creates dictionary containing information about each potential game
        # token (image location, width, and height):
        self._pieces = {'thimble': {'file': 'thimble.png', 'width': 30,
                                    'height': 40},
                        'wheelbarrow': {'file': 'wheelbarrow.png', 'width': 40,
                                        'height': 25},
                        'boot': {'file': 'boot.png', 'width': 40,
                                 'height': 40},
                        'boat': {'file': 'boat.png', 'width': 30,
                                 'height': 40},
                        'car': {'file': 'car.png', 'width': 40,
                                'height': 30},
                        'dog': {'file': 'dog.png', 'width': 40,
                                'height': 40},
                        'hat': {'file': 'hat.png', 'width': 40,
                                'height': 30},
                        'iron': {'file': 'iron.png', 'width': 40,
                                 'height': 35}}

    def display_pieces(self):
        """This function adds all the the potential game tokens to the
           window. * Only used in starting popup window as a way for
           players to choose tokens"""

        # creates each token image:
        self._thimble = Image(self._win, self._pieces['thimble']['file'],
                              self._pieces['thimble']['width'],
                              self._pieces['thimble']['height'], (450, 350))
        self._wheelbarrow = Image(self._win,
                                  self._pieces['wheelbarrow']['file'],
                                  self._pieces['wheelbarrow']['width'],
                                  self._pieces['wheelbarrow']['height'],
                                  (550, 350))
        self._boot = Image(self._win, self._pieces['boot']['file'],
                           self._pieces['boot']['width'],
                           self._pieces['boot']['height'], (650, 350))
        self._boat = Image(self._win, self._pieces['boat']['file'],
                           self._pieces['boat']['width'],
                           self._pieces['boat']['height'], (750, 350))
        self._car = Image(self._win, self._pieces['car']['file'],
                          self._pieces['car']['width'],
                          self._pieces['car']['height'], (450, 450))
        self._dog = Image(self._win, self._pieces['dog']['file'],
                          self._pieces['dog']['width'],
                          self._pieces['dog']['height'], (550, 450))
        self._hat = Image(self._win, self._pieces['hat']['file'],
                          self._pieces['hat']['width'],
                          self._pieces['hat']['height'], (650, 450))
        self._iron = Image(self._win, self._pieces['iron']['file'],
                           self._pieces['iron']['width'],
                           self._pieces['iron']['height'], (750, 450))

        # lists all the tokens:
        self._all_pieces = [self._thimble, self._wheelbarrow, self._boot,
                            self._boat, self._car, self._dog, self._hat,
                            self._iron]

        # adds each token to the window:
        for piece in self._all_pieces:
            self._win.add(piece)
            piece.set_depth(1)
            piece.add_handler(self)

    def remove_pieces(self):
        """This function removes all the potential game tokens from the
           window. * Only used in starting popup window as a way for
           players to choose tokens"""

        for piece in self._all_pieces:
            self._win.remove(piece)

    def handle_mouse_release(self, event):
        """This function handles the choice of a clicked token. Given the
           clicked token, the function adds the name of the token to the
           Game class's attribute _player_characters and changes the popup
           window to display the player's choice."""

        # gets location of the player's click:
        x = event.get_mouse_location()[0]
        y = event.get_mouse_location()[1]

        # based on the player's mouse location, a player's choice of token
        # is determined, added to Game._player_characters, and passed to
        # the popup window function PopUpWin.piece_picked()
        if 435 < x < 465 and 330 < y < 370:
            self._game._player_characters.append('thimble')
            self._game._start_win.piece_picked('thimble')
        if 530 < x < 570 and 338 < y < 362:
            self._game._player_characters.append('wheelbarrow')
            self._game._start_win.piece_picked('wheelbarrow')
        if 630 < x < 670 and 330 < y < 370:
            self._game._player_characters.append('boot')
            self._game._start_win.piece_picked('boot')
        if 735 < x < 765 and 330 < y < 370:
            self._game._player_characters.append('boat')
            self._game._start_win.piece_picked('boat')
        if 430 < x < 470 and 435 < y < 465:
            self._game._player_characters.append('car')
            self._game._start_win.piece_picked('car')
        if 530 < x < 570 and 430 < y < 470:
            self._game._player_characters.append('dog')
            self._game._start_win.piece_picked('dog')
        if 630 < x < 670 and 435 < y < 465:
            self._game._player_characters.append('hat')
            self._game._start_win.piece_picked('hat')
        if 730 < x < 770 and 430 < y < 470:
            self._game._player_characters.append('iron')
            self._game._start_win.piece_picked('iron')

    def start_piece(self, piece, player, board):
        """This function creates the game piece for the given player."""

        self._board = board

        # creates the image of the token:
        self._piece = Image(self._win, self._pieces[piece]['file'],
                            self._pieces[piece]['width'],
                            self._pieces[piece]['height'],
                            self._board._locations[player._piece_loc])
        self._piece.set_depth(9)

    def move_piece(self, player, advance, jail=False):
        """Given the player and the number of spaces the token will advance,
           this function moves the player's game token around the board."""

        self._advance = advance
        self._jail = jail

        # determines the spot the player will move to by adding the value of
        # the die roll to the player's current location:
        self._move_piece_to = player._piece_loc + self._advance

        # if the player moves all the way around the board (passes "GO"), $200
        # is added to their money - the new money value is displayed:
        if self._move_piece_to > 40:
            player._money += 200
            player.remove_money()
            player.display_money()

        # since there are only 40 spots on the board, keeps played on the board
        # by modding by 40:
        piece_loc = self._move_piece_to % 40
        if piece_loc == 0:
            piece_loc = 40

        # checks if player is required to "Go to Jail":
        if self._jail:
            # checks if player has a get out of "Jail Free" card:
            if player._jail_free:
                # adds popup window and calls the function
                # PopUpWin.jail_free_choice() - allows players to choose if
                # they would like to use their "Jail Free" card
                jail_free_win = PopUpWin(self._win, player, self._game)
                jail_free_win.jail_free_choice()
            else:
                # sends player to jail by moving them to the jail board spot,
                # setting the player's location to spot 11 ("Just Visiting")
                # because the player's next roll will move from that spot,
                # removing the dice with handlers and adding new dice that
                # don't have handlers, adds the popup window, and
                # calls the function PopUpWin.jail() - tells player that they
                # were thrown in jail
                player._player_piece.move_to(self._board._locations[41])
                player.set_piece_loc(11)
                self._game._die1.remove_die()
                self._game._die2.remove_die()
                self._game._die1.create_die()
                self._game._die2.create_die()
                jail_win = PopUpWin(self._win, player, self._game)
                jail_win.jail()
        else:
            # moves player along board by changing their piece location and
            # moving them to the window coordinates for the given spot listed
            # in Board._locations:
            player.set_piece_loc(piece_loc)
            player._player_piece.move_to(self._board._locations
                                         [player._piece_loc])


class Player(object):
    """This class creates all the attributes specific to individual players
       of Monopoly. It allows for changes made to a player's token location
       and money value to be updated at any point of the game."""

    # the constructor of the Player class:
    def __init__(self, win, game_pieces, piece, board, idx):

        self._win = win
        self._game_pieces = game_pieces
        self._piece = piece
        self._board = board
        self._idnum = idx

        # initializes the player's token location, money, "Jail Free" card
        # possession, owned properties (their board locations), dictionary of
        # owned properties in each set, and dictionary of owned properties to
        # be displayed:
        self._piece_loc = 1
        self._money = 1500
        self._jail_free = False
        self._properties = []
        self._prop_kinds = {'brown': {'have': 0, 'max': 2},
                            'lt blue': {'have': 0, 'max': 3},
                            'pink': {'have': 0, 'max': 3},
                            'orange': {'have': 0, 'max': 3},
                            'red': {'have': 0, 'max': 3},
                            'yellow': {'have': 0, 'max': 3},
                            'green': {'have': 0, 'max': 3},
                            'dk blue': {'have': 0, 'max': 2},
                            'railroad': {'have': 0, 'max': 5},
                            'utility': {'have': 0, 'max': 5}}
        self._prop_display = {}

        # uses the GamePieces.start_piece() funtion to create the player's
        # game piece given their choice of token, assigns GamePieces._piece
        # (the GraphicalObject, or image, of the token) so the player specific
        # token can be moved around the board, and adds the token to
        # the window:
        self._game_pieces.start_piece(self._piece, self, self._board)
        self._player_piece = self._game_pieces._piece
        self._win.add(self._player_piece)

    def set_piece_loc(self, piece_loc):
        """This function allows for the player's token location to be redefined
           at any point of the game."""

        self._piece_loc = piece_loc

    # the functions Player.display_money() and Player.remove_money() are often
    # used together in this game in order to display a player's current money
    # value after a property is bought, taxes are paid, etc.:
    def display_money(self):
        """This function allows for the player's money value to be displayed at
           any point of the game."""

        # creates the money text and adds it to the window:
        self._money_text = Text(self._win, str(self._money), 18, (1075, 205))
        self._money_text.set_depth(1)
        self._win.add(self._money_text)

    def remove_money(self):
        """This function allows for the player's money value to be removed from
           the window at any point of the game."""

        self._win.remove(self._money_text)

    def display_player_title(self):
        """This function displays whose turn it is."""

        # creates the turn title text and adds it to the window:
        self._player_title = Text(self._win, 'PLAYER ' + str(self._idnum) +
                                  "'S TURN", 25, (900, 20))
        self._win.add(self._player_title)

    def remove_player_title(self):
        """This function removes the text that states whose turn it is."""

        self._win.remove(self._player_title)

    def display_properties(self):
        """This function displays all the properties that a player owns."""

        # checks if the player owns any properties:
        if len(self._prop_display.keys()) != 0:
            # for each property that is owned, the corresponding deed card is
            # displayed:
            for i in range(1, len(self._properties) + 1):
                self._win.add(self._prop_display[i])

    def remove_properties(self):
        """This function removes all the properties that a player owns from
           the window."""

        # checks if the player owns any properties:
        if len(self._prop_display.keys()) != 0:
            # for each owned property, the corresponding deed card is removed
            # from the window:
            for i in range(1, len(self._properties) + 1):
                self._win.remove(self._prop_display[i])


class Die(object):
    """This class creates a die."""

    def __init__(self, win, center):

        self._win = win
        self._center = center

        # creates a dicitionary of the pip centers given the center of the die,
        # dictionary keys correspond to the number of pips on the die face:
        self._pip_centers = {1: [self._center],
                             2: [(self._center[0] - 14, self._center[1] + 14),
                                 (self._center[0] + 14, self._center[1] - 14)],
                             3: [self._center,
                                 (self._center[0] - 14, self._center[1] + 14),
                                 (self._center[0] + 14, self._center[1] - 14)],
                             4: [(self._center[0] - 14, self._center[1] - 14),
                                 (self._center[0] - 14, self._center[1] + 14),
                                 (self._center[0] + 14, self._center[1] - 14),
                                 (self._center[0] + 14, self._center[1] + 14)],
                             5: [self._center,
                                 (self._center[0] - 14, self._center[1] - 14),
                                 (self._center[0] - 14, self._center[1] + 14),
                                 (self._center[0] + 14, self._center[1] - 14),
                                 (self._center[0] + 14, self._center[1] + 14)],
                             6: [(self._center[0] - 10, self._center[1] - 14),
                                 (self._center[0] - 10, self._center[1] + 14),
                                 (self._center[0] + 10, self._center[1] - 14),
                                 (self._center[0] + 10, self._center[1] + 14),
                                 (self._center[0], self._center[1] - 14),
                                 (self._center[0], self._center[1] + 14)]}

        # initializes _pip_center attribute as 1 pip:
        self._pip_center = self._pip_centers[1]

        # creates the die body and pips and adds the pips to the window:
        self.create_die()
        self.create_pips()

    # because a handler is added to the die body, the functions
    # Die.create_die() and Die.remove_die() are often used together throughout
    # the game in order to make sure the player cannot roll after they have
    # completed their rolls for the turn - once the player cannot roll, the die
    # with the handler is removed and a new die (that cannot be rolled) is
    # added to preserve the aesthetic:
    def create_die(self):
        """This function creates the die body and adds it to the window."""

        self._die = Square(self._win, 40, self._center)
        self._die.set_fill_color('white')
        self._die.set_border_color('black')
        self._die.set_depth(2)
        self._win.add(self._die)

    def remove_die(self):
        """This function removes the die body from the window."""

        self._win.remove(self._die)

    def create_pips(self):
        """This function creates the pips for the die."""

        # initializes the list of pips created:
        self._pips = []
        # creates a pip for each center in _pip_center:
        for center in self._pip_center:
            self._pip = Circle(self._win, 3, center)
            self._pip.set_fill_color('black')
            self._pip.set_border_color('black')
            self._pip.set_depth(1)
            self._pips.append(self._pip)

        # adds pips to the window:
        for pip in self._pips:
            self._win.add(pip)

    def remove_pips_from_win(self):
        """This function removes the pips from the window."""

        for pip in self._pips:
            self._win.remove(pip)

    def add_handler(self, handler):
        """This function adds the handler to the die."""

        self._die.add_handler(handler)


class DieHandler(EventHandler):
    """This class is the handler for the Die class. It allows for each die to
       be rolled together and calls for the piece to be moved and the action
       for the spot the player landed on to be performed."""

    # the constructor for the DieHandler class
    def __init__(self, win, die1, die2, game_pieces, spots, player, game,
                 roll_doubles):

        # calls the EventHandler parent class so that methods belonging to
        # that class are accessible:
        EventHandler.__init__(self)

        self._win = win
        self._die1 = die1
        self._die2 = die2
        self._game_pieces = game_pieces
        self._spots = spots
        self._player = player
        self._game = game
        self._roll_doubles = roll_doubles

        # initiates the die roll as not rigged, adds the secret button and its
        # handler:
        self._rigged = False
        self._secret_button = SecretButton(self._win)
        self._secret_button.start_secret_button(self)

    def set_die_roll(self, die1, die2):
        """This sets the die roll based on the inputted value."""

        self._die1_roll = die1
        self._die2_roll = die2
        self._rigged = True

    def handle_mouse_enter(self):
        """This function changes the button's body color to red when the player
           puts the mouse on the button."""

        self._die1._die.set_border_color('red')
        self._die2._die.set_border_color('red')

    def handle_mouse_leave(self):
        """This function changes the button's body color to black when the
           player take the mouse off the button."""

        self._die1._die.set_border_color('black')
        self._die2._die.set_border_color('black')

    def handle_mouse_release(self):
        """This function handles what happends when the die is clicked."""

        # checks if game is rigged:
        if self._rigged is False:

            # rolls each dice by finding a random number between 1 and 6:
            self._die1_roll = random.randint(1, 6)
            self._die2_roll = random.randint(1, 6)

        self._rigged = False

        # changes each die's _pip_center based on the die roll:
        self._die1._pip_center = self._die1._pip_centers[self._die1_roll]
        self._die2._pip_center = self._die2._pip_centers[self._die2_roll]

        # takes pips off the window and adds new pips from the latest die roll:
        self._die1.remove_pips_from_win()
        self._die2.remove_pips_from_win()
        self._die1.create_pips()
        self._die2.create_pips()

        # determines the number of spaces the player will advance based on
        # their roll:
        self._advance = self._die1_roll + self._die2_roll

        # checks if the player rolled doubles:
        if self._die1_roll != self._die2_roll:
            # if player doesn't roll doubles, the die body is removed and added
            # again:
            self._die1.remove_die()
            self._die2.remove_die()
            self._die1.create_die()
            self._die2.create_die()
            self._secret_button.end_secret_button()
            # calls the function GamePieces.move_piece() to move player token:
            self._game_pieces.move_piece(self._player, self._advance)
            # calls the function Spots.spot_action() to perform the action
            # given to the spot that was landed on - the variable same_roll is
            # False:
            self._spots.spot_action(False, self._advance)

        elif self._die1_roll == self._die2_roll and self._roll_doubles < 2:
            # if the player rolls doubles and has gotten doubles less than two
            # times in succession, increases the _roll_doubles count by 1:
            self._roll_doubles += 1
            # calls the function GamePieces.move_piece() to move player token:
            self._game_pieces.move_piece(self._player, self._advance)
            # calls the function Spots.spot_action() to perform the action
            # given to the spot that was landed on - the variable same_roll is
            # True:
            self._spots.spot_action(True, self._advance)

        elif self._die1_roll == self._die2_roll and self._roll_doubles == 2:
            # if the player rolls doubles and has rolled doubles twice before
            # in succession, the die body is removed and added again:
            self._die1.remove_die()
            self._die2.remove_die()
            self._die1.create_die()
            self._die2.create_die()
            self._secret_button.end_secret_button()
            # calls the function GamePieces.move_piece() - GamePieces._jail
            # is True:
            self._game_pieces.move_piece(self._player, self._advance, True)


class SecretButton(EventHandler):
    """This class creates a secret button that allows for the player to
       secretly input the value they want the die to show. (To cheat.)"""

    # constructor for the SecretButton class:
    def __init__(self, win):

        EventHandler.__init__(self)
        self._win = win

        # creates the secret button off screen:
        self._secret_button = Rectangle(self._win, 1, 1, (1100, 0))

    def start_secret_button(self, diehandler):
        """This function adds the handler to the secret button."""

        self._win.add(self._secret_button)
        self._secret_button.add_handler(self)

        self._diehandler = diehandler

    def end_secret_button(self):
        """This function removes the secret button."""

        self._win.remove(self._secret_button)

    def handle_key_release(self, event):
        """This function determines what key was pressed and sends the
           information to the DieHandler class."""

        # determines what key was pressed:
        key = event.get_key()

        # based on the key pressed, tells the DieHandler class what roll
        # the player wants to be displayed:
        if key == '2':
            self._diehandler.set_die_roll(1, 1)
        elif key == '3':
            self._diehandler.set_die_roll(1, 2)
        elif key == '4':
            self._diehandler.set_die_roll(2, 2)
        elif key == '5':
            self._diehandler.set_die_roll(2, 3)
        elif key == '6':
            self._diehandler.set_die_roll(3, 3)
        elif key == '7':
            self._diehandler.set_die_roll(3, 4)
        elif key == '8':
            self._diehandler.set_die_roll(4, 4)
        elif key == '9':
            self._diehandler.set_die_roll(4, 5)
        elif key == '0':
            self._diehandler.set_die_roll(5, 5)
        elif key == '1':
            self._diehandler.set_die_roll(5, 6)
        elif key == 't':
            self._diehandler.set_die_roll(6, 6)


class Spots(object):
    """This class determines the type of spot that was landed on and performs
       the actions specific to that spot."""

    # the constructor for the Spots class:
    def __init__(self, win, player, buy_prop, board, game):

        self._win = win
        self._player = player
        self._buy_prop = buy_prop
        self._properties = board._properties
        self._game = game

    def set_ownership(self, piece_loc, player_idnum):
        """This function sets the owner of a property given the property's spot
           number and the player's id number."""

        self._properties[str(piece_loc)]['owned'] = player_idnum

    def get_ownership(self, piece_loc):
        """This function returns the owner of a specific property."""

        return self._properties[str(piece_loc)]['owned']

    def spot_action(self, same_roll, advance=0):
        """This function determines the type of spot the player landed on and
           performs the actions that go along with the spot."""

        # determines the type of spot:
        type_of_spot = self._properties[str(self._player._piece_loc)]['type']

        # checks if the spot is a 'deed', 'utility', or 'railroad':
        if type_of_spot == 'deed' or (type_of_spot == 'utility' or
                                      type_of_spot == 'railroad'):
            # adds image of the property deed to the window:
            self._prop = Image(self._win,
                               self._properties[str(self._player._piece_loc)]
                               ['image info'], 160, 200, (800, 170))
            self._prop.set_depth(1)
            self._win.add(self._prop)

            # checks if the property is not yet owned:
            if self.get_ownership(self._player._piece_loc) == 0:
                # subtracts the price of the property from the player's money
                self._player._money -= (self._properties
                                        [str(self._player._piece_loc)]
                                        ['price'])

                # checks if player has enough money to buy:
                if self._player._money > 0:
                    # calls the function BuyProperty.buy() so that the player
                    # can choose whether or not to buy:
                    self._buy_prop.buy(self._properties, self._prop, same_roll)

                else:
                    # adds prices of property back to player's money:
                    self._player._money += (self._properties
                                            [str(self._player._piece_loc)]
                                            ['price'])
                    # removes the deed image from the window:
                    self._win.remove(self._prop)
                    # calls the function BuyProperty.cant_buy() so that the
                    # player is told they don't have enough money to buy:
                    self._buy_prop.cant_buy(self._properties, same_roll)

            # checks if the property is owned and it is not owned by the
            # current player:
            elif (self.get_ownership(self._player._piece_loc) != 0 and
                  self.get_ownership(self._player._piece_loc) !=
                  self._player._idnum):
                # removes the deed image from the window:
                self._win.remove(self._prop)

                # checks if the type of spot is a 'deed':
                if type_of_spot == 'deed':
                    # determines the amount of rent the player must pay:
                    money_lost = (self._properties
                                  [str(self._player._piece_loc)]['rent']['0'])

                    if self._properties[str(self._player._piece_loc)]['houses'] > 0:

                        money_lost = (self._properties
                                      [str(self._player._piece_loc)]
                                      ['rent']
                                      [str(self._properties
                                           [str(self._player._piece_loc)]
                                           ['houses'])])

                    # checks if other player owns all of the properties in the
                    # set:
                    elif ((self._game._other._prop_kinds
                         [self._properties[str(self._player._piece_loc)]
                          ['set']]['have']) ==
                        (self._game._other._prop_kinds
                         [self._properties[str(self._player._piece_loc)]
                          ['set']]['max'])):
                        # doubles the money_lost
                        money_lost = money_lost * 2

                    # subtracts money_lost from the player's money:
                    self._player._money -= money_lost

                    # checks if the player doesn't have enough money to
                    # pay rent:
                    if self._player._money < 0:
                        # calls the function BuyProperty.bankrupcy() so that
                        # the player can declare bankrupcy:
                        self._buy_prop.bankrupcy()

                    else:
                        # calls the function BuyProperty.pay() so that the
                        # player can pay the rent:
                        self._buy_prop.pay(self._properties, same_roll,
                                           money_lost)

                # checks if the type of spot is a 'utility':
                elif type_of_spot == 'utility':
                    # determines the amount of rent the player must pay:
                    money_lost = (self._properties
                                  [str(self._player._piece_loc)]['rent']
                                  [str(self._game._other._prop_kinds
                                       ['utility']['have'])] * advance)
                    # subtracts money_lost from the player's money:
                    self._player._money -= money_lost

                    # checks if the player doesn't have enough money to
                    # pay rent:
                    if self._player._money < 0:
                        # calls the function BuyProperty.bankrupcy() so that
                        # the player can declare bankrupcy:
                        self._buy_prop.bankrupcy()

                    else:
                        # calls the function BuyProperty.pay() so that the
                        # player can pay the rent:
                        self._buy_prop.pay(self._properties, same_roll,
                                           money_lost, advance)

                # chekcs if the type of spot is a 'railroad':
                elif type_of_spot == 'railroad':
                    # determines the amount of rent the player must pay:
                    money_lost = (self._properties
                                  [str(self._player._piece_loc)]['rent']
                                  [str(self._game._other._prop_kinds
                                       ['railroad']['have'])])
                    # subtracts money_lost from the player's money:
                    self._player._money -= money_lost

                    # checks if the player doesn't have enough money to
                    # pay rent:
                    if self._player._money < 0:
                        # calls the function BuyProperty.bankrupcy() so that
                        # the player can declare bankrupcy:
                        self._buy_prop.bankrupcy()

                    else:
                        # calls the function BuyProperty.pay() so that the
                        # player can pay the rent:
                        self._buy_prop.pay(self._properties, same_roll,
                                           money_lost)

            # checks if the player already owns the property:
            elif (self.get_ownership(self._player._piece_loc) ==
                  self._player._idnum):
                # removes the property deed from the window:
                self._win.remove(self._prop)
                # calls the function BuyProperty.already_own() so that the
                # player is notified that they already own the property:
                self._buy_prop.already_own(same_roll)

        # checks if the type of spot is a 'tax':
        elif type_of_spot == 'tax':
            # checks if the name of the property is "Income Tax":
            if (self._properties[str(self._player._piece_loc)]
                    ['name']) == 'Income Tax':
                # calls the function BuyProperty.income_tax() so that the
                # player can choose which payment to make:
                self._buy_prop.income_tax(same_roll)

            # checks if the name of the property is "Luxury Tax":
            elif (self._properties
                  [str(self._player._piece_loc)]['name']) == 'Luxury Tax':
                # subtracts the luxury tax payment from player's money:
                self._player._money -= 200

                # checks if the player doesn't have enough money to
                # pay the tax:
                if self._player._money < 0:
                    # calls the function BuyProperty.bankrupcy() so that
                    # the player can declare bankrupcy:
                    self._buy_prop.bankrupcy()

                else:
                    # adds and removes the player's money from the window to
                    # display the most current values:
                    self._player.remove_money()
                    self._player.display_money()
                    # calls the function BuyProperty.luxury_tax() so that the
                    # player is notified they played a luxury tax:
                    self._buy_prop.luxury_tax(same_roll)

        # checks if the type of spot is "0" or "collect":
        elif type_of_spot == '0' or type_of_spot == 'collect':
            # calls the function BuyProperty.safe() so that the player is
            # notified they landed on a safe spot:
            self._buy_prop.safe(same_roll)

        # checks if the type of spot is "jail":
        elif type_of_spot == 'jail':
            # calls the function GamePieces.move_piece() to move the player's
            # token to jail:
            self._game._game_pieces.move_piece(self._player, 0, True)

        # checks if the type of spot is "card":
        elif type_of_spot == 'card':
            # checks if the name of the property is "Chance":
            if (self._properties[str(self._player._piece_loc)]
                    ['name']) == 'Chance':
                # calls the function Cards.chance() so that a chance card will
                # be picked:
                self._game._cards.chance(self, same_roll)

            # checks if the name of the property is "Community Chest":
            elif (self._properties[str(self._player._piece_loc)]
                  ['name']) == 'Community Chest':
                # calls the function Cards.communtiy() so that a community
                # chest card will be picked:
                self._game._cards.community(self, same_roll)


class BuyProperty(object):
    """This class contains functions that correspond to the actions landing
       on different spots would cause."""

    # the constructor for the BuyProperty class:
    def __init__(self, win, player, other, game):

        self._win = win
        self._player = player
        self._other = other
        self._game = game

    def buy(self, properties, prop, same_roll):
        """This function allows the player to choose whether or not to buy
           a property."""

        # adds a buy and pass button to window and adds their handlers:
        buy_button = Button(self._win, 70, 40, (935, 90), 'green', 'BUY', 18,
                            'buy')
        pass_button = Button(self._win, 70, 40, (935, 140), 'yellow', 'PASS',
                             18, 'pass')
        buy_button.add_handler(self._player, self._other, properties,
                               self._game, self, same_roll, prop, pass_button)
        pass_button.add_handler(self._player, self._other, properties,
                                self._game, self, same_roll, prop, buy_button)

        # calls the function info_window():
        self.info_window(self._player, properties)

    def info_window(self, player, properties):
        """This function creates an info window where addition information
           about the property is displayed."""

        # adds the box that contains the information:
        self._info_win = Rectangle(self._win, 70, 100, (935, 220))
        self._info_win.set_depth(2)
        self._win.add(self._info_win)
        # adds the word "COST" to the box:
        self._price_word = Text(self._win, 'COST:', 10, (922, 178))
        self._price_word.set_depth(1)
        self._win.add(self._price_word)
        # adds the price of the property to the box:
        self._price_info = Text(self._win, '$' +
                                str(properties[str(player._piece_loc)]
                                    ['price']), 12, (935, 193))
        self._price_info.set_depth(1)
        self._win.add(self._price_info)
        # adds the words "NUMBER OWNED IN SET" to the box:
        self._monop_words1 = Text(self._win, 'NUMBER', 10, (931, 210))
        self._monop_words1.set_depth(1)
        self._win.add(self._monop_words1)
        self._monop_words2 = Text(self._win, 'OWNED', 10, (928, 225))
        self._monop_words2.set_depth(1)
        self._win.add(self._monop_words2)
        self._monop_words3 = Text(self._win, 'IN SET:', 10, (927, 240))
        self._monop_words3.set_depth(1)
        self._win.add(self._monop_words3)
        # adds the number of properties the player owns in the set to
        # the box:
        self._monop_info = Text(self._win, str(player._prop_kinds
                                               [properties
                                                [str(player._piece_loc)]
                                                ['set']]['have']),
                                16, (935, 258))
        self._monop_info.set_depth(1)
        self._win.add(self._monop_info)

    def remove_info_window(self):
        """This function removes everything in the info window from the
           window."""

        self._win.remove(self._info_win)
        self._win.remove(self._price_word)
        self._win.remove(self._price_info)
        self._win.remove(self._monop_words1)
        self._win.remove(self._monop_words2)
        self._win.remove(self._monop_words3)
        self._win.remove(self._monop_info)

    def pay(self, properties, same_roll, money_lost, advance=0):
        """This function creates a popup window that tells the player they
           paid rent."""

        # updates the player's money displayed on the window:
        self._player.remove_money()
        self._player.display_money()
        # adds a popup window describing the rent payed:
        pay_win = PopUpWin(self._win, self._player, self._game)
        pay_win.pay(properties, same_roll, money_lost, advance)

    def cant_buy(self, properties, same_roll):
        """This function creates a popup window that tells the player they
           can't buy the property."""

        cant_win = PopUpWin(self._win, self._player, self._game)
        cant_win.cant_buy(same_roll, properties)

    def income_tax(self, same_roll):
        """This function creates a popup window where the player can
           choose the tax they want to pay."""

        income_win = PopUpWin(self._win, self._player, self._game)
        income_win.tax_choice(same_roll)

    def luxury_tax(self, same_roll):
        """This function creates a popup window where the player can
           see that they payed the luxury tax."""

        luxury_win = PopUpWin(self._win, self._player, self._game)
        luxury_win.pay_tax(same_roll)

    def already_own(self, same_roll):
        """This function creates a popup window that tells the player
           they already own the property."""

        owned_win = PopUpWin(self._win, self._player, self._game)
        owned_win.player_owns(same_roll)

    def safe(self, same_roll):
        """This function creates a popup window that tells the player
           they landed on a safe spot."""

        safe_win = PopUpWin(self._win, self._player, self._game)
        safe_win.safe(same_roll)

    def bankrupcy(self):
        """This function creates a popup window that allows the player to
           declare bankrupcy."""

        bankrupcy_win = PopUpWin(self._win, self._player, self._game)
        bankrupcy_win.bankrupcy()


class Cards(object):
    """This class controls the actions for the Chance and Community Chest
       cards."""

    # the constructor for the Cards class:
    def __init__(self, win, player, other, board, game):

        self._win = win
        self._player = player
        self._other = other
        self._board = board
        self._game = game

        # lists all the possible Chance cards that could be picked:
        self._chance_cards = ['Go', 'Ill Ave', 'St Char Plc', 'Util', 'Rail',
                              '$50 Div', 'Jail Free', 'Back 3', 'Go Jail',
                              'Poor Tax', 'Read Rail', 'Boardwalk',
                              'Chairman', 'Loan Matures']

        # lists all the possible Community Chest cards that could be picked:
        self._comm_cards = ['Go', 'Bank Error', 'Doc Fee',
                            'Jail Free', 'Go Jail', 'Opera', 'Holiday',
                            'Income Refund', 'Life Insur', 'Hosp Fee',
                            'Sch Fee', 'Cons Fee', 'Beauty', 'Inherit']

    def chance(self, spots, same_roll):
        """This function controls the actions for the Chance cards."""

        self._spots = spots

        # picks a random card:
        card = random.choice(self._chance_cards)
        # creates the popup window:
        pop_win = PopUpWin(self._win, self._player, self._game)

        # checks the type of the card:
        if card == 'Go':
            # moves the player's token to the "GO" spot and sets its location
            # to that spot:
            self._player._player_piece.move_to(self._board._locations[1])
            self._player.set_piece_loc(1)
            # adds $200 to the player's money and updates the money on the
            # window:
            self._player._money += 200
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.chance():
            pop_win.chance('Go', same_roll)

        elif card == 'Ill Ave':
            # checks if the player will pass "Go":
            if 25 <= self._player._piece_loc <= 40:
                # adds $200 to the player's money and updates the money on the
                # window:
                self._player._money += 200
                self._player.remove_money()
                self._player.display_money()
            # moves the player's token to the "Illinois Ave." spot and sets its
            # location to that spot:
            self._player._player_piece.move_to(self._board._locations[25])
            self._player.set_piece_loc(25)
            # calls the function PopUpWin.chance():
            pop_win.chance('Ill Ave', same_roll, self._spots)

        elif card == 'St Char Plc':
            # checks if the player will pass "Go":
            if 12 <= self._player._piece_loc <= 40:
                # adds $200 to the player's money and updates the money on the
                # window:
                self._player._money += 200
                self._player.remove_money()
                self._player.display_money()
            # moves the player's token to the "St. Charles Place" spot and sets
            # its location to that spot:
            self._player._player_piece.move_to(self._board._locations[12])
            self._player.set_piece_loc(12)
            # calls the function PopUpWin.chance():
            pop_win.chance('St Char Plc', same_roll, self._spots)

        elif card == 'Util':
            # checks if the player will pass "Go":
            if 29 <= self._player._piece_loc <= 40:
                # adds $200 to the player's money and updates the money on the
                # window:
                self._player._money += 200
                self._player.remove_money()
                self._player.display_money()
            # determines what the next utility spot is, moves the player's
            # token to that utility, and sets its location to that spot:
            if self._player._piece_loc < 13 or self._player._piece_loc >= 29:
                self._player._player_piece.move_to(self._board._locations[13])
                self._player.set_piece_loc(13)
            elif 13 <= self._player._piece_loc < 29:
                self._player._player_piece.move_to(self._board._locations[29])
                self._player.set_piece_loc(29)
            # calls the function PopUpWin.chance():
            pop_win.chance('Util', same_roll, self._spots)

        elif card == 'Rail':
            # checks if the player will pass "Go":
            if 36 <= self._player._piece_loc <= 40:
                # adds $200 to the player's money and updates the money on the
                # window:
                self._player._money += 200
                self._player.remove_money()
                self._player.display_money()
            # determines what the next railroad spot is, moves the player's
            # token to that railroad, and sets its location to that spot:
            if self._player._piece_loc < 6 or self._player._piece_loc >= 36:
                self._player._player_piece.move_to(self._board._locations[6])
                self._player.set_piece_loc(6)
            elif 6 <= self._player._piece_loc < 16:
                self._player._player_piece.move_to(self._board._locations[16])
                self._player.set_piece_loc(16)
            elif 16 <= self._player._piece_loc < 26:
                self._player._player_piece.move_to(self._board._locations[26])
                self._player.set_piece_loc(26)
            elif 26 <= self._player._piece_loc < 36:
                self._player._player_piece.move_to(self._board._locations[36])
                self._player.set_piece_loc(36)
            # calls the function PopUpWin.chance():
            pop_win.chance('Rail', same_roll, self._spots)

        elif card == '$50 Div':
            # adds $50 to the player's money and updates the money on the
            # window:
            self._player._money += 50
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.chance():
            pop_win.chance('$50 Div', same_roll)

        elif card == 'Jail Free':
            # updates the player's "Jail Free" status - the player now has the
            # possiblity to get out of going to jail:
            self._player._jail_free = True
            # calls the function PopUpWin.chance():
            pop_win.chance('Jail Free', same_roll)

        elif card == 'Back 3':
            # determines the new location of the player, moves the player's
            # token to the spot, and sets the player's new location to that
            # spot:
            new_loc = self._player._piece_loc - 3
            self._player._player_piece.move_to(self._board._locations[new_loc])
            self._player.set_piece_loc(new_loc)
            # calls the function PopUpWin.chance():
            pop_win.chance('Back 3', same_roll, self._spots)

        elif card == 'Go Jail':
            # calls the function PopUpWin.chance():
            pop_win.chance('Go Jail')

        elif card == 'Poor Tax':
            # subtracts $15 from the player's money and updates the money on
            # the window:
            self._player._money -= 15
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.chance():
            pop_win.chance('Poor Tax', same_roll)

        elif card == 'Read Rail':
            # checks if the player will pass "Go":
            if 6 <= self._player._piece_loc <= 40:
                # adds $200 to the player's money and updates the money on the
                # window:
                self._player._money += 200
                self._player.remove_money()
                self._player.display_money()
            # moves the player's token to the "Reading Railroad" spot and sets
            # the player's new location to that spot:
            self._player._player_piece.move_to(self._board._locations[6])
            self._player.set_piece_loc(6)
            # calls the function PopUpWin.chance():
            pop_win.chance('Read Rail', same_roll, self._spots)

        elif card == 'Boardwalk':
            # checks if the player will pass "Go":
            if self._player._piece_loc == 40:
                # adds $200 to the player's money and updates the money on the
                # window:
                self._player._money += 200
                self._player.remove_money()
                self._player.display_money()
            # moves the player's token to the "Boardwalk" spot and sets
            # the player's new location to that spot:
            self._player._player_piece.move_to(self._board._locations[40])
            self._player.set_piece_loc(40)
            # calls the function PopUpWin.chance():
            pop_win.chance('Boardwalk', same_roll, self._spots)

        elif card == 'Chairman':
            # subtracts $50 from the player's money and updates the money on
            # on the window:
            self._player._money -= 50
            self._player.remove_money()
            self._player.display_money()
            # adds $50 to the other player's money:
            self._other._money += 50
            # calls the function PopUpWin.chance():
            pop_win.chance('Chairman', same_roll)

        elif card == 'Loan Matures':
            # adds $150 to the player's money and updates the money on the
            # window:
            self._player._money += 150
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.chance():
            pop_win.chance('Loan Matures', same_roll)

    def community(self, spots, same_roll):
        """This function controls the actions for the Community Chest cards."""

        self._spots = spots

        # picks a random card:
        card = random.choice(self._comm_cards)
        # creates the popup window:
        pop_win = PopUpWin(self._win, self._player, self._game)

        # checks the type of card:
        if card == 'Go':
            # moves the player's token to the "GO" spot and sets the player's
            # new location to that spot:
            self._player._player_piece.move_to(self._board._locations[1])
            self._player.set_piece_loc(1)
            # adds $200 to the player's money and updates the money on the
            # window:
            self._player._money += 200
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.community():
            pop_win.community('Go', same_roll)

        elif card == 'Bank Error':
            # adds $200 to the player's money and updates the money on the
            # window:
            self._player._money += 200
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.community():
            pop_win.community('Bank Error', same_roll)

        elif card == 'Doc Fee':
            # subtracts $50 from the player's money and updates the money on
            # on the window:
            self._player._money -= 50
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.community():
            pop_win.community('Doc Fee', same_roll)

        elif card == 'Jail Free':
            # updates the player's "Jail Free" status - the player now has the
            # possiblity to get out of going to jail:
            self._player._jail_free = True
            # calls the function PopUpWin.community():
            pop_win.community('Jail Free', same_roll)

        elif card == 'Go Jail':
            # calls the function PopUpWin.community():
            pop_win.community('Go Jail')

        elif card == 'Opera':
            # adds $50 to the player's money and updates the money on the
            # window:
            self._player._money += 50
            self._player.remove_money()
            self._player.display_money()
            # subtracts $50 from the other player's money:
            self._other._money -= 50
            # calls the function PopUpWin.community():
            pop_win.community('Opera', same_roll)

        elif card == 'Holiday':
            # adds $100 to the player's money and updates the money on the
            # window:
            self._player._money += 100
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.community():
            pop_win.community('Holiday', same_roll)

        elif card == 'Income Refund':
            # adds $20 to the player's money and updates the money on the
            # window:
            self._player._money += 20
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.community():
            pop_win.community('Income Refund', same_roll)

        elif card == 'Life Insur':
            # adds $100 to the player's money and updates the money on the
            # window:
            self._player._money += 100
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.community():
            pop_win.community('Life Insur', same_roll)

        elif card == 'Hosp Fee':
            # subtracts $100 from the player's money and updates the money on
            # on the window:
            self._player._money -= 100
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.community():
            pop_win.community('Hosp Fee', same_roll)

        elif card == 'Sch Fee':
            # subtracts $150 from the player's money and updates the money on
            # on the window:
            self._player._money -= 150
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.community():
            pop_win.community('Sch Fee', same_roll)

        elif card == 'Cons Fee':
            # adds $25 to the player's money and updates the money on the
            # window:
            self._player._money += 25
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.community():
            pop_win.community('Cons Fee', same_roll)

        elif card == 'Beauty':
            # adds $10 to the player's money and updates the money on the
            # window:
            self._player._money += 10
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.community():
            pop_win.community('Beauty', same_roll)

        elif card == 'Inherit':
            # adds $100 to the player's money and updates the money on the
            # window:
            self._player._money += 100
            self._player.remove_money()
            self._player.display_money()
            # calls the function PopUpWin.community():
            pop_win.community('Inherit', same_roll)

class Houses(object):
    """This class allows for houses to be added to properties on the board. It
       determines the locations of the buttons and house spots that go along
       with this function."""

    def __init__(self, win, game):

        self._win = win
        self._game = game

        # creates a dictionary of the house button locations for each set:
        self._house_add_locs = {'brown': [(580, 600), (465, 600)],
                                'lt blue': [(290, 600), (180, 600),
                                            (120, 600)],
                                'pink': [(100, 580), (100, 465), (100, 410)],
                                'orange': [(100, 290), (100, 180), (100, 120)],
                                'red': [(120, 100), (235, 100), (290, 100)],
                                'yellow': [(410, 100), (465, 100), (580, 100)],
                                'green': [(600, 120), (600, 180), (600, 290)],
                                'dk blue': [(600, 465), (600, 580)]}

        # creates a dictionary of the locations of the houses that correspond
        # to each house button:
        self._house_locs = {'(580, 600)': {'spots': [(595, 620), (580, 620),
                                                     (565, 620)], 'prop': 2},
                            '(465, 600)': {'spots': [(480, 620), (465, 620),
                                                     (450, 620)], 'prop': 4},
                            '(290, 600)': {'spots': [(305, 620), (290, 620),
                                                     (275, 620)], 'prop': 7},
                            '(180, 600)': {'spots': [(195, 620), (180, 620),
                                                     (165, 620)], 'prop': 9},
                            '(120, 600)': {'spots': [(135, 620), (120, 620),
                                                     (105, 620)], 'prop': 10},
                            '(100, 580)': {'spots': [(80, 595), (80, 580),
                                                     (80, 565)], 'prop': 12},
                            '(100, 465)': {'spots': [(80, 480), (80, 465),
                                                     (80, 450)], 'prop': 14},
                            '(100, 410)': {'spots': [(80, 425), (80, 410),
                                                     (80, 395)], 'prop': 15},
                            '(100, 290)': {'spots': [(80, 305), (80, 290),
                                                     (80, 275)], 'prop': 17},
                            '(100, 180)': {'spots': [(80, 195), (80, 180),
                                                     (80, 165)], 'prop': 19},
                            '(100, 120)': {'spots': [(80, 135), (80, 120),
                                                     (80, 105)], 'prop': 20},
                            '(120, 100)': {'spots': [(105, 80), (120, 80),
                                                     (135, 80)], 'prop': 22},
                            '(235, 100)': {'spots': [(220, 80), (235, 80),
                                                     (250, 80)], 'prop': 24},
                            '(290, 100)': {'spots': [(275, 80), (290, 80),
                                                     (305, 80)], 'prop': 25},
                            '(410, 100)': {'spots': [(395, 80), (410, 80),
                                                     (425, 80)], 'prop': 27},
                            '(465, 100)': {'spots': [(450, 80), (465, 80),
                                                     (480, 80)], 'prop': 28},
                            '(580, 100)': {'spots': [(565, 80), (580, 80),
                                                     (595, 80)], 'prop': 30},
                            '(600, 120)': {'spots': [(620, 105), (620, 120),
                                                     (620, 135)], 'prop': 32},
                            '(600, 180)': {'spots': [(620, 165), (620, 180),
                                                     (620, 195)], 'prop': 33},
                            '(600, 290)': {'spots': [(620, 275), (620, 290),
                                                     (620, 305)], 'prop': 35},
                            '(600, 465)': {'spots': [(620, 450), (620, 465),
                                                     (620, 480)], 'prop': 38},
                            '(600, 580)': {'spots': [(620, 565), (620, 580),
                                                     (620, 595)], 'prop': 40}}

    def display_house_buttons(self, house_sets):
        """This function adds the buttons that allow the player to buy houses
           to the board."""

        # initializes a list of all the buttons:
        self._buttons = []

        # adds buttons for each property in the sets totally owned by the
        # player:
        for set_typ in house_sets:
            for center in self._house_add_locs[set_typ]:
                button = Button(self._win, 10, 10, center, 'yellow', '+', 5,
                                'house')
                button.add_handler(None, None, None, self._game, None, None,
                                   None, None, None)
                button._button.set_depth(9)
                button._button_text.set_depth(8)
                self._buttons.append(button)

    def remove_house_buttons(self):
        """This function removes all the buttons from the window."""

        # checks if there are any buttons to remove:
        if len(self._buttons) > 0:   
            for button in self._buttons:
                self._win.remove(button._button)
                self._win.remove(button._button_text)


class Button(EventHandler):
    """This class creates a button that perform different actions based on
       their type."""

    # the constructor for the Button class:
    def __init__(self, win, width, height, center, color, text, text_size,
                 typ):

        # calls the EventHandler parent class so that methods belonging to
        # that class are accessible:
        EventHandler.__init__(self)

        self._win = win
        self._width = width
        self._height = height
        self._center = center
        self._color = color
        self._text = text
        self._text_size = text_size
        self._type = typ

        # creates the body of the button and adds it to the window:
        self._button = Rectangle(self._win, self._width, self._height,
                                 self._center)
        self._button.set_fill_color(self._color)
        self._button.set_border_color('black')
        self._button.set_depth(2)
        self._win.add(self._button)

        # creates the text of the button and adds it to the window:
        self._button_text = Text(self._win, self._text, self._text_size,
                                 self._center)
        self._button_text.set_depth(1)
        self._win.add(self._button_text)

    def add_handler(self, player, other, properties, game, buy_prop, same_roll,
                    prop=None, other_button=None, pop_up=None):
        """This function adds the handler to the button body and text. It also
           allows for the input of more variables needed for the action the
           button performs."""

        self._player = player
        self._other = other
        self._properties = properties
        self._game = game
        self._buy_prop = buy_prop
        self._same_roll = same_roll
        self._prop = prop
        self._other_button = other_button
        self._pop_up = pop_up

        # adds handlers:
        self._button.add_handler(self)
        self._button_text.add_handler(self)

    def handle_mouse_enter(self):
        """This function changes the button's body color to red when the player
           puts the mouse on the button."""

        self._button.set_border_color('red')

    def handle_mouse_leave(self):
        """This function changes the button's body color to black when the
           player takes the mouse off the button."""

        self._button.set_border_color('black')

    def handle_mouse_release(self):
        """This function handles the action when the button is clicked based on
           its specified type."""

        # checks the type of the button:
        if self._type == 'start':
            # removes the two buttons and their text from the window:
            self._win.remove(self._button)
            self._win.remove(self._button_text)
            self._win.remove(self._other_button._button)
            self._win.remove(self._other_button._button_text)
            self._win.remove(self._pop_up._logo)
            # calls the function PopUpWin.pick_pieces() with player 1 picking:
            self._pop_up.pick_pieces(1)

        elif self._type == 'rules':
            # removes the two buttons and their text from the window:
            self._win.remove(self._button)
            self._win.remove(self._button_text)
            self._win.remove(self._other_button._button)
            self._win.remove(self._other_button._button_text)
            self._win.remove(self._pop_up._logo)
            # calls the function PopUpWin.rules()
            self._pop_up.rules()

        elif self._type == 'buy':
            # sets the owner of the spot as the player's id number:
            self._game._spots.set_ownership(self._player._piece_loc,
                                            self._player._idnum)
            # appends the location of the spot to the list of the player's
            # properties:
            self._player._properties.append(self._player._piece_loc)
            # increases the number of properties owned in the property's set
            # by 1:
            (self._player._prop_kinds[self._properties
             [str(self._player._piece_loc)]['set']]['have']) += 1
            # updates the player's money on the window:
            self._player.remove_money()
            self._player.display_money()
            # determines the number of deeds owned by the player:
            self._num_of_deeds = len(self._player._properties)
            # scales down the size of the displayed property deed and sets the
            # depth and moves it to the display window based on the number of
            # deeds:
            self._prop.scale(13 / 16)
            self._prop.set_depth(30 - self._num_of_deeds)
            if self._num_of_deeds <= 8:
                self._prop.move_to((780, 415 + (25 *
                                                (self._num_of_deeds - 1))))
            elif 8 < self._num_of_deeds <= 16:
                self._prop.move_to((920, 415 + (25 *
                                                (self._num_of_deeds - 9))))
            elif 16 < self._num_of_deeds <= 24:
                self._prop.move_to((1060, 415 + (25 *
                                                 (self._num_of_deeds - 17))))
            # adds the property to the the player's _prop_display dictionary:
            self._player._prop_display[self._num_of_deeds] = self._prop
            # removes the two buttons and their text to the window:
            self._win.remove(self._button)
            self._win.remove(self._button_text)
            self._win.remove(self._other_button._button)
            self._win.remove(self._other_button._button_text)
            # calls the function BuyProperty.remove_info_window()
            self._buy_prop.remove_info_window()
            # checks is the player rolled doubles:
            if self._same_roll:
                # adds the popup window that tells the player to roll again:
                pop_up = PopUpWin(self._win, None, self._game)
                pop_up.roll_again()
            else:
                # calls the function Game.add_end_turn_button()
                self._game.add_end_turn_button()

        elif self._type == 'pass':
            # adds the price of the property back to the player's money:
            self._player._money += (self._properties
                                    [str(self._player._piece_loc)]
                                    ['price'])
            # removes the two buttons and their text to the window:
            self._win.remove(self._button)
            self._win.remove(self._button_text)
            self._win.remove(self._other_button._button)
            self._win.remove(self._other_button._button_text)
            # removes the deed image from the window:
            self._win.remove(self._prop)
            # calls the function BuyProperty.remove_info_window()
            self._buy_prop.remove_info_window()
            # checks is the player rolled doubles:
            if self._same_roll:
                # adds the popup window that tells the player to roll again:
                pop_up = PopUpWin(self._win, None, self._game)
                pop_up.roll_again()
            else:
                # calls the function Game.add_end_turn_button()
                self._game.add_end_turn_button()

        elif self._type == '10%':
            # determines the money lost after paying the tax (10% of the
            # player's current money), subtracts the money_lost from the
            # player's money, and updates the player's money on the
            # window:
            money_lost = int(self._player._money * 0.1)
            self._player._money -= money_lost
            self._player.remove_money()
            self._player.display_money()
            # removes the two buttons and their text to the window:
            self._win.remove(self._button)
            self._win.remove(self._button_text)
            self._win.remove(self._other_button._button)
            self._win.remove(self._other_button._button_text)
            # calls the functions PopUpWin.tax_choice_end() and
            # PopUpWin.close_buttons():
            self._pop_up.tax_choice_end(money_lost)
            self._pop_up.close_buttons()

        elif self._type == '200':
            # sets the money_lost as $200, subtracts money_lost from the
            # player's money:
            money_lost = 200
            self._player._money -= 200
            # removes the two buttons and their text to the window:
            self._win.remove(self._button)
            self._win.remove(self._button_text)
            self._win.remove(self._other_button._button)
            self._win.remove(self._other_button._button_text)
            # determines if the player has enough money to pay the tax:
            if self._player._money < 0:
                # removes the text from the window:
                self._win.remove(self._pop_up._tax_explain)
                self._win.remove(self._pop_up._tax_choice)
                # calls the function PopUpWin.bankrupcy():
                self._pop_up.bankrupcy()
            else:
                # updates the player's money on the window:
                self._player.remove_money()
                self._player.display_money()
                # calls the functions PopUpWin.tax_choice_end() and
                # PopUpWin.close_buttons():
                self._pop_up.tax_choice_end(money_lost)
                self._pop_up.close_buttons()

        elif self._type == 'jail free yes':
            # updates the player's "Jail Free" status - the player now cannot
            # get out of going to jail:
            self._player._jail_free = False
            # removes the two buttons and their text to the window:
            self._win.remove(self._button)
            self._win.remove(self._button_text)
            self._win.remove(self._other_button._button)
            self._win.remove(self._other_button._button_text)
            # calls the functions PopUpWin.jail_free_choice_end() and
            # PopUpWin.close_buttons():
            self._pop_up.jail_free_choice_end('yes')
            self._pop_up.close_buttons()

        elif self._type == 'jail free no':
            # removes the two buttons and their text to the window:
            self._win.remove(self._button)
            self._win.remove(self._button_text)
            self._win.remove(self._other_button._button)
            self._win.remove(self._other_button._button_text)
            # calls the functions PopUpWin.jail_free_choice_end()
            self._pop_up.jail_free_choice_end('no')

        elif self._type == 'bankrupcy':
            # removes the button and its text:
            self._win.remove(self._button)
            self._win.remove(self._button_text)
            # calls the function PopUpWin.bankrupcy_end()
            self._pop_up.bankrupcy_end()

        elif self._type == 'house':
            # checks if all three houses have already been added:
            if len(self._game._houses._house_locs
                   [str(self._center)]['spots']) > 0:
                # subtracts the price of the house from the player's money:
                self._game._player._money -= (self._game._board._properties
                                              [str(self._game._houses._house_locs
                                                   [str(self._center)]
                                                   ['prop'])]['house cost'])
                # checks if the player has enough money to buy:
                if self._game._player._money > 0:
                    # updates the player's money on the window:
                    self._game._player.remove_money()
                    self._game._player.display_money()
                    # adds another house to the property:
                    (self._game._board._properties
                     [str(self._game._houses._house_locs[str(self._center)]
                     ['prop'])]['houses']) += 1
                    # finds the center of the house on the board and makes sure
                    # no other house can be placed there:
                    center = (self._game._houses._house_locs
                              [str(self._center)]['spots'].pop(0))
                    # creates the house and adds it to the window:
                    house = Rectangle(self._win, 10, 10, center)
                    house.set_fill_color('red')
                    house.set_depth(9)
                    self._win.add(house)
                    # creates the popup window that tells player that they
                    # bought a house:
                    bought = PopUpWin(self._win, None, self._game)
                    bought.bought_house(self._game._board._properties
                                        [str(self._game._houses._house_locs
                                             [str(self._center)]['prop'])]
                                        ['name'])

                else:
                    # creates the popup window that tells the player they
                    # don't have enough money to buy the house:
                    cant_buy = PopUpWin(self._win, None, self._game)
                    cant_buy.cant_house(self._game._board._properties
                                        [str(self._game._houses._house_locs
                                             [str(self._center)]
                                             ['prop'])]['name'])


class PopUpWin(EventHandler):
    """This class creates a popup window. The window contains different
       information based on the function called."""

    # the constructor for the PopUpWin class:
    def __init__(self, win, player, game):

        # calls the EventHandler parent class so that methods belonging to
        # that class are accessible:
        EventHandler.__init__(self)

        self._win = win
        self._player = player
        self._game = game

        # creates the window and adds it to the window:
        self._window = Rectangle(self._win, 500, 400, (600, 350))
        self._window.set_depth(4)
        self._win.add(self._window)

    def close_buttons(self):
        """This function adds a close button to the window."""

        # creates the body of the close button and adds it to the window:
        self._x = Square(self._win, 20, (370, 170))
        self._x.set_depth(2)
        self._x.set_fill_color('red')
        self._win.add(self._x)
        self._x.add_handler(self)

        # creates the text of the close button and adds it to the window:
        self._x_text = Text(self._win, 'X', 12, (370, 170))
        self._x_text.set_depth(1)
        self._win.add(self._x_text)
        self._x_text.add_handler(self)

    def start(self):
        """This function create the information for the start popup window."""

        # creates the logo and adds it to the window:
        self._logo = Image(self._win, 'monopoly_logo.jpg', 450, 130,
                           (600, 250))
        self._logo.set_depth(1)
        self._win.add(self._logo)

        # creates "Start" and "Rules" buttons and adds handlers to them:
        self._start_button = Button(self._win, 150, 90, (500, 400), 'white',
                                    'START GAME', 15, 'start')
        self._rules_button = Button(self._win, 150, 90, (700, 400), 'white',
                                    'SHOW RULES', 15, 'rules')
        self._start_button.add_handler(None, None, None, self._game, None,
                                       None, None, self._rules_button, self)
        self._rules_button.add_handler(None, None, None, self._game, None,
                                       None, None, self._start_button, self)

    def pick_pieces(self, player_number):
        """This function creates the information that allows the players to
           choose playing tokens."""

        self._player_number = player_number

        # checks which player is choosing their token:
        if self._player_number == 1:
            # sets _type equal to 'next' in order to make the next player
            # choose their token:
            self._type = 'next'

        else:
            # sets _type equal to 'start' in order to start playing the game
            self._type = 'start'

        # creates the text that says the player should pick a token and adds
        # it to the window:
        self._pick_piece = Text(self._win, 'Player ' +
                                str(self._player_number) +
                                ' pick a game token!', 20, (600, 250))
        self._win.add(self._pick_piece)
        self._pick_piece.set_depth(1)

        # calls the function GamePieces.display_pieces():
        self._game._game_pieces.display_pieces()

    def piece_picked(self, piece):
        """This function creates the information that tells the player which
           token they picked."""

        # removes the text on the window and calls the function
        # GamePieces.remove_pieces():
        self._win.remove(self._pick_piece)
        self._game._game_pieces.remove_pieces()

        # creates the text that says the player picked a token and adds it to
        # the window:
        self._picked_piece_text = Text(self._win, 'Player ' +
                                       str(self._player_number) +
                                       ' picked the ' + piece +
                                       '!', 20, (600, 300))
        self._picked_piece_text.set_depth(1)
        self._win.add(self._picked_piece_text)

        # creates an image of the token picked and adds it to the window:
        self._picked = Image(self._win,
                             self._game._game_pieces._pieces[piece]['file'],
                             (self._game._game_pieces._pieces[piece]
                              ['width'] * 2),
                             (self._game._game_pieces._pieces[piece]
                              ['height'] * 2),
                             (600, 400))
        self._picked.set_depth(1)
        self._win.add(self._picked)

        # calls the function close_buttons():
        self.close_buttons()

    def rules(self):
        """This function creates the information that tells the players the
           rules of this Monopoly game."""

        # sets _type as 'rules':
        self._type = 'rules'

        # creates the text for all the rules of Monopoly:
        self._rules = Text(self._win, 'Monopoly Rules', 25, (600, 180))
        self._rule1 = Text(self._win, '1.  Each player starts on "GO"',
                           10, (460, 210))
        self._rule2 = Text(self._win, '2.  Click the dice to roll - if ' +
                           'doubles are thrown you may roll again', 10,
                           (561, 230))
        self._rule3 = Text(self._win, '3.  According to the space your ' +
                           'token reaches, you may be entiled to buy real', 10,
                           (597, 250))
        self._rule4 = Text(self._win, 'estate or other properties - or ' +
                           'obliged to pay rent, pay taxes, draw a Chance', 10,
                           (610, 270))
        self._rule5 = Text(self._win, 'or Community Chest card, Go to ' +
                           'Jail, etc.', 10, (512, 290))
        self._rule6 = Text(self._win, '4.  You may buy a property for the ' +
                           'price shown next to the deed card', 10, (572, 310))
        self._rule7 = Text(self._win, '5.  When you land on a property owned' +
                           ' by another player, the owner collects', 10,
                           (595, 330))
        self._rule8 = Text(self._win, 'rent from you in accordance with the ' +
                           'list printed on its Title Deed card', 10,
                           (594, 350))
        self._rule9 = Text(self._win, '6.  When you land on a "Chance" or ' +
                           '"Community Chest" space, take a card', 10,
                           (593, 370))
        self._rule10 = Text(self._win, 'for the indicated deck and follow ' +
                            'the instructions', 10, (533, 390))
        self._rule11 = Text(self._win, '7.  You land in Jail when... (1) ' +
                            'your token lands on the space "Go to Jail";', 10,
                            (585, 410))
        self._rule12 = Text(self._win, '(2) you draw a card marked "Go to ' +
                            'Jail"; or (3) you roll doubles three times', 10,
                            (605, 430))
        self._rule13 = Text(self._win, 'in succession - when you are sent ' +
                            'to jail, you do not pass "GO"', 10, (575, 450))
        self._rule14 = Text(self._win, '(no other penalties are incurred)', 10,
                            (480, 470))
        self._rule15 = Text(self._win, '8.  You declare bankrupcy if you ' +
                            'owe more than you can pay either to another', 10,
                            (585, 490))
        self._rule16 = Text(self._win, 'player or to the Bank - only cash ' +
                            'savings can be put towards payments;', 10,
                            (589, 510))
        self._rule17 = Text(self._win, 'you may not mortgage properties', 10,
                            (476, 530))

        # creates a list of all the rules and adds all the rules to the window:
        self._rule = [self._rules, self._rule1, self._rule2, self._rule3,
                      self._rule4, self._rule5, self._rule6, self._rule7,
                      self._rule8, self._rule9, self._rule10, self._rule11,
                      self._rule12, self._rule13, self._rule14, self._rule15,
                      self._rule16, self._rule17]
        for rule in self._rule:
            rule.set_depth(1)
            self._win.add(rule)

        # calls the function close_button()
        self.close_buttons()

    def tax_choice(self, same_roll):
        """This function creates the information that allows the player to
           choose whether they want to pay 10% or $200."""

        self._same_roll = same_roll
        # sets _type as 'tax':
        self._type = 'tax'

        # creates the text for the popup window and adds it to the window:
        self._tax_explain = Text(self._win, 'You landed on Income Tax!', 25,
                                 (600, 250))
        self._tax_explain.set_depth(1)
        self._win.add(self._tax_explain)
        self._tax_choice = Text(self._win, 'Choose to either pay $200 or 10%' +
                                ' of your money.', 15, (600, 300))
        self._tax_choice.set_depth(1)
        self._win.add(self._tax_choice)

        # creates "Start" and "Rules" buttons and adds handlers to them:
        self._per = Button(self._win, 100, 70, (530, 400), 'white',
                           'PAY 10%', 15, '10%')
        self._pay_200 = Button(self._win, 100, 70, (670, 400), 'white',
                               'Pay $200', 15, '200')
        self._per.add_handler(self._player, None, None, self._game, None,
                              None, None, self._pay_200, self)
        self._pay_200.add_handler(self._player, None, None, self._game, None,
                                  None, None, self._per, self)

    def tax_choice_end(self, money_lost):
        """This function creates information that tells the player how much
           they payed in income tax."""

        # removes the current text from the window:
        self._win.remove(self._tax_explain)
        self._win.remove(self._tax_choice)

        # creates the text that says how much was paid and adds it to the
        # window:
        self._end_tax_text = Text(self._win, 'You paid $' +
                                  str(money_lost), 20, (600, 350))
        self._end_tax_text.set_depth(1)
        self._win.add(self._end_tax_text)

    def pay_tax(self, same_roll):
        """This function creates the information that tells the player they
           payed a Luxury Tax."""

        self._same_roll = same_roll
        # sets _type as 'luxury':
        self._type = 'luxury'

        # creates the text for the popup window and adds it to the window:
        self._luxury_explain = Text(self._win, 'You landed on Luxury Tax!', 25,
                                    (600, 300))
        self._luxury_explain.set_depth(1)
        self._win.add(self._luxury_explain)
        self._luxury_pay = Text(self._win, 'Pay $200', 30, (600, 350))
        self._luxury_pay.set_depth(1)
        self._win.add(self._luxury_pay)

        # calls the function close_buttons():
        self.close_buttons()

    def roll_again(self):
        """This function creates the information that tells the player to roll
           again."""

        # sets _type as 'roll_again':
        self._type = 'roll_again'

        # creates the text for the popup and adds it to the window:
        self._roll_again_text = Text(self._win, 'ROLL AGAIN!', 30, (600, 350))
        self._roll_again_text.set_depth(1)
        self._win.add(self._roll_again_text)

        # calls the function close_buttons():
        self.close_buttons()

    def player_owns(self, same_roll):
        """This function creates the information that tells the player that
           they already own the property they landed on."""

        self._same_roll = same_roll
        # sets _type as 'player_owns':
        self._type = 'player_owns'

        # creates the text for the popup and adds it to the window:
        self._already_own_text = Text(self._win, 'You already own this ' +
                                      'property!', 25, (600, 350))
        self._already_own_text.set_depth(1)
        self._win.add(self._already_own_text)

        # calls the function close_buttons():
        self.close_buttons()

    def safe(self, same_roll):
        """This function creates the information that tells the player that
           they landed on a safe spot."""

        self._same_roll = same_roll
        # sets _type as 'safe':
        self._type = 'safe'

        # creates the text for the popup and adds it to the window:
        self._safe_text = Text(self._win, 'You are safe!', 30, (600, 350))
        self._safe_text.set_depth(1)
        self._win.add(self._safe_text)

        # calls the function close_buttons():
        self.close_buttons()

    def jail(self):
        """This function creates the information that tells the player that
           they were thrown in jail."""

        # sets _type as 'jail':
        self._type = 'jail'

        # creates the text for the popup and adds it to the window:
        self._jail_text = Text(self._win, 'You were thrown in jail!', 27,
                               (600, 350))
        self._jail_text.set_depth(1)
        self._win.add(self._jail_text)

        # calls the function close_buttons():
        self.close_buttons()

    def jail_free_choice(self):
        """This function creates the information that allows the player to
           choose whether or not to use their "Jail Free" card."""

        # sets _type as 'jail free':
        self._type = 'jail free'

        # creates the popup window's text and adds it to the window:
        self._jail_free_ask = Text(self._win, 'Would you like to use your' +
                                   ' get out of Jail Free card?', 15,
                                   (600, 300))
        self._jail_free_ask.set_depth(1)
        self._win.add(self._jail_free_ask)

        # creates two buttons and adds their handlers:
        self._yes = Button(self._win, 100, 70, (530, 400), 'white',
                           'YES', 15, 'jail free yes')
        self._no = Button(self._win, 100, 70, (670, 400), 'white',
                          'NO', 15, 'jail free no')
        self._yes.add_handler(self._player, None, None, self._game, None,
                              None, None, self._no, self)
        self._no.add_handler(self._player, None, None, self._game, None,
                             None, None, self._yes, self)

    def jail_free_choice_end(self, answer):
        """This function creates the information that tells the player
           that they used the "Jail Free" card or sends the player to jail."""

        # checks if player used their "Jail Free" card:
        if answer == 'yes':
            # removes any text from the popup window:
            self._win.remove(self._jail_free_ask)
            # creates popup text and adds it to window:
            self._jail_free_yes = Text(self._win, 'You used your get' +
                                       ' out of Jail Free card!', 20,
                                       (600, 350))
            self._jail_free_yes.set_depth(1)
            self._win.add(self._jail_free_yes)

        elif answer == 'no':
            # removes any text from the popup window:
            self._win.remove(self._jail_free_ask)
            # moves the player token to jail and sets the player's piece
            # location:
            self._player._player_piece.move_to(self._game._board._locations
                                               [41])
            self._player.set_piece_loc(11)
            # calls the function jail():
            self.jail()

    def pay(self, properties, same_roll, money_paid, advance=0):
        """This function creates the information that tells the player
           how much they paid in rent."""

        self._same_roll = same_roll
        # sets _type as 'pay':
        self._type = 'pay'

        # creates the text that says which property was landed on and adds it
        # to the window:
        self._loc_text = Text(self._win, 'You landed on ' +
                              properties[str(self._player._piece_loc)]['name'],
                              20, (600, 300))
        self._loc_text.set_depth(1)
        self._win.add(self._loc_text)

        # adds the money paid by the player to the other player:
        self._game._other._money += money_paid

        # creates the text that says how much was payed to the owner and adds
        # it to the window:
        self._pay_text = Text(self._win, 'You paid Player ' +
                              str(properties[str(self._player._piece_loc)]
                                  ['owned']) + ' $' + str(money_paid), 28,
                              (600, 350))
        self._pay_text.set_depth(1)
        self._win.add(self._pay_text)

        # calls the function close_buttons():
        self.close_buttons()

    def cant_buy(self, same_roll, properties):
        """This fucntion creates the information that tells the player that
           they don't have enough money to buy the property."""

        # sets _type as 'cant buy':
        self._type = 'cant buy'
        self._same_roll = same_roll

        # creates the text for the popup and adds it to the window:
        self._cant_text1 = Text(self._win, 'You dont have enough money', 20,
                                (600, 300))
        self._cant_text1.set_depth(1)
        self._win.add(self._cant_text1)

        self._cant_text2 = Text(self._win, 'to buy ' +
                                properties[str(self._player._piece_loc)]
                                ['name'], 20, (600, 350))
        self._cant_text2.set_depth(1)
        self._win.add(self._cant_text2)

        # calls the function close_buttons():
        self.close_buttons()

    def chance(self, typ, same_roll=False, spots=None):
        """This function creates the information that tells the player which
           Chance card they picked."""

        # sets _type as 'card':
        self._type = 'card'
        self._sub_type = typ
        self._spots = spots
        self._same_roll = same_roll

        # creates the popup text and adds it to the window:
        self._card_text = Text(self._win, 'You landed on Chance!', 20,
                               (600, 250))
        self._card_text.set_depth(1)
        self._win.add(self._card_text)

        # creates the card image and adds it to the window:
        self._card = Image(self._win, 'blankchance.jpg', 320, 200,
                           (600, 400))
        self._card.set_depth(3)
        self._win.add(self._card)

        # based on the type of card that is picked, the corresponding
        # instructions and images are added to the window:
        if self._sub_type == 'Go':
            self._card_text1 = Text(self._win, 'Advance to Go', 15,
                                    (520, 335))
            self._card_text2 = Text(self._win, 'Collect $200', 15,
                                    (520, 365))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'chance_go.jpg', 200, 170,
                                     (655, 400))

        elif self._sub_type == 'Ill Ave':
            self._card_text1 = Text(self._win, 'Advance to Illinois' +
                                    ' Avenue', 15, (570, 335))
            self._card_text2 = Text(self._win, 'If you pass Go,',
                                    12, (520, 395))
            self._card_text3 = Text(self._win, 'collect $200', 12,
                                    (520, 425))
            self._card_image = Image(self._win, 'chance_ill_ave.jpg', 150,
                                     130, (675, 420))

        elif self._sub_type == 'St Char Plc':
            self._card_text1 = Text(self._win, 'Advance to St. ' +
                                    'Charles Place', 15, (590, 335))
            self._card_text2 = Text(self._win, 'If you pass Go,',
                                    12, (520, 395))
            self._card_text3 = Text(self._win, 'collect $200', 12,
                                    (520, 425))
            self._card_image = Image(self._win, 'chance_st_char.jpg', 150,
                                     120, (675, 420))

        elif self._sub_type == 'Util':
            self._card_text1 = Text(self._win, 'Advance to nearest ' +
                                    'utility', 15, (590, 335))
            self._card_text2 = Text(self._win, 'If you pass Go,',
                                    12, (520, 395))
            self._card_text3 = Text(self._win, 'collect $200', 12,
                                    (520, 425))
            self._card_image = Image(self._win, 'chance_util.jpg', 120, 145,
                                     (675, 420))

        elif self._sub_type == 'Rail':
            self._card_text1 = Text(self._win, 'Advance to nearest ' +
                                    'railroad', 15, (590, 335))
            self._card_text2 = Text(self._win, 'If you pass Go,',
                                    12, (520, 395))
            self._card_text3 = Text(self._win, 'collect $200', 12,
                                    (520, 425))
            self._card_image = Image(self._win, 'chance_railroad.png', 150,
                                     90, (675, 420))

        elif self._sub_type == '$50 Div':
            self._card_text1 = Text(self._win, 'Bank pays you ' +
                                    'dividend of $50', 15, (600, 335))
            self._card_text2 = Text(self._win, '', 1, (1500, 0))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'chance_div.jpg', 150, 70,
                                     (675, 420))

        elif self._sub_type == 'Jail Free':
            self._card_text1 = Text(self._win, 'Get out of',
                                    15, (520, 375))
            self._card_text2 = Text(self._win, 'jail free', 15,
                                    (520, 405))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'chance_jail_free.jpg', 150,
                                     150, (675, 420))

        elif self._sub_type == 'Back 3':
            self._card_text1 = Text(self._win, 'Go back', 15,
                                    (520, 375))
            self._card_text2 = Text(self._win, '3 spaces', 15,
                                    (520, 405))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'chance_back_3.jpg', 150,
                                     130, (675, 420))

        elif self._sub_type == 'Go Jail':
            self._card_text1 = Text(self._win, 'Go to Jail', 15,
                                    (520, 375))
            self._card_text2 = Text(self._win, 'Do not pass go', 15,
                                    (520, 405))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'chance_go_jail.jpg', 150,
                                     70, (675, 420))

        elif self._sub_type == 'Poor Tax':
            self._card_text1 = Text(self._win, 'Pay poor',
                                    15, (520, 375))
            self._card_text2 = Text(self._win, 'tax of $15', 15,
                                    (520, 405))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'chance_pay_tax.jpg', 130,
                                     150, (675, 420))

        elif self._sub_type == 'Read Rail':
            self._card_text1 = Text(self._win, 'Advance to Reading' +
                                    ' Railroad', 15, (590, 335))
            self._card_text2 = Text(self._win, 'If you pass Go,',
                                    12, (520, 395))
            self._card_text3 = Text(self._win, 'collect $200', 12,
                                    (520, 425))
            self._card_image = Image(self._win, 'chance_railroad.png', 150,
                                     85, (675, 420))

        elif self._sub_type == 'Boardwalk':
            self._card_text1 = Text(self._win, 'Advance to Boardwalk',
                                    15, (590, 335))
            self._card_text2 = Text(self._win, 'If you pass Go,',
                                    12, (520, 395))
            self._card_text3 = Text(self._win, 'collect $200', 12,
                                    (520, 425))
            self._card_image = Image(self._win, 'chance_boardwalk.jpg', 150,
                                     80, (675, 420))

        elif self._sub_type == 'Chairman':
            self._card_text1 = Text(self._win, 'You have been',
                                    15, (530, 345))
            self._card_text2 = Text(self._win, 'elected Chairman', 15,
                                    (530, 375))
            self._card_text3 = Text(self._win, 'Pay each player $50',
                                    12, (530, 415))
            self._card_image = Image(self._win, 'chance_chairman.jpg',
                                     150, 120, (675, 420))

        elif self._sub_type == 'Loan Matures':
            self._card_text1 = Text(self._win, 'Your building',
                                    15, (530, 345))
            self._card_text2 = Text(self._win, 'loan matures', 15,
                                    (530, 375))
            self._card_text3 = Text(self._win, 'Collect $150', 12,
                                    (530, 415))
            self._card_image = Image(self._win, 'chance_loan.jpg', 130, 150,
                                     (675, 420))

        self._card_text1.set_depth(1)
        self._card_text2.set_depth(1)
        self._card_text3.set_depth(1)
        self._card_image.set_depth(2)
        self._win.add(self._card_text1)
        self._win.add(self._card_text2)
        self._win.add(self._card_text3)
        self._win.add(self._card_image)

        # calls the function close_buttons():
        self.close_buttons()

    def community(self, typ, same_roll=False):
        """This function creates the information that tells the player which
           Community Chest card they picked."""

        self._spots = None
        # sets _type as 'card':
        self._type = 'card'
        self._sub_type = typ
        self._same_roll = same_roll

        # creates the popup text and adds it to the window:
        self._card_text = Text(self._win, 'You landed on Community Chest!',
                               20, (600, 250))
        self._card_text.set_depth(1)
        self._win.add(self._card_text)

        # creates the card image and adds it to the window:
        self._card = Image(self._win, 'blankcomm.jpg', 320, 200,
                           (600, 400))
        self._card.set_depth(3)
        self._win.add(self._card)

        # based on the type of card that is picked, the corresponding
        # instructions and images are added to the window:
        if self._sub_type == 'Go':
            self._card_text1 = Text(self._win, 'Advance to Go', 15,
                                    (520, 335))
            self._card_text2 = Text(self._win, 'Collect $200', 15,
                                    (520, 365))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'comm_go.jpg', 200, 170,
                                     (655, 400))

        elif self._sub_type == 'Bank Error':
            self._card_text1 = Text(self._win, 'Bank error in',
                                    15, (530, 345))
            self._card_text2 = Text(self._win, 'your favor', 15,
                                    (530, 375))
            self._card_text3 = Text(self._win, 'Collect $200', 12,
                                    (530, 415))
            self._card_image = Image(self._win, 'comm_bank_err.jpg', 150,
                                     130, (675, 420))

        elif self._sub_type == 'Doc Fee':
            self._card_text1 = Text(self._win, "Doctor's fees",
                                    15, (520, 375))
            self._card_text2 = Text(self._win, 'Pay $50', 15,
                                    (520, 405))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'comm_doc_fee.jpg', 150,
                                     130, (675, 420))

        elif self._sub_type == 'Jail Free':
            self._card_text1 = Text(self._win, 'Get out of',
                                    15, (520, 375))
            self._card_text2 = Text(self._win, 'jail free', 15,
                                    (520, 405))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'comm_jail_free.jpg', 180,
                                     150, (655, 420))

        elif self._sub_type == 'Go Jail':
            self._card_text1 = Text(self._win, 'Go to Jail', 15,
                                    (520, 375))
            self._card_text2 = Text(self._win, 'Do not pass go', 15,
                                    (520, 405))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'comm_go_jail.jpg', 150,
                                     120, (675, 420))

        elif self._sub_type == 'Opera':
            self._card_text1 = Text(self._win, 'Grand Opera Night',
                                    15, (590, 335))
            self._card_text2 = Text(self._win, 'Collect $50 from every',
                                    12, (530, 395))
            self._card_text3 = Text(self._win, 'player for seats', 12,
                                    (530, 425))
            self._card_image = Image(self._win, 'comm_opera.jpg', 130,
                                     150, (675, 420))

        elif self._sub_type == 'Holiday':
            self._card_text1 = Text(self._win, 'Holiday Fund matures',
                                    12, (530, 375))
            self._card_text2 = Text(self._win, 'Collect $100', 12,
                                    (530, 405))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'comm_holiday.jpg', 130,
                                     130, (675, 420))

        elif self._sub_type == 'Income Refund':
            self._card_text1 = Text(self._win, 'Income tax refund',
                                    12, (530, 375))
            self._card_text2 = Text(self._win, 'Collect $20', 12,
                                    (530, 405))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'comm_holiday.jpg', 130,
                                     130, (675, 420))

        elif self._sub_type == 'Life Insur':
            self._card_text1 = Text(self._win, 'Life insurance matures',
                                    12, (530, 375))
            self._card_text2 = Text(self._win, 'Collect $100', 12,
                                    (530, 405))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'comm_life_insur.jpg', 130,
                                     130, (675, 420))

        elif self._sub_type == 'Hosp Fee':
            self._card_text1 = Text(self._win, 'Pay hospital fees',
                                    15, (530, 375))
            self._card_text2 = Text(self._win, 'of $100', 15,
                                    (530, 405))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'comm_hosp_fee.jpg', 130,
                                     110, (675, 420))

        elif self._sub_type == 'Sch Fee':
            self._card_text1 = Text(self._win, 'Pay school fees',
                                    15, (530, 375))
            self._card_text2 = Text(self._win, 'of $150', 15,
                                    (530, 405))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'comm_sch_fee.jpg', 150,
                                     150, (675, 420))

        elif self._sub_type == 'Cons Fee':
            self._card_text1 = Text(self._win, 'Receive $25',
                                    15, (530, 375))
            self._card_text2 = Text(self._win, 'consultancy fee', 15,
                                    (530, 405))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'comm_cons_fee.jpg', 130,
                                     120, (675, 420))

        elif self._sub_type == 'Beauty':
            self._card_text1 = Text(self._win, 'You have won second',
                                    12, (535, 365))
            self._card_text2 = Text(self._win, 'prize in a beauty contest',
                                    12, (535, 395))
            self._card_text3 = Text(self._win, 'Collect $10', 12,
                                    (535, 435))
            self._card_image = Image(self._win, 'comm_beauty.jpg', 130,
                                     150, (675, 420))

        elif self._sub_type == 'Inherit':
            self._card_text1 = Text(self._win, 'You inherit $100', 15,
                                    (520, 355))
            self._card_text2 = Text(self._win, '', 1, (1500, 0))
            self._card_text3 = Text(self._win, '', 1, (1500, 0))
            self._card_image = Image(self._win, 'comm_inherit.jpg', 200, 170,
                                     (655, 400))

        self._card_text1.set_depth(1)
        self._card_text2.set_depth(1)
        self._card_text3.set_depth(1)
        self._card_image.set_depth(2)
        self._win.add(self._card_text1)
        self._win.add(self._card_text2)
        self._win.add(self._card_text3)
        self._win.add(self._card_image)

        # calls function close_buttons():
        self.close_buttons()

    def bought_house(self, prop_name):

        # sets _type as 'bought house':
        self._type = 'bought house'

        # creates the text for the popup and adds it to the window:
        self._cant_text1 = Text(self._win, 'You bought a house', 20,
                                (600, 300))
        self._cant_text1.set_depth(1)
        self._win.add(self._cant_text1)

        self._cant_text2 = Text(self._win, 'on ' +
                                prop_name, 20, (600, 350))
        self._cant_text2.set_depth(1)
        self._win.add(self._cant_text2)

        # calls the function close_buttons():
        self.close_buttons()   

    def cant_house(self, prop_name):

        # sets _type as 'cant buy house':
        self._type = 'cant buy house'

        # creates the text for the popup and adds it to the window:
        self._cant_text1 = Text(self._win, 'You dont have enough money', 20,
                                (600, 300))
        self._cant_text1.set_depth(1)
        self._win.add(self._cant_text1)

        self._cant_text2 = Text(self._win, 'to buy a house for ' +
                                prop_name, 20, (600, 350))
        self._cant_text2.set_depth(1)
        self._win.add(self._cant_text2)

        # calls the function close_buttons():
        self.close_buttons()        

    def bankrupcy(self):
        """This function creates the information that allows the player to
           declare bankrupcy."""

        # creates the popup text and adds it to the window:
        self._bankrupcy_text = Text(self._win, "You don't have enough " +
                                    "money to pay!", 15, (600, 300))
        self._bankrupcy_text.set_depth(1)
        self._win.add(self._bankrupcy_text)

        # creates the bankrupcy button and adds a handler:
        self._bankrupcy_button = Button(self._win, 150, 80, (600, 400),
                                        'white', 'Declare Bankrupcy', 12,
                                        'bankrupcy')
        self._bankrupcy_button.add_handler(self._player, None, None,
                                           self._game, None, None, None,
                                           None, self)

    def bankrupcy_end(self):
        """This function creates the information that says which player won
           the game."""

        # removes text already on the popup window:
        self._win.remove(self._bankrupcy_text)

        # creates the popup text and adds it to the window:
        self._winner_text = Text(self._win, 'Player ' +
                                 str(self._game._other._idnum) +
                                 ' won the game!', 20, (600, 350))
        self._winner_text.set_depth(1)
        self._win.add(self._winner_text)

    def handle_mouse_enter(self, event):
        """This function changes the button's body color to red when the player
           puts the mouse on the button."""

        self._x.set_border_color('red')

    def handle_mouse_leave(self, event):
        """This function changes the button's body color to black when the
           player removes the mouse from the button."""

        self._x.set_border_color('black')

    def handle_mouse_release(self, event):
        """This function handles what happens when the popup window is close
           based on the type of window it is."""

        # removes the window and the close button from the window:
        self._win.remove(self._window)
        self._win.remove(self._x)
        self._win.remove(self._x_text)

        # checks the type of the popup window:
        if self._type == 'next':
            # removes the text from the popup window:
            self._win.remove(self._picked_piece_text)
            self._win.remove(self._picked)
            # adds the popup window to the window:
            self._win.add(self._window)
            # calls the function pick_pieces with Player 2 picking a token:
            self.pick_pieces(2)

        elif self._type == 'start':
            # removes the text from the popup window:
            self._win.remove(self._picked_piece_text)
            self._win.remove(self._picked)
            # calls the function Game.create_players():
            self._game.create_players()

        elif self._type == 'rules':
            # adds the popup window to the window:
            self._win.add(self._window)
            # removes all the rules from the window:
            for rule in self._rule:
                self._win.remove(rule)
            # calls the function pick_pieces with Player 1 picking a token:
            self.pick_pieces(1)

        elif self._type == 'tax':
            # removes text from popup window:
            self._win.remove(self._end_tax_text)
            # checks if the player rolled doubles:
            if self._same_roll:
                # creates roll again popup window:
                pop_up = PopUpWin(self._win, None, self._game)
                pop_up.roll_again()
            else:
                # calls the function Game.add_end_turn_button():
                self._game.add_end_turn_button()

        elif self._type == 'luxury':
            # removes text from popup window:
            self._win.remove(self._luxury_explain)
            self._win.remove(self._luxury_pay)
            # checks if the player rolled doubles:
            if self._same_roll:
                # creates roll again popup window:
                pop_up = PopUpWin(self._win, None, self._game)
                pop_up.roll_again()
            else:
                # calls the function Game.add_end_turn_button():
                self._game.add_end_turn_button()

        elif self._type == 'roll_again':
            # removes text from popup window:
            self._win.remove(self._roll_again_text)

        elif self._type == 'player_owns':
            # removes text from popup window:
            self._win.remove(self._already_own_text)
            # checks if the player rolled doubles:
            if self._same_roll:
                # creates roll again popup window:
                pop_up = PopUpWin(self._win, None, self._game)
                pop_up.roll_again()
            else:
                # calls the function Game.add_end_turn_button():
                self._game.add_end_turn_button()

        elif self._type == 'safe':
            # removes text from popup window:
            self._win.remove(self._safe_text)
            # checks if the player rolled doubles:
            if self._same_roll:
                # creates roll again popup window:
                pop_up = PopUpWin(self._win, None, self._game)
                pop_up.roll_again()
            else:
                # calls the function Game.add_end_turn_button():
                self._game.add_end_turn_button()

        elif self._type == 'jail':
            # removes text from popup window:
            self._win.remove(self._jail_text)
            # calls the function Game.add_end_turn_button():
            self._game.add_end_turn_button()

        elif self._type == 'pay':
            # removes text from popup window:
            self._win.remove(self._loc_text)
            self._win.remove(self._pay_text)
            # checks if the player rolled doubles:
            if self._same_roll:
                # creates roll again popup window:
                pop_up = PopUpWin(self._win, None, self._game)
                pop_up.roll_again()
            else:
                # calls the function Game.add_end_turn_button():
                self._game.add_end_turn_button()

        elif self._type == 'cant buy':
            # removes text from popup window:
            self._win.remove(self._cant_text1)
            self._win.remove(self._cant_text2)
            # checks if the player rolled doubles:
            if self._same_roll:
                # creates roll again popup window:
                pop_up = PopUpWin(self._win, None, self._game)
                pop_up.roll_again()
            else:
                # calls the function Game.add_end_turn_button():
                self._game.add_end_turn_button()

        elif self._type == 'card':
            # removes text from popup window:
            self._win.remove(self._card_text)
            self._win.remove(self._card)
            self._win.remove(self._card_text1)
            self._win.remove(self._card_text2)
            self._win.remove(self._card_text3)
            self._win.remove(self._card_image)
            # checks if spot action must happen:
            if self._spots is not None:
                # calls the function Spots.spot_action():
                self._spots.spot_action(self._same_roll)
            else:
                # checks if the type is "Go Jail":
                if self._sub_type == 'Go Jail':
                    # calls the function GamePieces.move_piece():
                    self._game._game_pieces.move_piece(self._player, 0, True)
                    # checks if the player rolled doubles:
                elif self._same_roll:
                    # creates roll again popup window:
                    pop_up = PopUpWin(self._win, None, self._game)
                    pop_up.roll_again()
                else:
                    # calls the function Game.add_end_turn_button():
                    self._game.add_end_turn_button()

        elif self._type == 'jail free':
            # removes text from popup window:
            self._win.remove(self._jail_free_yes)
            # calls the function Game.add_end_turn_button():
            self._game.add_end_turn_button()

        elif self._type == 'cant buy house' or self._type == 'bought house':
            # removes text from popup window:
            self._win.remove(self._cant_text1)
            self._win.remove(self._cant_text2)




def program(win):
    """This function starts the game by adjusting the window size and calling
       GameManager."""

    # changes window size:
    win.set_height(700)
    win.set_width(1200)

    GameManager(win)


def main():
    """This function starts the GraphicsPackage and calls the function
       program."""

    StartGraphicsSystem(program)


if __name__ == '__main__':
    main()
