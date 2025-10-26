from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Package Class: Represents a single package and its current delivery status.
class Package:
    def __init__(self, pkg_id, address, city, state, zip_code, deadline, weight, notes):
        # Package attributes
        self.id = pkg_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.deadline = deadline
        self.weight = weight
        self.notes = notes
        
        # Delivery status attributes
        self.status = "At Hub"  # Possible statuses: 'At Hub', 'En Route', 'Delivered'
        self.delivery_time = None
        self.departure_time = None

    def __str__(self):
        # String representation for easy printing and lookup
        delivery_info = f"Delivered at: {self.delivery_time.strftime('%H:%M:%S')}" if self.delivery_time else "Not Delivered"
        return (f"Package ID: {self.id}, Address: {self.address}, Deadline: {self.deadline}, "
                f"Weight: {self.weight}, Status: {self.status}, {delivery_info}")

# HashTable Class (Separate Chaining): Used for efficient O(1) average time 
# package insertion and lookup based on Package ID.
class HashTable:
    def __init__(self, capacity=40):
        self.capacity = capacity
        self.table = [[] for _ in range(capacity)]

    def _hash(self, key):
        # Simple modulo hash function
        return key % self.capacity

    def insert(self, key, value):
        # Insert or update a package (key=id, value=Package object)
        bucket = self._hash(key)
        bucket_list = self.table[bucket]

        # Check for update (if key already exists)
        for i, (k, v) in enumerate(bucket_list):
            if k == key:
                bucket_list[i] = (key, value)
                return

        # Insert new package
        bucket_list.append((key, value))

    def lookup(self, key):
        # Retrieve a package based on its ID
        bucket = self._hash(key)
        bucket_list = self.table[bucket]

        for k, v in bucket_list:
            if k == key:
                return v
        return None

# Truck Class: Represents a delivery truck with its capacity, speed, and state.
class Truck:
    def __init__(self, truck_id, start_time, capacity=16, speed_mph=18):
        self.id = truck_id
        self.start_time = start_time
        self.packages = []
        self.current_time = start_time
        self.current_mileage = 0.0
        self.current_location = "4001 South 700 East"  # Assumed Depot Address
        self.capacity = capacity
        self.speed = speed_mph
        self.route = [] # List of addresses in order of delivery

def load_packages_from_excel(file_path, hash_table):
    try:
        # Use header=7 (8th row, 0-indexed) as the header row based on file inspection
        df = pd.read_excel(file_path, header=7)
    except Exception as e:
        print(f"❌ CRITICAL ERROR: Could not read Package file: {e}")
        return False

    # Robust column standardization (removes spaces, special chars, converts to lower)
    df.columns = df.columns.astype(str).str.strip().str.lower()
    df.columns = df.columns.str.replace('[^a-z0-9\s]', ' ', regex=True)
    df.columns = df.columns.str.replace('\s+', ' ', regex=True).str.strip()

    # Rename the problematic notes column to a standard name for easy lookup
    # This addresses the previous issue with column name 'page 1 of 1pagespecial notes'
    df = df.rename(columns={'page 1 of 1pagespecial notes': 'notes'}, errors='ignore')
    
    for index, row in df.iterrows():
        # Stop if package id is NaN, indicating end of data in the spreadsheet
        if pd.isna(row.get("package id")):
             break
        
        try:
            # Data extraction using standardized, lowercase column names
            pkg = Package(
                # Use split('.')[0] to safely convert potential floats (e.g., 1.0) to integers
                pkg_id = int(str(row["package id"]).strip().split('.')[0]), 
                address = str(row["address"]).strip(),
                city = str(row["city"]).strip(),
                state = str(row["state"]).strip(),
                zip_code = str(row["zip"]).strip().split('.')[0], 
                deadline = str(row["delivery deadline"]).strip(),
                weight = str(row["weight kilo"]).strip(),
                notes = str(row.get("notes", "")).strip().replace('nan', '')
            )
            hash_table.insert(pkg.id, pkg)

        except KeyError as e:
            print(f"❌ CRITICAL ERROR: Missing expected column {e}. Check your Excel file headers!")
            return False 
        except Exception as e:
            print(f"❌ ERROR inserting package at index {index}: {e}")
            continue

    print("✅ All packages loaded successfully!")
    return True