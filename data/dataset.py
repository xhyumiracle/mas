import json
import os

def read_gaia_json(filepath="/mnt/d/Agent/mas/data/gaia/level_1.json"):
    """
    Read and parse a JSON file from the specified path.
    
    Args:
        filepath (str): Path to the JSON file
        
    Returns:
        dict: Parsed JSON content
    """
    try:
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return None
            
        # Open and read the JSON file
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        print(f"Successfully loaded JSON from {filepath}")
        return data
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

# Example usage:
# gaia_data = read_gaia_json()
# print(gaia_data)