import pickle

def save(game, filename):
    if len(filename) <= 1:
        return "Need a filename to save to!"

    with open(filename[1:], mode='wb') as save_file:
        pickle.dump(game, save_file)

    return "Saved to " + filename[1:]

def load(game, filename):
    if len(filename) <= 1:
        return "Need a filename to load from!"

    with open(filename[1:], mode='rb') as save_file:
        loaded = pickle.load(save_file)
        game.__dict__.update(loaded.__dict__)

    return "Game loaded from " + filename[1:]

def look(game, thing):
    if len(thing) > 1:
        thing = thing[1:]
        if thing in game.room.items:
            return game.room.items[thing].description
        else:
            return "Can't look at " + thing

    return game.room.describe()

def change_room(game, direction):
    if game.room is None:
        return "Oops, you're not on the map. You should get that checked out."

    direction = direction[1:]
    if direction in game.room.nearby:
        game.room = game.rooms[game.room.nearby[direction]]
        return game.room.describe()
    else: 
        return "Can't go that way."

def get(game, item):
    item = item[1:]
    if item in game.room.items:
        i = game.room.items[item]
        game.player.inventory[i.name] = i
        del game.room.items[item]
        return "Got " + i.description
    else:
        return "Couldn't get " + item

def inventory(game, item):
    inventory = game.player.inventory

    if len(item) > 1:
        if item[1:] in inventory:
            return "Have got " + inventory[item[1:]].description
        else:
            return "Haven't got a " + item[1:]
    else:
        if len(inventory):
            ret = ["Inventory: \n"]
            for name,item in inventory.items():
                ret.append(item.description)
                ret.append(', ')
            ret[-1] = '. '
            return ''.join(ret)
        else:
            return "You haven't got any items."

def say(game, thing): 
    ret = []
    for npc in game.room.npcs:
        response, carry_on = npc.tell(thing)
        if response:
            ret.append(npc.name + ": " + response)
            if not carry_on:
                break

    return ''.join(ret)

def quit(game, thing):
    game.done = True
    return "Bye!"

def unknown_command(game, command):
    return "Hey, " + command  + " isn't a command!"

