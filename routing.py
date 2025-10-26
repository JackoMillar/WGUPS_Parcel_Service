# routing.py
# Contains the logic for the Nearest Neighbor routing simulation and relies on the Truck class.

from datetime import datetime, timedelta
# Assuming 'distances.py' correctly exports 'get_distance'
from distances import get_distance
# NEW: Import Truck from package_model as per user's instruction
from package_model import Truck 

# select_next_package: Finds the closest, undelivered package currently 'En Route'.
# Uses the Nearest Neighbor heuristic.
def select_next_package(truck, package_hash_table):
    min_distance = float('inf')
    next_package_id = None

    current_address = truck.current_location

    # Iterate only over packages currently loaded on the truck
    for pkg_id in truck.packages:
        pkg = package_hash_table.lookup(pkg_id)
        # Only consider packages that are loaded and not yet delivered
        if pkg and pkg.status == "En Route":
            distance = get_distance(current_address, pkg.address)
            
            if distance < min_distance:
                min_distance = distance
                next_package_id = pkg_id
    
    return next_package_id, min_distance

# run_delivery_simulation: Executes the delivery for a single truck.
def run_delivery_simulation(truck, package_hash_table):
    # Set the departure time for all packages on the truck
    for pkg_id in truck.packages:
        pkg = package_hash_table.lookup(pkg_id)
        if pkg:
            # Only update status and departure time if the package is still 'At Hub'
            if pkg.status == "At Hub":
                pkg.status = "En Route"
                pkg.departure_time = truck.start_time

    # Routing loop: runs until all packages on the truck are delivered
    while any(package_hash_table.lookup(pkg_id).status == "En Route" for pkg_id in truck.packages):
        
        # 1. Select the next closest package using the Nearest Neighbor heuristic
        next_id, distance_to_next = select_next_package(truck, package_hash_table)

        if next_id is None:
            # All packages on the truck are delivered
            break 
            
        next_pkg = package_hash_table.lookup(next_id)
        
        # 2. Handle Address Correction (Constraint for Package 9)
        # The correct address is available at 10:20 AM. Check if the truck has reached that time.
        if next_id == 9 and truck.current_time >= datetime(2025, 10, 26, 10, 20):
            # Apply the correction: Address and Zip
            next_pkg.address = "410 S State St" 
            next_pkg.zip_code = "84111"
            # Since the address changed, recalculate the distance from the current location
            # This is critical for the nearest neighbor algorithm to work correctly after the address change
            distance_to_next = get_distance(truck.current_location, next_pkg.address)

        # 3. Calculate travel time and update truck time/mileage
        time_to_travel = timedelta(hours=distance_to_next / truck.speed)
        truck.current_time += time_to_travel
        truck.current_mileage += distance_to_next
        truck.current_location = next_pkg.address
        
        # Log the stop in the route
        truck.route.append(next_pkg.id)

        # 4. Deliver the package
        next_pkg.status = "Delivered"
        next_pkg.delivery_time = truck.current_time
        
        print(f"Truck {truck.id}: Delivered Pkg {next_pkg.id} to {next_pkg.address} at {next_pkg.delivery_time.strftime('%H:%M:%S')}. Total Miles: {truck.current_mileage:.2f}")

    # After all deliveries, return to the hub
    HUB_ADDRESS = "4001 South 700 East"
    distance_to_hub = get_distance(truck.current_location, HUB_ADDRESS)
    time_to_hub = timedelta(hours=distance_to_hub / truck.speed)
    
    # Only travel back to hub if the truck is not already there (which shouldn't happen)
    if distance_to_hub > 0.0:
        truck.current_time += time_to_hub
        truck.current_mileage += distance_to_hub

    print(f"\nTruck {truck.id} returned to Hub at {truck.current_time.strftime('%H:%M:%S')}. Total Route Miles: {truck.current_mileage:.2f}\n")
    return truck.current_mileage
