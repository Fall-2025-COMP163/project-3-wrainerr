"""
COMP 163 - Project 3: Quest Chronicles
Game Data Module - Starter Code

Name: Rayner Paulino-Payano

AI Usage: [Document any AI assistance used]

This module handles loading and validating game data from text files.
"""

import os
from custom_exceptions import (
    InvalidDataFormatError,
    MissingDataFileError,
    CorruptedDataError
)

# ============================================================================
# DATA LOADING FUNCTIONS
# ============================================================================

def load_quests(filename="data/quests.txt"):
    """
    Load quest data from file
    
    Expected format per quest (separated by blank lines):
    QUEST_ID: unique_quest_name
    TITLE: Quest Display Title
    DESCRIPTION: Quest description text
    REWARD_XP: 100
    REWARD_GOLD: 50
    REQUIRED_LEVEL: 1
    PREREQUISITE: previous_quest_id (or NONE)
    
    Returns: Dictionary of quests {quest_id: quest_data_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Quest file not found: {filename}")
        
    try:
        with open(filename, 'r') as f:
            content = f.read().strip()
    except (IOError, PermissionError) as e:
        raise CorruptedDataError(f"Could not read quest file: {e}")
        
    if not content:
        return {}
        
    quests = {}
    blocks = content.split('\n\n')
    
    for block in blocks:
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if not lines:
            continue
            
        try:
            quest_data = parse_quest_block(lines)
            validate_quest_data(quest_data)
            quests[quest_data['quest_id']] = quest_data
        except InvalidDataFormatError as e:
            raise InvalidDataFormatError(f"Failed to parse quest block: {e}")
            
    return quests

def load_items(filename="data/items.txt"):
    """
    Load item data from file
    
    Expected format per item (separated by blank lines):
    ITEM_ID: unique_item_name
    NAME: Item Display Name
    TYPE: weapon|armor|consumable
    EFFECT: stat_name:value (e.g., strength:5 or health:20)
    COST: 100
    DESCRIPTION: Item description
    
    Returns: Dictionary of items {item_id: item_data_dict}
    Raises: MissingDataFileError, InvalidDataFormatError, CorruptedDataError
    """
    if not os.path.exists(filename):
        raise MissingDataFileError(f"Item file not found: {filename}")
        
    try:
        with open(filename, 'r') as f:
            content = f.read().strip()
    except (IOError, PermissionError) as e:
        raise CorruptedDataError(f"Could not read item file: {e}")
        
    if not content:
        return {}
        
    items = {}
    blocks = content.split('\n\n')
    
    for block in blocks:
        lines = [line.strip() for line in block.split('\n') if line.strip()]
        if not lines:
            continue
            
        try:
            item_data = parse_item_block(lines)
            validate_item_data(item_data)
            items[item_data['item_id']] = item_data
        except InvalidDataFormatError as e:
            raise InvalidDataFormatError(f"Failed to parse item block: {e}")
            
    return items

def validate_quest_data(quest_dict):
    """
    Validate that quest dictionary has all required fields
    
    Required fields: quest_id, title, description, reward_xp, 
                    reward_gold, required_level, prerequisite
    
    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields
    """
    required_fields = [
        "quest_id", "title", "description", "reward_xp", 
        "reward_gold", "required_level", "prerequisite"
    ]
    
    for field in required_fields:
        if field not in quest_dict:
            raise InvalidDataFormatError(f"Missing required field: {field}")
            
    if not isinstance(quest_dict['reward_xp'], int):
        raise InvalidDataFormatError("reward_xp must be an integer")
    if not isinstance(quest_dict['reward_gold'], int):
        raise InvalidDataFormatError("reward_gold must be an integer")
    if not isinstance(quest_dict['required_level'], int):
        raise InvalidDataFormatError("required_level must be an integer")
        
    return True

def validate_item_data(item_dict):
    """
    Validate that item dictionary has all required fields
    
    Required fields: item_id, name, type, effect, cost, description
    Valid types: weapon, armor, consumable
    
    Returns: True if valid
    Raises: InvalidDataFormatError if missing required fields or invalid type
    """
    required_fields = ["item_id", "name", "type", "effect", "cost", "description"]
    valid_types = ["weapon", "armor", "consumable"]
    
    for field in required_fields:
        if field not in item_dict:
            raise InvalidDataFormatError(f"Missing required field: {field}")
            
    if item_dict['type'] not in valid_types:
        raise InvalidDataFormatError(f"Invalid item type: {item_dict['type']}")
        
    if not isinstance(item_dict['cost'], int):
        raise InvalidDataFormatError("cost must be an integer")
        
    return True

def create_default_data_files():
    """
    Create default data files if they don't exist
    This helps with initial setup and testing
    """
    if not os.path.exists("data"):
        try:
            os.makedirs("data")
        except OSError as e:
            print(f"Error creating data directory: {e}")
            return

    quests_path = os.path.join("data", "quests.txt")
    if not os.path.exists(quests_path):
        try:
            with open(quests_path, 'w') as f:
                f.write("QUEST_ID: quest_001\n")
                f.write("TITLE: The Beginning\n")
                f.write("DESCRIPTION: Defeat your first enemy.\n")
                f.write("REWARD_XP: 100\n")
                f.write("REWARD_GOLD: 50\n")
                f.write("REQUIRED_LEVEL: 1\n")
                f.write("PREREQUISITE: NONE\n")
        except IOError:
            print("Failed to create default quests.txt")

    items_path = os.path.join("data", "items.txt")
    if not os.path.exists(items_path):
        try:
            with open(items_path, 'w') as f:
                f.write("ITEM_ID: potion_small\n")
                f.write("NAME: Small Potion\n")
                f.write("TYPE: consumable\n")
                f.write("EFFECT: health:20\n")
                f.write("COST: 25\n")
                f.write("DESCRIPTION: Restores 20 health.\n")
                f.write("\n")
                f.write("ITEM_ID: sword_basic\n")
                f.write("NAME: Iron Sword\n")
                f.write("TYPE: weapon\n")
                f.write("EFFECT: strength:5\n")
                f.write("COST: 100\n")
                f.write("DESCRIPTION: A basic iron sword.\n")
        except IOError:
            print("Failed to create default items.txt")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_quest_block(lines):
    """
    Parse a block of lines into a quest dictionary
    
    Args:
        lines: List of strings representing one quest
    
    Returns: Dictionary with quest data
    Raises: InvalidDataFormatError if parsing fails
    """
    quest = {}
    try:
        for line in lines:
            if ": " in line:
                key, value = line.split(": ", 1)
                quest[key.lower()] = value
        
        if 'reward_xp' in quest:
            quest['reward_xp'] = int(quest['reward_xp'])
        if 'reward_gold' in quest:
            quest['reward_gold'] = int(quest['reward_gold'])
        if 'required_level' in quest:
            quest['required_level'] = int(quest['required_level'])
            
        return quest
    except ValueError:
        raise InvalidDataFormatError("Invalid numeric value in quest data")

def parse_item_block(lines):
    """
    Parse a block of lines into an item dictionary
    
    Args:
        lines: List of strings representing one item
    
    Returns: Dictionary with item data
    Raises: InvalidDataFormatError if parsing fails
    """
    item = {}
    try:
        for line in lines:
            if ": " in line:
                key, value = line.split(": ", 1)
                item[key.lower()] = value
                
        if 'cost' in item:
            item['cost'] = int(item['cost'])
            
        return item
    except ValueError:
        raise InvalidDataFormatError("Invalid numeric value in item data")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== GAME DATA MODULE TEST ===")
    
    create_default_data_files()
    
    try:
        quests = load_quests()
        print(f"Loaded {len(quests)} quests")
        for qid, qdata in quests.items():
            print(f"- {qdata['title']}")
    except (MissingDataFileError, InvalidDataFormatError, CorruptedDataError) as e:
        print(f"Quest Error: {e}")
    
    try:
        items = load_items()
        print(f"Loaded {len(items)} items")
        for iid, idata in items.items():
            print(f"- {idata['name']}")
    except (MissingDataFileError, InvalidDataFormatError, CorruptedDataError) as e:
        print(f"Item Error: {e}")