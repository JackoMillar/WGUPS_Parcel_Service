# distances.py
# Handles loading and providing distance data between WGUPS locations.

import numpy as np
import pandas as pd

address_names = []
distance_matrix = None

# load_distance_data: Loads addresses and the distance matrix from the Excel file.
def load_distance_data(file_path):
    global address_names
    global distance_matrix
    
    try:
        # Load the Excel file. We skip the first 7 rows (header=None and then skip 7)
        # We read everything so we can correctly determine the addresses.
        df = pd.read_excel(file_path, header=None)
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Could not read Distance file: {e}")
        return False

    # The actual data starts at row index 7 (the 8th row)
    data_start_row = 7
    
    # Extract the addresses from column 1 (index 0) starting from row 8 (index 7)
    # These are the full names/addresses, including the Hub which should be first.
    # We clean and take only the address/location part which is in the first column
    address_names_raw = df.iloc[data_start_row:, 1].astype(str).str.strip().tolist()
    
    # IMPORTANT: Clean up the addresses to match the package data format.
    # The addresses are in the first row and first column of the matrix data block (starting at index 1 and 7)
    # We need to extract the clean address string from the Excel cell contents
    
    # 1. Extract Addresses (Column B, starting from Row 8)
    address_names = []
    for full_address_string in df.iloc[data_start_row:, 1]:
        # Addresses in the table often have the name/description and then the street address.
        # We try to clean it to get just the street address, which is the key.
        addr_line = str(full_address_string).strip()
        # Look for the second line which is usually the street address or standardize to the format.
        if '\n' in addr_line:
             # Take the line that looks most like a street address (e.g., the second line)
             parts = addr_line.split('\n')
             # Check if the third part exists and use it if it looks like an address line
             clean_address = parts[1].strip() if len(parts) > 1 else parts[0].strip()
        else:
             clean_address = addr_line

        # Remove the zip code in parentheses if present, to match the package format
        clean_address = clean_address.split('(')[0].strip()

        # Manually ensure the Hub is the first address in the distance matrix if needed
        # The Hub address is "4001 South 700 East" based on package file
        if clean_address == "4001 South 700 East":
            address_names.insert(0, clean_address)
        elif clean_address and clean_address not in address_names:
            address_names.append(clean_address)
            
    # Remove any empty or malformed entries, and re-order to ensure the Hub is first.
    HUB_ADDRESS = "4001 South 700 East"
    if HUB_ADDRESS in address_names:
        address_names.remove(HUB_ADDRESS)
        address_names.insert(0, HUB_ADDRESS)
    else:
        # If the Hub wasn't correctly captured, add it as the first location
        address_names.insert(0, HUB_ADDRESS)


    # 2. Extract the Distance Matrix (Data starts at row 8, column 3 (index 2))
    # We expect a square matrix of size N x N, where N is the length of address_names.
    N = len(address_names)
    
    # Read the data block: rows starting from 7, columns starting from 2 (C)
    # The distance values themselves start at column index 2 (C), row index 7 (8th row)
    distance_data = df.iloc[data_start_row : data_start_row + N, 2 : 2 + N]

    # Convert distance matrix to numeric, coercing errors to NaN and filling NaN with 0.
    distance_matrix = distance_data.apply(pd.to_numeric, errors='coerce').fillna(0).values
    
    # Check dimensions again before attempting symmetry
    if distance_matrix.shape[0] != distance_matrix.shape[1]:
        print(f"❌ ERROR: Distance matrix is not square. Shape is {distance_matrix.shape}. Expected {N}x{N}.")
        return False
    
    # Convert distance matrix to be symmetric (for robustness, assuming distance A->B == B->A)
    # This is the line that caused the ValueError, now executed on a square matrix.
    distance_matrix = np.maximum(distance_matrix, distance_matrix.T)
    
    print(f"✅ Distance data loaded. Total locations: {len(address_names)}. Matrix shape: {distance_matrix.shape}")
    return True

# get_address_index: Returns the index for a given address in the distance matrix.
def get_address_index(address):
    # Standardize the address by stripping whitespace and ensuring it matches the cleaned list.
    clean_address = address.strip()
    
    try:
        # Find the index of the full address string.
        index = address_names.index(clean_address)
        return index
    except ValueError:
        # Handle cases where the package address is not in the distance table's list
        # We need a robust matching system here, especially for similar addresses
        
        # Simple fallback for addresses that might be slightly different
        for i, name in enumerate(address_names):
            if clean_address in name or name in clean_address:
                return i
        
        print(f"⚠️ Warning: Address not found in distance data: '{address}'")
        return -1 # Return -1 to indicate failure

# get_distance: Returns the distance between two addresses.
def get_distance(addr1, addr2):
    global distance_matrix
    if distance_matrix is None:
        return float('inf')

    # Get indices for both addresses
    idx1 = get_address_index(addr1)
    idx2 = get_address_index(addr2)

    if idx1 == -1 or idx2 == -1:
        # If either address is not found, return an effectively infinite distance
        return float('inf') 

    # Look up the distance in the matrix
    # The index from the list (0, 1, 2...) corresponds directly to the matrix index
    return distance_matrix[idx1, idx2]
