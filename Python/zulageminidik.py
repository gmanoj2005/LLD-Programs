import datetime
import random
import heapq
import time

# --- 1. Core Classes ---

class User:
    """Base class for all users in the system."""
    def __init__(self, id, name, password, age, gender):
        self.id = id
        self.name = name
        self.password = password
        self.age = age
        self.gender = gender

    def login(self, name, password):
        """Authenticates user credentials."""
        return self.name == name and self.password == password

    def __repr__(self):
        return f"User(ID: {self.id}, Name: {self.name}, Type: {self.__class__.__name__})"

class Customer(User):
    """Represents a customer in the Zula system."""
    def __init__(self, id, name, password, age, gender):
        super().__init__(id, name, password, age, gender)
        self.trip_history = []  # List of Ride objects

    def view_history(self):
        """Returns the customer's ride history."""
        return self.trip_history

class Driver(User):
    """Represents a cab driver in the Zula system."""
    def __init__(self, id, name, password, age, gender, current_location_id):
        super().__init__(id, name, password, age, gender)
        self.current_location_id = current_location_id  # Stores current location ID
        self.is_on_rest = False  # True if driver is on a mandatory rest period
        self.total_trips = 0
        self.total_fare_earned = 0.0
        self.total_commission_earned = 0.0 # Commission for driver from Zula (70% of fare)
        self.trip_history = []  # List of Ride objects

    def complete_ride(self, ride):
        """Updates driver stats and sets rest status after a ride."""
        self.total_trips += 1
        self.total_fare_earned += ride.fare
        self.total_commission_earned += (ride.fare - ride.zula_commission)
        self.trip_history.append(ride)
        self.is_on_rest = True  # Driver goes on rest after a trip

    def view_my_summary(self):
        """Returns a summary of the driver's performance."""
        # Using driver ID as Cab ID for simplicity as 1 driver per cab
        return {
            "Cab ID": self.id,
            "Total Trips": self.total_trips,
            "Total Fare Earned": self.total_fare_earned,
            "Total Commission Earned (from Zula)": self.total_commission_earned,
            "Trip Details": [{
                "Source": ride.source_id, # Storing ID for ZulaSystem to resolve name
                "Destination": ride.destination_id, # Storing ID for ZulaSystem to resolve name
                "Fare": ride.fare,
                "Path": ride.path, # Storing path (list of IDs)
                "Start Time": ride.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "End Time": ride.end_time.strftime("%Y-%m-%d %H:%M:%S")
            } for ride in self.trip_history]
        }

class Admin(User):
    """Represents an admin user with management privileges."""
    def __init__(self, id, name, password, age, gender):
        super().__init__(id, name, password, age, gender)

class Location:
    """Represents a geographical location in the system."""
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"Location(ID: {self.id}, Name: {self.name})"

class Cab:
    """Represents a cab (vehicle) in the Zula system."""
    def __init__(self, id, current_location_id, driver_id):
        self.id = id
        self.current_location_id = current_location_id
        self.driver_id = driver_id  # Link to the driver
        self.is_available = True  # True if not currently on a trip

    def set_location(self, new_location_id):
        """Updates the cab's current location."""
        self.current_location_id = new_location_id

    def set_availability(self, status):
        """Sets the cab's availability status."""
        self.is_available = status

    def __repr__(self):
        return (f"Cab(ID: {self.id}, Location ID: {self.current_location_id}, "
                f"Driver ID: {self.driver_id}, Available: {self.is_available})")

class Ride:
    """Represents a completed ride transaction."""
    def __init__(self, id, customer_id, driver_id, cab_id, source_id, destination_id, fare, zula_commission, path, start_time, end_time):
        self.id = id
        self.customer_id = customer_id
        self.driver_id = driver_id
        self.cab_id = cab_id
        self.source_id = source_id
        self.destination_id = destination_id
        self.fare = fare
        self.zula_commission = zula_commission
        self.path = path # List of location IDs representing the optimal path taken
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        return (f"Ride(ID: {self.id}, From: {self.source_id} to {self.destination_id}, "
                f"Cab ID: {self.cab_id}, Fare: {self.fare:.2f}, Path: {self.path})")

