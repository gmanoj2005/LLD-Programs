import datetime
import random

class User:
    def __init__(self, id, name, password, age, gender):
        self.id = id
        self.name = name
        self.password = password
        self.age = age
        self.gender = gender

    def login(self, name, password):
        return self.name == name and self.password == password

    def __repr__(self):
        return f"User(ID: {self.id}, Name: {self.name}, Type: {self.__class__.__name__})"
    
class Customer(User):
    def __init__(self, id, name, password, age, gender):
        super().__init__(id, name, password, age, gender)
        self.trip_history = []  # List of Ride objects

    def view_history(self):
        return self.trip_history

    # hail_cab and confirm_ride logic will be handled by ZulaSystem,
    # Customer object will interact with ZulaSystem for these actions.

class Driver(User):
    def __init__(self, id, name, password, age, gender, current_location_id):
        super().__init__(id, name, password, age, gender)
        self.current_location_id = current_location_id  # Store location ID
        self.is_on_rest = False
        self.total_trips = 0
        self.total_fare_earned = 0.0
        self.total_commission_earned = 0.0 # Commission for driver from Zula
        self.trip_history = []  # List of Ride objects

    def complete_ride(self, ride):
        self.total_trips += 1
        self.total_fare_earned += ride.fare
        self.total_commission_earned += (ride.fare - ride.zula_commission) # Driver gets 70% of fare
        self.trip_history.append(ride)
        self.is_on_rest = True  # Set driver to rest after a trip

    def view_my_summary(self):
        return {
            "Cab ID": self.id, # Using driver ID as Cab ID for simplicity as 1 driver per cab
            "Total Trips": self.total_trips,
            "Total Fare Earned": self.total_fare_earned,
            "Total Commission Earned (from Zula)": self.total_commission_earned,
            "Trip Details": [{
                "Source": ride.source.name,
                "Destination": ride.destination.name,
                "Fare": ride.fare,
                "Start Time": ride.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "End Time": ride.end_time.strftime("%Y-%m-%d %H:%M:%S")
            } for ride in self.trip_history]
        }

class Admin(User):
    def __init__(self, id, name, password, age, gender):
        super().__init__(id, name, password, age, gender)

    # Admin actions like CURD for cabs, locations, and users
    # will be methods within the ZulaSystem, called by an Admin instance.

class Location:
    def __init__(self, id, name, distance_from_origin):
        self.id = id
        self.name = name
        self.distance_from_origin = distance_from_origin

    def __repr__(self):
        return f"Location(ID: {self.id}, Name: {self.name}, Dist: {self.distance_from_origin})"

class Cab:
    def __init__(self, id, current_location_id, driver_id):
        self.id = id
        self.current_location_id = current_location_id
        self.driver_id = driver_id  # Link to the driver
        self.is_available = True  # True if not currently on a trip

    def set_location(self, new_location_id):
        self.current_location_id = new_location_id

    def set_availability(self, status):
        self.is_available = status

    def __repr__(self):
        return f"Cab(ID: {self.id}, Location: {self.current_location_id}, Driver: {self.driver_id}, Available: {self.is_available})"

class Ride:
    def __init__(self, id, customer_id, driver_id, cab_id, source, destination, fare, zula_commission, start_time, end_time):
        self.id = id
        self.customer_id = customer_id
        self.driver_id = driver_id
        self.cab_id = cab_id
        self.source = source  # Location object
        self.destination = destination # Location object
        self.fare = fare
        self.zula_commission = zula_commission
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return (f"Ride(ID: {self.id}, From: {self.source.name} to {self.destination.name}, "
                f"Cab ID: {self.cab_id}, Fare: {self.fare:.2f})")

import time
import math

