import os
from settings import cls
import db
 
def menu():
    os.system(cls)
    while 1:
        print("Menu")
        print("[1]: Add Bot")
        print("[2]: Display Bots")
        print("[3]: Start Bot")
        print("[4]: Delete Bot")
        print("[0]: Exit\n")
        option = int(input("-> "))

        if option > 4 or option < 0:
            os.system(cls)
            print("Invalid option\n")
            continue
        else:
            if option == 1: menu_add()
            elif option == 2: menu_show()
            elif option == 3: return menu_start()
            elif option == 4: menu_delete()
            elif option == 0: exit()

def menu_delete():
    bots= db.get_bots_names()
    os.system(cls)
    if len(bots) <= 0:
        print("No bots available, add a bot first!")
        return
    
    bots = db.get_bots_full()

    while 1:
        print("Select a bot to delete")
        for i, bot in enumerate(bots):
            print("[{}]:{}".format(i,bot[1]))

        option = int(input("-> "))
        if option < 0 or option > i:            
            os.system(cls)
            print("Invalid option!")
            continue

        os.system(cls)
        print("ARE YOU SURE YOU WANT TO DELETE \'"+ bots[option][1]+"\'?")
        print("True\\False")
        delete = input("-> ").lower()
        if delete.lower() == "true" or delete.lower() == "y":
            db.delete_bot(id = bots[option][0])
            os.system(cls)
            return

def menu_start():
    bots= db.get_bots_names()
    os.system(cls)
    if len(bots) <= 0:
        print("No bots available, add a bot first!")
        return
    
    bots = db.get_bots_full()

    while 1:
        print("Select a bot")
        for i, bot in enumerate(bots):
            print("[{}]:{}".format(i,bot[1]))
        
        option = int(input("-> "))
        if option < 0 or option > i:            
            os.system(cls)
            print("Invalid option!")
            continue
        
        return bots[option]

def menu_select():
    os.system(cls)
    x = 0
    bots = db.get_bots_names()
    while 1:
        if bots is not None and len(bots) != 0 :
            for i in bots:
                print("["+ str(x) + "]: " + i[1])
                x = x+1
            option = int(input("Select a bot"))
            if option > x or option < 0:
                os.system(cls)
                print("Invalid bot id!\n")
            else: 
                return bots[option][1]
        else:
            os.system(cls)
            print("There Are no bots added yet :( ")
            return None
        
def menu_add():
    os.system(cls)
    print("Add a Bot")
    print("---------")
    name = input("Name: ")
    token = input("Token: ")
    app_id = input("App id: ")
    db.add_bot(name, token,app_id)
    os.system(cls)
    print("The bot has been successfully added!\n")
    return True

def menu_show():
    os.system(cls)
    x = 0
    bots = db.get_bots_names()
    while 1:
        if bots is not None and len(bots) != 0 :
            for i in bots:
                print("["+ str(x) + "]: " + i[1])
                x = x+1
            print("")
            input("Press Enter to exit")
            os.system(cls)
            break
        else:
            os.system(cls)
            print("There Are no bots added yet :( ")
            return

