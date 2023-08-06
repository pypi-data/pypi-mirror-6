from gazebo.commands import unknown_command
import re

class Game:
    """
    The game object. Handles setup, user interaction, etc.
    Subclass and implement additional methods to make your game.
    """

    done = False # Set to True to end the game
    room = None # Contains a Room that is the current room
    prompt = '> ' 
    
    def __init__(self, player, commands, rooms, room):
        """
        player: An instance of Player.
        commands: A dict of ("typed command", function_name). Look in command.py for more details on command functions.
        rooms: A dict of ("short name", Room instance). The short name is used to refer to rooms internally.
        room: A Room instance, probably from rooms. This is the room where you start.
        """
        self.player = player
        self.commands = commands
        self.rooms = rooms
        self.room = room

    def get_input(self):
        """ Prompt user for actions """
        command = input(self.prompt)
        self.process_command(command)

    def process_command(self, command):
        """ Process commands from the user and hand off to the derived actions """
        for key, action in self.commands.items():
            if command.startswith(key):
                output = action(self, command[len(key):])
                if output:
                    print(output)

                # store the last command run and its inputs, perhaps for use in self.upate()
                self.last_command = (action, key, command[len(key):])
                return

        output = unknown_command(self, command)
        if output:
            print(output)
        self.last_commnand = (unknown_command, '', command)

    def start(self):
        """ Called when the game starts. """
        pass

    def update(self):
        """ Called after every command. Use to update state and move stuff around """
        pass

    def run(self):
        self.start()
        while(not self.done):
            self.get_input()
            self.update()

class Room:
    """ 
    A Room. Tracks description, adjacent rooms, and contents.
    """
    
    def __init__(self, description, nearby, items, npcs):
        """
        description: The room description, printed out every time you look or enter a room.
        nearby: Nearby rooms. A dict of ("move command", "room short name").
        items: An array of Item objects that are in the room. 
        npcs: An array of NPC objects that are in the room.
        """

        self.description = description
        self.nearby = nearby
        self.items = self._make_dict(items)
        self.npcs = npcs

    def _make_dict(self, things):
        d = {}
        for thing in things:
            d[thing.name] = thing
        return d

    def describe(self):
        """ Describe the room, using nearby rooms, items, and npcs """
        ret = ['You are in ', self.description]

        if len(self.nearby):
            ret.append(' Obvious exits are ')
            for key in sorted(self.nearby.keys()):
                ret.append(key)
                ret.append(', ')
            ret[-1] = '.'

        if len(self.items):
            ret.append(' There is a ')
            for item in self.items.keys():
                ret.append(item)
                ret.append(', ')
            ret[-1] = '.'

        if len(self.npcs):
            ret.append("\n")
            for npc in self.npcs:
                ret.append(npc.name)
                ret.append(', ')
                ret.append(npc.description)
                ret.append('; ')
            ret[-1] = '.'

        return ''.join(ret)

class Item:
    """ 
    An item. 
    """
    def __init__(self, name, description):
        """
        name: The item name
        description: The description of the item
        """
        self.name = name
        self.description = description

class Player:
    """ 
    A player
    """

    def __init__(self, inventory = {}):
        """ 
        inventory: a dict of ("name", Item) pairs that the player has in their inventory
        """
        self.inventory = inventory

class NPC:
    """
    An NPC or enemy
    """
    def __init__(self, name, description, language):
        """
        name: The name of the npc.
        description: A description of the NPC. 
        language: A list of 3-tuples of ("regex", "response", True/False). 
            Regexes are matched in order. 
            The response is expanded with match groups from the regex, so it is possible to rudimentarily adaptively talk to the user.
            If the regex matches and the 3rd value is False, no more NPCs process the message. Otherwise, other NPCs in the room may receive the message.
        """

        self.name = name
        self.description = description
        self.language = []
        # Compile regexes for language
        for regex, response, carry_on in language:
            self.language.append((re.compile(regex), response, carry_on))

    def tell(self, thing):
        for regex, response, carry_on in self.language:
            match = regex.match(thing)
            if match:
                return (response % match.groups(), carry_on)

        return (None, True)

