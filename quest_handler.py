"""
COMP 163 - Project 3: Quest Chronicles
Quest Handler Module - Starter Code

Name: Rayner Paulino-Payano

AI Usage: AI Used to handle missing item names, normalize combat reward keys,
and make save-file parsing more robust.

This module handles quest management, dependencies, and completion.
"""

import character_manager
from custom_exceptions import (
    QuestNotFoundError,
    QuestRequirementsNotMetError,
    QuestAlreadyCompletedError,
    QuestNotActiveError,
    InsufficientLevelError
)

# ============================================================================
# QUEST MANAGEMENT
# ============================================================================

def accept_quest(character, quest_id, quest_data_dict):
    """
    Accept a new quest
    
    Args:
        character: Character dictionary
        quest_id: Quest to accept
        quest_data_dict: Dictionary of all quest data
    
    Requirements to accept quest:
    - Character level >= quest required_level
    - Prerequisite quest completed (if any)
    - Quest not already completed
    - Quest not already active
    
    Returns: True if quest accepted
    Raises:
        QuestNotFoundError if quest_id not in quest_data_dict
        InsufficientLevelError if character level too low
        QuestRequirementsNotMetError if prerequisite not completed
        QuestAlreadyCompletedError if quest already done
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest {quest_id} not found.")

    quest = quest_data_dict[quest_id]

    if character['level'] < quest['required_level']:
        raise InsufficientLevelError(f"Level {quest['required_level']} required.")

    if quest['prerequisite'] != "NONE" and quest['prerequisite'] not in character['completed_quests']:
        raise QuestRequirementsNotMetError(f"Prerequisite {quest['prerequisite']} not completed.")

    if quest_id in character['completed_quests']:
        raise QuestAlreadyCompletedError(f"Quest {quest_id} already completed.")

    if quest_id in character['active_quests']:
        return False

    character['active_quests'].append(quest_id)
    return True

def complete_quest(character, quest_id, quest_data_dict):
    """
    Complete an active quest and grant rewards
    
    Args:
        character: Character dictionary
        quest_id: Quest to complete
        quest_data_dict: Dictionary of all quest data
    
    Rewards:
    - Experience points (reward_xp)
    - Gold (reward_gold)
    
    Returns: Dictionary with reward information
    Raises:
        QuestNotFoundError if quest_id not in quest_data_dict
        QuestNotActiveError if quest not in active_quests
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest {quest_id} not found.")

    if quest_id not in character['active_quests']:
        raise QuestNotActiveError(f"Quest {quest_id} is not active.")

    quest = quest_data_dict[quest_id]
    
    character['active_quests'].remove(quest_id)
    character['completed_quests'].append(quest_id)

    character_manager.gain_experience(character, quest['reward_xp'])
    character_manager.add_gold(character, quest['reward_gold'])

    return {
        "xp": quest['reward_xp'],
        "gold": quest['reward_gold']
    }

def abandon_quest(character, quest_id):
    """
    Remove a quest from active quests without completing it
    
    Returns: True if abandoned
    Raises: QuestNotActiveError if quest not active
    """
    if quest_id not in character['active_quests']:
        raise QuestNotActiveError(f"Quest {quest_id} is not active.")

    character['active_quests'].remove(quest_id)
    return True

def get_active_quests(character, quest_data_dict):
    """
    Get full data for all active quests
    
    Returns: List of quest dictionaries for active quests
    """
    active_quests = []
    for quest_id in character['active_quests']:
        if quest_id in quest_data_dict:
            active_quests.append(quest_data_dict[quest_id])
    return active_quests

def get_completed_quests(character, quest_data_dict):
    """
    Get full data for all completed quests
    
    Returns: List of quest dictionaries for completed quests
    """
    completed_quests = []
    for quest_id in character['completed_quests']:
        if quest_id in quest_data_dict:
            completed_quests.append(quest_data_dict[quest_id])
    return completed_quests

def get_available_quests(character, quest_data_dict):
    """
    Get quests that character can currently accept
    
    Available = meets level req + prerequisite done + not completed + not active
    
    Returns: List of quest dictionaries
    """
    available = []
    for quest_id, quest_data in quest_data_dict.items():
        if can_accept_quest(character, quest_id, quest_data_dict):
            available.append(quest_data)
    return available

# ============================================================================
# QUEST TRACKING
# ============================================================================

def is_quest_completed(character, quest_id):
    """
    Check if a specific quest has been completed
    
    Returns: True if completed, False otherwise
    """
    return quest_id in character['completed_quests']

def is_quest_active(character, quest_id):
    """
    Check if a specific quest is currently active
    
    Returns: True if active, False otherwise
    """
    return quest_id in character['active_quests']

def can_accept_quest(character, quest_id, quest_data_dict):
    """
    Check if character meets all requirements to accept quest
    
    Returns: True if can accept, False otherwise
    Does NOT raise exceptions - just returns boolean
    """
    if quest_id not in quest_data_dict:
        return False
        
    quest = quest_data_dict[quest_id]
    
    if character['level'] < quest['required_level']:
        return False
        
    if quest['prerequisite'] != "NONE" and quest['prerequisite'] not in character['completed_quests']:
        return False
        
    if quest_id in character['completed_quests']:
        return False
        
    if quest_id in character['active_quests']:
        return False
        
    return True