class ZulaSystem:
    def __init__(self):
        self.next_user_id = 1
        self.next_location_id = 1
        self.next_cab_id = 1
        self.next_ride_id = 1

        # In-memory data storage
        self.cab_drivers = {}  # {driver_id: Driver object}
        self.customers = {}  # {customer_id: Customer object}
        self.admins = {}  # {admin_id: Admin object}
        self.users_by_credentials = {}  # {(name, password): user_id}

        self.locations = {}  # {location_id: Location object}
        self.cabs = {}  # {cab_id: Cab object}
        # {location_id: [cab_id1, cab_id2, ...]}
        self.cab_locations = {}
        # {driver_id: True/False} True if on rest
        self.unavailable_drivers = set()
        self.rides_history = {}  # {ride_id: Ride object}

        self.initialize_data() # Initialize with some dummy data

    def _generate_id(self, prefix):
        if prefix == "user":
            _id = self.next_user_id
            self.next_user_id += 1
        elif prefix == "location":
            _id = self.next_location_id
            self.next_location_id += 1
        elif prefix == "cab":
            _id = self.next_cab_id
            self.next_cab_id += 1
        elif prefix == "ride":
            _id = self.next_ride_id
            self.next_ride_id += 1
        else:
            raise ValueError("Invalid ID prefix")
        return _id

    # Task 1: Initialize or load tables
    def initialize_data(self):
        # Locations (A --- B --- C --- M ----- P ----- G)
        self.add_location(name="A", distance_from_origin=0)
        self.add_location(name="B", distance_from_origin=2)
        self.add_location(name="C", distance_from_origin=5)
        self.add_location(name="M", distance_from_origin=10)
        self.add_location(name="P", distance_from_origin=15)
        self.add_location(name="G", distance_from_origin=20)

        # Drivers
        self.signup("driver", "ram", "hsigh", 32, "M", initial_location_name="A")
        self.signup("driver", "raja", "dfksf", 22, "F", initial_location_name="P")
        self.signup("driver", "sita", "abcd", 28, "F", initial_location_name="C")
        self.signup("driver", "mohan", "1234", 40, "M", initial_location_name="A")

        # Customers
        self.signup("customer", "cust1", "pass1", 25, "M")
        self.signup("customer", "cust2", "pass2", 30, "F")

        # Admin
        self.signup("admin", "admin1", "adminpass", 35, "M")

        # Initial Cab Locations - already handled by driver signup/cab creation

    # Helper to get location by name
    def _get_location_by_name(self, name):
        for loc_id, loc_obj in self.locations.items():
            if loc_obj.name == name:
                return loc_obj
        return None

    # Task 2: Login / Sign Up
    def signup(self, user_type, name, password, age, gender, initial_location_name=None):
        if (name, password) in self.users_by_credentials:
            print(f"Error: User with name '{name}' and password already exists.")
            return None

        user_id = self._generate_id("user")
        user = None

        if user_type == "customer":
            user = Customer(user_id, name, password, age, gender)
            self.customers[user_id] = user
        elif user_type == "driver":
            if not initial_location_name:
                print("Error: Driver must have an initial location.")
                return None
            location_obj = self._get_location_by_name(initial_location_name)
            if not location_obj:
                print(f"Error: Location '{initial_location_name}' not found.")
                return None

            user = Driver(user_id, name, password, age, gender, location_obj.id)
            self.cab_drivers[user_id] = user

            # Create a cab for the driver
            cab_id = self._generate_id("cab")
            cab = Cab(cab_id, location_obj.id, user_id)
            self.cabs[cab_id] = cab
            if location_obj.id not in self.cab_locations:
                self.cab_locations[location_obj.id] = []
            self.cab_locations[location_obj.id].append(cab_id)
            print(f"Cab {cab_id} assigned to driver {user.name} at {location_obj.name}.")
        elif user_type == "admin":
            user = Admin(user_id, name, password, age, gender)
            self.admins[user_id] = user
        else:
            print("Invalid user type.")
            return None

        self.users_by_credentials[(name, password)] = user_id
        print(f"Successfully signed up {user_type} {name} with ID {user_id}.")
        return user

    def login(self, user_type, name, password):
        user_id = self.users_by_credentials.get((name, password))
        if not user_id:
            print("Login failed: Invalid credentials.")
            return None

        user = None
        if user_type == "customer" and user_id in self.customers:
            user = self.customers[user_id]
        elif user_type == "driver" and user_id in self.cab_drivers:
            user = self.cab_drivers[user_id]
        elif user_type == "admin" and user_id in self.admins:
            user = self.admins[user_id]
        else:
            print("Login failed: User type mismatch or user not found.")
            return None

        if user and user.login(name, password):
            print(f"Login successful for {user_type} {name}.")
            return user
        else:
            print("Login failed: Internal error or credentials mismatch.")
            return None

    # Helper methods to get objects
    def get_driver_by_id(self, driver_id):
        return self.cab_drivers.get(driver_id)

    def get_customer_by_id(self, customer_id):
        return self.customers.get(customer_id)

    def get_admin_by_id(self, admin_id):
        return self.admins.get(admin_id)

    def get_location_by_id(self, location_id):
        return self.locations.get(location_id)

    def get_cab_by_id(self, cab_id):
        return self.cabs.get(cab_id)

    def get_location_name(self, location_id):
        loc = self.get_location_by_id(location_id)
        return loc.name if loc else "Unknown Location"

    def get_cab_driver_id(self, cab_id):
        cab = self.get_cab_by_id(cab_id)
        return cab.driver_id if cab else None

    def get_driver_name(self, driver_id):
        driver = self.get_driver_by_id(driver_id)
        return driver.name if driver else "Unknown Driver"

    # Task 4: Hail a cab & Fare Calculation
    def calculate_fare(self, source_location_id, destination_location_id):
        source_loc = self.get_location_by_id(source_location_id)
        dest_loc = self.get_location_by_id(destination_location_id)
        if not source_loc or not dest_loc:
            return None # Or raise error

        distance = abs(source_loc.distance_from_origin - dest_loc.distance_from_origin)
        fare = distance * 10
        return fare

    def get_closest_available_driver_info(self, source_location_id):
        source_loc = self.get_location_by_id(source_location_id)
        if not source_loc:
            print("Error: Source location not found.")
            return []

        available_cabs_info = []
        for loc_id, cab_ids_at_loc in self.cab_locations.items():
            location_obj = self.get_location_by_id(loc_id)
            if not location_obj:
                continue

            for cab_id in cab_ids_at_loc:
                cab = self.get_cab_by_id(cab_id)
                if not cab or not cab.is_available:
                    continue

                driver = self.get_driver_by_id(cab.driver_id)
                # Task 3: Driver rest
                if driver and not driver.is_on_rest:
                    distance_to_pickup = abs(source_loc.distance_from_origin - location_obj.distance_from_origin)
                    available_cabs_info.append({
                        "cab_id": cab.id,
                        "driver_id": driver.id,
                        "current_location_id": loc_id,
                        "distance_to_pickup": distance_to_pickup
                    })

        # Sort by distance to pickup, then by driver's total trips for fair allocation (Task 8)
        available_cabs_info.sort(key=lambda x: (x["distance_to_pickup"], self.cab_drivers[x["driver_id"]].total_trips))

        return available_cabs_info

    def hail_cab(self, customer_id, source_location_name, destination_location_name):
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            print("Error: Customer not found.")
            return None

        source_loc = self._get_location_by_name(source_location_name)
        dest_loc = self._get_location_by_name(destination_location_name)
        if not source_loc:
            print(f"Error: Source location '{source_location_name}' not found.")
            return None
        if not dest_loc:
            print(f"Error: Destination location '{destination_location_name}' not found.")
            return None

        fare = self.calculate_fare(source_loc.id, dest_loc.id)
        if fare is None:
            print("Error calculating fare. Invalid locations.")
            return None

        recommended_cabs_info = []
        closest_drivers_info = self.get_closest_available_driver_info(source_loc.id)

        print("\nRecommended Cabs:")
        print("--------------------------------------------------")
        print(f"{'Location':<15} {'Cab ID':<10} {'Driver':<15} {'Distance to Pickup':<20}")
        print("--------------------------------------------------")
        for cab_info in closest_drivers_info:
            cab_id = cab_info["cab_id"]
            driver_id = cab_info["driver_id"]
            current_location_id = cab_info["current_location_id"]
            distance_to_pickup = cab_info["distance_to_pickup"]

            driver = self.get_driver_by_id(driver_id)
            if driver and not driver.is_on_rest: # Double check for rest period (Task 3)
                recommended_cabs_info.append({
                    "cab_id": cab_id,
                    "driver_id": driver_id,
                    "current_location_id": current_location_id,
                    "location_name": self.get_location_name(current_location_id),
                    "driver_name": driver.name,
                    "distance_to_pickup": distance_to_pickup
                })
                print(f"{self.get_location_name(current_location_id):<15} {cab_id:<10} {driver.name:<15} {distance_to_pickup:<20}")

        if not recommended_cabs_info:
            print("No cabs available at the moment.")
            return None

        # Simulate customer choosing a cab (e.g., the first one for simplicity)
        chosen_cab_info = recommended_cabs_info[0]
        print(f"\nCustomer confirms booking with Cab ID {chosen_cab_info['cab_id']} "
              f"driven by {chosen_cab_info['driver_name']}.")

        # Process the ride
        ride = self.process_ride(
            customer_id,
            chosen_cab_info["driver_id"],
            chosen_cab_info["cab_id"],
            source_loc.id,
            dest_loc.id
        )
        return ride

    def process_ride(self, customer_id, driver_id, cab_id, source_id, destination_id):
        customer = self.get_customer_by_id(customer_id)
        driver = self.get_driver_by_id(driver_id)
        cab = self.get_cab_by_id(cab_id)
        source_loc = self.get_location_by_id(source_id)
        dest_loc = self.get_location_by_id(destination_id)

        if not all([customer, driver, cab, source_loc, dest_loc]):
            print("Error: Invalid data for processing ride.")
            return None

        fare = self.calculate_fare(source_id, destination_id)
        zula_commission = fare * 0.30  # Task 6: Zula's 30% commission

        start_time = datetime.datetime.now()
        # Simulate travel time
        time.sleep(1)
        end_time = datetime.datetime.now()

        ride_id = self._generate_id("ride")
        ride = Ride(ride_id, customer_id, driver_id, cab_id, source_loc, dest_loc, fare, zula_commission, start_time, end_time)
        self.rides_history[ride_id] = ride

        # Update driver and cab status
        driver.complete_ride(ride)
        cab.set_location(destination_id) # Cab moves to destination
        cab.set_availability(True) # Cab is available after dropping off
        self.unavailable_drivers.add(driver.id) # Driver on rest (Task 3)

        # Update cab_locations mapping
        self.update_cab_location_in_memory(cab_id, source_id, destination_id)

        customer.trip_history.append(ride)

        print(f"\nRide completed! Ride ID: {ride.id}")
        print(f"  From: {source_loc.name} to {dest_loc.name}")
        print(f"  Cab ID: {cab_id}, Driver: {driver.name}")
        print(f"  Fare: ${fare:.2f}")
        print(f"  Zula's Commission: ${zula_commission:.2f}")
        print(f"  Driver {driver.name} is now on rest.")
        return ride

    # Task 5: View Customer History
    def view_customer_history(self, customer_id):
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            print("Error: Customer not found.")
            return

        if not customer.trip_history:
            print(f"Customer {customer.name} has no ride history.")
            return

        print(f"\n--- Ride History for Customer: {customer.name} ---")
        print("------------------------------------------------------------------------------------")
        print(f"{'Source':<10} {'Destination':<12} {'Cab ID':<8} {'Fare':<8} {'Driver':<15} {'Zula Commission':<18}")
        print("------------------------------------------------------------------------------------")
        for ride in customer.trip_history:
            driver_name = self.get_driver_name(ride.driver_id)
            print(f"{ride.source.name:<10} {ride.destination.name:<12} {ride.cab_id:<8} {ride.fare:<8.2f} {driver_name:<15} {ride.zula_commission:<18.2f}")
        print("------------------------------------------------------------------------------------")

    # Task 6: Zula's Commission (Integrated into process_ride and view_admin_summary)
    def view_zula_commission_summary(self):
        total_zula_commission = sum(ride.zula_commission for ride in self.rides_history.values())
        print(f"\n--- Zula's Commission Summary ---")
        print(f"Total Zula's Commission from all rides: ${total_zula_commission:.2f}")
        return {"total_zula_commission": total_zula_commission}

    # Task 7: Admin - Redirect cabs
    def redirect_cabs(self, admin_id, source_location_name):
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        source_loc = self._get_location_by_name(source_location_name)
        if not source_loc:
            print(f"Error: Location '{source_location_name}' not found.")
            return False

        cabs_at_location = self.cab_locations.get(source_loc.id, [])
        if len(cabs_at_location) <= 2:
            print(f"No more than 2 cabs at {source_loc.name}. No redirection needed.")
            return False

        cabs_to_redirect_ids = cabs_at_location[2:] # Keep first 2, redirect the rest
        redirected_count = 0

        # Find available locations to redirect to
        target_locations = [loc_id for loc_id in self.locations.keys() if loc_id != source_loc.id]
        if not target_locations:
            print("No other locations available for redirection.")
            return False

        print(f"\nRedirecting cabs from {source_loc.name}:")
        for cab_id in cabs_to_redirect_ids:
            cab = self.get_cab_by_id(cab_id)
            if cab:
                # Simple round-robin or random redirection for fairness
                new_location_id = random.choice(target_locations)
                new_location_name = self.get_location_name(new_location_id)

                self.update_cab_location_in_memory(cab.id, source_loc.id, new_location_id)
                cab.set_location(new_location_id)
                driver = self.get_driver_by_id(cab.driver_id)
                if driver:
                    driver.current_location_id = new_location_id
                print(f"  Cab {cab.id} (Driver: {driver.name if driver else 'N/A'}) redirected from {source_loc.name} to {new_location_name}.")
                redirected_count += 1
        print(f"Total {redirected_count} cabs redirected.")
        return True

    def update_cab_location_in_memory(self, cab_id, old_location_id, new_location_id):
        if old_location_id in self.cab_locations and cab_id in self.cab_locations[old_location_id]:
            self.cab_locations[old_location_id].remove(cab_id)
            if not self.cab_locations[old_location_id]:
                del self.cab_locations[old_location_id] # Clean up empty list

        if new_location_id not in self.cab_locations:
            self.cab_locations[new_location_id] = []
        if cab_id not in self.cab_locations[new_location_id]: # Avoid duplicates
            self.cab_locations[new_location_id].append(cab_id)

    # Task 8: Allocate fairly to all drivers (integrated into get_closest_available_driver_info sorting)
    # The sorting prioritizes closer cabs, then those with fewer total trips.

    # Task 9: Admin CURD Cabs
    def admin_add_cab(self, admin_id, driver_id, initial_location_name):
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        driver = self.get_driver_by_id(driver_id)
        if not driver:
            print(f"Error: Driver with ID {driver_id} not found.")
            return False

        # Check if driver already has a cab
        for cab in self.cabs.values():
            if cab.driver_id == driver_id:
                print(f"Error: Driver {driver.name} already has a cab (ID: {cab.id}).")
                return False

        location_obj = self._get_location_by_name(initial_location_name)
        if not location_obj:
            print(f"Error: Location '{initial_location_name}' not found.")
            return False

        cab_id = self._generate_id("cab")
        cab = Cab(cab_id, location_obj.id, driver_id)
        self.cabs[cab_id] = cab

        if location_obj.id not in self.cab_locations:
            self.cab_locations[location_obj.id] = []
        self.cab_locations[location_obj.id].append(cab_id)

        driver.current_location_id = location_obj.id # Update driver's location
        print(f"Admin added Cab {cab_id} for driver {driver.name} at {location_obj.name}.")
        return True

    def admin_remove_cab(self, admin_id, cab_id):
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        cab = self.get_cab_by_id(cab_id)
        if not cab:
            print(f"Error: Cab with ID {cab_id} not found.")
            return False

        # Remove from cab_locations
        if cab.current_location_id in self.cab_locations and cab_id in self.cab_locations[cab.current_location_id]:
            self.cab_locations[cab.current_location_id].remove(cab_id)
            if not self.cab_locations[cab.current_location_id]:
                del self.cab_locations[cab.current_location_id]

        # Remove from cabs dictionary
        del self.cabs[cab_id]

        # Optionally, disassociate from driver (e.g., driver is now cab-less)
        driver = self.get_driver_by_id(cab.driver_id)
        if driver:
            print(f"Driver {driver.name} is now without a cab.")

        print(f"Admin removed Cab {cab_id}.")
        return True

    def admin_update_cab_location(self, admin_id, cab_id, new_location_name):
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        cab = self.get_cab_by_id(cab_id)
        if not cab:
            print(f"Error: Cab with ID {cab_id} not found.")
            return False

        new_location_obj = self._get_location_by_name(new_location_name)
        if not new_location_obj:
            print(f"Error: New location '{new_location_name}' not found.")
            return False

        old_location_id = cab.current_location_id
        self.update_cab_location_in_memory(cab_id, old_location_id, new_location_obj.id)
        cab.set_location(new_location_obj.id)

        driver = self.get_driver_by_id(cab.driver_id)
        if driver:
            driver.current_location_id = new_location_obj.id

        print(f"Admin updated Cab {cab_id} location from {self.get_location_name(old_location_id)} to {new_location_name}.")
        return True

    # Task 10: Admin CURD Locations
    def add_location(self, admin_id=None, name=None, distance_from_origin=None):
        if admin_id: # Only require admin for manual add, not for initial data load
            admin = self.get_admin_by_id(admin_id)
            if not admin:
                print("Error: Admin not found.")
                return False

        if not name or distance_from_origin is None:
            print("Error: Name and distance are required for adding a location.")
            return False

        # Check for existing location with same name
        if self._get_location_by_name(name):
            print(f"Error: Location with name '{name}' already exists.")
            return False

        location_id = self._generate_id("location")
        location = Location(location_id, name, distance_from_origin)
        self.locations[location_id] = location
        self.cab_locations[location_id] = [] # Initialize empty list for cabs at this location
        print(f"Location '{name}' (ID: {location_id}) added.")
        return True

    def admin_remove_location(self, admin_id, location_name):
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        location_obj = self._get_location_by_name(location_name)
        if not location_obj:
            print(f"Error: Location '{location_name}' not found.")
            return False

        # Check if any cabs are at this location
        if self.cab_locations.get(location_obj.id):
            print(f"Error: Cannot remove location '{location_name}'. Cabs are currently assigned to it.")
            return False

        del self.locations[location_obj.id]
        if location_obj.id in self.cab_locations:
            del self.cab_locations[location_obj.id] # Remove its entry
        print(f"Admin removed Location '{location_name}' (ID: {location_obj.id}).")
        return True

    def admin_update_location(self, admin_id, old_location_name, new_name=None, new_distance=None):
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        location_obj = self._get_location_by_name(old_location_name)
        if not location_obj:
            print(f"Error: Location '{old_location_name}' not found.")
            return False

        updated = False
        if new_name and new_name != location_obj.name:
            # Check for name conflict
            if self._get_location_by_name(new_name):
                print(f"Error: Location with new name '{new_name}' already exists.")
                return False
            location_obj.name = new_name
            updated = True
        if new_distance is not None and new_distance != location_obj.distance_from_origin:
            location_obj.distance_from_origin = new_distance
            updated = True

        if updated:
            print(f"Admin updated Location '{old_location_name}' (ID: {location_obj.id}).")
        else:
            print(f"No updates for Location '{old_location_name}'.")
        return updated

    # Task 11: View summary of all cabs (Admin)
    def view_all_cabs_summary(self, admin_id):
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return

        print("\n--- Zula Cab Summary (Admin View) ---")
        if not self.cabs:
            print("No cabs registered in the system.")
            return

        for cab_id, cab in self.cabs.items():
            driver = self.get_driver_by_id(cab.driver_id)
            if not driver:
                print(f"Cab ID: {cab_id} has no associated driver. Skipping details.")
                continue

            print(f"\nCab ID: {cab.id}")
            print(f"  Driver: {driver.name} (ID: {driver.id})")
            print(f"  Current Location: {self.get_location_name(cab.current_location_id)}")
            print(f"  Availability: {'Available' if cab.is_available and not driver.is_on_rest else 'Busy/On Rest'}")
            print(f"  Total Trips: {driver.total_trips}")
            print(f"  Total Fare Earned (by driver): ${driver.total_fare_earned:.2f}")
            print(f"  Total Driver Commission (from Zula): ${driver.total_commission_earned:.2f}")

            print("  Trip Details:")
            if not driver.trip_history:
                print("    No trips recorded for this cab/driver.")
            else:
                print("    ------------------------------------------------------------------------------------")
                print(f"    {'Source':<10} {'Destination':<12} {'Fare':<8} {'Start Time':<20} {'End Time':<20}")
                print("    ------------------------------------------------------------------------------------")
                for ride in driver.trip_history:
                    print(f"    {ride.source.name:<10} {ride.destination.name:<12} {ride.fare:<8.2f} {ride.start_time.strftime('%H:%M:%S'):<20} {ride.end_time.strftime('%H:%M:%S'):<20}")
                print("    ------------------------------------------------------------------------------------")

    # Task 12: Driver sees only his/her details
    def view_driver_summary(self, driver_id):
        driver = self.get_driver_by_id(driver_id)
        if not driver:
            print("Error: Driver not found.")
            return

        print(f"\n--- Driver Summary for {driver.name} (ID: {driver.id}) ---")
        summary = driver.view_my_summary()
        print(f"  Current Location: {self.get_location_name(driver.current_location_id)}")
        print(f"  Status: {'On Rest' if driver.is_on_rest else 'Available'}")
        print(f"  Total Trips: {summary['Total Trips']}")
        print(f"  Total Fare Earned: ${summary['Total Fare Earned']:.2f}")
        print(f"  Total Commission from Zula: ${summary['Total Commission Earned (from Zula)']:.2f}")

        print("\n  Trip Details:")
        if not summary["Trip Details"]:
            print("    No trips recorded.")
        else:
            print("    ------------------------------------------------------------------------------------")
            print(f"    {'Source':<10} {'Destination':<12} {'Fare':<8} {'Start Time':<20} {'End Time':<20}")
            print("    ------------------------------------------------------------------------------------")
            for trip in summary["Trip Details"]:
                print(f"    {trip['Source']:<10} {trip['Destination']:<12} {trip['Fare']:<8.2f} {trip['Start Time']:<20} {trip['End Time']:<20}")
            print("    ------------------------------------------------------------------------------------")

    # Task 13: Admin CURD all tables
    # Admin CURD for Cab Driver Table (User management - drivers)
    def admin_add_driver(self, admin_id, name, password, age, gender, initial_location_name):
        return self.signup("driver", name, password, age, gender, initial_location_name)

    def admin_remove_driver(self, admin_id, driver_id):
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False
        
        driver = self.get_driver_by_id(driver_id)
        if not driver:
            print(f"Error: Driver with ID {driver_id} not found.")
            return False

        # Remove associated cab if any
        cab_to_remove = None
        for cab_id, cab in self.cabs.items():
            if cab.driver_id == driver_id:
                cab_to_remove = cab_id
                break
        if cab_to_remove:
            self.admin_remove_cab(admin_id, cab_to_remove)

        # Remove from users_by_credentials
        for (n, p), u_id in list(self.users_by_credentials.items()):
            if u_id == driver_id:
                del self.users_by_credentials[(n, p)]
                break

        del self.cab_drivers[driver_id]
        print(f"Admin removed Driver {driver.name} (ID: {driver_id}).")
        return True

    def admin_update_driver(self, admin_id, driver_id, name=None, password=None, age=None, gender=None, current_location_name=None):
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        driver = self.get_driver_by_id(driver_id)
        if not driver:
            print(f"Error: Driver with ID {driver_id} not found.")
            return False

        updated = False
        old_name_password = (driver.name, driver.password)

        if name and name != driver.name:
            driver.name = name
            updated = True
        if password and password != driver.password:
            driver.password = password
            updated = True
        if age is not None and age != driver.age:
            driver.age = age
            updated = True
        if gender and gender != driver.gender:
            driver.gender = gender
            updated = True
        if current_location_name:
            new_loc_obj = self._get_location_by_name(current_location_name)
            if new_loc_obj:
                driver.current_location_id = new_loc_obj.id
                # Also update associated cab's location if it exists
                for cab_id, cab in self.cabs.items():
                    if cab.driver_id == driver_id:
                        self.update_cab_location_in_memory(cab_id, cab.current_location_id, new_loc_obj.id)
                        cab.set_location(new_loc_obj.id)
                        break
                updated = True
            else:
                print(f"Warning: New location '{current_location_name}' not found for driver update.")

        if updated:
            # Update users_by_credentials if name or password changed
            if old_name_password != (driver.name, driver.password):
                if old_name_password in self.users_by_credentials:
                    del self.users_by_credentials[old_name_password]
                self.users_by_credentials[(driver.name, driver.password)] = driver_id
            print(f"Admin updated Driver {driver.name} (ID: {driver_id}).")
        else:
            print(f"No updates for Driver {driver.name} (ID: {driver_id}).")
        return updated

    # Admin CURD for Customer Table (User management - customers)
    def admin_add_customer(self, admin_id, name, password, age, gender):
        return self.signup("customer", name, password, age, gender)

    def admin_remove_customer(self, admin_id, customer_id):
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        customer = self.get_customer_by_id(customer_id)
        if not customer:
            print(f"Error: Customer with ID {customer_id} not found.")
            return False
        
        # Remove from users_by_credentials
        for (n, p), u_id in list(self.users_by_credentials.items()):
            if u_id == customer_id:
                del self.users_by_credentials[(n, p)]
                break

        del self.customers[customer_id]
        print(f"Admin removed Customer {customer.name} (ID: {customer_id}).")
        return True

    def admin_update_customer(self, admin_id, customer_id, name=None, password=None, age=None, gender=None):
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        customer = self.get_customer_by_id(customer_id)
        if not customer:
            print(f"Error: Customer with ID {customer_id} not found.")
            return False

        updated = False
        old_name_password = (customer.name, customer.password)

        if name and name != customer.name:
            customer.name = name
            updated = True
        if password and password != customer.password:
            customer.password = password
            updated = True
        if age is not None and age != customer.age:
            customer.age = age
            updated = True
        if gender and gender != customer.gender:
            customer.gender = gender
            updated = True

        if updated:
            # Update users_by_credentials if name or password changed
            if old_name_password != (customer.name, customer.password):
                if old_name_password in self.users_by_credentials:
                    del self.users_by_credentials[old_name_password]
                self.users_by_credentials[(customer.name, customer.password)] = customer_id
            print(f"Admin updated Customer {customer.name} (ID: {customer_id}).")
        else:
            print(f"No updates for Customer {customer.name} (ID: {customer_id}).")
        return updated

    # Admin CURD for Admin Table (User management - admins)
    def admin_add_admin(self, admin_id, name, password, age, gender):
        return self.signup("admin", name, password, age, gender)

    def admin_remove_admin(self, admin_id, target_admin_id):
        acting_admin = self.get_admin_by_id(admin_id)
        if not acting_admin:
            print("Error: Admin not found.")
            return False

        if admin_id == target_admin_id:
            print("Error: An admin cannot remove themselves.")
            return False

        target_admin = self.get_admin_by_id(target_admin_id)
        if not target_admin:
            print(f"Error: Admin with ID {target_admin_id} not found.")
            return False
        
        # Remove from users_by_credentials
        for (n, p), u_id in list(self.users_by_credentials.items()):
            if u_id == target_admin_id:
                del self.users_by_credentials[(n, p)]
                break

        del self.admins[target_admin_id]
        print(f"Admin removed Admin {target_admin.name} (ID: {target_admin_id}).")
        return True

    def admin_update_admin(self, admin_id, target_admin_id, name=None, password=None, age=None, gender=None):
        acting_admin = self.get_admin_by_id(admin_id)
        if not acting_admin:
            print("Error: Admin not found.")
            return False

        target_admin = self.get_admin_by_id(target_admin_id)
        if not target_admin:
            print(f"Error: Admin with ID {target_admin_id} not found.")
            return False

        updated = False
        old_name_password = (target_admin.name, target_admin.password)

        if name and name != target_admin.name:
            target_admin.name = name
            updated = True
        if password and password != target_admin.password:
            target_admin.password = password
            updated = True
        if age is not None and age != target_admin.age:
            target_admin.age = age
            updated = True
        if gender and gender != target_admin.gender:
            target_admin.gender = gender
            updated = True

        if updated:
            # Update users_by_credentials if name or password changed
            if old_name_password != (target_admin.name, target_admin.password):
                if old_name_password in self.users_by_credentials:
                    del self.users_by_credentials[old_name_password]
                self.users_by_credentials[(target_admin.name, target_admin.password)] = target_admin_id
            print(f"Admin updated Admin {target_admin.name} (ID: {target_admin_id}).")
        else:
            print(f"No updates for Admin {target_admin.name} (ID: {target_admin_id}).")
        return updated

