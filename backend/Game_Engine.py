import curses
import random
import time
import pickle
import os
import tkinter as tk

from queue import Queue

from backend.Players import Player
from frontend.gui import GUI

from logger import debug_print
from Units import *
from Building import *
from Actions import *
from frontend.Terrain import Map
try:
    from frontend import gui
    USE_PYGAME = True
except ImportError:
    USE_PYGAME = False
    debug_print("Pygame not installed; running without Pygame features such as 2.5D map view.")

from html_report import generate_html_report

from IA import IA

from zReseau import *

'''
    Log modifications
    24/05/25@tkdev1755 : Changé les appels des fonctions send_message et recvFrom vers des appels de méthodes de la classe NetworkEngine
    24/05/25@tkdev1755 : Changé la manière dont le networkEngine est initialisé
    24/05/25@tkdev1755 : Ajouté un attribut networkGame et joinNetworkGame pour gérer une partie en réseau et activer les fonctionnalités liées à celle-ci
    25/05/25@tkdev1755 : Ajouté un attribut netName à la classe player

'''

# GameEngine Class
class GameEngine:
    def __init__(self, game_mode, map_size, players, sauvegarde=False,networkEngine=None,networkGame=False, joinNetworkGame=False,messageDecoder=None, joinIndex=-1):
        self.game_mode = game_mode
        self.map_size = map_size
        self.players = players
        self.map = Map(*map_size)  # Create a map object
        self.turn = 0
        self.is_paused = False  # Flag to track if the game is paused
        self.changed_tiles = set()  # Set to track changed tiles
        self.networkEngine = networkEngine
        self.networkGame = networkGame
        self.joinNetworkGame = joinNetworkGame
        self.messageDecoder = messageDecoder
        self.joinIndex = joinIndex
        # IA related attributes
        # If the player doesn't join another client game on the network, or doesn't play online, initialize the AIs normally
        if not joinNetworkGame:
            self.ias = [IA(player, player.ai_profile, self.map, time.time()) for player in self.players]  # Instantiate IA for each player
            for i in range(len(self.players)):
                self.players[i].ai = self.ias[i]
            self.IA_used = False
        else:
            print(f"IA from join, players are {self.players}")
            self.ias = [IA(player, player.ai_profile, self.map, time.time()) for player in self.players]  # Instantiate IA for each player
            for i in range(len(self.players)):
                self.players[i].ai = self.ias[i]
            self.IA_used = False
            pass

        # Sauvegarde related attributes
        if not sauvegarde and not joinNetworkGame:
            Building.place_starting_buildings(self.map)   # Place starting town centers on the map
            Unit.place_starting_units(self.players, self.map)  # Place starting units on the map
        elif joinNetworkGame and joinIndex != -1:
            print("Overriding building placement")
            Building.place_starting_buildings(self.map, override=self.joinIndex)
            Unit.place_starting_units(self.players, self.map)  # Place starting units on the map
        self.debug_print = debug_print
        self.current_time = time.time()

        self.terminalon = True

        # GUI thread related attributes
        self.gui_running = False
        self.data_queue = Queue()
        self.gui_thread = None

    def initMessageDecoder(self):
        if self.networkEngine is None:
            self.debug_print("[initMessageDecoder]--- Waiting for networkEngine to be initialized ")
        else:
            self.messageDecoder = MessageDecoder(self, self.networkEngine)

    def initNetworkEngine(self):
        if self.networkEngine is None:
            self.networkEngine = NetworkEngine()
            self.networkEngine.create_socket()
            self.networkEngine.gameEngine = self
        elif self.networkEngine.socket is None:
            self.networkEngine.create_socket()
            self.networkEngine.gameEngine = self
        else:
            self.networkEngine.gameEngine = self

    def start_gui_thread(self):
        """Initialize and start the GUI thread"""
        if not self.gui_thread:
            self.data_queue = Queue()
            self.gui_thread = GUI(self.data_queue)
            self.gui_thread.start()
            self.gui_running = True

    def stop_gui_thread(self):
        """Stop the GUI thread safely"""
        if self.gui_thread:
            #self.gui_thread.stop()
            self.gui_thread = None
            self.gui_running = False

    def update_gui(self):
        """Send current game state to GUI thread"""
        if self.gui_running and not self.data_queue.full():
            self.data_queue.put(self)

    def get_current_time(self):
        """Retourne le temps actuel si le jeu n'est pas en pause"""
        if not self.is_paused:
            return time.time()
        return self.current_time

    #fonction pour interpréter un message 


    def move_by_id(self,id,data): #juste, remplace la position de l'unité d'id id par position 
        pos = (float(data[0]),float(data[1]))
        for player in self.players:
            print(player.units)
            if player.netName == data[2] :
                for unit in player.units :
                    if unit.id == id :
                        unit.position = pos
                        return

        #newguy =Unit.spawn_unit(Villager,int(float(pos[0])),int(float(pos[1])),self.players[int(data[2])-1],self.map)
        #newguy.id = int(id)
        #print(newguy.id)
        newguy = self.custom_spawn(pos, data[2])
        newguy.id = int(id)
        print("Unit had spawned")

    def set_building_by_id(self,id,data): #action,id,(player.id,name,x,y)
        string=data[1][2:-1]
        for player in self.players:
            if player.netName == data[0] :
                for building in player.buildings :
                    if building.id == id :
                        return #building aleady exists
                if string == "TownCenter":
                    this_class=Keep
                elif string == "House":
                    this_class=House
                elif string == "Camp":
                    this_class=Camp
                elif string == "Farm":
                    this_class=Farm
                elif string == "Barracks":
                    this_class=Barracks
                elif string == "Stable":
                    this_class=Stable
                elif string == "ArcheryRange":
                    this_class=ArcheryRange
                else:
                    print("problèmes lecture classe batiment:",string)
                    return
                building_instance = TownCenter(self.players[int(data[0])-1])
                newbuild = Building.spawn_building(self.players[int(data[0])-1],int(data[2]),int(data[3]),this_class,self.map)
                newbuild.id = int(id)
                print(newbuild.id)

        for player in self.players:
            if player.netName is None:
                player.netName = data[0]
                if string == "TownCenter":
                    this_class=Keep
                elif string == "House":
                    this_class=House
                elif string == "Camp":
                    this_class=Camp
                elif string == "Farm":
                    this_class=Farm
                elif string == "Barracks":
                    this_class=Barracks
                elif string == "Stable":
                    this_class=Stable
                elif string == "ArcheryRange":
                    this_class=ArcheryRange
                else:
                    print("problèmes lecture classe batiment:",string)
                    return
                building_instance = TownCenter(self.players[int(data[0])-1])
                newbuild = Building.spawn_building(self.players[int(data[0])-1],int(data[2]),int(data[3]),this_class,self.map)
                newbuild.id = int(id)
                print(newbuild.id)

    def set_resource_by_position(self,id,data): #action,id,(x,y,ressource,amount) ,self.map.grid[y][x] pour avoir la tuile, 
        x,y = int(data[0]),int(data[1])
        amount = float(data[3])
        string = data[2][2:-1]
        if string == 'None':
            self.map.grid[y][x].resource = None
        elif string == 'Wood':
            self.map.grid[y][x].resource = Wood()
            self.map.grid[y][x].resource.type = "Wood"
            self.map.grid[y][x].resource.amount = amount
            self.map.resources["Wood"].append((x, y))
        elif data[2] == "Gold":
            self.map.grid[y][x].resource = Gold()
            self.map.grid[y][x].resource.type = "Gold"
            self.map.grid[y][x].resource.amount = amount
        elif data[2] == "Food":
            self.map.grid[y][x].resource = Food()
            self.map.grid[y][x].resource.amount = amount
            self.map.resources["Food"].append((x,y))
        else:
            print("set_resource problème lecture data:",data[2])

    def send_world_size(self):
        #message = MessageDecoder.create_message("SendSize",0,(self.map.width,self.map.height))
        # Ligne ci-dessus non nécessaire -> Une méthode existe déjà dans le NetworkEngine pour envoyer la taille
        #self.networkEngine.send_size(map_size)
        pass

    def custom_spawn (self,pos,name):
        #print(self.players)
        for player in self.players :
            if player.netName == name:
                unit = Villager(player,(pos[0],pos[1]))
                player.units.append(unit)
                unit.position = (pos[0],pos[1])
                player.population += 1
                self.map.place_unit(int(pos[0]),int(pos[1]), unit)
                print("I return unit")
                return unit
        for player in self.players:
            if player.netName is None:
                player.netName = name
                unit = Villager(player, (pos[0], pos[1]))
                player.units.append(unit)
                unit.position = (pos[0], pos[1])
                player.population += 1
                self.map.place_unit(int(pos[0]), int(pos[1]), unit)
                return unit

    def initDummyPlayers(self):
        for i in range(3):
            pl = Player(f"Dumb Player {i+2}", "Leans", "Aggressive", i+2)
            self.players.append(pl)
        pass

    def run(self, stdscr):
        # Initialize the starting view position
        top_left_x, top_left_y = 0, 0
        viewport_width, viewport_height = 30, 30
        # Display the initial viewport
        #Initialize correctly Networkengine and MessageDecoder to ensure there will be no bug
        self.initNetworkEngine()
        self.initMessageDecoder()
        self.initDummyPlayers()
        self.players[0].netName = self.networkEngine.name # par définition le player 1 est le joueur local
        stdscr.clear()  # Clear the screen

        if self.terminalon :
            self.map.display_viewport(stdscr, top_left_x, top_left_y, viewport_width, viewport_height, Map_is_paused=self.is_paused)  # Display the initial viewport

        #Creates a socket

        try:
            while not self.check_victory():
                # Mettre à jour current_time au début de chaque itération si le jeu n'est pas en pause
                if not self.is_paused:
                    self.current_time = time.time()

                # Handle input
                curses.curs_set(0)  # Hide cursor
                stdscr.nodelay(True)  # Make getch() non-blocking
                key = stdscr.getch()  # Get the key pressed by the user
                action = Action(self.map)

                if key == curses.KEY_UP or key == ord('z'):
                    top_left_y = max(0, top_left_y - 1)
                elif key == curses.KEY_DOWN or key == ord('s'):
                    top_left_y = min(self.map.height - viewport_height, top_left_y + 1)
                elif key == curses.KEY_LEFT or key == ord('q'):
                    top_left_x = max(0, top_left_x - 1)
                elif key == curses.KEY_RIGHT or key == ord('d'):
                    top_left_x = min(self.map.width - viewport_width, top_left_x + 1)
                elif key == ord('Z'):
                    top_left_y = max(0, top_left_y - 5)
                elif key == ord('S'):
                    top_left_y = min(self.map.height - viewport_height, top_left_y + 5)
                elif key == ord('Q'):
                    top_left_x = max(0, top_left_x - 5)
                elif key == ord('D'):   
                    top_left_x = min(self.map.width - viewport_width, top_left_x + 5)

                ###### TEST KEYS #######

                elif key == ord('r'):
                    self.debug_print(self.players[0].buildings[0].position)
                    self.debug_print(action.get_adjacent_positions(self.players[0].buildings[0].position[0], self.players[0].buildings[0].position[1], self.players[0].buildings[0].size))
                elif key == ord('o'):
                    self.terminalon = not self.terminalon   
                elif key == ord('i'):
                    action.construct_building(self.players[2].units[1], Keep, 10, 10, self.players[2], self.get_current_time())
                    action.move_unit(self.players[1].units[1],15,15,self.get_current_time())
                elif key == ord('u'):
                    Building.kill_building(self.players[0], self.players[0].buildings[0], self.map)
                elif key == ord('y'):
                    Building.kill_building(self.players[0], self.players[0].buildings[-1], self.map)
                elif key == ord('t'):
                    self.players[0].owned_resources["Wood"] = 100


                #########################

                ###### CHEAT KEYS #######

                elif key == ord('g'):
                    self.players[0].owned_resources["Gold"] += 5000
                elif key == ord('w'):
                    self.players[0].owned_resources["Wood"] += 5000
                elif key == ord('f'):
                    self.players[0].owned_resources["Food"] += 5000
                elif key == ord('h'):
                    for player in self.players:
                        player.owned_resources["Gold"] = 0
                        player.owned_resources["Wood"] = 0
                        player.owned_resources["Food"] = 0

                #########################


                elif key == curses.KEY_F9:
                    if not self.gui_running:
                        self.start_gui_thread()
                    else:
                        self.stop_gui_thread()
                        stdscr.clear()
                        stdscr.refresh()
                        continue
                elif key == ord('\t'):  # TAB key
                    generate_html_report(self.players)
                    self.debug_print(f"HTML report generated at turn {self.turn}")
                    if self.is_paused == False:
                        self.is_paused = True
                        self.debug_print("Game paused.")
                elif key == ord('p'):
                    self.is_paused = not self.is_paused
                    if self.is_paused:
                        self.debug_print("Game paused.")
                    else:
                        self.debug_print("Game resumed.")

                elif key == ord('n'):
                        self.IA_used = not self.IA_used
                        self.debug_print(f"IA used: {self.IA_used}")

                elif key == curses.KEY_F10: 
                    self.save_game()
                elif key == curses.KEY_F12:
                    # Find the latest save file in the directory
                    save_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'annex')
                    save_files = [f for f in os.listdir(save_dir) if f.endswith('.dat')]
                    if save_files:
                        latest_save_file = max(save_files, key=lambda f: os.path.getctime(os.path.join(save_dir, f)))
                        latest_save_path = os.path.join(save_dir, latest_save_file)
                        self.load_game(latest_save_path)
                    else:
                        self.debug_print("No save files found.")

                #check for any messages received
                #message = create_message("SetUnit",3,(32,32,2))
                #self.interpret_message(message)
            
                try:
                    data= self.networkEngine.recvMessage()
                    print("received message: %s" % data)
                    self.messageDecoder.interpret_message(data.decode('utf-8'))
                except BlockingIOError:
                    pass
                except ConnectionResetError:
                    pass
                """ except Exception as e:
                    print("Exception lors de la réception d'une data ! : ",e)
                    raise Exception("Problems")"""

                #call the AI if the player didn't join another client game on the network
                if not self.joinNetworkGame:
                    if not self.is_paused and self.turn % 200 == 0 and self.IA_used == True: # Call the IA every 5 turns: change 0, 5, 10, 15, ... depending on lag
                        for ia in self.ias:
                            ia.current_time_called = self.get_current_time()  # Update the current time for each IA
                            ia.run()  # Run the AI logic for each player
                else:
                    # Manage the case when the client joined another game on the network
                    if not self.is_paused and self.turn % 200 == 0 and self.IA_used == True: # Call the IA every 5 turns: change 0, 5, 10, 15, ... depending on lag
                        ia = self.ias[0]
                        ia.current_time_called = self.get_current_time()  # Update the current time for each IA
                        ia.run()
                        if ia.noActionsToDo:
                            randomTile = (random.randint(0,self.map_size[0]), random.randint(0,self.map_size[1]))
                            self.debug_print(f"AI Has nothing to do so we need to ask for a random tile on the map, position is {randomTile}")
                            #self.networkEngine.askForProperty(randomTile)


                if not self.is_paused and self.turn % 10 == 0:
                    # Move units toward their target position
                    for player in self.players:
                        if player.netName == self.networkEngine.name:
                            for unit in player.units:
                                if unit.task == "going_to_battle":
                                    action.go_battle(unit, unit.target_attack, self.get_current_time())
                                elif unit.task == "attacking":
                                    action._attack(unit, unit.target_attack, self.get_current_time())
                                    message = MessageDecoder.create_message("SetUnitHealth", unit.id, (unit.hp, player.netName))
                                    self.networkEngine.send_message(message)
                                    print(message)
                                elif unit.target_position:
                                    target_x, target_y = unit.target_position
                                    action.move_unit(unit, target_x, target_y, self.get_current_time())
                                    #envoyer "Set;ID;Data" pour indiquer le nouvel emplacement
                                    message=MessageDecoder.create_message("SetUnit", unit.id, (unit.position[0],unit.position[1],player.netName))
                                    self.networkEngine.send_message(message)
                                    print(message)
                                elif unit.task == "gathering" or unit.task == "returning":
                                    x,y = unit.target_resource #target_resource est une position, ligne ajoutée par moi
                                    action._gather(unit, unit.last_gathered, self.get_current_time())
                                    #envoyer "SetResource;ID;Data" pour indiquer l'état de la ressource, data=(x,y,ressource,amount)
                                    this_tile = self.map.grid[y][x]
                                    if this_tile.resource == None:
                                        message= MessageDecoder.create_message("SetResource",this_tile.id,(x,y,"None",0))
                                    else:
                                        message= MessageDecoder.create_message("SetResource",this_tile.id,(x,y,this_tile.resource.type,this_tile.resource.amount))
                                    self.networkEngine.send_message(message) # Remplace le send_message(message, self.networkEngine.socket)
                                    print(message)
                                elif unit.task == "marching":
                                    x,y = unit.target_resource #target_resource est une position, ligne ajoutée par moi
                                    action.gather_resources(unit, unit.last_gathered, self.get_current_time())
                                    #envoyer "SetResource;ID;Data" pour indiquer l'état de la ressource, data=(x,y,ressource,amount)
                                    this_tile = self.map.grid[y][x]
                                    if this_tile.resource == None:
                                        message= MessageDecoder.create_message("SetResource",this_tile.id,(x,y,"None",0))
                                    else:
                                        message= MessageDecoder.create_message("SetResource",this_tile.id,(x,y,this_tile.resource.type,this_tile.resource.amount))
                                    self.networkEngine.send_message(message) # Remplace le send_message(message, self.networkEngine.socket)
                                    print(message)
                                elif unit.task == "is_attacked":
                                    action._attack(unit, unit.is_attacked_by, self.get_current_time())
                                elif unit.task == "going_to_construction_site":
                                    action.construct_building(unit, unit.construction_type, unit.target_building[0], unit.target_building[1], player, self.get_current_time())
                                elif unit.task == "constructing":
                                    action._construct(unit, unit.construction_type, unit.target_building[0], unit.target_building[1], player, self.get_current_time())
                            for building in player.buildings:
                                #envoie le building pendant dix tours à la création, le renverra de temps en temps
                                if building.sent_count: #action,id,(player.id,name,x,y)
                                    message= MessageDecoder.create_message("SetBuilding", building.id, (building.player.id,building.name,building.position[0],building.position[1]))
                                    self.networkEngine.send_message(message)
                                    building.sent_count -= 1
                                    print(message)

                                if hasattr(building, 'training_queue') and building.training_queue != []:
                                    unit = building.training_queue[0]
                                    Unit.train_unit(unit, unit.spawn_position[0], unit.spawn_position[1], player, unit.spawn_building, self.map, self.get_current_time())
                                """elif type(building).__name__ == "Keep":
                                    nearby_enemies = IA.find_nearby_enemies(building.player.ai, max_distance=building.range, unit_position=building.position)  # 5 tile radius
                                    if nearby_enemies:
                                        closest_enemy = min(nearby_enemies,
                                            key=lambda e: IA.calculate_distance(building.player.ai, pos1=unit.position, pos2=e.position))
                                        action.attack_target(building, target=closest_enemy, current_time_called=self.current_time, game_map=self.map)
                                    else:
                                        building.target = None"""

                # Clear the screen and display the new part of the map after moving
                stdscr.clear()
                if self.terminalon :
                    self.map.display_viewport(stdscr, top_left_x, top_left_y, viewport_width, viewport_height, Map_is_paused=self.is_paused)
                stdscr.refresh()

                if self.gui_running:
                    self.update_gui()

                self.turn += 1

            active_players = [p for p in self.players if p.units or p.buildings]
            self.debug_print(f"Player {active_players[0].name} wins the game!", 'Magenta')
            input("Press Enter to exit...")

        except KeyboardInterrupt:
            self.networkEngine.socket.close()
            self.debug_print("Properly closing the socket",'Yellow')
            self.debug_print("Game interrupted. Exiting...", 'Yellow')
        finally:
            if self.gui_running:
                self.stop_gui_thread()

    def check_victory(self):
        if self.turn % 500 == 0: # Check if the game is over
            active_players = [p for p in self.players if p.units or p.buildings] # Check if the player has units and buildings
            return len(active_players) == -2 # Check if there is only one player left
        else:
            return False

    #condition de victoire: être le dernier joueur avec des bâtiments
    def victory(self):
    
        def big_text(text):
            root = tk.Tk()
            root.title("Texte en gros")
            label = tk.Label(root, text=text, font=("Arial", 48), padx=20, pady=20)
            label.pack(expand=True)
            root.mainloop()

        if GameEngine.check_victory(GameEngine.self) ==True:
            time.stop()
            GUI.load_image(GUI.IMG_PATH / "victory.png")
            big_text(f"Player {GameEngine.active_players[0].name} wins the game!")

    def pause_game(self):
        self.is_paused = not self.is_paused

    def save_game(self, filename=None):
        if not self.is_paused:
            self.is_paused = True
            self.debug_print("Game paused.")
        
        # Generate a filename if none is provided
        if filename is None:
            for i in range(10):  # Limit to 10 auto-saves
                filename = f"../assets/annex/game_save{i}.dat"
                if not os.path.exists(filename):  # Check if the file exists
                    break
            else:
                self.debug_print("No available slots to save the game.")
                return
        else:
            # If a filename is provided, add a unique suffix if necessary
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filename):
                filename = f"{base}_{counter}{ext}"
                counter += 1

        # Save the game state
        try:
            with open(filename, 'wb') as f:
                game_state = {
                    'players': self.players,
                    'map': self.map,
                    'turn': self.turn,
                    'is_paused': self.is_paused,
                    'changed_tiles': self.changed_tiles,
                    'ias': self.ias  # Add self.ias to the saved state
                }
                pickle.dump(game_state, f)
            self.debug_print(f"Game saved to {filename}.")
        except Exception as e:
            self.debug_print(f"Error saving game: {e}")


    def load_game(self, filename):
        if not self.is_paused:
            self.is_paused = True
            self.debug_print("Game paused.")
        try:
            with open(filename, 'rb') as f:
                game_state = pickle.load(f)
                self.players = game_state['players']
                self.map = game_state['map']
                self.turn = game_state['turn']
                self.is_paused = game_state['is_paused']
                self.changed_tiles = game_state['changed_tiles']
                self.ias = game_state.get('ias', None)  # Load self.ias or set it to None if missing
                self.current_time = time.time()
            self.debug_print(f"Game loaded from {filename}.")
        except Exception as e:
            self.debug_print(f"Error loading game: {e}")
            
    def update_unit_health(self, uid, data):
        """command like : "SetUnitHealth;ID;Data" and Data = (health,player.netName)"""
        for player in self.players:
            # print(player.units)
            if player.netName == data[1] :
                for unit in player.units :
                    if unit.id == uid :
                        unit.position = data[0]
                        return