def get_quest_prerequisite_chain(quest_id, quest_data_dict):
    """
    Get the full chain of prerequisites for a quest
    
    Returns: List of quest IDs in order [earliest_prereq, ..., quest_id]
    Example: If Quest C requires Quest B, which requires Quest A:
             Returns ["quest_a", "quest_b", "quest_c"]
    
    Raises: QuestNotFoundError if quest doesn't exist
    """
    if quest_id not in quest_data_dict:
        raise QuestNotFoundError(f"Quest {quest_id} not found.")

    chain = [quest_id]
    current_id = quest_id

    while True:
        current_quest = quest_data_dict[current_id]
        prereq = current_quest['prerequisite']
        
        if prereq == "NONE":
            break
            
        if prereq not in quest_data_dict:
            raise QuestNotFoundError(f"Prerequisite {prereq} not found.")
            
        chain.append(prereq)
        current_id = prereq
        
    return chain[::-1]

# ============================================================================
# QUEST STATISTICS
# ============================================================================

def get_quest_completion_percentage(character, quest_data_dict):
    """
    Calculate what percentage of all quests have been completed
    
    Returns: Float between 0 and 100
    """
    total_quests = len(quest_data_dict)
    if total_quests == 0:
        return 0.0
        
    completed_count = len(character['completed_quests'])
    return (completed_count / total_quests) * 100

def get_total_quest_rewards_earned(character, quest_data_dict):
    """
    Calculate total XP and gold earned from completed quests
    
    Returns: Dictionary with 'total_xp' and 'total_gold'
    """
    total_xp = 0
    total_gold = 0
    
    for quest_id in character['completed_quests']:
        if quest_id in quest_data_dict:
            quest = quest_data_dict[quest_id]
            total_xp += quest['reward_xp']
            total_gold += quest['reward_gold']
            
    return {"total_xp": total_xp, "total_gold": total_gold}

def get_quests_by_level(quest_data_dict, min_level, max_level):
    """
    Get all quests within a level range
    
    Returns: List of quest dictionaries
    """
    result = []
    for quest in quest_data_dict.values():
        if min_level <= quest['required_level'] <= max_level:
            result.append(quest)
    return result

# ============================================================================
# DISPLAY FUNCTIONS
# ============================================================================

def display_quest_info(quest_data):
    """
    Display formatted quest information
    
    Shows: Title, Description, Rewards, Requirements
    """
    print(f"\n=== {quest_data['title']} ===")
    print(f"Description: {quest_data['description']}")
    print(f"Level Required: {quest_data['required_level']}")
    print(f"Prerequisite: {quest_data['prerequisite']}")
    print(f"Rewards: {quest_data['reward_xp']} XP, {quest_data['reward_gold']} Gold")

def display_quest_list(quest_list):
    """
    Display a list of quests in summary format
    
    Shows: Title, Required Level, Rewards
    """
    if not quest_list:
        print("No quests available.")
        return

    print(f"{'Title':<30} {'Lvl':<5} {'XP':<5} {'Gold':<5}")
    print("-" * 50)
    for quest in quest_list:
        print(f"{quest['title']:<30} {quest['required_level']:<5} {quest['reward_xp']:<5} {quest['reward_gold']:<5}")

def display_character_quest_progress(character, quest_data_dict):
    """
    Display character's quest statistics and progress
    
    Shows:
    - Active quests count
    - Completed quests count
    - Completion percentage
    - Total rewards earned
    """
    active_count = len(character['active_quests'])
    completed_count = len(character['completed_quests'])
    percentage = get_quest_completion_percentage(character, quest_data_dict)
    rewards = get_total_quest_rewards_earned(character, quest_data_dict)
    
    print("\n=== Quest Progress ===")
    print(f"Active Quests: {active_count}")
    print(f"Completed Quests: {completed_count}")
    print(f"Completion: {percentage:.1f}%")
    print(f"Total Earnings: {rewards['total_xp']} XP, {rewards['total_gold']} Gold")

# ============================================================================
# VALIDATION
# ============================================================================

def validate_quest_prerequisites(quest_data_dict):
    """
    Validate that all quest prerequisites exist
    
    Checks that every prerequisite (that's not "NONE") refers to a real quest
    
    Returns: True if all valid
    Raises: QuestNotFoundError if invalid prerequisite found
    """
    for quest_id, quest_data in quest_data_dict.items():
        prereq = quest_data['prerequisite']
        if prereq != "NONE" and prereq not in quest_data_dict:
            raise QuestNotFoundError(f"Quest {quest_id} has invalid prerequisite: {prereq}")
    return True

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== QUEST HANDLER TEST ===")
    
    test_char = {
        'level': 1,
        'active_quests': [],
        'completed_quests': [],
        'experience': 0,
        'gold': 100,
        'health': 100,
        'max_health': 100,
        'strength': 10,
        'magic': 5
    }
    
    test_quests = {
        'quest_001': {
            'quest_id': 'quest_001',
            'title': 'First Steps',
            'description': 'Complete your first quest',
            'reward_xp': 50,
            'reward_gold': 25,
            'required_level': 1,
            'prerequisite': 'NONE'
        }
    }
    
    try:
        accept_quest(test_char, 'quest_001', test_quests)
        print("Quest accepted!")
        
        display_character_quest_progress(test_char, test_quests)
        
        rewards = complete_quest(test_char, 'quest_001', test_quests)
        print(f"Quest completed! Earned {rewards['xp']} XP and {rewards['gold']} Gold")
        
        display_character_quest_progress(test_char, test_quests)
        
    except Exception as e:
        print(f"Error: {e}")