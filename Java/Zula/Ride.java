import java.util.*;

public class Ride {
    private Location source, dest;
    private Cab cab;
    private Customer customer;
    private int fare, commission;
    private List<String> path;

    public Ride(Location source, Location dest, Cab cab, int fare, Customer customer, List<String> path) {
        this.source = source;
        this.dest = dest;
        this.cab = cab;
        this.fare = fare;
        this.customer = customer;
        this.path = path;
        this.commission = (int)(fare * 0.3);
    }

    public int getFare() { return fare; }
    public int getCommission() { return commission; }
    public Location getSource() { return source; }
    public Location getDest() { return dest; }
    public List<String> getPath() { return path; }
    public Cab getCab() { return cab; }
    public Customer getCustomer() { return customer; }
}
