'''
Created on 18 Feb 2012
@author: Qasim

Coordinates start from 0,0 in an image
'''

import time
import os.path
import logging
import math as maths

from PIL import ImageGrab, Image
import win32api, win32con

from dna import Tower
import dna

DEBUG = False

#(x,y) mouse locations in game_view for the locations in DNA
"""optimal-locations-1
LOC_MAP = {
    1: (209, 114),
    2: (273, 113),
    3: (240, 180),
    4: (205, 180),
    5: (272, 177),
    6: (271, 80),
    7: (208, 80),
    8: (240, 400),
    9: (240, 370)
}
"""
LOC_MAP = {
     1: (210, 110),  2: (270, 110),  3: (210, 175),  4: (240, 175),
     5: (270, 175),  6: (175, 240),  7: (305, 240),  8: (240, 335),
     9: (240, 370), 10: (175, 115), 11: (300, 115), 12: (175, 175),
    13: (305, 175), 14: (145, 205), 15: (175, 205), 16: (205, 210),
    17: (145, 240), 18: (200, 240), 19: (140, 275), 20: (175, 275),
    21: (205, 275), 22: (275, 210), 23: (300, 210), 24: (330, 210),
    25: (270, 240), 26: (335, 240), 27: (270, 275), 28: (300, 275),
    29: (335, 275), 30: (240, 305), 31: (210, 340), 32: (270, 340)
}

TOWER_MAP = {
    Tower.blue: (515, 160),
    Tower.green: (515, 180),
    Tower.yellow: (515, 210)
}

UPGRADE_BUTTON = (510, 280)
CAN_UPGRADE_COLOUR = (50, 66, 52)

def mmove(point):
    """Move the mouse to (x, y) point"""
    win32api.SetCursorPos(point)

def mclick(point):
    """Click the mouse at (x, y) point"""
    win32api.SetCursorPos(point)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, point[0], point[1], 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, point[0], point[1], 0, 0)


#(Width, height) of game image (including the grey pixel boundary)
GAME_AREA = (643, 483)


NUMBER_START_LOC = 552, 28 #Location of Level number
NUMBER_GAP = 1 #Gap between number images
NUMBER_IMAGE_SIZE = 10, 11 #Size of each number
NUMBER_IMAGE = {} #Actual images for comparison

_BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_IMAGES_PATH = os.path.join(_BASE_PATH, "atd_data", "images", "number-{}.png")
_numbers_img_locations = [_IMAGES_PATH.format(i) for i in range(10)]
for i, number_file in enumerate(_numbers_img_locations):
    _number_image = Image.open(number_file)
    NUMBER_IMAGE[i] = _number_image.load()


def get_image_mismatch(image1, image2, size):
    """Return location of the first mismatch of two images (fast_images)"""
    for x in range(size[0]):
        for y in range(size[1]):
            if image1[x, y] != image2[x, y]:
                return (x, y, image1[x, y], image2[x, y])

def is_grey_boundary_colour(colour):
    """Return whether this colour is suitable to be mistaken for the grey
    boundary"""
    if colour[0] >= 223 and colour[0] <= 225 and\
      colour[1] >= 224 and colour[1] <= 226 and\
      colour[2] >= 226 and colour[2] <= 228:
        return True
    return False

def identify_game_offset():
    """Return the offset (GAME_OFFSET) for the game area using GAME_EDGE_COLOURS
    
    Return None if no game area was found"""
    
    game_image = ImageGrab.grab()
    fast_image = game_image.load()
    width, height = game_image.size
    for x in range(width-GAME_AREA[0]):
        for y in range(height-GAME_AREA[1]):
            for loc, colour in GAME_EDGE_COLOURS.items():
                image_colour = fast_image[loc[0]+x, loc[1]+y]
                if colour is None:
                    if not is_grey_boundary_colour(image_colour):
                        break
                elif image_colour != colour:
                    break
            else: #Did not break
                return x, y
    return None

class GameStateError(Exception):
    pass

class GameStateBoundaryError(GameStateError):
    def __init__(self, point, colour_at_point):
        self.point = point
        self.colour_at_point = colour_at_point
    
    def __str__(self):
        err = "Game boundary did not match on game image obtained. "+\
        "At point {}, the expected colour was <see code>, "+\
        "but the colour obtained was {}"
        return err.format(self.point, self.colour_at_point)


class GameStateFrameMismatch(GameStateError):
    def __init__(self, msg=""):
        if self.msg:
            self.msg = msg
        else:
            self.msg = "Image does not match this state."
    
    def __str__(self):
            return self.msg


