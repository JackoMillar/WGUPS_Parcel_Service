# {STUDENT_ID_HERE}
# WGUPS Routing Program - main.py
# This file serves as the main entry point, handling imports, truck loading, and simulation execution.

from datetime import datetime
from package_model import HashTable, load_packages_from_excel
from distances import load_distance_data # Only need to load data here
from routing import Truck, run_delivery_simulation

# Initialize the global package hash table
package_table = HashTable()

def main():
    # 1. Global Setup (Start Time)
    START_TIME = datetime(2025, 10, 26, 8, 0, 0) # 8:00 AM Start
    DELAYED_DEPARTURE_TIME = datetime(2025, 10, 26, 9, 5, 0) # Truck 2 leaves at 9:05 AM
    
    # 2. Load Data (Packages and Distances)
    if not load_distance_data("WGUPS Distance Table.xlsx"):
        # The load function prints the error, so we just exit here
        return
    if not load_packages_from_excel("WGUPS Package File.xlsx", package_table):
        # The load function prints the error, so we just exit here
        return

    # 3. Manual Truck Loading (Meeting all Constraints)
    # The loading strategy is designed to meet all deadlines and grouping/truck constraints.
    
    # Truck 2 (Driver 2): Delayed departure at 9:05 AM. Must take all delayed and Truck 2 only packages.
    # Grouped: (13, 15, 19, 20)
    # Delayed: 6, 25, 28, 32
    # Truck 2 Only: 3, 18, 36
    truck_2_pkgs = [
        3, 6, 18, 25, 28, 32, 36, 
        13, 15, 19, 20, 
        29, 30, 31, 34, 40 # Fill remaining capacity with 10:30 deadlines/EOD for efficiency
    ] # Total: 16 packages
    truck2 = Truck(2, DELAYED_DEPARTURE_TIME)
    truck2.packages = truck_2_pkgs
    
    # Truck 1 (Driver 1, Route 1): Starts at 8:00 AM. Targets 10:30 deadlines first.
    # Remaining 10:30 Deadlines: 1, 16
    truck_1_pkgs = [
        1, 16, 
        4, 5, 7, 8, 10, 11, 12, 14, 17, 21, 22, 23, 24, 26 # EOD Packages
    ] # Total: 16 packages
    truck1 = Truck(1, START_TIME)
    truck1.packages = truck_1_pkgs

    # Truck 3 (Driver 1, Route 2): Handles the remaining 8 packages, including Pkg 9.
    # Pkg 9 address correction is available at 10:20 AM. This late route ensures we wait for the correction.
    truck_3_pkgs = [2, 9, 27, 33, 35, 37, 38, 39]
    truck3 = Truck(3, START_TIME) # Temp start time, will be updated after Truck 1 returns.
    truck3.packages = truck_3_pkgs

    # 4. Run Simulations
    
    # Run Truck 1 (Driver 1, Route 1)
    mileage_truck1 = run_delivery_simulation(truck1, package_table)
    
    # Driver 1 takes Truck 3 immediately upon returning from Truck 1 route
    truck3.start_time = truck1.current_time
    truck3.current_time = truck3.start_time
    
    # Run Truck 2 (Driver 2 - runs concurrently/separately, starts at 9:05 AM)
    mileage_truck2 = run_delivery_simulation(truck2, package_table)
    
    # Run Truck 3 (Driver 1, Route 2)
    mileage_truck3 = run_delivery_simulation(truck3, package_table)

    # 5. Reporting
    total_mileage = mileage_truck1 + mileage_truck2 + mileage_truck3
    
    print("\n=======================================================")
    print(f"| FINAL REPORT: WGUPS DELIVERY SIMULATION            |")
    print("=======================================================")
    print(f"| Truck 1 Mileage (Route 1): {mileage_truck1:.2f} miles")
    print(f"| Truck 2 Mileage (Route 1): {mileage_truck2:.2f} miles")
    print(f"| Truck 3 Mileage (Route 2): {mileage_truck3:.2f} miles")
    print("-------------------------------------------------------")
    print(f"| TOTAL ALL ROUTES MILEAGE: {total_mileage:.2f} miles")
    print("=======================================================\n")
    
    # Example lookup test at the end of the day
    print(f"Package 1 (Test Lookup): {package_table.lookup(1)}")
    print(f"Package 9 (Test Lookup): {package_table.lookup(9)}")
    print(f"Package 20 (Test Lookup): {package_table.lookup(20)}")


if __name__ == "__main__":
    main()