class Graph:
    """
    Implements a weighted graph using an adjacency list to represent locations and road connections.
    Uses Dijkstra's algorithm for shortest path finding.
    """
    def __init__(self):
        self.adj_list = {} # {location_id: [(neighbor_id, weight), ...]}

    def add_node(self, node_id):
        """Adds a node (location) to the graph if it doesn't exist."""
        if node_id not in self.adj_list:
            self.adj_list[node_id] = []

    def add_edge(self, loc1_id, loc2_id, weight):
        """
        Adds a bidirectional edge between two locations with a given weight.
        Assumes an undirected graph for roads.
        """
        self.add_node(loc1_id)
        self.add_node(loc2_id)
        self.adj_list[loc1_id].append((loc2_id, weight))
        self.adj_list[loc2_id].append((loc1_id, weight))

    def get_shortest_path(self, start_id, end_id):
        """
        Finds the shortest path and distance between two locations using Dijkstra's algorithm.
        Returns a tuple: (shortest_distance, list_of_location_ids_in_path).
        Returns (float('inf'), []) if no path exists.
        """
        if start_id not in self.adj_list or end_id not in self.adj_list:
            return float('inf'), []

        distances = {node: float('inf') for node in self.adj_list}
        distances[start_id] = 0
        previous_nodes = {node: None for node in self.adj_list}
        priority_queue = [(0, start_id)] # (distance, node) - min-heap

        while priority_queue:
            current_distance, current_node = heapq.heappop(priority_queue)

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self.adj_list[current_node]:
                distance = current_distance + weight
                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(priority_queue, (distance, neighbor))

        # Reconstruct path
        path = []
        current = end_id
        while current is not None:
            path.insert(0, current)
            current = previous_nodes[current]

        # If the start_id is not the first element, it means no path was found to end_id
        if not path or path[0] != start_id:
            return float('inf'), []

        return distances[end_id], path

# --- 2. ZulaSystem - The Core Application Logic ---

