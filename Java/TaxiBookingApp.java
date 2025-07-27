import java.util.*;

// Taxi class
class Taxi {
    private int taxiId;
    private String driverName;
    private String location;
    private boolean isAvailable;

    public Taxi(int taxiId, String driverName, String location) {
        this.taxiId = taxiId;
        this.driverName = driverName;
        this.location = location;
        this.isAvailable = true;
    }

    public int getTaxiId() {
        return taxiId;
    }

    public String getDriverName() {
        return driverName;
    }

    public String getLocation() {
        return location;
    }

    public boolean isAvailable() {
        return isAvailable;
    }

    public void book() {
        isAvailable = false;
    }

    public void release() {
        isAvailable = true;
    }

    @Override
    public String toString() {
        return "🚖 Taxi ID: " + taxiId +
                ", Driver: " + driverName +
                ", Location: " + location +
                ", Available: " + (isAvailable ? "Yes" : "No");
    }
}

// Ride class
class Ride {
    private static int rideCounter = 1;
    private int rideId;
    private Taxi taxi;
    private String source;
    private String destination;
    private Date time;

    public Ride(Taxi taxi, String source, String destination) {
        this.rideId = rideCounter++;
        this.taxi = taxi;
        this.source = source;
        this.destination = destination;
        this.time = new Date();
    }

    public int getRideId() {
        return rideId;
    }

    public Taxi getTaxi() {
        return taxi;
    }

    @Override
    public String toString() {
        return "🧾 Ride ID: " + rideId +
                ", Taxi: " + taxi.getTaxiId() +
                ", Driver: " + taxi.getDriverName() +
                ", From: " + source +
                ", To: " + destination +
                ", Time: " + time;
    }
}

// User class
class User {
    private String username;
    private String password;
    private List<Ride> rides;

    public User(String username, String password) {
        this.username = username;
        this.password = password;
        this.rides = new ArrayList<>();
    }

    public String getUsername() {
        return username;
    }

    public boolean checkPassword(String input) {
        return this.password.equals(input);
    }

    public void bookRide(List<Taxi> taxis, String source, String destination) {
        for (Taxi t : taxis) {
            if (t.isAvailable()) {
                t.book();
                Ride ride = new Ride(t, source, destination);
                rides.add(ride);
                System.out.println("✅ Ride booked successfully!");
                System.out.println(ride);
                return;
            }
        }
        System.out.println("❌ No taxis available right now.");
    }

    public void cancelRide(int rideId) {
        Iterator<Ride> it = rides.iterator();
        while (it.hasNext()) {
            Ride r = it.next();
            if (r.getRideId() == rideId) {
                r.getTaxi().release();
                it.remove();
                System.out.println("✅ Ride cancelled.");
                return;
            }
        }
        System.out.println("❌ Ride not found.");
    }

    public void showRides() {
        if (rides.isEmpty()) {
            System.out.println("📝 No rides booked.");
        } else {
            for (Ride r : rides) {
                System.out.println(r);
            }
        }
    }
}

// TaxiBookingSystem class
class TaxiBookingSystem {
    private List<Taxi> taxis;
    private Map<String, User> users;

    public TaxiBookingSystem() {
        taxis = new ArrayList<>();
        users = new HashMap<>();
    }

    public void addTaxi(Taxi taxi) {
        taxis.add(taxi);
    }

    public void showTaxis() {
        for (Taxi t : taxis) {
            System.out.println(t);
        }
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

    public List<Taxi> getTaxis() {
        return taxis;
    }
}

// Main class
public class TaxiBookingApp {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        TaxiBookingSystem system = new TaxiBookingSystem();

        // Preload some taxis
        system.addTaxi(new Taxi(1, "Ravi", "Delhi"));
        system.addTaxi(new Taxi(2, "Anjali", "Mumbai"));
        system.addTaxi(new Taxi(3, "John", "Bangalore"));

        User currentUser = null;

        while (true) {
            if (currentUser == null) {
                System.out.println("\n--- Taxi Booking System ---");
                System.out.println("1. Register");
                System.out.println("2. Login");
                System.out.println("3. Exit");
                System.out.print("Enter choice: ");
                String choice = sc.nextLine();

                switch (choice) {
                    case "1":
                        System.out.print("Username: ");
                        String u = sc.nextLine();
                        System.out.print("Password: ");
                        String p = sc.nextLine();
                        system.registerUser(u, p);
                        break;
                    case "2":
                        System.out.print("Username: ");
                        String lu = sc.nextLine();
                        System.out.print("Password: ");
                        String lp = sc.nextLine();
                        currentUser = system.login(lu, lp);
                        break;
                    case "3":
                        System.out.println("👋 Goodbye!");
                        sc.close();
                        return;
                    default:
                        System.out.println("⚠️ Invalid choice.");
                }
            } else {
                System.out.println("\n--- Welcome " + currentUser.getUsername() + " ---");
                System.out.println("1. View Available Taxis");
                System.out.println("2. Book Ride");
                System.out.println("3. Cancel Ride");
                System.out.println("4. My Ride History");
                System.out.println("5. Logout");
                System.out.print("Enter choice: ");
                String choice = sc.nextLine();

                switch (choice) {
                    case "1":
                        system.showTaxis();
                        break;
                    case "2":
                        System.out.print("Enter Pickup Location: ");
                        String src = sc.nextLine();
                        System.out.print("Enter Destination: ");
                        String dest = sc.nextLine();
                        currentUser.bookRide(system.getTaxis(), src, dest);
                        break;
                    case "3":
                        currentUser.showRides();
                        System.out.print("Enter Ride ID to cancel: ");
                        try {
                            int rideId = Integer.parseInt(sc.nextLine());
                            currentUser.cancelRide(rideId);
                        } catch (NumberFormatException e) {
                            System.out.println("⚠️ Invalid Ride ID.");
                        }
                        break;
                    case "4":
                        currentUser.showRides();
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
