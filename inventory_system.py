"""
COMP 163 - Project 3: Quest Chronicles
Inventory System Module - Starter Code

Name: Rayner Paulino-Payano

AI Usage: [Document any AI assistance used]

This module handles inventory management, item usage, and equipment.
"""

from custom_exceptions import (
    InventoryFullError,
    ItemNotFoundError,
    InsufficientResourcesError,
    InvalidItemTypeError
)

# Maximum inventory size
MAX_INVENTORY_SIZE = 20

# ============================================================================
# INVENTORY MANAGEMENT
# ============================================================================

def add_item_to_inventory(character, item_id):
    """
    Add an item to character's inventory
    
    Args:
        character: Character dictionary
        item_id: Unique item identifier
    
    Returns: True if added successfully
    Raises: InventoryFullError if inventory is at max capacity
    """
    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
    
    character['inventory'].append(item_id)
    return True

def remove_item_from_inventory(character, item_id):
    """
    Remove an item from character's inventory
    
    Args:
        character: Character dictionary
        item_id: Item to remove
    
    Returns: True if removed successfully
    Raises: ItemNotFoundError if item not in inventory
    """
    if item_id not in character['inventory']:
        raise ItemNotFoundError(f"Item {item_id} not found in inventory.")
    
    character['inventory'].remove(item_id)
    return True

def has_item(character, item_id):
    """
    Check if character has a specific item
    
    Returns: True if item in inventory, False otherwise
    """
    return item_id in character['inventory']

def count_item(character, item_id):
    """
    Count how many of a specific item the character has
    
    Returns: Integer count of item
    """
    return character['inventory'].count(item_id)

def get_inventory_space_remaining(character):
    """
    Calculate how many more items can fit in inventory
    
    Returns: Integer representing available slots
    """
    return MAX_INVENTORY_SIZE - len(character['inventory'])

def clear_inventory(character):
    """
    Remove all items from inventory
    
    Returns: List of removed items
    """
    removed_items = character['inventory'][:]
    character['inventory'] = []
    return removed_items

# ============================================================================
# ITEM USAGE
# ============================================================================

def use_item(character, item_id, item_data):
    """
    Use a consumable item from inventory
    
    Args:
        character: Character dictionary
        item_id: Item to use
        item_data: Item information dictionary from game_data
    
    Item types and effects:
    - consumable: Apply effect and remove from inventory
    - weapon/armor: Cannot be "used", only equipped
    
    Returns: String describing what happened
    Raises: 
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'consumable'
    """
    if item_id not in character['inventory']:
        raise ItemNotFoundError(f"Item {item_id} not found.")
    
    if item_data['type'] != 'consumable':
        item_name = item_data.get('name', item_id)
        raise InvalidItemTypeError(f"Item {item_name} is not consumable.")
    
    stat_name, value = parse_item_effect(item_data['effect'])
    apply_stat_effect(character, stat_name, value)
    
    character['inventory'].remove(item_id)
    item_name = item_data.get('name', item_id)
    return f"Used {item_name}."

def equip_weapon(character, item_id, item_data):
    """
    Equip a weapon
    
    Args:
        character: Character dictionary
        item_id: Weapon to equip
        item_data: Item information dictionary
    
    Weapon effect format: "strength:5" (adds 5 to strength)
    
    If character already has weapon equipped:
    - Unequip current weapon (remove bonus)
    - Add old weapon back to inventory
    
    Returns: String describing equipment change
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'weapon'
    """
    if item_id not in character['inventory']:
        raise ItemNotFoundError(f"Item {item_id} not found.")
    
    if item_data['type'] != 'weapon':
        item_name = item_data.get('name', item_id)
        raise InvalidItemTypeError(f"Item {item_name} is not a weapon.")
    
    if 'equipped_weapon' in character and character['equipped_weapon']:
        unequip_weapon(character)
        
    stat_name, value = parse_item_effect(item_data['effect'])
    apply_stat_effect(character, stat_name, value)
    
    character['inventory'].remove(item_id)
    character['equipped_weapon'] = item_id
    character['weapon_bonus'] = (stat_name, value)
    
    item_name = item_data.get('name', item_id)
    return f"Equipped {item_name}."

def equip_armor(character, item_id, item_data):
    """
    Equip armor
    
    Args:
        character: Character dictionary
        item_id: Armor to equip
        item_data: Item information dictionary
    
    Armor effect format: "max_health:10" (adds 10 to max_health)
    
    If character already has armor equipped:
    - Unequip current armor (remove bonus)
    - Add old armor back to inventory
    
    Returns: String describing equipment change
    Raises:
        ItemNotFoundError if item not in inventory
        InvalidItemTypeError if item type is not 'armor'
    """
    if item_id not in character['inventory']:
        raise ItemNotFoundError(f"Item {item_id} not found.")
    
    if item_data['type'] != 'armor':
        item_name = item_data.get('name', item_id)
        raise InvalidItemTypeError(f"Item {item_name} is not armor.")
    
    if 'equipped_armor' in character and character['equipped_armor']:
        unequip_armor(character)
        
    stat_name, value = parse_item_effect(item_data['effect'])
    apply_stat_effect(character, stat_name, value)
    
    character['inventory'].remove(item_id)
    character['equipped_armor'] = item_id
    character['armor_bonus'] = (stat_name, value)
    
    item_name = item_data.get('name', item_id)
    return f"Equipped {item_name}."