class ZulaSystem:
    """
    Manages all data and operations for the Zula Cab Booking System.
    Acts as the central orchestrator, holding all in-memory data.
    """
    def __init__(self):
        self.next_user_id = 1
        self.next_location_id = 1
        self.next_cab_id = 1
        self.next_ride_id = 1

        # In-memory data storage (dictionaries for O(1) average lookup)
        self.cab_drivers = {}  # {driver_id: Driver object}
        self.customers = {}  # {customer_id: Customer object}
        self.admins = {}  # {admin_id: Admin object}
        self.users_by_credentials = {}  # {(name, password): user_id} maps to any user type

        self.locations = {}  # {location_id: Location object}
        self.location_names_to_ids = {} # {location_name: location_id} for quick lookup by name
        self.cabs = {}  # {cab_id: Cab object}
        # {location_id: [cab_id1, cab_id2, ...]} - for quick lookup of cabs at a location
        self.cab_locations = {}
        self.unavailable_drivers = set() # {driver_id} - for drivers currently on rest
        self.rides_history = {}  # {ride_id: Ride object} - all completed rides

        self.location_graph = Graph() # Graph for shortest path calculations

        self.initialize_data() # Populate with initial dummy data

    def _generate_id(self, prefix):
        """Generates a unique ID based on the prefix."""
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

    # --- Task 1: Initialize Tables ---
    def initialize_data(self):
        """Initializes the system with predefined locations, drivers, customers, and admins."""
        # Locations (A --- B --- C --- M ----- P ----- G) and their connections
        # Distances are now between directly connected nodes
        self.add_location_to_system(name="A")
        self.add_location_to_system(name="B")
        self.add_location_to_system(name="C")
        self.add_location_to_system(name="M")
        self.add_location_to_system(name="P")
        self.add_location_to_system(name="G")
        self.add_location_to_system(name="X") # Add an isolated location for testing

        # Define connections (edges in the graph) and their weights (distances)
        self.add_road_connection("A", "B", 2)
        self.add_road_connection("B", "C", 3)
        self.add_road_connection("C", "M", 5)
        self.add_road_connection("M", "P", 5)
        self.add_road_connection("P", "G", 7)
        self.add_road_connection("A", "M", 10) # Direct route, potentially shorter than A->B->C->M
        self.add_road_connection("C", "G", 12) # Direct route
        self.add_road_connection("B", "P", 8) # Another cross-connection

        # Drivers
        self.signup("driver", "ram", "hsigh", 32, "M", initial_location_name="A")
        self.signup("driver", "raja", "dfksf", 22, "F", initial_location_name="P")
        self.signup("driver", "sita", "abcd", 28, "F", initial_location_name="C")
        self.signup("driver", "mohan", "1234", 40, "M", initial_location_name="A")

        # Customers
        self.signup("customer", "cust1", "pass1", 25, "M")
        self.signup("customer", "cust2", "pass2", 30, "F")

        # Admin
        self.signup("admin", "adminpass", "admin", 35, "M")

    # Helper methods to get objects or their properties
    def _get_location_id_by_name(self, name):
        """Retrieves a location ID by its name."""
        return self.location_names_to_ids.get(name)

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

    # --- Task 2: Login / Sign Up ---
    def signup(self, user_type, name, password, age, gender, initial_location_name=None):
        """Registers a new user (customer, driver, or admin)."""
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
            location_id = self._get_location_id_by_name(initial_location_name)
            if location_id is None:
                print(f"Error: Location '{initial_location_name}' not found.")
                return None

            user = Driver(user_id, name, password, age, gender, location_id)
            self.cab_drivers[user_id] = user

            # Create a cab for the driver
            cab_id = self._generate_id("cab")
            cab = Cab(cab_id, location_id, user_id)
            self.cabs[cab_id] = cab
            if location_id not in self.cab_locations:
                self.cab_locations[location_id] = []
            self.cab_locations[location_id].append(cab_id)
            print(f"Cab {cab_id} assigned to driver {user.name} at {self.get_location_name(location_id)}.")
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
        """Authenticates a user for login."""
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

    # --- Task 4: Hail a Cab & Fare Calculation (Updated for optimal path) ---
    def calculate_fare(self, source_id, destination_id):
        """Calculates fare based on the shortest path distance."""
        distance, _ = self.location_graph.get_shortest_path(source_id, destination_id)
        if distance == float('inf'):
            return None # No path found
        fare = distance * 10 # Fare is distance multiplied by 10 for each unit
        return fare

    def get_optimal_path(self, source_id, destination_id):
        """Returns the optimal path (list of location IDs) and its distance."""
        return self.location_graph.get_shortest_path(source_id, destination_id)

    def get_closest_available_driver_info(self, source_location_id):
        """
        Finds available drivers closest to the source, prioritizing those
        not on rest and then by fair allocation (fewer trips).
        """
        available_cabs_info = []
        for cab_id, cab in self.cabs.items():
            if not cab.is_available: # Cab is currently on a trip
                continue

            driver = self.get_driver_by_id(cab.driver_id)
            if not driver or driver.is_on_rest: # Task 3: Driver is on rest
                continue

            # Calculate path from cab's current location to customer's pickup location
            dist_to_pickup, path_to_pickup = self.get_optimal_path(cab.current_location_id, source_location_id)

            if dist_to_pickup != float('inf'): # Only consider if a path exists
                available_cabs_info.append({
                    "cab_id": cab.id,
                    "driver_id": driver.id,
                    "current_location_id": cab.current_location_id,
                    "distance_to_pickup": dist_to_pickup,
                    "path_to_pickup": path_to_pickup
                })

        # Task 8: Allocate fairly - sort by distance to pickup, then by driver's total trips
        available_cabs_info.sort(key=lambda x: (x["distance_to_pickup"], self.cab_drivers[x["driver_id"]].total_trips))

        return available_cabs_info

    def hail_cab(self, customer_id, source_location_name, destination_location_name):
        """
        Allows a customer to hail a cab, recommends options, and processes the ride.
        """
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            print("Error: Customer not found.")
            return None

        source_loc_id = self._get_location_id_by_name(source_location_name)
        dest_loc_id = self._get_location_id_by_name(destination_location_name)
        if source_loc_id is None:
            print(f"Error: Source location '{source_location_name}' not found.")
            return None
        if dest_loc_id is None:
            print(f"Error: Destination location '{destination_location_name}' not found.")
            return None

        fare_for_ride = self.calculate_fare(source_loc_id, dest_loc_id)
        if fare_for_ride is None:
            print("Error: No path found between source and destination. Cannot hail cab.")
            return None

        ride_path, ride_distance = self.get_optimal_path(source_loc_id, dest_loc_id)
        if ride_distance == float('inf'):
            print("Error: No optimal path found for the ride. Cannot hail cab.")
            return None

        recommended_cabs_info = []
        closest_drivers_info = self.get_closest_available_driver_info(source_loc_id)

        print("\nRecommended Cabs:")
        print("-------------------------------------------------------------------------------------------------")
        print(f"{'Cab Location':<15} {'Cab ID':<10} {'Driver':<15} {'Dist to Pickup':<18} {'Ride Fare':<12} {'Optimal Path':<30}")
        print("-------------------------------------------------------------------------------------------------")
        for cab_info in closest_drivers_info:
            cab_id = cab_info["cab_id"]
            driver_id = cab_info["driver_id"]
            current_location_id = cab_info["current_location_id"]
            distance_to_pickup = cab_info["distance_to_pickup"]
            # path_to_pickup = cab_info["path_to_pickup"] # Can display if needed

            driver = self.get_driver_by_id(driver_id)
            # This check is redundant due to `get_closest_available_driver_info` filtering, but harmless.
            if driver and not driver.is_on_rest:
                recommended_cabs_info.append({
                    "cab_id": cab_id,
                    "driver_id": driver_id,
                    "current_location_id": current_location_id,
                    "location_name": self.get_location_name(current_location_id),
                    "driver_name": driver.name,
                    "distance_to_pickup": distance_to_pickup,
                    "fare": fare_for_ride,
                    "ride_path": ride_path # This is the path for the actual ride
                })
                path_names = "->".join([self.get_location_name(loc_id) for loc_id in ride_path])
                print(f"{self.get_location_name(current_location_id):<15} {cab_id:<10} {driver.name:<15} {distance_to_pickup:<18.2f} ${fare_for_ride:<11.2f} {path_names:<30}")

        if not recommended_cabs_info:
            print("No cabs available at the moment or no path found for the requested ride.")
            return None

        # For simplicity, automatically select the first recommended cab.
        # In a real system, the customer would choose and "accept".
        chosen_cab_info = recommended_cabs_info[0]
        print(f"\nCustomer confirms booking with Cab ID {chosen_cab_info['cab_id']} "
              f"driven by {chosen_cab_info['driver_name']}.")

        # Process the ride
        ride = self.process_ride(
            customer_id,
            chosen_cab_info["driver_id"],
            chosen_cab_info["cab_id"],
            source_loc_id,
            dest_loc_id,
            chosen_cab_info["fare"],
            chosen_cab_info["ride_path"]
        )
        return ride

    def process_ride(self, customer_id, driver_id, cab_id, source_id, destination_id, fare, path):
        """
        Completes a ride transaction, updates system state, and records history.
        """
        customer = self.get_customer_by_id(customer_id)
        driver = self.get_driver_by_id(driver_id)
        cab = self.get_cab_by_id(cab_id)

        if not all([customer, driver, cab]):
            print("Error: Invalid data for processing ride.")
            return None

        zula_commission = fare * 0.30  # Task 6: Zula's 30% commission

        start_time = datetime.datetime.now()
        # Simulate travel time based on distance. A small delay per unit of distance.
        distance, _ = self.get_optimal_path(source_id, destination_id)
        if distance == float('inf'): # Fallback, should not happen if hail_cab works
            distance = 1
        time.sleep(distance * 0.05) # Adjust sleep time for simulation speed
        end_time = datetime.datetime.now()

        ride_id = self._generate_id("ride")
        ride = Ride(ride_id, customer_id, driver_id, cab_id, source_id, destination_id, fare, zula_commission, path, start_time, end_time)
        self.rides_history[ride_id] = ride

        # Update driver and cab status
        driver.complete_ride(ride)
        cab.set_location(destination_id) # Cab's location is updated to the destination
        cab.set_availability(True) # Cab is available after dropping off
        self.unavailable_drivers.add(driver.id) # Driver is now on rest (Task 3)

        # Update cab_locations mapping in the system's memory
        self.update_cab_location_in_memory(cab_id, source_id, destination_id)

        customer.trip_history.append(ride)

        print(f"\nRide completed! Ride ID: {ride.id}")
        print(f"  From: {self.get_location_name(source_id)} to {self.get_location_name(destination_id)}")
        print(f"  Cab ID: {cab_id}, Driver: {driver.name}")
        print(f"  Fare: ${fare:.2f}")
        print(f"  Zula's Commission: ${zula_commission:.2f}")
        print(f"  Optimal Path: {' -> '.join([self.get_location_name(loc) for loc in path])}")
        print(f"  Driver {driver.name} is now on rest.")
        return ride

    # --- Task 5: View Customer History ---
    def view_customer_history(self, customer_id):
        """Prints the ride history for a given customer."""
        customer = self.get_customer_by_id(customer_id)
        if not customer:
            print("Error: Customer not found.")
            return

        if not customer.trip_history:
            print(f"Customer {customer.name} has no ride history.")
            return

        print(f"\n--- Ride History for Customer: {customer.name} ---")
        print("--------------------------------------------------------------------------------------------------------------------")
        print(f"{'Source':<10} {'Destination':<12} {'Cab ID':<8} {'Fare':<8} {'Driver':<15} {'Zula Commission':<18} {'Path Taken':<30}")
        print("--------------------------------------------------------------------------------------------------------------------")
        for ride in customer.trip_history:
            driver_name = self.get_driver_name(ride.driver_id)
            source_name = self.get_location_name(ride.source_id)
            destination_name = self.get_location_name(ride.destination_id)
            path_names = "->".join([self.get_location_name(loc_id) for loc_id in ride.path])
            print(f"{source_name:<10} {destination_name:<12} {ride.cab_id:<8} {ride.fare:<8.2f} {driver_name:<15} {ride.zula_commission:<18.2f} {path_names:<30}")
        print("--------------------------------------------------------------------------------------------------------------------")

    # --- Task 6: Zula's Commission ---
    def view_zula_commission_summary(self):
        """Calculates and prints the total commission earned by Zula."""
        total_zula_commission = sum(ride.zula_commission for ride in self.rides_history.values())
        print(f"\n--- Zula's Commission Summary ---")
        print(f"Total Zula's Commission from all rides: ${total_zula_commission:.2f}")
        return {"total_zula_commission": total_zula_commission}

    # --- Task 7: Admin - Redirect Cabs ---
    def redirect_cabs(self, admin_id, source_location_name):
        """
        Admin action to redirect cabs from a location if there are more than 2 cabs.
        Redirects to another random available location.
        """
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        source_loc_id = self._get_location_id_by_name(source_location_name)
        if source_loc_id is None:
            print(f"Error: Location '{source_location_name}' not found.")
            return False

        cabs_at_location = self.cab_locations.get(source_loc_id, [])
        if len(cabs_at_location) <= 2:
            print(f"No more than 2 cabs at {source_location_name}. No redirection needed.")
            return False

        cabs_to_redirect_ids = cabs_at_location[2:] # Keep first 2, redirect the rest
        redirected_count = 0

        # Find available target locations (all nodes in the graph except the source)
        target_locations = [loc_id for loc_id in self.locations.keys() if loc_id != source_loc_id]
        if not target_locations:
            print("No other locations available for redirection.")
            return False

        print(f"\nRedirecting cabs from {self.get_location_name(source_loc_id)}:")
        for cab_id in cabs_to_redirect_ids:
            cab = self.get_cab_by_id(cab_id)
            if cab:
                # Select a random new location for the cab
                new_location_id = random.choice(target_locations)
                new_location_name = self.get_location_name(new_location_id)

                self.update_cab_location_in_memory(cab.id, source_loc_id, new_location_id)
                cab.set_location(new_location_id)
                driver = self.get_driver_by_id(cab.driver_id)
                if driver:
                    driver.current_location_id = new_location_id
                print(f"  Cab {cab.id} (Driver: {driver.name if driver else 'N/A'}) redirected from {self.get_location_name(source_loc_id)} to {new_location_name}.")
                redirected_count += 1
        print(f"Total {redirected_count} cabs redirected.")
        return True

    def update_cab_location_in_memory(self, cab_id, old_location_id, new_location_id):
        """Helper to update cab's position in the cab_locations dictionary."""
        # Remove cab from old location's list
        if old_location_id in self.cab_locations and cab_id in self.cab_locations[old_location_id]:
            self.cab_locations[old_location_id].remove(cab_id)
            if not self.cab_locations[old_location_id]:
                del self.cab_locations[old_location_id] # Clean up empty list

        # Add cab to new location's list
        if new_location_id not in self.cab_locations:
            self.cab_locations[new_location_id] = []
        if cab_id not in self.cab_locations[new_location_id]: # Avoid duplicates
            self.cab_locations[new_location_id].append(cab_id)

    # --- Task 8: Allocate fairly to all drivers (Integrated into get_closest_available_driver_info sorting) ---

    # --- Task 9: Admin CURD Cabs (Add/ Remove / Update) ---
    def admin_add_cab(self, admin_id, driver_id, initial_location_name):
        """Admin adds a new cab and assigns it to an existing driver."""
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        driver = self.get_driver_by_id(driver_id)
        if not driver:
            print(f"Error: Driver with ID {driver_id} not found.")
            return False

        # Check if driver already has a cab
        for cab_obj in self.cabs.values():
            if cab_obj.driver_id == driver_id:
                print(f"Error: Driver {driver.name} already has a cab (ID: {cab_obj.id}).")
                return False

        location_id = self._get_location_id_by_name(initial_location_name)
        if location_id is None:
            print(f"Error: Location '{initial_location_name}' not found.")
            return False

        cab_id = self._generate_id("cab")
        cab = Cab(cab_id, location_id, driver_id)
        self.cabs[cab_id] = cab

        if location_id not in self.cab_locations:
            self.cab_locations[location_id] = []
        self.cab_locations[location_id].append(cab_id)

        driver.current_location_id = location_id # Update driver's location
        print(f"Admin added Cab {cab_id} for driver {driver.name} at {self.get_location_name(location_id)}.")
        return True

    def admin_remove_cab(self, admin_id, cab_id):
        """Admin removes a cab from the system."""
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
        """Admin updates a cab's current location."""
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        cab = self.get_cab_by_id(cab_id)
        if not cab:
            print(f"Error: Cab with ID {cab_id} not found.")
            return False

        new_location_id = self._get_location_id_by_name(new_location_name)
        if new_location_id is None:
            print(f"Error: New location '{new_location_name}' not found.")
            return False

        old_location_id = cab.current_location_id
        self.update_cab_location_in_memory(cab_id, old_location_id, new_location_id)
        cab.set_location(new_location_id)

        driver = self.get_driver_by_id(cab.driver_id)
        if driver:
            driver.current_location_id = new_location_id

        print(f"Admin updated Cab {cab_id} location from {self.get_location_name(old_location_id)} to {new_location_name}.")
        return True

    # --- Task 10: Admin CURD Locations ---
    def add_location_to_system(self, admin_id=None, name=None):
        """
        Adds a new location to the system and the location graph.
        Can be called by admin or internally during initialization.
        """
        if admin_id: # Only require admin for manual add, not for initial data load
            admin = self.get_admin_by_id(admin_id)
            if not admin:
                print("Error: Admin not found.")
                return False

        if not name:
            print("Error: Name is required for adding a location.")
            return None

        if self._get_location_id_by_name(name) is not None:
            print(f"Error: Location with name '{name}' already exists.")
            return None

        location_id = self._generate_id("location")
        location = Location(location_id, name)
        self.locations[location_id] = location
        self.location_names_to_ids[name] = location_id
        self.cab_locations[location_id] = [] # Initialize empty list for cabs at this location
        self.location_graph.add_node(location_id) # Add node to the graph
        print(f"Location '{name}' (ID: {location_id}) added.")
        return location

    def add_road_connection(self, loc1_name, loc2_name, distance):
        """
        Adds a road connection (edge) between two existing locations in the graph.
        This is how the network of roads is defined.
        """
        loc1_id = self._get_location_id_by_name(loc1_name)
        loc2_id = self._get_location_id_by_name(loc2_name)
        if loc1_id is None or loc2_id is None:
            print(f"Error: One or both locations ({loc1_name}, {loc2_name}) not found to add connection.")
            return False
        if distance <= 0:
            print("Error: Distance must be positive for a road connection.")
            return False
        self.location_graph.add_edge(loc1_id, loc2_id, distance)
        print(f"Added road connection between {loc1_name} and {loc2_name} with distance {distance}.")
        return True

    def admin_remove_location(self, admin_id, location_name):
        """Admin removes a location from the system."""
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        location_id = self._get_location_id_by_name(location_name)
        if location_id is None:
            print(f"Error: Location '{location_name}' not found.")
            return False

        # Check if any cabs are currently at this location
        if self.cab_locations.get(location_id):
            print(f"Error: Cannot remove location '{location_name}'. Cabs are currently assigned to it. Redirect them first.")
            return False

        # Check if any drivers have this as their current location (without a cab)
        for driver in self.cab_drivers.values():
            if driver.current_location_id == location_id:
                print(f"Error: Driver {driver.name} is currently at location '{location_name}'. Reassign them first.")
                return False

        # NOTE: In a more complex system, you'd also need to handle historical rides
        # that might reference this location or remove edges from the graph.
        # For this design, we'll simply remove the node from the active locations.
        # The graph will retain the node in its adjacency list, but no new paths will go there.

        del self.locations[location_id]
        del self.location_names_to_ids[location_name]
        if location_id in self.cab_locations:
            del self.cab_locations[location_id] # Remove its entry

        print(f"Admin removed Location '{location_name}' (ID: {location_id}).")
        return True

    def admin_update_location_name(self, admin_id, old_location_name, new_location_name):
        """Admin updates a location's name."""
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        location_obj = self.locations.get(self._get_location_id_by_name(old_location_name))
        if not location_obj:
            print(f"Error: Location '{old_location_name}' not found.")
            return False

        if self._get_location_id_by_name(new_location_name) is not None:
            print(f"Error: A location with the new name '{new_location_name}' already exists.")
            return False

        # Update the name in the Location object and the name-to-ID mapping
        location_obj.name = new_location_name
        del self.location_names_to_ids[old_location_name]
        self.location_names_to_ids[new_location_name] = location_obj.id
        print(f"Admin updated Location name from '{old_location_name}' to '{new_location_name}'.")
        return True
    
    # NOTE: Updating distances would require removing and re-adding edges in the Graph.
    # This is more complex and left out for brevity, as it implies network restructuring.

    # --- Task 11: View summary of all cabs (Admin) ---
    def view_all_cabs_summary(self, admin_id):
        """Admin views a detailed summary of all cabs and their drivers."""
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
                print("    --------------------------------------------------------------------------------------------------------------------")
                print(f"    {'Source':<10} {'Destination':<12} {'Fare':<8} {'Path Taken':<30} {'Start Time':<20} {'End Time':<20}")
                print("    --------------------------------------------------------------------------------------------------------------------")
                for ride in driver.trip_history:
                    source_name = self.get_location_name(ride.source_id)
                    destination_name = self.get_location_name(ride.destination_id)
                    path_names = "->".join([self.get_location_name(loc_id) for loc_id in ride.path])
                    print(f"    {source_name:<10} {destination_name:<12} {ride.fare:<8.2f} {path_names:<30} {ride.start_time.strftime('%H:%M:%S'):<20} {ride.end_time.strftime('%H:%M:%S'):<20}")
                print("    --------------------------------------------------------------------------------------------------------------------")

    # --- Task 12: Driver sees only his/her details ---
    def view_driver_summary(self, driver_id):
        """A driver views their own performance summary."""
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
            print("    --------------------------------------------------------------------------------------------------------------------")
            print(f"    {'Source':<10} {'Destination':<12} {'Fare':<8} {'Path Taken':<30} {'Start Time':<20} {'End Time':<20}")
            print("    --------------------------------------------------------------------------------------------------------------------")
            for trip in summary["Trip Details"]:
                source_name = self.get_location_name(trip['Source'])
                destination_name = self.get_location_name(trip['Destination'])
                path_names = "->".join([self.get_location_name(loc_id) for loc_id in trip['Path']])
                print(f"    {source_name:<10} {destination_name:<12} {trip['Fare']:<8.2f} {path_names:<30} {trip['Start Time']:<20} {trip['End Time']:<20}")
            print("    --------------------------------------------------------------------------------------------------------------------")

    # --- Task 13: Admin CURD All Tables (Users, Locations, Cabs) ---
    # Admin CURD for Cab Driver Table (User management - drivers)
    def admin_add_driver(self, admin_id, name, password, age, gender, initial_location_name):
        """Admin adds a new driver (and automatically a cab)."""
        return self.signup("driver", name, password, age, gender, initial_location_name)

    def admin_remove_driver(self, admin_id, driver_id):
        """Admin removes a driver and their associated cab."""
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
            self.admin_remove_cab(admin_id, cab_to_remove) # Use admin_remove_cab for consistency

        # Remove from users_by_credentials
        found_cred = False
        for (n, p), u_id in list(self.users_by_credentials.items()): # Use list to modify while iterating
            if u_id == driver_id and self.cab_drivers.get(u_id) == driver:
                del self.users_by_credentials[(n, p)]
                found_cred = True
                break
        
        del self.cab_drivers[driver_id]
        print(f"Admin removed Driver {driver.name} (ID: {driver_id}).")
        return True

    def admin_update_driver(self, admin_id, driver_id, name=None, password=None, age=None, gender=None, current_location_name=None):
        """Admin updates a driver's details."""
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
            new_loc_id = self._get_location_id_by_name(current_location_name)
            if new_loc_id:
                driver.current_location_id = new_loc_id
                # Also update associated cab's location if it exists
                for cab_id, cab in self.cabs.items():
                    if cab.driver_id == driver_id:
                        self.update_cab_location_in_memory(cab_id, cab.current_location_id, new_loc_id)
                        cab.set_location(new_loc_id)
                        break
                updated = True
            else:
                print(f"Warning: New location '{current_location_name}' not found for driver update. Location not changed.")

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
        """Admin adds a new customer."""
        return self.signup("customer", name, password, age, gender)

    def admin_remove_customer(self, admin_id, customer_id):
        """Admin removes a customer."""
        admin = self.get_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            return False

        customer = self.get_customer_by_id(customer_id)
        if not customer:
            print(f"Error: Customer with ID {customer_id} not found.")
            return False
        
        # Remove from users_by_credentials
        found_cred = False
        for (n, p), u_id in list(self.users_by_credentials.items()):
            if u_id == customer_id and self.customers.get(u_id) == customer:
                del self.users_by_credentials[(n, p)]
                found_cred = True
                break

        del self.customers[customer_id]
        print(f"Admin removed Customer {customer.name} (ID: {customer_id}).")
        return True

    def admin_update_customer(self, admin_id, customer_id, name=None, password=None, age=None, gender=None):
        """Admin updates a customer's details."""
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
        """Admin adds a new admin user."""
        return self.signup("admin", name, password, age, gender)

    def admin_remove_admin(self, admin_id, target_admin_id):
        """Admin removes another admin user."""
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
        found_cred = False
        for (n, p), u_id in list(self.users_by_credentials.items()):
            if u_id == target_admin_id and self.admins.get(u_id) == target_admin:
                del self.users_by_credentials[(n, p)]
                found_cred = True
                break

        del self.admins[target_admin_id]
        print(f"Admin removed Admin {target_admin.name} (ID: {target_admin_id}).")
        return True

    def admin_update_admin(self, admin_id, target_admin_id, name=None, password=None, age=None, gender=None):
        """Admin updates another admin user's details."""
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


