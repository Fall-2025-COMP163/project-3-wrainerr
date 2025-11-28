"""
COMP 163 - Project 3: Quest Chronicles
Character Manager Module - Starter Code

Name: Rayner Paulino-Payano

AI Usage: [Document any AI assistance used]

This module handles character creation, loading, and saving.
"""

import os
from custom_exceptions import (
    InvalidCharacterClassError,
    CharacterNotFoundError,
    SaveFileCorruptedError,
    InvalidSaveDataError,
    CharacterDeadError
)

# ============================================================================
# CHARACTER MANAGEMENT FUNCTIONS
# ============================================================================

def create_character(name, character_class):
    """
    Create a new character with stats based on class
    
    Valid classes: Warrior, Mage, Rogue, Cleric
    
    Returns: Dictionary with character data including:
            - name, class, level, health, max_health, strength, magic
            - experience, gold, inventory, active_quests, completed_quests
    
    Raises: InvalidCharacterClassError if class is not valid
    """
    valid_classes = {
        "Warrior": {"health": 120, "max_health": 120, "strength": 15, "magic": 5},
        "Mage": {"health": 80, "max_health": 80, "strength": 8, "magic": 20},
        "Rogue": {"health": 90, "max_health": 90, "strength": 12, "magic": 10},
        "Cleric": {"health": 100, "max_health": 100, "strength": 10, "magic": 15}
    }

    if character_class not in valid_classes:
        raise InvalidCharacterClassError(f"Invalid class: {character_class}")

    stats = valid_classes[character_class]
    
    return {
        "name": name,
        "class": character_class,
        "level": 1,
        "health": stats["health"],
        "max_health": stats["max_health"],
        "strength": stats["strength"],
        "magic": stats["magic"],
        "experience": 0,
        "gold": 100,
        "inventory": [],
        "active_quests": [],
        "completed_quests": []
    }

def save_character(character, save_directory="data/save_games"):
    """
    Save character to file
    
    Filename format: {character_name}_save.txt
    
    File format:
    NAME: character_name
    CLASS: class_name
    LEVEL: 1
    HEALTH: 120
    MAX_HEALTH: 120
    STRENGTH: 15
    MAGIC: 5
    EXPERIENCE: 0
    GOLD: 100
    INVENTORY: item1,item2,item3
    ACTIVE_QUESTS: quest1,quest2
    COMPLETED_QUESTS: quest1,quest2
    
    Returns: True if successful
    Raises: PermissionError, IOError (let them propagate or handle)
    """
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
    
    filename = f"{character['name']}_save.txt"
    filepath = os.path.join(save_directory, filename)
    
    try:
        with open(filepath, 'w') as file:
            file.write(f"NAME: {character['name']}\n")
            file.write(f"CLASS: {character['class']}\n")
            file.write(f"LEVEL: {character['level']}\n")
            file.write(f"HEALTH: {character['health']}\n")
            file.write(f"MAX_HEALTH: {character['max_health']}\n")
            file.write(f"STRENGTH: {character['strength']}\n")
            file.write(f"MAGIC: {character['magic']}\n")
            file.write(f"EXPERIENCE: {character['experience']}\n")
            file.write(f"GOLD: {character['gold']}\n")
            
            inventory_str = ",".join(map(str, character['inventory']))
            file.write(f"INVENTORY: {inventory_str}\n")
            
            active_str = ",".join(map(str, character['active_quests']))
            file.write(f"ACTIVE_QUESTS: {active_str}\n")
            
            completed_str = ",".join(map(str, character['completed_quests']))
            file.write(f"COMPLETED_QUESTS: {completed_str}\n")
            
        return True
    except (PermissionError, IOError) as e:
        raise e

def load_character(character_name, save_directory="data/save_games"):
    """
    Load character from save file
    
    Args:
        character_name: Name of character to load
        save_directory: Directory containing save files
    
    Returns: Character dictionary
    Raises: 
        CharacterNotFoundError if save file doesn't exist
        SaveFileCorruptedError if file exists but can't be read
        InvalidSaveDataError if data format is wrong
    """
    filename = f"{character_name}_save.txt"
    filepath = os.path.join(save_directory, filename)
    
    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"Character {character_name} not found.")
    
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
    except (PermissionError, IOError) as e:
        raise SaveFileCorruptedError(f"Could not read save file: {e}")

    character = {}
    int_fields = ["LEVEL", "HEALTH", "MAX_HEALTH", "STRENGTH", "MAGIC", "EXPERIENCE", "GOLD"]
    list_fields = ["INVENTORY", "ACTIVE_QUESTS", "COMPLETED_QUESTS"]
    
    try:
        for line in lines:
            # tolerate blank or malformed lines
            if ":" not in line:
                continue

            parts = line.split(":", 1)
            if len(parts) < 2:
                continue

            key = parts[0].strip()
            value = parts[1].strip()

            key_upper = key.upper()
            if key_upper in int_fields:
                character[key.lower()] = int(value)
            elif key_upper in list_fields:
                if value:
                    character[key.lower()] = [v for v in value.split(",") if v]
                else:
                    character[key.lower()] = []
            else:
                character[key.lower()] = value
        
        validate_character_data(character)
        return character
        
    except (ValueError, IndexError) as e:
        raise InvalidSaveDataError(f"Data format error: {e}")

