import java.util.*;

public class Customer extends User {
    private List<Ride> rideHistory = new ArrayList<>();

    public Customer(String name, String password, int age, String gender) {
        super(name, password, age, gender);
    }

    public List<Ride> getRideHistory() { return rideHistory; }
    public void addRide(Ride ride) { rideHistory.add(ride); }

    @Override
    public String getRole() { return "Customer"; }
}
