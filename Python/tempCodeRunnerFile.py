# Zula In-Memory Cab Booking System

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import itertools

# Base User Class
class User(ABC):
    _id_counter = itertools.count(1)

    def __init__(self, name: str, password: str, age: int, gender: str):
        self.id = next(User._id_counter)
        self.name = name
        self.password = password
        self.age = age
        self.gender = gender

    @abstractmethod
    def get_role(self):
        pass

class Driver(User):
    def __init__(self, name, password, age, gender):
        super().__init__(name, password, age, gender)
        self.current_location = None
        self.is_available = True
        self.rest_flag = False
        self.total_trips = 0
        self.total_fare = 0
        self.ride_history = []

    def get_role(self):
        return "Driver"

class Customer(User):
    def __init__(self, name, password, age, gender):
        super().__init__(name, password, age, gender)
        self.ride_history = []

    def get_role(self):
        return "Customer"

class Admin(User):
    def get_role(self):
        return "Admin"

class Location:
    def __init__(self, name: str, distance: int):
        self.id = name.upper()
        self.name = name.upper()
        self.distance = distance

class Cab:
    _id_counter = itertools.count(1)

    def __init__(self, driver: Driver):
        self.id = next(Cab._id_counter)
        self.driver = driver
        self.current_location = None
        self.total_trips = 0
        self.total_fare = 0
        self.ride_history = []

class Ride:
    def __init__(self, source: Location, dest: Location, cab: Cab, fare: int, customer: Customer):
        self.source = source
        self.dest = dest
        self.cab = cab
        self.driver = cab.driver
        self.customer = customer
        self.fare = fare
        self.zula_commission = int(fare * 0.3)

class ZulaSystem:
    def __init__(self):
        self.drivers: Dict[int, Driver] = {}
        self.customers: Dict[int, Customer] = {}
        self.admins: Dict[int, Admin] = {}
        self.locations: Dict[str, Location] = {}
        self.cabs: Dict[int, Cab] = {}
        self.location_to_cabs: Dict[str, List[int]] = {}

    def signup_user(self, role: str, name: str, password: str, age: int, gender: str):
        if role.lower() == "driver":
            driver = Driver(name, password, age, gender)
            self.drivers[driver.id] = driver
            return driver
        elif role.lower() == "customer":
            customer = Customer(name, password, age, gender)
            self.customers[customer.id] = customer
            return customer
        elif role.lower() == "admin":
            admin = Admin(name, password, age, gender)
            self.admins[admin.id] = admin
            return admin

    def login_user(self, role: str, name: str, password: str):
        users = {
            "driver": self.drivers,
            "customer": self.customers,
            "admin": self.admins
        }.get(role.lower())

        for user in users.values():
            if user.name == name and user.password == password:
                return user
        return None

    def add_location(self, name: str, distance: int):
        loc = Location(name, distance)
        self.locations[loc.name] = loc
        self.location_to_cabs.setdefault(loc.name, [])

    def update_location(self, name: str, distance: int):
        if name.upper() in self.locations:
            self.locations[name.upper()].distance = distance

    def delete_location(self, name: str):
        name = name.upper()
        if name in self.locations:
            del self.locations[name]
            self.location_to_cabs.pop(name, None)

    def add_cab(self, driver_id: int, location_name: str):
        driver = self.drivers.get(driver_id)
        if not driver:
            raise ValueError("Driver not found")
        cab = Cab(driver)
        self.cabs[cab.id] = cab
        cab.current_location = location_name.upper()
        driver.current_location = location_name.upper()
        self.location_to_cabs.setdefault(location_name.upper(), []).append(cab.id)

    def remove_cab(self, cab_id: int):
        if cab_id in self.cabs:
            loc = self.cabs[cab_id].current_location
            if loc in self.location_to_cabs:
                self.location_to_cabs[loc].remove(cab_id)
            del self.cabs[cab_id]

    def update_cab_location(self, cab_id: int, new_location: str):
        cab = self.cabs.get(cab_id)
        if cab:
            old_loc = cab.current_location
            if old_loc in self.location_to_cabs:
                self.location_to_cabs[old_loc].remove(cab.id)
            self.location_to_cabs.setdefault(new_location.upper(), []).append(cab.id)
            cab.current_location = new_location.upper()
            cab.driver.current_location = new_location.upper()

    def hail_cab(self, customer: Customer, source: str, dest: str):
        src = self.locations.get(source.upper())
        dst = self.locations.get(dest.upper())
        if not src or not dst:
            print("Invalid location")
            return

        available_cabs = []
        for cab_id in self.location_to_cabs.get(source.upper(), []):
            cab = self.cabs[cab_id]
            driver = cab.driver
            if driver.is_available and not driver.rest_flag:
                distance = abs(dst.distance - src.distance)
                fare = distance * 10
                available_cabs.append((cab, fare))

        available_cabs.sort(key=lambda x: x[0].driver.total_trips)

        for cab, fare in available_cabs:
            print(f"Offering Cab {cab.id} driven by {cab.driver.name} | Fare: {fare}")
            ride = Ride(src, dst, cab, fare, customer)
            cab.ride_history.append(ride)
            cab.total_fare += fare
            cab.total_trips += 1
            cab.current_location = dst.name
            customer.ride_history.append(ride)
            cab.driver.ride_history.append(ride)
            cab.driver.total_fare += fare
            cab.driver.total_trips += 1
            cab.driver.rest_flag = True
            cab.driver.is_available = False
            cab.driver.current_location = dst.name
            return ride
        print("No cab available")

    def reset_driver_rest_flags(self):
        for driver in self.drivers.values():
            if driver.rest_flag:
                driver.rest_flag = False
                driver.is_available = True

    def view_customer_history(self, customer: Customer):
        return [(r.source.name, r.dest.name, r.cab.id, r.fare) for r in customer.ride_history]

    def view_ride_with_commission(self, user):
        if isinstance(user, Admin):
            for cab in self.cabs.values():
                for ride in cab.ride_history:
                    print(f"{ride.source.name} -> {ride.dest.name} | Cab: {ride.cab.id} | Fare: {ride.fare} | Commission: {ride.zula_commission}")
        elif isinstance(user, Driver):
            for ride in user.ride_history:
                print(f"{ride.source.name} -> {ride.dest.name} | Cab: {ride.cab.id} | Fare: {ride.fare} | Commission: {ride.zula_commission}")

    def admin_cab_summary(self):
        for cab in self.cabs.values():
            print(f"\nCab ID: {cab.id}")
            print(f"Total Trips: {cab.total_trips}")
            print(f"Total Fare: {cab.total_fare}")
            print(f"Total Commission: {int(cab.total_fare * 0.3)}")
            for ride in cab.ride_history:
                print(f"{ride.source.name} -> {ride.dest.name} | Fare: {ride.fare} | Customer: {ride.customer.name}")

    def rebalance_cabs(self):
        for loc, cabs in self.location_to_cabs.items():
            if len(cabs) > 2:
                excess = cabs[2:]
                for cab_id in excess:
                    new_loc = next((l for l in self.locations if l != loc), None)
                    if new_loc:
                        self.update_cab_location(cab_id, new_loc)

# This is the full LLD code. UI/CLI can be built on top of this.

