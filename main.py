"""
COMP 163 - Project 3: Quest Chronicles
Main Game Module - Starter Code

Name: Rayner Paulino-Payano

AI Usage: [Document any AI assistance used]

This is the main game file that ties all modules together.
Demonstrates module integration and complete game flow.
"""

import character_manager
import inventory_system
import quest_handler
import combat_system
import game_data
from custom_exceptions import *

current_character = None
all_quests = {}
all_items = {}
game_running = False

def main_menu():
    print("\n=== MAIN MENU ===")
    print("1. New Game")
    print("2. Load Game")
    print("3. Exit")
    
    try:
        choice = int(input("Enter choice (1-3): "))
        if 1 <= choice <= 3:
            return choice
        print("Invalid choice.")
    except ValueError:
        print("Please enter a number.")
    return 0

def new_game():
    global current_character, game_running
    
    print("\n=== NEW GAME ===")
    name = input("Enter character name: ")
    
    print("Classes: Warrior, Mage, Rogue, Cleric")
    char_class = input("Choose class: ").capitalize()
    
    try:
        current_character = character_manager.create_character(name, char_class)
        print(f"Character {name} created successfully!")
        character_manager.save_character(current_character)
        game_loop()
    except InvalidCharacterClassError as e:
        print(f"Error creating character: {e}")

def load_game():
    global current_character
    
    print("\n=== LOAD GAME ===")
    saved_chars = character_manager.list_saved_characters()
    
    if not saved_chars:
        print("No saved games found.")
        return

    print("Saved Characters:")
    for name in saved_chars:
        print(f"- {name}")
        
    name = input("Enter character name to load: ")
    
    try:
        current_character = character_manager.load_character(name)
        print(f"Loaded {name} successfully!")
        game_loop()
    except (CharacterNotFoundError, SaveFileCorruptedError, InvalidSaveDataError) as e:
        print(f"Error loading game: {e}")

def game_loop():
    global game_running, current_character
    
    game_running = True
    
    while game_running:
        if current_character['health'] <= 0:
            handle_character_death()
            if not game_running:
                break
                
        choice = game_menu()
        
        if choice == 1:
            view_character_stats()
        elif choice == 2:
            view_inventory()
        elif choice == 3:
            quest_menu()
        elif choice == 4:
            explore()
        elif choice == 5:
            shop()
        elif choice == 6:
            save_game()
            game_running = False
            print("Game saved. Returning to main menu.")

def game_menu():
    print(f"\n=== GAME MENU ({current_character['name']}) ===")
    print("1. View Character Stats")
    print("2. View Inventory")
    print("3. Quest Menu")
    print("4. Explore (Find Battles)")
    print("5. Shop")
    print("6. Save and Quit")
    
    try:
        choice = int(input("Enter choice (1-6): "))
        if 1 <= choice <= 6:
            return choice
        print("Invalid choice.")
    except ValueError:
        print("Please enter a number.")
    return 0

def view_character_stats():
    global current_character
    print(f"\n=== STATS: {current_character['name']} ===")
    print(f"Class: {current_character['class']}")
    print(f"Level: {current_character['level']}")
    print(f"XP: {current_character['experience']}")
    print(f"Health: {current_character['health']}/{current_character['max_health']}")
    print(f"Strength: {current_character['strength']}")
    print(f"Magic: {current_character['magic']}")
    print(f"Gold: {current_character['gold']}")
    
    if 'equipped_weapon' in current_character and current_character['equipped_weapon']:
        w_id = current_character['equipped_weapon']
        w_name = all_items[w_id]['name'] if w_id in all_items else w_id
        print(f"Weapon: {w_name}")
        
    if 'equipped_armor' in current_character and current_character['equipped_armor']:
        a_id = current_character['equipped_armor']
        a_name = all_items[a_id]['name'] if a_id in all_items else a_id
        print(f"Armor: {a_name}")
        
    quest_handler.display_character_quest_progress(current_character, all_quests)

def view_inventory():
    global current_character, all_items
    
    while True:
        inventory_system.display_inventory(current_character, all_items)
        print("\n1. Use Item")
        print("2. Equip Weapon")
        print("3. Equip Armor")
        print("4. Unequip Weapon")
        print("5. Unequip Armor")
        print("6. Back")
        
        choice = input("Choice: ")
        
        if choice == "6":
            break
            
        if choice in ["1", "2", "3"]:
            item_id = input("Enter item ID: ")
            if item_id not in all_items:
                print("Unknown item ID.")
                continue
            
            item_data = all_items[item_id]
            
            try:
                if choice == "1":
                    msg = inventory_system.use_item(current_character, item_id, item_data)
                    print(msg)
                elif choice == "2":
                    msg = inventory_system.equip_weapon(current_character, item_id, item_data)
                    print(msg)
                elif choice == "3":
                    msg = inventory_system.equip_armor(current_character, item_id, item_data)
                    print(msg)
            except (ItemNotFoundError, InvalidItemTypeError, InventoryFullError) as e:
                print(f"Error: {e}")
                
        elif choice == "4":
            try:
                item = inventory_system.unequip_weapon(current_character)
                if item:
                    print(f"Unequipped {item}")
                else:
                    print("No weapon equipped.")
            except InventoryFullError as e:
                print(f"Error: {e}")
                
        elif choice == "5":
            try:
                item = inventory_system.unequip_armor(current_character)
                if item:
                    print(f"Unequipped {item}")
                else:
                    print("No armor equipped.")
            except InventoryFullError as e:
                print(f"Error: {e}")

