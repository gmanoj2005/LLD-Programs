public class Admin extends User {
    public Admin(String name, String password, int age, String gender) {
        super(name, password, age, gender);
    }

    @Override
    public String getRole() { return "Admin"; }
}
