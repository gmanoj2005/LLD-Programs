import datetime

# ------------------------
# Train Class
# ------------------------
class Train:
    def __init__(self, train_no, name, source, destination, seats):
        self.train_no = train_no
        self.name = name
        self.source = source
        self.destination = destination
        self.total_seats = seats
        self.available_seats = seats

    def book_seat(self):
        if self.available_seats > 0:
            self.available_seats -= 1
            return True
        return False

    def cancel_seat(self):
        if self.available_seats < self.total_seats:
            self.available_seats += 1
            return True
        return False

    def __str__(self):
        return f"Train No: {self.train_no}, Name: {self.name}, From: {self.source}, To: {self.destination}, Available Seats: {self.available_seats}"

# ------------------------
# User Class
# ------------------------
class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.tickets = []

    def book_ticket(self, train):
        if train.book_seat():
            ticket = Ticket(self, train)
            self.tickets.append(ticket)
            print("✅ Ticket Booked Successfully!")
            print(ticket)
        else:
            print("❌ No seats available!")

    def cancel_ticket(self, ticket_id):
        for ticket in self.tickets:
            if ticket.ticket_id == ticket_id:
                ticket.train.cancel_seat()
                self.tickets.remove(ticket)
                print("✅ Ticket Canceled Successfully!")
                return
        print("❌ Ticket ID not found.")

    def show_tickets(self):
        if not self.tickets:
            print("📝 No tickets booked.")
        else:
            for t in self.tickets:
                print(t)

# ------------------------
# Ticket Class
# ------------------------
class Ticket:
    ticket_counter = 1

    def __init__(self, user, train):
        self.ticket_id = Ticket.ticket_counter
        Ticket.ticket_counter += 1
        self.user = user
        self.train = train
        self.booking_time = datetime.datetime.now()

    def __str__(self):
        return (f"🎟️ Ticket ID: {self.ticket_id}, Train: {self.train.name} ({self.train.train_no}), "
                f"From: {self.train.source}, To: {self.train.destination}, Booked at: {self.booking_time.strftime('%Y-%m-%d %H:%M:%S')}")

# ------------------------
# System Class
# ------------------------
class RailwaySystem:
    def __init__(self):
        self.trains = []
        self.users = {}

    def add_train(self, train):
        self.trains.append(train)

    def register_user(self, username, password):
        if username in self.users:
            print("❌ Username already exists!")
        else:
            self.users[username] = User(username, password)
            print("✅ Registration successful!")

    def login(self, username, password):
        user = self.users.get(username)
        if user and user.password == password:
            print(f"✅ Welcome {username}!")
            return user
        else:
            print("❌ Invalid credentials!")
            return None

    def show_trains(self):
        if not self.trains:
            print("🚫 No trains available.")
        for train in self.trains:
            print(train)

# ------------------------
# Main App Loop
# ------------------------
def main():
    system = RailwaySystem()

    # Preload some trains
    system.add_train(Train(101, "Express Line", "Delhi", "Mumbai", 5))
    system.add_train(Train(102, "Rajdhani", "Kolkata", "Delhi", 3))
    system.add_train(Train(103, "Shatabdi", "Chennai", "Bangalore", 4))

    current_user = None

    while True:
        if not current_user:
            print("\n--- Railway Ticket Booking ---")
            print("1. Register")
            print("2. Login")
            print("3. Exit")
            choice = input("Enter choice: ")

            if choice == '1':
                u = input("Enter username: ")
                p = input("Enter password: ")
                system.register_user(u, p)
            elif choice == '2':
                u = input("Enter username: ")
                p = input("Enter password: ")
                current_user = system.login(u, p)
            elif choice == '3':
                print("👋 Exiting...")
                break
            else:
                print("⚠️ Invalid choice!")
        else:
            print(f"\n--- Welcome {current_user.username} ---")
            print("1. View Trains")
            print("2. Book Ticket")
            print("3. Cancel Ticket")
            print("4. View My Tickets")
            print("5. Logout")
            choice = input("Enter choice: ")

            if choice == '1':
                system.show_trains()
            elif choice == '2':
                system.show_trains()
                train_no = int(input("Enter Train No to book: "))
                train = next((t for t in system.trains if t.train_no == train_no), None)
                if train:
                    current_user.book_ticket(train)
                else:
                    print("🚫 Train not found.")
            elif choice == '3':
                current_user.show_tickets()
                try:
                    tid = int(input("Enter Ticket ID to cancel: "))
                    current_user.cancel_ticket(tid)
                except ValueError:
                    print("⚠️ Invalid Ticket ID.")
            elif choice == '4':
                current_user.show_tickets()
            elif choice == '5':
                current_user = None
            else:
                print("⚠️ Invalid choice!")

if __name__ == "__main__":
    main()