def quest_menu():
    global current_character, all_quests
    
    while True:
        print("\n=== QUEST MENU ===")
        print("1. View Active Quests")
        print("2. View Available Quests")
        print("3. View Completed Quests")
        print("4. Accept Quest")
        print("5. Abandon Quest")
        print("6. Complete Quest (Test Mode)")
        print("7. Back")
        
        choice = input("Choice: ")
        
        if choice == "7":
            break
            
        if choice == "1":
            active = quest_handler.get_active_quests(current_character, all_quests)
            quest_handler.display_quest_list(active)
            
        elif choice == "2":
            available = quest_handler.get_available_quests(current_character, all_quests)
            quest_handler.display_quest_list(available)
            
        elif choice == "3":
            completed = quest_handler.get_completed_quests(current_character, all_quests)
            quest_handler.display_quest_list(completed)
            
        elif choice == "4":
            quest_id = input("Enter Quest ID to accept: ")
            try:
                if quest_handler.accept_quest(current_character, quest_id, all_quests):
                    print("Quest accepted!")
            except (QuestNotFoundError, InsufficientLevelError, QuestRequirementsNotMetError, QuestAlreadyCompletedError) as e:
                print(f"Cannot accept quest: {e}")
                
        elif choice == "5":
            quest_id = input("Enter Quest ID to abandon: ")
            try:
                quest_handler.abandon_quest(current_character, quest_id)
                print("Quest abandoned.")
            except QuestNotActiveError:
                print("Quest not active.")
                
        elif choice == "6":
            quest_id = input("Enter Quest ID to force complete: ")
            try:
                rewards = quest_handler.complete_quest(current_character, quest_id, all_quests)
                print(f"Quest completed! Gained {rewards['xp']} XP and {rewards['gold']} Gold.")
            except (QuestNotFoundError, QuestNotActiveError) as e:
                print(f"Error: {e}")

def explore():
    global current_character
    
    if not combat_system.can_character_fight(current_character):
        print("You are too weak to fight!")
        return
        
    enemy = combat_system.get_random_enemy_for_level(current_character['level'])
    battle = combat_system.SimpleBattle(current_character, enemy)
    
    try:
        result = battle.start_battle()
        
        if result['winner'] == 'player':
            print("\nVICTORY!")
            print(f"Gained {result['xp_gained']} XP and {result['gold_gained']} Gold.")
            character_manager.gain_experience(current_character, result['xp_gained'])
            character_manager.add_gold(current_character, result['gold_gained'])
        elif result['winner'] == 'escaped':
            print("\nYou ran away safely.")
        else:
            print("\nDEFEAT!")
            
    except CharacterDeadError:
        print("You have fallen in battle.")

def shop():
    global current_character, all_items
    
    print("\n=== ITEM SHOP ===")
    print(f"Your Gold: {current_character['gold']}")
    print("Available Items:")
    for item_id, item in all_items.items():
        print(f"- {item['name']} ({item['type']}): {item['cost']} Gold (ID: {item_id})")
        
    print("\n1. Buy Item")
    print("2. Sell Item")
    print("3. Back")
    
    choice = input("Choice: ")
    
    if choice == "1":
        item_id = input("Enter Item ID to buy: ")
        if item_id in all_items:
            try:
                inventory_system.purchase_item(current_character, item_id, all_items[item_id])
                print("Purchase successful!")
            except (InsufficientResourcesError, InventoryFullError) as e:
                print(f"Purchase failed: {e}")
        else:
            print("Item not found.")
            
    elif choice == "2":
        item_id = input("Enter Item ID to sell: ")
        if item_id in all_items:
            try:
                gold = inventory_system.sell_item(current_character, item_id, all_items[item_id])
                print(f"Sold for {gold} gold.")
            except ItemNotFoundError as e:
                print(f"Sale failed: {e}")
        else:
            print("Invalid item ID.")

def save_game():
    global current_character
    try:
        character_manager.save_character(current_character)
    except Exception as e:
        print(f"Error saving game: {e}")

def load_game_data():
    global all_quests, all_items
    all_quests = game_data.load_quests()
    all_items = game_data.load_items()

def handle_character_death():
    global current_character, game_running
    
    print("\n=== YOU HAVE DIED ===")
    print("1. Revive (Lose 50% Health, Keep items)")
    print("2. Quit to Main Menu")
    
    choice = input("Choice: ")
    if choice == "1":
        character_manager.revive_character(current_character)
        print("You have been revived.")
    else:
        game_running = False
        current_character = None

def display_welcome():
    print("=" * 50)
    print("     QUEST CHRONICLES - A MODULAR RPG ADVENTURE")
    print("=" * 50)
    print("\nWelcome to Quest Chronicles!")
    print("Build your character, complete quests, and become a legend!")
    print()

def main():
    display_welcome()
    
    try:
        load_game_data()
        print("Game data loaded successfully!")
    except MissingDataFileError:
        print("Creating default game data...")
        game_data.create_default_data_files()
        try:
            load_game_data()
        except Exception:
            print("Critical error creating defaults.")
            return
    except (InvalidDataFormatError, CorruptedDataError) as e:
        print(f"Error loading game data: {e}")
        return
    
    while True:
        choice = main_menu()
        
        if choice == 1:
            new_game()
        elif choice == 2:
            load_game()
        elif choice == 3:
            print("\nThanks for playing Quest Chronicles!")
            break

if __name__ == "__main__":
    main()