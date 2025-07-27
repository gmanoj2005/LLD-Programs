import random
from collections import defaultdict

# Entities
class User:
    def __init__(self, user_id, name, password, age, gender):
        self.id = user_id
        self.name = name
        self.password = password
        self.age = age
        self.gender = gender

class Driver(User):
    def __init__(self, user_id, name, password, age, gender):
        super().__init__(user_id, name, password, age, gender)
        self.is_available = True
        self.skip_next = False
        self.total_trips = 0
        self.total_fare = 0
        self.ride_history = []

class Customer(User):
    def __init__(self, user_id, name, password, age, gender):
        super().__init__(user_id, name, password, age, gender)
        self.ride_history = []

class Admin(User):
    pass

class Location:
    def __init__(self, loc_id, name, distance):
        self.id = loc_id
        self.name = name
        self.distance = distance

class Cab:
    def __init__(self, cab_id, driver, location):
        self.cab_id = cab_id
        self.driver = driver
        self.location = location

class Ride:
    def __init__(self, source, dest, cab, customer, fare, zula_commission):
        self.source = source
        self.dest = dest
        self.cab = cab
        self.customer = customer
        self.fare = fare
        self.zula_commission = zula_commission

# System
class ZulaSystem:
    def __init__(self):
        self.users = {}
        self.customers = {}
        self.drivers = {}
        self.admins = {}
        self.locations = {}
        self.location_cabs = defaultdict(list)
        self.cabs = {}
        self.rides = []
        self.next_user_id = 1
        self.next_location_id = 1
        self.next_cab_id = 1

    def signup_user(self, user_type, name, password, age, gender):
        user_id = self.next_user_id
        self.next_user_id += 1

        if user_type == "customer":
            user = Customer(user_id, name, password, age, gender)
            self.customers[user_id] = user
        elif user_type == "driver":
            user = Driver(user_id, name, password, age, gender)
            self.drivers[user_id] = user
        elif user_type == "admin":
            user = Admin(user_id, name, password, age, gender)
            self.admins[user_id] = user
        else:
            raise ValueError("Invalid user type")

        self.users[user_id] = user
        return user

    def login(self, name, password):
        for user in self.users.values():
            if user.name == name and user.password == password:
                return user
        return None

    def add_location(self, name, distance):
        loc_id = self.next_location_id
        self.next_location_id += 1
        location = Location(loc_id, name, distance)
        self.locations[name] = location
        return location

    def add_cab(self, driver_id, location_name):
        if location_name not in self.locations:
            raise ValueError("Invalid location")

        cab_id = self.next_cab_id
        self.next_cab_id += 1

        driver = self.drivers[driver_id]
        location = self.locations[location_name]
        cab = Cab(cab_id, driver, location)
        self.cabs[cab_id] = cab
        self.location_cabs[location_name].append(cab_id)
        return cab

    def hail_cab(self, customer, source_name, dest_name):
        if source_name not in self.locations or dest_name not in self.locations:
            print("Invalid location")
            return None

        source = self.locations[source_name]
        dest = self.locations[dest_name]
        distance = abs(dest.distance - source.distance)
        fare = distance * 10

        available_cabs = [cab for cab in self.cabs.values()
                          if cab.location.name == source_name and
                          cab.driver.is_available and not cab.driver.skip_next]

        if not available_cabs:
            print("No cabs available at this location.")
            return None

        available_cabs.sort(key=lambda c: c.driver.total_trips)
        selected_cab = available_cabs[0]

        commission = fare * 0.3
        ride = Ride(source, dest, selected_cab, customer, fare, commission)
        self.rides.append(ride)

        driver = selected_cab.driver
        driver.total_fare += fare
        driver.total_trips += 1
        driver.skip_next = True
        driver.ride_history.append(ride)
        driver.is_available = False

        customer.ride_history.append(ride)

        self.location_cabs[source_name].remove(selected_cab.cab_id)
        self.location_cabs[dest_name].append(selected_cab.cab_id)
        selected_cab.location = dest
        driver.is_available = True

        for drv in self.drivers.values():
            if drv.skip_next:
                drv.skip_next = False

        return ride

    def view_customer_history(self, customer):
        return [(r.source.name, r.dest.name, r.cab.cab_id, r.fare) for r in customer.ride_history]

    def view_ride_with_commission(self, user):
        for r in self.rides:
            print((r.source.name, r.dest.name, r.cab.cab_id, r.fare, r.zula_commission))

    def admin_cab_summary(self):
        for cab in self.cabs.values():
            driver = cab.driver
            print(f"Cab ID: {cab.cab_id}, Driver: {driver.name}")
            print(f"Total Trips: {driver.total_trips}, Total Fare: {driver.total_fare}, Commission: {driver.total_fare * 0.3}")
            for ride in driver.ride_history:
                print(f"  Trip: {ride.source.name} -> {ride.dest.name}, Fare: {ride.fare}")
            print("---")

    def driver_summary(self, driver):
        print(f"Driver: {driver.name}")
        print(f"Total Trips: {driver.total_trips}, Total Fare: {driver.total_fare}, Commission Earned: {driver.total_fare * 0.7}")
        for ride in driver.ride_history:
            print(f"  Ride: {ride.source.name} to {ride.dest.name}, Fare: {ride.fare}")

# --- Interactive CLI ---
def main():
    zula = ZulaSystem()
    zula.add_location("A", 0)
    zula.add_location("B", 10)
    zula.add_location("C", 20)
    zula.add_location("P", 50)

    while True:
        print("\n--- Zula Cab Booking System ---")
        print("1. Sign Up")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            role = input("Enter role (customer/driver/admin): ")
            name = input("Name: ")
            password = input("Password: ")
            age = int(input("Age: "))
            gender = input("Gender (M/F): ")
            user = zula.signup_user(role, name, password, age, gender)
            print(f"{role.capitalize()} signed up with ID: {user.id}")

        elif choice == "2":
            name = input("Name: ")
            password = input("Password: ")
            user = zula.login(name, password)
            if user:
                print(f"Welcome {user.name}!")
                if isinstance(user, Customer):
                    while True:
                        print("\n-- Customer Menu --")
                        print("1. Hail Cab")
                        print("2. View Ride History")
                        print("3. Logout")
                        c = input("Choose: ")
                        if c == "1":
                            src = input("Source location: ")
                            dst = input("Destination location: ")
                            ride = zula.hail_cab(user, src, dst)
                            if ride:
                                print(f"Cab {ride.cab.cab_id} assigned from {src} to {dst}, Fare: {ride.fare}")
                        elif c == "2":
                            for hist in zula.view_customer_history(user):
                                print(hist)
                        elif c == "3":
                            break
                elif isinstance(user, Admin):
                    while True:
                        print("\n-- Admin Menu --")
                        print("1. View Rides with Commission")
                        print("2. View Cab Summary")
                        print("3. Logout")
                        a = input("Choose: ")
                        if a == "1":
                            zula.view_ride_with_commission(user)
                        elif a == "2":
                            zula.admin_cab_summary()
                        elif a == "3":
                            break
                elif isinstance(user, Driver):
                    while True:
                        print("\n-- Driver Menu --")
                        print("1. View My Summary")
                        print("2. Logout")
                        d = input("Choose: ")
                        if d == "1":
                            zula.driver_summary(user)
                        elif d == "2":
                            break
            else:
                print("Invalid credentials.")

        elif choice == "3":
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()