def unequip_weapon(character):
    """
    Remove equipped weapon and return it to inventory
    
    Returns: Item ID that was unequipped, or None if no weapon equipped
    Raises: InventoryFullError if inventory is full
    """
    if 'equipped_weapon' not in character or not character['equipped_weapon']:
        return None
        
    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full, cannot unequip weapon.")
        
    item_id = character['equipped_weapon']
    
    if 'weapon_bonus' in character:
        stat_name, value = character['weapon_bonus']
        apply_stat_effect(character, stat_name, -value)
        del character['weapon_bonus']
        
    character['inventory'].append(item_id)
    character['equipped_weapon'] = None
    
    return item_id

def unequip_armor(character):
    """
    Remove equipped armor and return it to inventory
    
    Returns: Item ID that was unequipped, or None if no armor equipped
    Raises: InventoryFullError if inventory is full
    """
    if 'equipped_armor' not in character or not character['equipped_armor']:
        return None
        
    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory full, cannot unequip armor.")
        
    item_id = character['equipped_armor']
    
    if 'armor_bonus' in character:
        stat_name, value = character['armor_bonus']
        apply_stat_effect(character, stat_name, -value)
        del character['armor_bonus']
        
    character['inventory'].append(item_id)
    character['equipped_armor'] = None
    
    return item_id

# ============================================================================
# SHOP SYSTEM
# ============================================================================

def purchase_item(character, item_id, item_data):
    """
    Purchase an item from a shop
    
    Args:
        character: Character dictionary
        item_id: Item to purchase
        item_data: Item information with 'cost' field
    
    Returns: True if purchased successfully
    Raises:
        InsufficientResourcesError if not enough gold
        InventoryFullError if inventory is full
    """
    if character['gold'] < item_data['cost']:
        raise InsufficientResourcesError("Not enough gold.")
        
    if len(character['inventory']) >= MAX_INVENTORY_SIZE:
        raise InventoryFullError("Inventory is full.")
        
    character['gold'] -= item_data['cost']
    character['inventory'].append(item_id)
    return True

def sell_item(character, item_id, item_data):
    """
    Sell an item for half its purchase cost
    
    Args:
        character: Character dictionary
        item_id: Item to sell
        item_data: Item information with 'cost' field
    
    Returns: Amount of gold received
    Raises: ItemNotFoundError if item not in inventory
    """
    if item_id not in character['inventory']:
        raise ItemNotFoundError(f"Item {item_id} not found in inventory.")
        
    sell_value = item_data['cost'] // 2
    character['inventory'].remove(item_id)
    character['gold'] += sell_value
    return sell_value

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_item_effect(effect_string):
    """
    Parse item effect string into stat name and value
    
    Args:
        effect_string: String in format "stat_name:value"
    
    Returns: Tuple of (stat_name, value)
    Example: "health:20" → ("health", 20)
    """
    parts = effect_string.split(":")
    return parts[0], int(parts[1])

def apply_stat_effect(character, stat_name, value):
    """
    Apply a stat modification to character
    
    Valid stats: health, max_health, strength, magic
    
    Note: health cannot exceed max_health
    """
    if stat_name == "health":
        character['health'] += value
        if character['health'] > character['max_health']:
            character['health'] = character['max_health']
    elif stat_name == "max_health":
        character['max_health'] += value
        if character['health'] > character['max_health']:
            character['health'] = character['max_health']
    else:
        if stat_name in character:
            character[stat_name] += value

def display_inventory(character, item_data_dict):
    """
    Display character's inventory in formatted way
    
    Args:
        character: Character dictionary
        item_data_dict: Dictionary of all item data
    
    Shows item names, types, and quantities
    """
    if not character['inventory']:
        print("Inventory is empty.")
        return

    counts = {}
    for item_id in character['inventory']:
        counts[item_id] = counts.get(item_id, 0) + 1
        
    print("\n--- Inventory ---")
    for item_id, count in counts.items():
        if item_id in item_data_dict:
            name = item_data_dict[item_id]['name']
            item_type = item_data_dict[item_id]['type']
            print(f"{name} ({item_type}) x{count}")
        else:
            print(f"Unknown Item ({item_id}) x{count}")
            
    print(f"Space: {len(character['inventory'])}/{MAX_INVENTORY_SIZE}")
    print(f"Gold: {character['gold']}")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== INVENTORY SYSTEM TEST ===")
    
    test_char = {'inventory': [], 'gold': 100, 'health': 80, 'max_health': 80}
    
    try:
        add_item_to_inventory(test_char, "health_potion")
        print(f"Inventory: {test_char['inventory']}")
    except InventoryFullError:
        print("Inventory is full!")
    
    test_item = {
        'item_id': 'health_potion',
        'name': 'Small Potion',
        'type': 'consumable',
        'effect': 'health:20',
        'cost': 50
    }
    
    try:
        result = use_item(test_char, "health_potion", test_item)
        print(result)
        print(f"Health: {test_char['health']}")
    except ItemNotFoundError:
        print("Item not found")