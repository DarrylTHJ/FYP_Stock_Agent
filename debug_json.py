import os
import json

# Check this path matches your folder structure
TARGET_DIR = "./data/retail/processed" 

def inspect_first_file():
    if not os.path.exists(TARGET_DIR):
        print(f"ERROR: Directory not found: {TARGET_DIR}")
        return

    files = [f for f in os.listdir(TARGET_DIR) if f.endswith(".json")]
    if not files:
        print(f"ERROR: No .json files found in {TARGET_DIR}")
        return

    first_file = files[0]
    path = os.path.join(TARGET_DIR, first_file)
    
    print(f"--- Inspecting: {first_file} ---")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            print(f"Type of data: {type(data)}")
            
            if isinstance(data, dict):
                print(f"Top-level keys found: {list(data.keys())}")
                for key, value in data.items():
                    print(f" - Key '{key}' contains: {type(value)}")
                    if isinstance(value, list) and len(value) > 0:
                        print(f"   - First item in list: {value[0]}")
            elif isinstance(data, list):
                print("Data is a List (not a Dict).")
                if len(data) > 0:
                    print(f"First item: {data[0]}")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    inspect_first_file()