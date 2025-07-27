import java.util.*;
import java.util.stream.Collectors;

public class ZulaSystem {
    private Map<Integer, Driver> drivers = new HashMap<>();
    private Map<Integer, Customer> customers = new HashMap<>();
    private Map<Integer, Admin> admins = new HashMap<>();
    private Map<String, Location> locations = new HashMap<>();
    private Map<Integer, Cab> cabs = new HashMap<>();
    private Map<String, List<Integer>> locationToCabs = new HashMap<>();
    private Map<String, List<AbstractMap.SimpleEntry<String, Integer>>> graph = new HashMap<>();

    public User signupUser(String role, String name, String password, int age, String gender) {
        switch (role.toLowerCase()) {
            case "driver":
                Driver d = new Driver(name, password, age, gender);
                drivers.put(d.getId(), d);
                return d;
            case "customer":
                Customer c = new Customer(name, password, age, gender);
                customers.put(c.getId(), c);
                return c;
            case "admin":
                Admin a = new Admin(name, password, age, gender);
                admins.put(a.getId(), a);
                return a;
        }
        return null;
    }

    public User login(String role, String name, String password) {
        Collection<? extends User> users = switch (role.toLowerCase()) {
            case "driver" -> drivers.values();
            case "customer" -> customers.values();
            case "admin" -> admins.values();
            default -> List.of();
        };
        return users.stream().filter(u -> u.getName().equals(name) && u.getPassword().equals(password)).findFirst().orElse(null);
    }

    public void addLocation(String name, int dist) {
        locations.put(name.toUpperCase(), new Location(name, dist));
        locationToCabs.putIfAbsent(name.toUpperCase(), new ArrayList<>());
        graph.putIfAbsent(name.toUpperCase(), new ArrayList<>());
    }

    public void connectLocations(String a, String b, int dist) {
        graph.get(a.toUpperCase()).add(new AbstractMap.SimpleEntry<>(b.toUpperCase(), dist));
        graph.get(b.toUpperCase()).add(new AbstractMap.SimpleEntry<>(a.toUpperCase(), dist));
    }

    public void addCab(int driverId, String location) {
        Driver d = drivers.get(driverId);
        Cab c = new Cab(d);
        c.setCurrentLocation(location.toUpperCase());
        d.setCurrentLocation(location.toUpperCase());
        cabs.put(c.getId(), c);
        locationToCabs.get(location.toUpperCase()).add(c.getId());
    }

    private List<String> dijkstra(String src, String dst) {
        Map<String, Integer> dist = new HashMap<>();
        Map<String, String> prev = new HashMap<>();
        PriorityQueue<Map.Entry<String, Integer>> pq = new PriorityQueue<>(Map.Entry.comparingByValue);
        for (String node : graph.keySet()) dist.put(node, Integer.MAX_VALUE);
        dist.put(src, 0);
        pq.add(Map.entry(src, 0));

        while (!pq.isEmpty()) {
            String u = pq.poll().getKey();
            for (var pair : graph.getOrDefault(u, List.of())) {
                String v = pair.getKey();
                int weight = pair.getValue();
                int alt = dist.get(u) + weight;
                if (alt < dist.getOrDefault(v, Integer.MAX_VALUE)) {
                    dist.put(v, alt);
                    prev.put(v, u);
                    pq.add(Map.entry(v, alt));
                }
            }
        }

        List<String> path = new ArrayList<>();
        for (String at = dst; at != null; at = prev.get(at))
            path.add(at);
        Collections.reverse(path);
        return path;
    }

    public Ride hailCab(Customer c, String src, String dst) {
        List<Integer> cabIds = locationToCabs.getOrDefault(src.toUpperCase(), List.of());
        List<Ride> options = new ArrayList<>();
        List<String> path = dijkstra(src.toUpperCase(), dst.toUpperCase());

        int dist = 0;
        for (int i = 1; i < path.size(); i++) {
            String u = path.get(i - 1), v = path.get(i);
            for (var e : graph.get(u)) if (e.getKey().equals(v)) dist += e.getValue();
        }

        for (int id : cabIds) {
            Cab cab = cabs.get(id);
            Driver d = cab.getDriver();
            if (d.isAvailable() && !d.isRestFlag()) {
                int fare = dist * 10;
                Ride r = new Ride(locations.get(src.toUpperCase()), locations.get(dst.toUpperCase()), cab, fare, c, path);
                options.add(r);

                cab.addRide(r);
                d.addRide(r);
                cab.setCurrentLocation(dst.toUpperCase());
                d.setCurrentLocation(dst.toUpperCase());
                d.setAvailable(false);
                d.setRestFlag(true);
                c.addRide(r);
                return r;
            }
        }
        return null;
    }

    public void resetRestFlags() {
        for (Driver d : drivers.values()) {
            if (d.isRestFlag()) {
                d.setRestFlag(false);
                d.setAvailable(true);
            }
        }
    }

    public void viewCustomerHistory(Customer c) {
        for (Ride r : c.getRideHistory()) {
            System.out.println(r.getSource().getName() + " -> " + r.getDest().getName() +
                    " | Cab: " + r.getCab().getId() + " | Fare: " + r.getFare() + " | Route: " + String.join(" -> ", r.getPath()));
        }
    }

    public void viewRidesWithCommission(User u) {
        if (u instanceof Admin || u instanceof Driver) {
            Collection<Ride> rides = u instanceof Admin ?
                    cabs.values().stream().flatMap(c -> c.getRideHistory().stream()).toList() :
                    ((Driver) u).getRideHistory();

            for (Ride r : rides) {
                System.out.println(r.getSource().getName() + " -> " + r.getDest().getName() +
                        " | Cab: " + r.getCab().getId() + " | Fare: " + r.getFare() +
                        " | Commission: " + r.getCommission() +
                        " | Route: " + String.join(" -> ", r.getPath()));
            }
        }
    }

    public void adminCabSummary() {
        for (Cab cab : cabs.values()) {
            System.out.println("Cab ID: " + cab.getId());
            System.out.println("Total Trips: " + cab.getTotalTrips());
            System.out.println("Total Fare: " + cab.getTotalFare());
            System.out.println("Commission: " + (int)(cab.getTotalFare() * 0.3));
            for (Ride r : cab.getRideHistory()) {
                System.out.println(r.getSource().getName() + " -> " + r.getDest().getName() +
                        " | Fare: " + r.getFare() +
                        " | Customer: " + r.getCustomer().getName() +
                        " | Route: " + String.join(" -> ", r.getPath()));
            }
        }
    }

    public void rebalanceCabs() {
        for (var entry : locationToCabs.entrySet()) {
            List<Integer> cabsHere = entry.getValue();
            if (cabsHere.size() > 2) {
                List<Integer> extra = cabsHere.subList(2, cabsHere.size());
                String target = locations.keySet().stream().filter(l -> !l.equals(entry.getKey())).findFirst().orElse(null);
                if (target != null) {
                    for (int cabId : extra) updateCabLocation(cabId, target);
                }
            }
        }
    }

    public void updateCabLocation(int cabId, String newLocation) {
        Cab cab = cabs.get(cabId);
        String oldLoc = cab.getCurrentLocation();
        locationToCabs.get(oldLoc).remove(Integer.valueOf(cabId));
        cab.setCurrentLocation(newLocation.toUpperCase());
        cab.getDriver().setCurrentLocation(newLocation.toUpperCase());
        locationToCabs.get(newLocation.toUpperCase()).add(cabId);
    }
}
