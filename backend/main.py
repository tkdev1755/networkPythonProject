import os
import sys
import argparse
import curses
import config
from Players import Player
#from Mod_Game_Engine import Mod_GameEngine

norj = input("Tape n pour créer une partie et j pour join :")

if norj =='n' :

    # Ajouter le chemin du projet à sys.path pour ne pas avoir à le faire dans le terminal
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    sys.path.append(project_root)

    from backend.Starter_File import start_menu

    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description="Launch game with or without save and debug mode.")
        parser.add_argument(
            "-s", "--save", 
            type=str, 
            help="Path to save file (optional)."
        )
        parser.add_argument(
            "-d", "--debug", 
            action="store_true", 
            default=False, 
            help="Enable debug mode (default=False)."
        )
        args = parser.parse_args()
        config.debug_mode = args.debug
        start_menu(save_file=args.save)

else :
    players = []
    GameMode = "Utopia"
    map_size = (120,120)
    num_players = 2
    player1 = Player(
                        f'Player 1',
                        None,
                        None,
                        player_id=1
                    )
    player2 = Player(
                        f'Player 2',
                        None,
                        None,
                        player_id=2
                    )
    players.append(player1)
    players.append(player2)
    curses.wrapper(lambda stdscr: Mod_GameEngine(
                    game_mode=GameMode,
                    map_size=map_size,
                    players=players,
                    sauvegarde=False
                ).run(stdscr))
    