class GameStatePixelMismatch(GameStateFrameMismatch):
    """If you are giving (r, g, b) for the colours you can do 
    ((r, g, b), x) where x would be which component did not match."""
    def __init__(self, point, colour_obtained, colour_expected):
        self.point = point
        self.colour_obtained = colour_obtained
        self.colour_expected = colour_expected
    
    def __str__(self):
        err = "Image does not match this state. "+\
        "At point {0}, the expected colour was {1}, but the colour obtained "+\
        "was {2}"
        return err.format(self.point, self.colour_expected, self.colour_obtained)

class GameState:
    """A state of a game which you can check to see if you are in.
    
    data = (
        (check_type_func, {(x, y): (r, g, b), ...}),
        ...
    )
    """
    
    def __init__(self, data):
        self.data = data
    
    def check_against(self, image):
        for func, pixel_data in self.data:
            func(image, pixel_data)
        return True

def check_edge(image, pixel_data):
    """Check if data matches edge colours"""
    check_others = {}
    for pos, colours in pixel_data.items():
        if colours is None:
            colour = image[pos]
            if not (colour[0] >= 223 and colour[0] <= 225 and
                    colour[1] >= 224 and colour[1] <= 226 and
                    colour[2] >= 226 and colour[2] <= 228):
                raise GameStateBoundaryError(pos, colour)
        else:
            check_others[pos] = colours
    
    check_exact(image, check_others)


def check_exact(image, pixel_data):
    """Check if every pixel matches exactly the data
    
    Pixel data is {(x,y): (r,g,b), ...}"""
    for pos, colour in pixel_data.items():
        img_colour = image[pos]
        if colour != img_colour:
            raise GameStatePixelMismatch(pos, img_colour, colour)


def check_colours(image, pixel_data):
    """Check if every pixel is approximately (+-25%) the correct colour"""
    for pos, colours in pixel_data.items():
        img_colours = image[pos]
        for colour, img_colour in zip(colours, img_colours):
            if not (img_colour*0.75 <= colour <= img_colour*1.25):
                raise GameStatePixelMismatch(pos, 
                        (img_colours, img_colour), (colours, colour))


def check_partial(image, pixel_data):
    """Check if most pixels are approx. the correct colour"""
    correct = 0
    errors = []
    for pos, colours in pixel_data.items():
        img_colours = image[pos]
        for colour, img_colour in zip(colours, img_colours):
            if (img_colour*0.75 <= colour <= img_colour*1.25):
                correct += 1
            else:
                errors.append((colours, img_colours))
    
    if correct < len(pixel_data)*0.8:
        err = "Most pixels are not approx. the correct colour.\n"
        err += "(Colours expected, colours obtained):\n"
        err += str(errors)
        raise GameStateFrameMismatch(err)


#Used to establish the game region is correct
#(Includes the grey surrounding background along with black edge boundary)
#NOTE: Grey Boundary actually has RGB = {223-225, 224-226, 226-228} aprox.
GAME_EDGE_COLOURS = {
    (0, 0): None, #Grey boundary
    (1, 1): (0, 0, 0),
    (642, 482): (0, 0, 0),
    (643, 483): None #Grey boundary
}

#Main Menu State
STATE_MAINMENU = GameState((
    (check_edge, GAME_EDGE_COLOURS),
    (check_exact, {
        (187, 58): (33, 89, 149),   #Blue above Title Text
        (187, 62): (255, 255, 255), #Title Text
        (487, 76): (255, 255, 255), #Title Text
        (469, 124): (52, 106, 179), #Blue Background
        (45, 425): (59, 59, 59),    #Settings Button Bgr
        (156, 236): (9, 19, 34),    #'Arcade' text
        (160, 235): (199, 210, 225),#Arcade Bgr
        (155, 235): (25, 169, 70),  #Arcade Green Blob
        (136, 193): (150, 50, 75),  #Arcade Red Blob
        (505, 451): (228, 76, 38)   #Bottom-right Orange
    })
))

#Ingame State
STATE_INGAME = GameState((
    (check_edge, GAME_EDGE_COLOURS),
    (check_exact, {
        (632, 466): (200, 200, 200), #Start of pause button bottom-right
        (630, 467): (59, 59, 59),
        (627, 468): (200, 200, 200),
        (623, 468): (59, 59, 59),
        (609, 473): (39, 39, 39), #End of pause button bottom-right
        (600, 390): (59, 59, 59), #End Game Button
        (504, 31): (239, 28, 28), #Red Letter L in 'Level xx'
        
        (504, 122): (255, 255, 255), #White Letter 'B' in 'Build'
        (2, 2): (240, 240, 240), #Gray Top-left pixel
        #Gray left to the "3000€" Tower (popup box comes when clicking 'End game')
        (490, 230): (39, 39, 39)      
    })
))

