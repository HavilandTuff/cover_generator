#!/usr/bin/env python3
"""
Script to list all games from a game system folder and their corresponding image and marquee files.
Usage: python3 cover_generator.py <path_to_game_system_folder>
"""

import sys
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Tuple


def parse_gamelist(gamelist_path: str) -> List[Dict[str, str]]:
    """
    Parse the gamelist.xml file and extract game information.
    
    Args:
        gamelist_path: Path to the gamelist.xml file
        
    Returns:
        List of dictionaries containing game information
    """
    games = []
    
    try:
        tree = ET.parse(gamelist_path)
        root = tree.getroot()
        
        for game in root.findall('game'):
            game_info = {
                'id': game.get('id', 'N/A'),
                'name': game.findtext('name', 'Unknown'),
                'path': game.findtext('path', 'N/A'),
                'image': game.findtext('image', ''),
                'thumbnail': game.findtext('thumbnail', ''),
                'marquee': game.findtext('marquee', ''),
            }
            games.append(game_info)
    except ET.ParseError as e:
        print(f"Error parsing XML: {e}", file=sys.stderr)
        return []
    except FileNotFoundError:
        print(f"Error: gamelist.xml not found at {gamelist_path}", file=sys.stderr)
        return []
    
    return games


def check_file_exists(base_path: str, file_path: str) -> Tuple[bool, str]:
    """
    Check if a file exists relative to the base path.
    
    Args:
        base_path: Base directory path
        file_path: Relative file path from gamelist.xml
        
    Returns:
        Tuple of (exists: bool, full_path: str)
    """
    # Remove leading ./ from path if present
    clean_path = file_path.lstrip('./')
    full_path = os.path.join(base_path, clean_path)
    exists = os.path.isfile(full_path)
    return exists, full_path


def list_games(game_system_path: str) -> None:
    """
    List all games from the game system folder with their image and marquee files.
    
    Args:
        game_system_path: Path to the game system folder
    """
    # Verify the path exists
    if not os.path.isdir(game_system_path):
        print(f"Error: Directory '{game_system_path}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Check if gamelist.xml exists
    gamelist_path = os.path.join(game_system_path, 'gamelist.xml')
    if not os.path.isfile(gamelist_path):
        print(f"Error: gamelist.xml not found in '{game_system_path}'", file=sys.stderr)
        sys.exit(1)
    
    # Parse the gamelist
    games = parse_gamelist(gamelist_path)
    
    if not games:
        print("No games found in gamelist.xml", file=sys.stderr)
        sys.exit(1)
    
    complete_games = []
    for game in games:
        # Prefer thumbnail with 'thumb' in filename if present and exists
        thumb_path = game.get('thumbnail', '')
        thumb_ok = False
        if thumb_path and 'thumb' in os.path.basename(thumb_path).lower():
            thumb_exists, thumb_full = check_file_exists(game_system_path, thumb_path)
            if thumb_exists:
                image_path = thumb_full
                thumb_ok = True
        if not thumb_ok:
            # Fallback to image
            if not game['image']:
                continue
            image_exists, image_path = check_file_exists(game_system_path, game['image'])
            if not image_exists:
                continue
        if not game['marquee']:
            continue
        marquee_exists, _ = check_file_exists(game_system_path, game['marquee'])
        if marquee_exists:
            game['image_path'] = image_path
            complete_games.append(game)

    print(f"\n{'='*100}")
    print(f"Found {len(complete_games)} games with both image and marquee files")
    print(f"(Total games in gamelist.xml: {len(games)})")
    print(f"{'='*100}\n")

    cards_dir = os.path.join(os.path.dirname(__file__), 'cards')
    os.makedirs(cards_dir, exist_ok=True)

    card_paths = []
    for idx, game in enumerate(complete_games, 1):
        print(f"[{idx}] Game: {game['name']} (ID: {game['id']})")
        print(f"    Path: {game['path']}")
        print(f"    Image: {game['image']}")
        print(f"    Marquee: {game['marquee']}")
        card_filename = f"card_{idx:04d}.png"
        card_path = os.path.join(cards_dir, card_filename)
        generate_game_card(game['image_path'], card_path)
        card_paths.append(card_path)
        print(f"    Card generated: {card_path}")
        print()

    # Combine every 9 cards into a 3x3 grid on A4
    system_name = os.path.basename(os.path.abspath(game_system_path))
    combine_cards_to_a4(card_paths, system_name)

    print(f"{'='*100}")
    print(f"Summary:")
    print(f"  Complete games (with both image and marquee): {len(complete_games)}")
    print(f"  Incomplete games: {len(games) - len(complete_games)}")
    print(f"{'='*100}\n")

def combine_cards_to_a4(card_paths, system_name):
    """
    Combine every 9 card images into a 3x3 grid on an A4-sized image and save as systemname_pagenum.png.
    """
    import math
    import subprocess
    # A4 at 300dpi: 2480 x 3508 px
    a4_width, a4_height = 2480, 3508
    card_w, card_h = 638, 1012
    grid_cols, grid_rows = 3, 3
    margin_x = (a4_width - grid_cols * card_w) // (grid_cols + 1)
    margin_y = (a4_height - grid_rows * card_h) // (grid_rows + 1)
    page_count = math.ceil(len(card_paths) / 9)
    for page in range(page_count):
        page_cards = card_paths[page*9:(page+1)*9]
        # Create blank A4 image
        a4_path = f"{system_name}_{page+1:02d}.png"
        a4_full_path = os.path.join(os.path.dirname(card_paths[0]), a4_path)
        # Build ImageMagick command
        cmd = ["convert", "-size", f"{a4_width}x{a4_height}", "xc:white"]
        for idx, card in enumerate(page_cards):
            col = idx % grid_cols
            row = idx // grid_cols
            x = margin_x + col * (card_w + margin_x)
            y = margin_y + row * (card_h + margin_y)
            cmd += [card, "-geometry", f"+{x}+{y}", "-composite"]
        cmd.append(a4_full_path)
        try:
            subprocess.run(cmd, check=True)
            print(f"A4 page created: {a4_full_path}")
        except Exception as e:
            print(f"Error creating A4 page {a4_full_path}: {e}", file=sys.stderr)

def generate_game_card(game_image_path: str, output_path: str):
    """
    Generate a game card by compositing the game image onto the template.
    The template is 638x1012 px. The image is scaled and placed in area x1=30, y1=27 to x2=606, y2=948.
    """
    template_path = os.path.join(os.path.dirname(__file__), 'templates', 'template.png')
    x1, y1, x2, y2 = 30, 110, 606, 948
    width = x2 - x1
    height = y2 - y1
    import subprocess
    resize_str = f"{width}x{height}^"
    extent_str = f"{width}x{height}"
    try:
        temp_scaled = output_path + ".tmp.png"
        subprocess.run([
            "convert", game_image_path,
            "-resize", resize_str,
            "-gravity", "center",
            "-extent", extent_str,
            temp_scaled
        ], check=True)
        subprocess.run([
            "composite",
            "-geometry", f"+{x1}+{y1}",
            temp_scaled,
            template_path,
            output_path
        ], check=True)
        os.remove(temp_scaled)
    except Exception as e:
        print(f"Error generating card for {game_image_path}: {e}", file=sys.stderr)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 cover_generator.py <path_to_game_system_folder>")
        print("\nExample:")
        print("  python3 cover_generator.py ~/games/GameCube")
        sys.exit(1)
    
    game_system_path = sys.argv[1]
    print(f"Processing game system folder: {game_system_path}\n")
    list_games(game_system_path)


if __name__ == "__main__":
    main()