# --- 3. Main Program Loop for Interaction ---

def main():
    """Main function to run the Zula Cab Booking System interactive console."""
    zula = ZulaSystem()
    current_user = None

    while True:
        print("\n" + "="*40)
        print("  WELCOME TO ZULA CAB BOOKING SYSTEM  ")
        print("="*40)
        if current_user:
            print(f"Logged in as: {current_user.__class__.__name__} ({current_user.name})")
        else:
            print("Not logged in.")

        print("\n--- Main Menu ---")
        if not current_user:
            print("1. Login")
            print("2. Sign Up (Customer)")
            print("3. Sign Up (Driver)")
            print("4. Sign Up (Admin)")
            print("0. Exit")
        else:
            if isinstance(current_user, Customer):
                print("5. Hail a Cab")
                print("6. View My Ride History")
            elif isinstance(current_user, Driver):
                print("7. View My Summary")
                if current_user.is_on_rest:
                    print("8. End Rest Period (Make Available)")
            elif isinstance(current_user, Admin):
                print("9. Redirect Cabs (Admin)")
                print("10. View All Cabs Summary (Admin)")
                print("11. View Zula's Commission Summary (Admin)")
                print("12. Admin: CURD Cabs")
                print("13. Admin: CURD Locations")
                print("14. Admin: CURD Users")

            print("0. Logout")

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
                print("Exiting Zula System. Goodbye!")
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
                    print("Invalid choice for Customer. Please try again.")
            elif isinstance(current_user, Driver):
                if choice == '7': # View My Summary
                    zula.view_driver_summary(current_user.id)
                elif choice == '8': # End Rest Period
                    if current_user.is_on_rest:
                        current_user.is_on_rest = False
                        if current_user.id in zula.unavailable_drivers:
                            zula.unavailable_drivers.remove(current_user.id)
                        print(f"Driver {current_user.name} is now available for rides!")
                    else:
                        print("You are not currently on rest.")
                else:
                    print("Invalid choice for Driver. Please try again.")
            elif isinstance(current_user, Admin):
                if choice == '9': # Redirect Cabs
                    location_name = input("Enter location name to check for cab redirection: ")
                    zula.redirect_cabs(current_user.id, location_name)
                elif choice == '10': # View All Cabs Summary
                    zula.view_all_cabs_summary(current_user.id)
                elif choice == '11': # View Zula's Commission Summary
                    zula.view_zula_commission_summary()
                elif choice == '12': # Admin CURD Cabs
                    print("\n--- Admin: CURD Cabs Sub-menu ---")
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
                        print("Invalid choice. Returning to main menu.")
                elif choice == '13': # Admin CURD Locations
                    print("\n--- Admin: CURD Locations Sub-menu ---")
                    print("a. Add Location")
                    print("b. Add Road Connection")
                    print("c. Remove Location")
                    print("d. Update Location Name")
                    loc_crud_choice = input("Enter choice (a/b/c/d): ").lower()
                    if loc_crud_choice == 'a':
                        name = input("Enter new location name: ")
                        zula.add_location_to_system(current_user.id, name)
                    elif loc_crud_choice == 'b':
                        loc1_name = input("Enter name of first location: ")
                        loc2_name = input("Enter name of second location: ")
                        distance = float(input("Enter distance between them: "))
                        zula.add_road_connection(loc1_name, loc2_name, distance)
                    elif loc_crud_choice == 'c':
                        name = input("Enter location name to remove: ")
                        zula.admin_remove_location(current_user.id, name)
                    elif loc_crud_choice == 'd':
                        old_name = input("Enter current location name to update: ")
                        new_name = input("Enter new name: ")
                        zula.admin_update_location_name(current_user.id, old_name, new_name)
                    else:
                        print("Invalid choice. Returning to main menu.")
                elif choice == '14': # Admin CURD Users
                    print("\n--- Admin: CURD Users Sub-menu ---")
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
                            initial_loc = input("Enter initial location name for driver (e.g., A, B, C): ")
                        
                        if user_type == 'driver':
                            zula.admin_add_driver(current_user.id, name, password, age, gender, initial_loc)
                        elif user_type == 'customer':
                            zula.admin_add_customer(current_user.id, name, password, age, gender)
                        elif user_type == 'admin':
                            zula.admin_add_admin(current_user.id, name, password, age, gender)
                        else:
                            print("Invalid user type. User not added.")
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
                            print("Invalid user type. User not removed.")
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
                            print("Invalid user type. User not updated.")
                    else:
                        print("Invalid choice. Returning to main menu.")
                else:
                    print("Invalid choice. Please try again.")
            else: # Should not happen if current_user type is handled
                print("Invalid choice. Please try again.")
        else:
            print("Invalid choice. Please login or sign up.")

if __name__ == "__main__":
    main()