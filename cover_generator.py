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
    
    # Display results
    print(f"\n{'='*100}")
    print(f"Found {len(games)} games in {game_system_path}")
    print(f"{'='*100}\n")
    
    missing_files = []
    
    for idx, game in enumerate(games, 1):
        print(f"[{idx}] Game: {game['name']} (ID: {game['id']})")
        print(f"    Path: {game['path']}")
        
        # Check image file
        if game['image']:
            image_exists, image_full_path = check_file_exists(game_system_path, game['image'])
            status = "✓" if image_exists else "✗"
            print(f"    {status} Image: {game['image']}")
            if not image_exists:
                missing_files.append((game['name'], 'Image', game['image']))
        else:
            print(f"    ⚠ Image: Not specified in gamelist.xml")
        
        # Check marquee file
        if game['marquee']:
            marquee_exists, marquee_full_path = check_file_exists(game_system_path, game['marquee'])
            status = "✓" if marquee_exists else "✗"
            print(f"    {status} Marquee: {game['marquee']}")
            if not marquee_exists:
                missing_files.append((game['name'], 'Marquee', game['marquee']))
        else:
            print(f"    ⚠ Marquee: Not specified in gamelist.xml")
        
        print()
    
    # Summary
    print(f"{'='*100}")
    print(f"Summary:")
    print(f"  Total games: {len(games)}")
    print(f"  Missing files: {len(missing_files)}")
    
    if missing_files:
        print(f"\nMissing files:")
        for game_name, file_type, file_path in missing_files:
            print(f"  - {game_name}: {file_type} ({file_path})")
    
    print(f"{'='*100}\n")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 cover_generator.py <path_to_game_system_folder>")
        print("\nExample:")
        print("  python3 cover_generator.py ~/games/GameCube")
        sys.exit(1)
    
    game_system_path = sys.argv[1]
    list_games(game_system_path)


if __name__ == "__main__":
    main()
