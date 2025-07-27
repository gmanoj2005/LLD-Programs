import java.util.*;

public class Driver extends User {
    private String currentLocation;
    private boolean isAvailable = true, restFlag = false;
    private int totalTrips = 0, totalFare = 0;
    private List<Ride> rideHistory = new ArrayList<>();

    public Driver(String name, String password, int age, String gender) {
        super(name, password, age, gender);
    }

    public String getCurrentLocation() { return currentLocation; }
    public void setCurrentLocation(String loc) { this.currentLocation = loc; }

    public boolean isAvailable() { return isAvailable; }
    public void setAvailable(boolean available) { this.isAvailable = available; }

    public boolean isRestFlag() { return restFlag; }
    public void setRestFlag(boolean restFlag) { this.restFlag = restFlag; }

    public int getTotalTrips() { return totalTrips; }
    public int getTotalFare() { return totalFare; }
    public List<Ride> getRideHistory() { return rideHistory; }

    public void addRide(Ride ride) {
        rideHistory.add(ride);
        totalFare += ride.getFare();
        totalTrips++;
    }

    @Override
    public String getRole() { return "Driver"; }
}
