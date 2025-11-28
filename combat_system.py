"""
COMP 163 - Project 3: Quest Chronicles
Combat System Module - Starter Code

Name: Rayner Paulino-Payano

AI Usage: [Document any AI assistance used]

Handles combat mechanics
"""

import random
from custom_exceptions import (
    InvalidTargetError,
    CombatNotActiveError,
    CharacterDeadError,
    AbilityOnCooldownError
)

# ============================================================================
# ENEMY DEFINITIONS
# ============================================================================

def create_enemy(enemy_type):
    """
    Create an enemy based on type
    
    Example enemy types and stats:
    - goblin: health=50, strength=8, magic=2, xp_reward=25, gold_reward=10
    - orc: health=80, strength=12, magic=5, xp_reward=50, gold_reward=25
    - dragon: health=200, strength=25, magic=15, xp_reward=200, gold_reward=100
    
    Returns: Enemy dictionary
    Raises: InvalidTargetError if enemy_type not recognized
    """
    enemies = {
        "goblin": {"health": 50, "max_health": 50, "strength": 8, "magic": 2, "xp_reward": 25, "gold_reward": 10},
        "orc": {"health": 80, "max_health": 80, "strength": 12, "magic": 5, "xp_reward": 50, "gold_reward": 25},
        "dragon": {"health": 200, "max_health": 200, "strength": 25, "magic": 15, "xp_reward": 200, "gold_reward": 100}
    }
    
    if enemy_type.lower() not in enemies:
        raise InvalidTargetError(f"Enemy type '{enemy_type}' not recognized.")
        
    enemy_data = enemies[enemy_type.lower()].copy()
    enemy_data["name"] = enemy_type.capitalize()
    return enemy_data

def get_random_enemy_for_level(character_level):
    """
    Get an appropriate enemy for character's level
    
    Level 1-2: Goblins
    Level 3-5: Orcs
    Level 6+: Dragons
    
    Returns: Enemy dictionary
    """
    if character_level <= 2:
        return create_enemy("goblin")
    elif character_level <= 5:
        return create_enemy("orc")
    else:
        return create_enemy("dragon")

# ============================================================================
# COMBAT SYSTEM
# ============================================================================