#Game Over state
#Note the entire Highscore box seems to be translucent inc. text.
STATE_GAMEOVER = GameState((
    (check_edge, GAME_EDGE_COLOURS),
    (check_exact, {
        (632, 466): (200, 200, 200), #Start of pause button bottom-right
        (630, 467): (59, 59, 59),
        (627, 468): (200, 200, 200),
        (623, 468): (59, 59, 59),
        (609, 473): (39, 39, 39), #End of pause button bottom-right
        (600, 390): (59, 59, 59), #End Game Button
        (504, 31): (239, 28, 28), #Red Letter L in 'Level xx'
    }),
    (check_partial, {
        ( 27, 135): ( 55, 126, 233), #Left Blue Border #1
        ( 27, 232): ( 55, 126, 233), #Left #2
        (217, 419): ( 58, 129, 236), #Bottom
        (460, 380): ( 58, 129, 236), #Right
        (424,  53): ( 58, 129, 236), #Top Blue border
        (315, 325): ( 89, 171, 102), #Submit score green
        (300, 325): (204, 215, 232), #Grey left of submit score
        (200, 390): ( 69, 105, 159), #Menu blue
        (240, 390): (203, 213, 231), #In-between buttons grey
        (310, 390): ( 69, 106, 159), #Retry blue
        (460, 460): (157, 157, 157), #Grey background #1
        ( 15, 460): (128, 128, 128), #Grey #2
    })
))

STATE_UNKNOWN = GameState(())

class GameView:
    """Holds an image of the game which can be updated.
    
    It also determines the state of the game and whether it has changed
    (when you update the game image).
    It also determines information from the game
    (eg. money available, the level number)."""
    
    def __init__(self, game_offset=None):
        self.state = STATE_UNKNOWN
        self.game_offset = game_offset
        self.game_image = None
        self.fast_image = None #Holds the data for fast access of pixels
        self.level_num = None
    
    def set_game_offset(self, game_offset):
        self.game_offset = game_offset
    
    def capture(self):
        """Recapture the game area image."""
        game_image = ImageGrab.grab((self.game_offset[0], self.game_offset[1],
                                    self.game_offset[0] + GAME_AREA[0] + 1,
                                    self.game_offset[1] + GAME_AREA[1] + 1))
        self.game_image = game_image
        self.fast_image = game_image.load()
    
    def identify(self):
        """Identify current state and return whether it has changed.
        
        Also updates the level number."""
        states = [STATE_MAINMENU, STATE_INGAME, STATE_GAMEOVER]
        for state in states:
            is_match = False
            try:
                is_match = state.check_against(self.fast_image)
            except GameStateFrameMismatch:
                pass
            
            if is_match:
                if state is STATE_INGAME:
                    self.level_num = self.get_level_number()
                if self.state != state:
                    self.state = state
                    return True
                else:
                    return False
        
        #Did not match against any state
        self.state = STATE_UNKNOWN
        return True
    
    def getpixel(self, x, y):
        return self.fast_image[x, y]
    
    def can_build_tower(self, tower_type):
        if tower_type == dna.Tower.blue:
            return self.fast_image[TOWER_MAP[Tower.blue]] == (184, 206, 227)
        elif tower_type == dna.Tower.green:
            try:
                check_colours(self.fast_image, {
                    TOWER_MAP[Tower.green]: (101, 172, 100)
                })
            except GameStatePixelMismatch as err:
                logging.debug(str(err))
                return False
            else:
                return True
        elif tower_type == dna.Tower.yellow:
            try:
                check_colours(self.fast_image, {
                    TOWER_MAP[Tower.yellow]: (237, 231, 193)
                })
            except GameStatePixelMismatch as err:
                logging.debug(str(err))
                return False
            else:
                return True
        raise NotImplementedError("Tower: {} not supported".format(tower_type))
    
    def can_upgrade_tower(self, tower_loc):
        """Takes 1/2 second to check and moves and clicks the mouse"""
        tower_xy = (self.game_offset[0]+LOC_MAP[tower_loc][0],
                    self.game_offset[1]+LOC_MAP[tower_loc][1])
        mclick(tower_xy)
        time.sleep(0.3)
        self.capture()
        self.identify()
        if self.state != STATE_INGAME:
            return False
        
        return self.fast_image[UPGRADE_BUTTON] == CAN_UPGRADE_COLOUR
    
    def get_level_number(self):
        """Return the level number"""
        """ideas/numbers.txt:
        """
        level = []
        for i in range(3): #Scan three numbers only
            num_left = NUMBER_START_LOC[0] + i*(NUMBER_GAP + NUMBER_IMAGE_SIZE[0])
            num_top = NUMBER_START_LOC[1]
            num_right = num_left + NUMBER_IMAGE_SIZE[0]
            num_bottom = num_top + NUMBER_IMAGE_SIZE[1]
            
            scan_region = self.game_image.crop(
                            (num_left, num_top, num_right, num_bottom)).load()
            
            for test_num in range(10):
                m_loc = get_image_mismatch(scan_region, NUMBER_IMAGE[test_num],
                                           NUMBER_IMAGE_SIZE)
                if m_loc is None:
                    level.append(test_num)
                    break
            else:
                break
        try:
            level = int(''.join([str(i) for i in level]))
        except ValueError as e: #level is [], ie. unknown
            raise Exception('Unable to read level number') from e
        
        return level


