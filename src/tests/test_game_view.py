'''
Created on 6 Dec 2012

@author: Qasim

This will allow you to see whether the images are correctly identified.
This currently allows you to test for:
- States
- Can you build towers?
- Can you upgrade? (Location 1)
- What is the level number?
'''

import os.path
import sys
sys.path[0] = os.path.dirname(sys.path[0])

import atd_bot
from dna import Tower

if __name__ == '__main__':
    gv = atd_bot.GameView()
    
    while True:
        cmd = input("\nTest for ('h' help): ")
        if cmd == 'q':
            break
        if cmd == 'h':
            print('m: Main Menu')
            print('i: Ingame')
            print('g: Game Over')
            print('tb: Can build blue tower?')
            print('tg: Can build green tower?')
            print('ty: Can build yellow tower?')
            print('u1: Can upgrade tower at location 1?')
            print('lv: What is the level number?')
            print('j: Jump to a tower location.')
            print('q: Quit.')
            continue
        
        game_offset = atd_bot.identify_game_offset()
        if game_offset is None:
            print('Failure to identify game region.')
            continue
        
        gv.set_game_offset(game_offset)
        gv.capture()
        gv.identify()
        
        if cmd == 'm':
            try:
                is_success = atd_bot.STATE_MAINMENU.check_against(gv.fast_image)
            except atd_bot.GameStateFrameMismatch as err:
                print("FAIL:", str(err), sep="\n")
            else:
                print("SUCCESS: This is the main menu.")
        elif cmd == 'i':
            try:
                is_success = atd_bot.STATE_INGAME.check_against(gv.fast_image)
            except atd_bot.GameStateFrameMismatch as err:
                print("FAIL:", str(err), sep="\n")
            else:
                print("SUCCESS: This is in the game room.")
        elif cmd == 'g':
            try:
                is_success = atd_bot.STATE_GAMEOVER.check_against(gv.fast_image)
            except atd_bot.GameStateFrameMismatch as err:
                print("FAIL:", str(err), sep="\n")
            else:
                print("SUCCESS: This is in the game over screen.")
        elif cmd == 'tb':
            if gv.can_build_tower(Tower.blue):
                print("SUCCESS: You can build the blue tower.")
            else:
                print("FAIL: You CANNOT build the blue tower.")
        elif cmd == 'tg':
            if gv.can_build_tower(Tower.green):
                print("SUCCESS: You can build the green tower.")
            else:
                print("FAIL: You CANNOT build the green tower.")
        elif cmd == 'ty':
            if gv.can_build_tower(Tower.yellow):
                print("SUCCESS: You can build the yellow tower.")
            else:
                print("FAIL: You CANNOT build the yellow tower.")
        elif cmd == 'u1':
            if gv.can_upgrade_tower(1):
                print("SUCCESS: You can upgrade the tower at location 1.")
            else:
                print("FAIL: You CANNOT upgrade the tower at location 1.")
        elif cmd == "lv":
            print("Level is", gv.get_level_number())
        elif cmd == 'j':
            tl = int(input("Tower location: "))
            l = atd_bot.LOC_MAP[tl]
            o = gv.game_offset
            m = l[0] + o[0], l[1] + o[1]
            atd_bot.mmove(m)
            
    print('End.')
