public abstract class User {
    private static int counter = 1;
    protected int id;
    protected String name, password, gender;
    protected int age;

    public User(String name, String password, int age, String gender) {
        this.id = counter++;
        this.name = name;
        this.password = password;
        this.age = age;
        this.gender = gender;
    }

    public int getId() { return id; }
    public String getName() { return name; }
    public String getPassword() { return password; }

    public abstract String getRole();
}