class GameBotException(Exception):
    pass
class GameBotUnknownFrameError(GameBotException):
    def __str__(self):
        s = "An unknown frame was encountered during the game."
        return s


#TODO: When DNA fails mid-way mark that beginning portion as junk.
#So that any future DNA which has same beginning portion is given same score.


class GameBot:
    """The Bot Player.
    
    *Every 30 seconds the bot should pause for exactly 5 seconds,
    moving the mouse to the top-right to allow for ending of program.
    *After each move, the bot should move the mouse to the bottom-right
    to prevent the image from containing the mouse cursor."""
    
    FRAME_TIME = 1
    PAUSE_TIME = 5
    FRAMES_AFTER_PAUSE = int(30/FRAME_TIME)
    
    def __init__(self, dna, game_offset, bot_num=-1):
        self.bot_num = bot_num
        self.game_offset = game_offset
        self.dna = dna
        self.next_move_gen = dna.__iter__()
        
        self.retry_button = (self.game_offset[0]+340, self.game_offset[1]+390)
        self.gameover_mainmenu_button = (self.game_offset[0]+160,
                                         self.game_offset[1]+390)
        
        self.idle_point = (self.game_offset[0] + GAME_AREA[0] + 50,
                           self.game_offset[1] + GAME_AREA[1])
        self.long_idle_point = (self.game_offset[0] + GAME_AREA[0] + 50,
                                self.game_offset[1])
        self.unknown_frame_error = 0
        
        self.did_the_move = True
    
    def run(self, game_view):
        """Return the score"""
        self.game_view = game_view
        
        logging.info("Running Bot #{}".format(self.bot_num))
        logging.info("DNA: {}".format(self.dna))
        
        self.movenum = 0
        while True:
            self.movenum += 1
            if self.single_move() is False:
                s = "Ending Bot {} with score {}"
                s = s.format(self.bot_num, self.game_view.level_num)
                logging.info(s)
                return self.game_view.level_num
            
            if self.movenum % self.FRAMES_AFTER_PAUSE == 0 and DEBUG:
                #Move mouse to top-right
                logging.debug("Long Idle Pause.")
                mmove(self.long_idle_point)
                time.sleep(self.PAUSE_TIME)
            else:
                #Move mouse to bottom-right
                mmove(self.idle_point)
                time.sleep(self.FRAME_TIME)
        
    
    def single_move(self):
        self.game_view.capture()
        self.game_view.identify()
        
        #Reset unknown frame error
        if self.unknown_frame_error > 0:
            if self.game_view.state != STATE_UNKNOWN:
                self.unknown_frame_error = 0
        
        moves = {STATE_MAINMENU: self.main_menu_frame,
                 STATE_INGAME: self.ingame_frame,
                 STATE_GAMEOVER: self.gameover_frame,
                 STATE_UNKNOWN: self.unknown_frame}
        return moves[self.game_view.state]()
        
    def main_menu_frame(self):
        """Do the move for the main menu"""
        s = "Frame #{}, Level #{}, State: Main Menu => Clicking Arcade Button"
        s = s.format(self.movenum, self.game_view.level_num)
        logging.info(s)
        
        arcade_button_point = (self.game_offset[0]+100, self.game_offset[1]+250)
        mclick(arcade_button_point)
        mmove(self.idle_point)
        #time.sleep(7) #Some box in the bottom-left appears when you start the game.
    
    def ingame_frame(self):
        """Play the game!"""
        s = "Frame #{}, Level #{}, State: Ingame."
        s = s.format(self.movenum, self.game_view.level_num)
        logging.debug(s)
        
        if self.did_the_move:
            try:
                self.move_to_do = next(self.next_move_gen)
            except StopIteration:
                logging.debug("All moves done. Waiting for game to end.")
                return None
            
            loc = self.move_to_do.location
            if isinstance(self.move_to_do, dna.BaseBuild):
                tower_type = self.move_to_do.tower_type
                logging.debug("Build {} at {}.".format(tower_type, loc))
            elif isinstance(self.move_to_do, dna.BaseUpgrade):
                logging.debug("Upgrade at {}.".format(loc))
            
            self.did_the_move = False
        
        if isinstance(self.move_to_do, dna.BaseBuild):
            tower_type = self.move_to_do.tower_type
            loc = self.move_to_do.location
            if self.game_view.can_build_tower(tower_type):
                c_1 = (self.game_offset[0]+TOWER_MAP[tower_type][0],
                       self.game_offset[1]+TOWER_MAP[tower_type][1])
                c_2 = (self.game_offset[0]+LOC_MAP[loc][0],
                       self.game_offset[1]+LOC_MAP[loc][1])
                mclick(c_1)
                time.sleep(0.3)
                mclick(c_2)
                time.sleep(0.3)
                mclick(c_2)
                logging.debug("Built {} at {}.".format(tower_type, loc))
                self.did_the_move = True
            else:
                logging.debug("Cannot build {} at {}".format(tower_type, loc))
                
        elif isinstance(self.move_to_do, dna.BaseUpgrade):
            loc = self.move_to_do.location
            if self.game_view.can_upgrade_tower(loc):
                c_1 = (self.game_offset[0]+LOC_MAP[loc][0],
                       self.game_offset[1]+LOC_MAP[loc][1])
                c_2 = (self.game_offset[0]+UPGRADE_BUTTON[0],
                       self.game_offset[1]+UPGRADE_BUTTON[1])
                mclick(c_1)
                time.sleep(0.3)
                mclick(c_2)
                time.sleep(0.3)
                mclick(c_2)
                logging.debug("Upgraded at {}.".format(loc))
                self.did_the_move = True
            else:
                logging.debug("Cannot Upgrade at {}.".format(loc))
    
    def gameover_frame(self):
        """The Game Over/Score Screen"""
        s = "Frame #{}, Level #{}, State: Game over => Clicking Retry Button"
        s = s.format(self.movenum, self.game_view.level_num)
        logging.info(s)
        
        mclick(self.retry_button)
        mmove(self.idle_point)
        return False #Quit Bot
    
    def unknown_frame(self):
        """Unknown frame detected
        
        Wait 4 seconds to allow for any changes to happen and try again
        eg. high score screen takes a few seconds to load"""
        s = "Frame #{}, Level #{}, State: Unknown (#{})"
        s = s.format(self.movenum, self.game_view.level_num,
                     self.unknown_frame_error)
        logging.info(s)
        
        if self.unknown_frame_error == 0:
            logging.error("Pausing Bot for 5secs due to unknown frame error.")
            self.unknown_frame_error += 1
            time.sleep(4.0)
        else:
            logging.error("Exiting Bot due to unknown frame error.")
            raise GameBotUnknownFrameError

