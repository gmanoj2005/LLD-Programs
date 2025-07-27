import java.util.*;

class Train {
    private int trainNo;
    private String name;
    private String source;
    private String destination;
    private int totalSeats;
    private int availableSeats;

    public Train(int trainNo, String name, String source, String destination, int totalSeats) {
        this.trainNo = trainNo;
        this.name = name;
        this.source = source;
        this.destination = destination;
        this.totalSeats = totalSeats;
        this.availableSeats = totalSeats;
    }

    public boolean bookSeat() {
        if (availableSeats > 0) {
            availableSeats--;
            return true;
        }
        return false;
    }

    public boolean cancelSeat() {
        if (availableSeats < totalSeats) {
            availableSeats++;
            return true;
        }
        return false;
    }

    public int getTrainNo() {
        return trainNo;
    }

    public String getName() {
        return name;
    }

    public String getSource() {
        return source;
    }

    public String getDestination() {
        return destination;
    }

    public int getAvailableSeats() {
        return availableSeats;
    }

    @Override
    public String toString() {
        return "Train No: " + trainNo + ", Name: " + name +
               ", From: " + source + ", To: " + destination +
               ", Available Seats: " + availableSeats;
    }
}

class Ticket {
    private static int ticketCounter = 1;
    private int ticketId;
    private Train train;
    private Date bookingTime;

    public Ticket(Train train) {
        this.ticketId = ticketCounter++;
        this.train = train;
        this.bookingTime = new Date();
    }

    public int getTicketId() {
        return ticketId;
    }

    public Train getTrain() {
        return train;
    }

    @Override
    public String toString() {
        return "🎟️ Ticket ID: " + ticketId +
               ", Train: " + train.getName() + " (" + train.getTrainNo() + ")" +
               ", From: " + train.getSource() + ", To: " + train.getDestination() +
               ", Booked at: " + bookingTime;
    }
}

class User {
    private String username;
    private String password;
    private List<Ticket> tickets;

    public User(String username, String password) {
        this.username = username;
        this.password = password;
        this.tickets = new ArrayList<>();
    }

    public String getUsername() {
        return username;
    }

    public boolean checkPassword(String input) {
        return this.password.equals(input);
    }

    public void bookTicket(Train train) {
        if (train.bookSeat()) {
            Ticket ticket = new Ticket(train);
            tickets.add(ticket);
            System.out.println("✅ Ticket booked successfully!");
            System.out.println(ticket);
        } else {
            System.out.println("❌ No available seats on this train.");
        }
    }

    public void cancelTicket(int ticketId) {
        Iterator<Ticket> iterator = tickets.iterator();
        while (iterator.hasNext()) {
            Ticket t = iterator.next();
            if (t.getTicketId() == ticketId) {
                t.getTrain().cancelSeat();
                iterator.remove();
                System.out.println("✅ Ticket canceled successfully.");
                return;
            }
        }
        System.out.println("❌ Ticket ID not found.");
    }

    public void showTickets() {
        if (tickets.isEmpty()) {
            System.out.println("📝 No tickets booked.");
        } else {
            for (Ticket t : tickets) {
                System.out.println(t);
            }
        }
    }
}

class RailwaySystem {
    private List<Train> trains;
    private Map<String, User> users;

    public RailwaySystem() {
        trains = new ArrayList<>();
        users = new HashMap<>();
    }

    public void addTrain(Train train) {
        trains.add(train);
    }

    public void showTrains() {
        if (trains.isEmpty()) {
            System.out.println("🚫 No trains available.");
        } else {
            for (Train t : trains) {
                System.out.println(t);
            }
        }
    }

    public Train findTrain(int trainNo) {
        for (Train t : trains) {
            if (t.getTrainNo() == trainNo) return t;
        }
        return null;
    }

    public void registerUser(String username, String password) {
        if (users.containsKey(username)) {
            System.out.println("❌ Username already exists.");
        } else {
            users.put(username, new User(username, password));
            System.out.println("✅ Registration successful.");
        }
    }

    public User login(String username, String password) {
        User user = users.get(username);
        if (user != null && user.checkPassword(password)) {
            System.out.println("✅ Welcome " + username + "!");
            return user;
        } else {
            System.out.println("❌ Invalid credentials.");
            return null;
        }
    }
}

public class RailwayBookingApp {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        RailwaySystem system = new RailwaySystem();

        // Add some trains
        system.addTrain(new Train(101, "Express Line", "Delhi", "Mumbai", 5));
        system.addTrain(new Train(102, "Rajdhani", "Kolkata", "Delhi", 3));
        system.addTrain(new Train(103, "Shatabdi", "Chennai", "Bangalore", 4));

        User currentUser = null;

        while (true) {
            if (currentUser == null) {
                System.out.println("\n--- Railway Ticket Booking ---");
                System.out.println("1. Register");
                System.out.println("2. Login");
                System.out.println("3. Exit");
                System.out.print("Enter choice: ");
                String choice = sc.nextLine();

                switch (choice) {
                    case "1":
                        System.out.print("Enter username: ");
                        String ru = sc.nextLine();
                        System.out.print("Enter password: ");
                        String rp = sc.nextLine();
                        system.registerUser(ru, rp);
                        break;
                    case "2":
                        System.out.print("Enter username: ");
                        String lu = sc.nextLine();
                        System.out.print("Enter password: ");
                        String lp = sc.nextLine();
                        currentUser = system.login(lu, lp);
                        break;
                    case "3":
                        System.out.println("👋 Exiting...");
                        return;
                    default:
                        System.out.println("⚠️ Invalid choice.");
                }
            } else {
                System.out.println("\n--- Welcome " + currentUser.getUsername() + " ---");
                System.out.println("1. View Trains");
                System.out.println("2. Book Ticket");
                System.out.println("3. Cancel Ticket");
                System.out.println("4. View My Tickets");
                System.out.println("5. Logout");
                System.out.print("Enter choice: ");
                String choice = sc.nextLine();

                switch (choice) {
                    case "1":
                        system.showTrains();
                        break;
                    case "2":
                        system.showTrains();
                        System.out.print("Enter Train No to book: ");
                        int trainNo = Integer.parseInt(sc.nextLine());
                        Train train = system.findTrain(trainNo);
                        if (train != null) {
                            currentUser.bookTicket(train);
                        } else {
                            System.out.println("🚫 Train not found.");
                        }
                        break;
                    case "3":
                        currentUser.showTickets();
                        System.out.print("Enter Ticket ID to cancel: ");
                        int ticketId = Integer.parseInt(sc.nextLine());
                        currentUser.cancelTicket(ticketId);
                        break;
                    case "4":
                        currentUser.showTickets();
                        break;
                    case "5":
                        currentUser = null;
                        break;
                    default:
                        System.out.println("⚠️ Invalid choice.");
                }
            }
        }
    }
}