def list_saved_characters(save_directory="data/save_games"):
    """
    Get list of all saved character names
    
    Returns: List of character names (without _save.txt extension)
    """
    if not os.path.exists(save_directory):
        return []
    
    saved_chars = []
    try:
        for filename in os.listdir(save_directory):
            if filename.endswith("_save.txt"):
                name = filename.replace("_save.txt", "")
                saved_chars.append(name)
        return saved_chars
    except OSError:
        return []

def delete_character(character_name, save_directory="data/save_games"):
    """
    Delete a character's save file
    
    Returns: True if deleted successfully
    Raises: CharacterNotFoundError if character doesn't exist
    """
    filename = f"{character_name}_save.txt"
    filepath = os.path.join(save_directory, filename)
    
    if not os.path.exists(filepath):
        raise CharacterNotFoundError(f"Character {character_name} not found.")
    
    try:
        os.remove(filepath)
        return True
    except OSError as e:
        raise e

# ============================================================================
# CHARACTER OPERATIONS
# ============================================================================

def gain_experience(character, xp_amount):
    """
    Add experience to character and handle level ups
    
    Level up formula: level_up_xp = current_level * 100
    Example when leveling up:
    - Increase level by 1
    - Increase max_health by 10
    - Increase strength by 2
    - Increase magic by 2
    - Restore health to max_health
    
    Raises: CharacterDeadError if character health is 0
    """
    if character['health'] <= 0:
        raise CharacterDeadError("Character is dead and cannot gain experience.")
    
    character['experience'] += xp_amount
    
    while character['experience'] >= character['level'] * 100:
        character['experience'] -= character['level'] * 100
        character['level'] += 1
        character['max_health'] += 10
        character['strength'] += 2
        character['magic'] += 2
        character['health'] = character['max_health']

def add_gold(character, amount):
    """
    Add gold to character's inventory
    
    Args:
        character: Character dictionary
        amount: Amount of gold to add (can be negative for spending)
    
    Returns: New gold total
    Raises: ValueError if result would be negative
    """
    new_total = character['gold'] + amount
    if new_total < 0:
        raise ValueError("Insufficient gold.")
    
    character['gold'] = new_total
    return character['gold']

def heal_character(character, amount):
    """
    Heal character by specified amount
    
    Health cannot exceed max_health
    
    Returns: Actual amount healed
    """
    if character['health'] <= 0:
        return 0
        
    missing_health = character['max_health'] - character['health']
    heal_amount = amount if amount < missing_health else missing_health
    
    character['health'] += heal_amount
    return heal_amount

def is_character_dead(character):
    """
    Check if character's health is 0 or below
    
    Returns: True if dead, False if alive
    """
    return character['health'] <= 0

def revive_character(character):
    """
    Revive a dead character with 50% health
    
    Returns: True if revived
    """
    if character['health'] > 0:
        return False
        
    character['health'] = character['max_health'] // 2
    return True

# ============================================================================
# VALIDATION
# ============================================================================

def validate_character_data(character):
    """
    Validate that character dictionary has all required fields
    
    Required fields: name, class, level, health, max_health, 
                    strength, magic, experience, gold, inventory,
                    active_quests, completed_quests
    
    Returns: True if valid
    Raises: InvalidSaveDataError if missing fields or invalid types
    """
    required_fields = [
        "name", "class", "level", "health", "max_health", 
        "strength", "magic", "experience", "gold", 
        "inventory", "active_quests", "completed_quests"
    ]
    
    for field in required_fields:
        if field not in character:
            raise InvalidSaveDataError(f"Missing required field: {field}")
            
    numeric_fields = ["level", "health", "max_health", "strength", "magic", "experience", "gold"]
    for field in numeric_fields:
        if not isinstance(character[field], int):
            raise InvalidSaveDataError(f"Field {field} must be an integer.")
            
    list_fields = ["inventory", "active_quests", "completed_quests"]
    for field in list_fields:
        if not isinstance(character[field], list):
            raise InvalidSaveDataError(f"Field {field} must be a list.")
            
    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== CHARACTER MANAGER TEST ===")
    
    try:
        char = create_character("TestHero", "Warrior")
        print(f"Created: {char['name']} the {char['class']}")
        print(f"Stats: HP={char['health']}, STR={char['strength']}, MAG={char['magic']}")
        
        gain_experience(char, 150)
        print(f"Leveled Up: Lvl {char['level']}, HP={char['health']}/{char['max_health']}")
        
        add_gold(char, 50)
        print(f"Gold: {char['gold']}")
        
        save_character(char)
        print("Character saved successfully")
        
        loaded = load_character("TestHero")
        print(f"Loaded: {loaded['name']} - Level {loaded['level']}")
        
        delete_character("TestHero")
        print("Character deleted successfully")
        
    except Exception as e:
        print(f"Test failed: {e}")