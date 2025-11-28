# COMP 163: Project 3 - Quest Chronicles

[](https://classroom.github.com/a/wnCpjX4n)
[](https://classroom.github.com/online_ide?assignment_repo_id=21703061&assignment_repo_type=AssignmentRepo)

**Student Name:** Rayner Paulino-Payano
**Section:** 6

## Overview

Quest Chronicles is a modular, text-based RPG adventure game. It demonstrates mastery of Python **Exceptions** and **Modules** by splitting game logic into distinct, manageable files. Players create a character, manage an inventory, complete quests, and battle enemies in a turn-based combat system.

## Project Structure

```
quest_chronicles/
├── main.py                     # Game launcher & main loop
├── character_manager.py        # Character creation, saving, and loading
├── inventory_system.py         # Item management, equipment, and shop
├── quest_handler.py            # Quest tracking and validation
├── combat_system.py            # Turn-based battle mechanics
├── game_data.py                # Data loading (IO) and validation
├── custom_exceptions.py        # Centralized exception definitions
├── data/
│   ├── quests.txt              # Quest database
│   ├── items.txt               # Item database
│   └── save_games/             # User save files
└── README.md                   # Project documentation
```

## How to Play

1.  **Setup:** Ensure you have Python 3 installed.

2.  **Launch:** Run the game from the terminal:

    ```bash
    python main.py
    ```

    *(Note: If the `data/` folder is missing, the game will automatically create default data files on the first run.)*

3.  **Gameplay:**

      * **New Game:** Select a name and class (Warrior, Mage, Rogue, Cleric).
      * **Main Menu:**
          * **View Stats:** Check your health, gold, and XP.
          * **Inventory:** Equip weapons/armor or use potions.
          * **Quests:** Accept new quests or view progress.
          * **Explore:** Engage in combat to earn XP and Gold.
          * **Shop:** Buy better gear or sell loot.
          * **Save & Quit:** Saves your progress to `data/save_games/`.

## Module Architecture

The project is organized into focused modules to separate concerns:

  * **`main.py`**: The entry point. It handles the high-level game loop, user input for menus, and coordinates the flow between other modules.
  * **`character_manager.py`**: Handles the lifecycle of the character dictionary. It contains logic for creating new characters (with class-specific stats), saving them to text files, and parsing those files back into Python dictionaries.
  * **`inventory_system.py`**: Manages the list of items held by the player. It handles logic for ensuring the inventory doesn't exceed capacity, applying stat effects from consumables, and calculating stat bonuses when equipping/unequipping weapons and armor.
  * **`quest_handler.py`**: manages the state of quests. It validates if a user *can* accept a quest (level requirements, prerequisites) and handles the transition of quests from "Active" to "Completed" while awarding XP/Gold.
  * **`combat_system.py`**: Contains the logic for the battle loop. It generates enemies based on player level, calculates damage based on stats, and manages the turn-based flow until victory or defeat.
  * **`game_data.py`**: The Data Access Layer. It is responsible for reading `quests.txt` and `items.txt`, parsing the specific file formats, and validating that the loaded data contains all required fields.
  * **`custom_exceptions.py`**: Contains no logic, only class definitions for custom errors (e.g., `InventoryFullError`, `CharacterDeadError`).

## Exception Strategy

The game uses a robust hierarchy of custom exceptions defined in `custom_exceptions.py`. This allows the main game loop to handle specific errors gracefully without crashing.

  * **Data Loading:** `game_data.py` raises `MissingDataFileError` or `CorruptedDataError` if game files are absent or unreadable. `InvalidDataFormatError` is raised if specific fields (like `cost` or `damage`) are missing or are the wrong data type.
  * **Game Logic:**
      * **Inventory:** `InventoryFullError` prevents picking up items when capacity is reached. `InsufficientResourcesError` is raised by the shop if the player lacks gold.
      * **Combat:** `CharacterDeadError` is raised when health hits 0, triggering the "Game Over" or "Revive" logic in `main.py`. `CombatNotActiveError` prevents combat actions (like attacking) outside of battle.
      * **Quests:** `QuestRequirementsNotMetError` ensures players cannot skip prerequisites or level requirements.

## Design Choices

1.  **Dictionaries for Entities:** Instead of using Python Classes for Characters and Enemies, this project uses Dictionaries. This adheres to the strict requirement of using only Modules and Exceptions concepts. It also makes serialization (saving to text) straightforward.
2.  **Text-Based Save Format:** Save files use a human-readable `KEY: VALUE` format (e.g., `HEALTH: 100`). This makes debugging easier and allows the save files to be edited manually if needed for testing.
3.  **Dynamic Parsing:** The `game_data` module is designed to be resilient. It splits file content by blank lines to separate entries, allowing for easy expansion of the `items.txt` and `quests.txt` databases without changing code.
4.  **Modular dependencies:** `main.py` imports everything, but the sub-modules (like `inventory` or `combat`) are kept relatively independent, making unit testing significantly easier.

## AI Usage

**AI Tool Used:** Google Gemini (Large Language Model)

**Usage Description:**
I utilized AI as a "pair programmer" to assist with the implementation of the module logic based on the provided starter docstrings.

1.  **Code Generation:** I provided the docstrings and function signatures to the AI, and it generated the implementation logic for the core modules (`character_manager`, `inventory_system`, etc.).
2.  **Refactoring:** I used the AI to refine the `save_character` function to ensure file paths were handled safely using `os.path.join`.
3.  **Debugging:** The AI helped identify that `inventory` lists needed to be converted to strings before being written to the save file to prevent `TypeError` during the `.join()` operation.

## Creativity & Customization

  * **Class Balance:** Adjusted the starting stats for the `Mage` and `Cleric` to make early-game combat more survivable.
  * **Stat Calculation:** Implemented a damage formula in `combat_system` that scales based on the enemy's strength vs. the player's defense (derived from strength).
  * **Fail-safes:** Added a `create_default_data_files` function in `game_data.py` to ensure the game is playable immediately after cloning, even if data files are missing.