class SimpleBattle:
    """
    Simple turn-based combat system
    
    Manages combat between character and enemy
    """
    
    def __init__(self, character, enemy):
        """Initialize battle with character and enemy"""
        self.character = character
        self.enemy = enemy
        self.combat_active = False
        self.turn_counter = 0
    
    def start_battle(self):
        """
        Start the combat loop
        
        Returns: Dictionary with battle results:
                {'winner': 'player'|'enemy', 'xp_gained': int, 'gold_gained': int}
        
        Raises: CharacterDeadError if character is already dead
        """
        if self.character['health'] <= 0:
            raise CharacterDeadError("Character is dead.")
            
        self.combat_active = True
        display_battle_log(f"Battle started between {self.character['name']} and {self.enemy['name']}!")
        
        while self.combat_active:
            self.turn_counter += 1
            display_combat_stats(self.character, self.enemy)
            
            try:
                self.player_turn()
            except CombatNotActiveError: 
                break 

            if not self.combat_active:
                break
                
            winner = self.check_battle_end()
            if winner:
                if winner == 'player':
                    return get_victory_rewards(self.enemy)
                else:
                    return {'winner': 'enemy', 'xp_gained': 0, 'gold_gained': 0}
            
            self.enemy_turn()
            
            winner = self.check_battle_end()
            if winner:
                if winner == 'player':
                    return get_victory_rewards(self.enemy)
                else:
                    return {'winner': 'enemy', 'xp_gained': 0, 'gold_gained': 0}
                    
        return {'winner': 'escaped', 'xp_gained': 0, 'gold_gained': 0}
    
    def player_turn(self):
        """
        Handle player's turn
        
        Displays options:
        1. Basic Attack
        2. Special Ability (if available)
        3. Try to Run
        
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active.")
            
        print("\n1. Attack")
        print("2. Special Ability")
        print("3. Run")
        
        choice = input("Choose action: ")
        
        if choice == "1":
            damage = self.calculate_damage(self.character, self.enemy)
            self.apply_damage(self.enemy, damage)
            display_battle_log(f"You hit {self.enemy['name']} for {damage} damage.")
        elif choice == "2":
            try:
                msg = use_special_ability(self.character, self.enemy)
                display_battle_log(msg)
            except AbilityOnCooldownError as e:
                display_battle_log(str(e))
                self.player_turn()
        elif choice == "3":
            if self.attempt_escape():
                display_battle_log("Escaped successfully!")
                self.combat_active = False
            else:
                display_battle_log("Escape failed!")
        else:
            print("Invalid choice.")
            self.player_turn()
    
    def enemy_turn(self):
        """
        Handle enemy's turn - simple AI
        
        Enemy always attacks
        
        Raises: CombatNotActiveError if called outside of battle
        """
        if not self.combat_active:
            raise CombatNotActiveError("Combat is not active.")
            
        damage = self.calculate_damage(self.enemy, self.character)
        self.apply_damage(self.character, damage)
        display_battle_log(f"{self.enemy['name']} hits you for {damage} damage.")
    
    def calculate_damage(self, attacker, defender):
        """
        Calculate damage from attack
        
        Damage formula: attacker['strength'] - (defender['strength'] // 4)
        Minimum damage: 1
        
        Returns: Integer damage amount
        """
        dmg = attacker['strength'] - (defender['strength'] // 4)
        return max(1, dmg)
    
    def apply_damage(self, target, damage):
        """
        Apply damage to a character or enemy
        
        Reduces health, prevents negative health
        """
        target['health'] -= damage
        if target['health'] < 0:
            target['health'] = 0
    
    def check_battle_end(self):
        """
        Check if battle is over
        
        Returns: 'player' if enemy dead, 'enemy' if character dead, None if ongoing
        """
        if self.enemy['health'] <= 0:
            self.combat_active = False
            return 'player'
        elif self.character['health'] <= 0:
            self.combat_active = False
            return 'enemy'
        return None
    
    def attempt_escape(self):
        """
        Try to escape from battle
        
        50% success chance
        
        Returns: True if escaped, False if failed
        """
        if random.random() < 0.5:
            self.combat_active = False
            return True
        return False

# ============================================================================
# SPECIAL ABILITIES
# ============================================================================

def use_special_ability(character, enemy):
    """
    Use character's class-specific special ability
    
    Example abilities by class:
    - Warrior: Power Strike (2x strength damage)
    - Mage: Fireball (2x magic damage)
    - Rogue: Critical Strike (3x strength damage, 50% chance)
    - Cleric: Heal (restore 30 health)
    
    Returns: String describing what happened
    Raises: AbilityOnCooldownError if ability was used recently
    """
    try:
        if character['class'].lower() == "warrior":
            return warrior_power_strike(character, enemy)
        elif character['class'].lower() == "mage":
            return mage_fireball(character, enemy)
        elif character['class'].lower() == "rogue":
            return rogue_critical_strike(character, enemy)
        elif character['class'].lower() == "cleric":
            return cleric_heal(character)
        else:
            raise AbilityOnCooldownError("No special ability available.")
    except KeyError:
        raise AbilityOnCooldownError("Character class not defined.")

def warrior_power_strike(character, enemy):
    """Warrior special ability"""
    damage = character['strength'] * 2
    enemy['health'] = max(0, enemy['health'] - damage)
    return f"Power Strike! Dealt {damage} damage."

def mage_fireball(character, enemy):
    """Mage special ability"""
    damage = character['magic'] * 2
    enemy['health'] = max(0, enemy['health'] - damage)
    return f"Fireball! Dealt {damage} magic damage."

def rogue_critical_strike(character, enemy):
    """Rogue special ability"""
    if random.random() < 0.5:
        damage = character['strength'] * 3
        enemy['health'] = max(0, enemy['health'] - damage)
        return f"Critical Strike! Dealt {damage} massive damage."
    else:
        damage = character['strength']
        enemy['health'] = max(0, enemy['health'] - damage)
        return f"Critical missed! Normal hit for {damage} damage."

def cleric_heal(character):
    """Cleric special ability"""
    heal_amt = 30
    character['health'] = min(character['max_health'], character['health'] + heal_amt)
    return f"Healed for {heal_amt} health."

# ============================================================================
# COMBAT UTILITIES
# ============================================================================

def can_character_fight(character):
    """
    Check if character is in condition to fight
    
    Returns: True if health > 0 and not in battle
    """
    return character['health'] > 0

def get_victory_rewards(enemy):
    """
    Calculate rewards for defeating enemy
    
    Returns: Dictionary with 'xp' and 'gold'
    """
    return {
        'winner': 'player',
        'xp_gained': enemy['xp_reward'],
        'gold_gained': enemy['gold_reward']
    }

def display_combat_stats(character, enemy):
    """
    Display current combat status
    
    Shows both character and enemy health/stats
    """
    print(f"\n{character['name']}: HP={character['health']}/{character['max_health']}")
    print(f"{enemy['name']}: HP={enemy['health']}/{enemy['max_health']}")

def display_battle_log(message):
    """
    Display a formatted battle message
    """
    print(f">>> {message}")

# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("=== COMBAT SYSTEM TEST ===")
    
    try:
        goblin = create_enemy("goblin")
        print(f"Created {goblin['name']}")
        
        test_char = {
            'name': 'Hero',
            'class': 'Warrior',
            'health': 120,
            'max_health': 120,
            'strength': 15,
            'magic': 5
        }

        battle = SimpleBattle(test_char, goblin)
        result = battle.start_battle()
        print(f"Battle result: {result}")
        
    except Exception as e:
        print(f"Test failed: {e}")