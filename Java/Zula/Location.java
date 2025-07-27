public class Location {
    private final String name;
    private final int distance;

    public Location(String name, int distance) {
        this.name = name.toUpperCase();
        this.distance = distance;
    }

    public String getName() { return name; }
    public int getDistance() { return distance; }
}
