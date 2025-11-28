# Cover Generator for Zaparoo service

This project provides a script to generate printable game cover cards for your game system collections. The script processes a `gamelist.xml` file and associated images to create individual game cards and compiles them into printable A4 sheets.

## Features
- Lists all games in a specified system folder with available images and marquees
- Interactively lets you choose between main image and thumbnail if both are present
- Uses a customizable template for card backgrounds
- Automatically scales and positions game images on the template
- Combines every 9 cards into a 3x3 grid on an A4-sized image for easy printing

## Requirements
- Python 3.x
- [ImageMagick](https://imagemagick.org/) (for `convert` and `composite` commands)
- Linux system (uses `xdg-open` for image preview)

## Usage
1. Place your `gamelist.xml` and images in your game system folder (e.g., `~/Batocera/userdata/roms/gamecube`).
2. Place your card template as `templates/template.png` (provided in this repo).
3. Run the script:

```bash
python3 cover_generator.py <path_to_game_system_folder>
```

- The script will process each game, ask you to choose between image and thumbnail if both are present, and generate card images in the `cards/` directory.
- Every 9 cards will be combined into a 3x3 grid on an A4-sized image, named `<system_name>_01.png`, `<system_name>_02.png`, etc.

## Example
```bash
python3 cover_generator.py ~/Batocera/userdata/roms/gamecube
```

## Template Attribution
The card template (`template.png`) and the inspiration for this project are based on resources from [zaparoo-helpers](https://github.com/thwonp/zaparoo-helpers/tree/main). 

## AI Assistance
This script and documentation were developed with the help of an AI agent (GitHub Copilot), which assisted in code generation, refactoring, and documentation.

---

**Enjoy creating your custom game cover cards!**