def consistent(numlist):
    """Return whether numbers are consistent enough"""
    maxallowed = maths.floor(min(numlist)*1.05)
    return (max(numlist) <= maxallowed)

def score_func(dna):
    """Score a DNA string. Takes average of 3 attempts."""
    scores = []
    for i in range(1, 6):
        time.sleep(1.0)
        
        game_offset = identify_game_offset()
        if game_offset is None:
            logging.error("Unable to find game area.")
            return None
        logging.debug("Screen Coordinates for TOP-LEFT pixel of game area: {}"\
              .format(game_offset))
        
        game_view = GameView(game_offset)
        game_bot = GameBot(dna, game_offset, i)
        
        try:
            score = game_bot.run(game_view)
            if score is None:
                logging.error("Game level returned is None.")
        except GameBotUnknownFrameError:
            score = None
            logging.error("Score is None due to unknown frame error.")
        
        if score is not None:
            logging.debug("Score: {}".format(score))
            scores.append(score)
        else:
            logging.error("Obtained None score - aborting DNA score attempt.")
            return None
        
        #Early exit due to consistent scores
        if i >= 3 and consistent(scores):
            logging.info("Early scoring-exit due to consistent scores.")
            break
        
    avg_score = maths.floor(sum(scores)/len(scores))
    
    logging.debug("Scores obtained: {}".format(scores))
    logging.info("Average score: {}".format(avg_score))
    return avg_score