def main():
    zula = ZulaSystem()

    # Simulate login for different users
    current_user = None

    while True:
        print("\n--- Zula Cab System ---")
        if current_user:
            print(f"Logged in as: {current_user.__class__.__name__} ({current_user.name})")
        else:
            print("Not logged in.")

        print("\nOptions:")
        if not current_user:
            print("1. Login")
            print("2. Sign Up (Customer)")
            print("3. Sign Up (Driver)")
            print("4. Sign Up (Admin)")
        else:
            if isinstance(current_user, Customer):
                print("5. Hail a Cab")
                print("6. View My Ride History")
            elif isinstance(current_user, Driver):
                print("7. View My Summary")
                # Simulate ending rest period for a driver
                if current_user.is_on_rest:
                    print("8. End Rest Period")
            elif isinstance(current_user, Admin):
                print("9. Redirect Cabs")
                print("10. View All Cabs Summary")
                print("11. View Zula's Commission Summary")
                print("12. Admin: CURD Cabs (Add/Remove/Update Location)")
                print("13. Admin: CURD Locations (Add/Remove/Update)")
                print("14. Admin: CURD Users (Add/Remove/Update)")

            print("0. Logout" if current_user else "0. Exit")

        choice = input("Enter your choice: ")

        if choice == '1': # Login
            user_type = input("Enter user type (customer/driver/admin): ").lower()
            name = input("Enter username: ")
            password = input("Enter password: ")
            current_user = zula.login(user_type, name, password)
        elif choice == '2': # Sign Up Customer
            name = input("Enter username: ")
            password = input("Enter password: ")
            age = int(input("Enter age: "))
            gender = input("Enter gender (M/F): ")
            current_user = zula.signup("customer", name, password, age, gender)
        elif choice == '3': # Sign Up Driver
            name = input("Enter username: ")
            password = input("Enter password: ")
            age = int(input("Enter age: "))
            gender = input("Enter gender (M/F): ")
            initial_location_name = input("Enter initial location name (e.g., A, B, C): ")
            current_user = zula.signup("driver", name, password, age, gender, initial_location_name)
        elif choice == '4': # Sign Up Admin
            name = input("Enter username: ")
            password = input("Enter password: ")
            age = int(input("Enter age: "))
            gender = input("Enter gender (M/F): ")
            current_user = zula.signup("admin", name, password, age, gender)
        elif choice == '0': # Logout / Exit
            if current_user:
                print(f"Logging out {current_user.name}.")
                current_user = None
            else:
                print("Exiting Zula System.")
                break
        elif current_user: # Actions only if logged in
            if isinstance(current_user, Customer):
                if choice == '5': # Hail a Cab
                    source = input("Enter source location name: ")
                    destination = input("Enter destination location name: ")
                    zula.hail_cab(current_user.id, source, destination)
                elif choice == '6': # View My Ride History
                    zula.view_customer_history(current_user.id)
                else:
                    print("Invalid choice for Customer.")
            elif isinstance(current_user, Driver):
                if choice == '7': # View My Summary
                    zula.view_driver_summary(current_user.id)
                elif choice == '8': # End Rest Period
                    if current_user.is_on_rest:
                        current_user.is_on_rest = False
                        if current_user.id in zula.unavailable_drivers:
                            zula.unavailable_drivers.remove(current_user.id)
                        print(f"Driver {current_user.name} is now available.")
                    else:
                        print("You are not currently on rest.")
                else:
                    print("Invalid choice for Driver.")
            elif isinstance(current_user, Admin):
                if choice == '9': # Redirect Cabs
                    location_name = input("Enter location name to check for redirection: ")
                    zula.redirect_cabs(current_user.id, location_name)
                elif choice == '10': # View All Cabs Summary
                    zula.view_all_cabs_summary(current_user.id)
                elif choice == '11': # View Zula's Commission Summary
                    zula.view_zula_commission_summary()
                elif choice == '12': # Admin CURD Cabs
                    print("\n--- Admin: CURD Cabs ---")
                    print("a. Add Cab (assign to existing driver)")
                    print("b. Remove Cab")
                    print("c. Update Cab Location")
                    cab_crud_choice = input("Enter choice (a/b/c): ").lower()
                    if cab_crud_choice == 'a':
                        driver_id = int(input("Enter driver ID to assign cab to: "))
                        initial_loc = input("Enter initial location name for the cab: ")
                        zula.admin_add_cab(current_user.id, driver_id, initial_loc)
                    elif cab_crud_choice == 'b':
                        cab_id = int(input("Enter Cab ID to remove: "))
                        zula.admin_remove_cab(current_user.id, cab_id)
                    elif cab_crud_choice == 'c':
                        cab_id = int(input("Enter Cab ID to update: "))
                        new_loc = input("Enter new location name: ")
                        zula.admin_update_cab_location(current_user.id, cab_id, new_loc)
                    else:
                        print("Invalid choice.")
                elif choice == '13': # Admin CURD Locations
                    print("\n--- Admin: CURD Locations ---")
                    print("a. Add Location")
                    print("b. Remove Location")
                    print("c. Update Location")
                    loc_crud_choice = input("Enter choice (a/b/c): ").lower()
                    if loc_crud_choice == 'a':
                        name = input("Enter location name: ")
                        distance = int(input("Enter distance from origin: "))
                        zula.add_location(current_user.id, name, distance)
                    elif loc_crud_choice == 'b':
                        name = input("Enter location name to remove: ")
                        zula.admin_remove_location(current_user.id, name)
                    elif loc_crud_choice == 'c':
                        old_name = input("Enter current location name to update: ")
                        new_name = input("Enter new name (leave blank to keep current): ")
                        new_distance_str = input("Enter new distance from origin (leave blank to keep current): ")
                        new_distance = int(new_distance_str) if new_distance_str else None
                        zula.admin_update_location(current_user.id, old_name, new_name, new_distance)
                    else:
                        print("Invalid choice.")
                elif choice == '14': # Admin CURD Users
                    print("\n--- Admin: CURD Users ---")
                    print("a. Add User")
                    print("b. Remove User")
                    print("c. Update User")
                    user_crud_choice = input("Enter choice (a/b/c): ").lower()
                    if user_crud_choice == 'a':
                        user_type = input("Enter user type (customer/driver/admin): ").lower()
                        name = input("Enter name: ")
                        password = input("Enter password: ")
                        age = int(input("Enter age: "))
                        gender = input("Enter gender (M/F): ")
                        initial_loc = None
                        if user_type == 'driver':
                            initial_loc = input("Enter initial location name for driver: ")
                        if user_type == 'driver':
                            zula.admin_add_driver(current_user.id, name, password, age, gender, initial_loc)
                        elif user_type == 'customer':
                            zula.admin_add_customer(current_user.id, name, password, age, gender)
                        elif user_type == 'admin':
                            zula.admin_add_admin(current_user.id, name, password, age, gender)
                        else:
                            print("Invalid user type.")
                    elif user_crud_choice == 'b':
                        user_type = input("Enter user type to remove (customer/driver/admin): ").lower()
                        user_id = int(input("Enter User ID to remove: "))
                        if user_type == 'customer':
                            zula.admin_remove_customer(current_user.id, user_id)
                        elif user_type == 'driver':
                            zula.admin_remove_driver(current_user.id, user_id)
                        elif user_type == 'admin':
                            zula.admin_remove_admin(current_user.id, user_id)
                        else:
                            print("Invalid user type.")
                    elif user_crud_choice == 'c':
                        user_type = input("Enter user type to update (customer/driver/admin): ").lower()
                        user_id = int(input("Enter User ID to update: "))
                        name = input("Enter new name (leave blank to keep current): ")
                        password = input("Enter new password (leave blank to keep current): ")
                        age_str = input("Enter new age (leave blank to keep current): ")
                        age = int(age_str) if age_str else None
                        gender = input("Enter new gender (M/F, leave blank to keep current): ")
                        
                        kwargs = {}
                        if name: kwargs['name'] = name
                        if password: kwargs['password'] = password
                        if age is not None: kwargs['age'] = age
                        if gender: kwargs['gender'] = gender

                        if user_type == 'customer':
                            zula.admin_update_customer(current_user.id, user_id, **kwargs)
                        elif user_type == 'driver':
                            current_location_name = input("Enter new current location name for driver (leave blank to keep current): ")
                            if current_location_name: kwargs['current_location_name'] = current_location_name
                            zula.admin_update_driver(current_user.id, user_id, **kwargs)
                        elif user_type == 'admin':
                            zula.admin_update_admin(current_user.id, user_id, **kwargs)
                        else:
                            print("Invalid user type.")
                    else:
                        print("Invalid choice.")
            else:
                print("Invalid choice.")
        else:
            print("Invalid choice. Please login or sign up.")

if __name__ == "__main__":
    main()