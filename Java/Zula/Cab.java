import java.util.*;

public class Cab {
    private static int counter = 1;
    private int id;
    private Driver driver;
    private String currentLocation;
    private int totalFare = 0, totalTrips = 0;
    private List<Ride> rideHistory = new ArrayList<>();

    public Cab(Driver driver) {
        this.id = counter++;
        this.driver = driver;
    }

    public int getId() { return id; }
    public Driver getDriver() { return driver; }
    public void setCurrentLocation(String loc) { this.currentLocation = loc; }
    public String getCurrentLocation() { return currentLocation; }

    public void addRide(Ride ride) {
        rideHistory.add(ride);
        totalFare += ride.getFare();
        totalTrips++;
    }

    public int getTotalFare() { return totalFare; }
    public int getTotalTrips() { return totalTrips; }
    public List<Ride> getRideHistory() { return rideHistory; }
}
