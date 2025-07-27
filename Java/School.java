import java.util.*;

// ----------------------
// Person (Base Class)
// ----------------------
abstract class Person {
    protected String name;
    protected int age;
    protected String id;

    public Person(String name, int age, String id) {
        this.name = name;
        this.age = age;
        this.id = id;
    }

    public String getId() {
        return id;
    }

    public abstract void showDetails();
}

// ----------------------
// Student Class
// ----------------------
class Student extends Person {
    private String grade;
    private List<String> attendance;

    public Student(String name, int age, String id, String grade) {
        super(name, age, id);
        this.grade = grade;
        this.attendance = new ArrayList<>();
    }

    public void markAttendance(String date) {
        attendance.add(date);
    }

    public void showAttendance() {
        System.out.println("📅 Attendance for " + name + ":");
        for (String date : attendance) {
            System.out.println(" - " + date);
        }
    }

    @Override
    public void showDetails() {
        System.out.println("🧑 Student ID: " + id + ", Name: " + name + ", Age: " + age + ", Grade: " + grade);
    }
}

// ----------------------
// Teacher Class
// ----------------------
class Teacher extends Person {
    private String subject;

    public Teacher(String name, int age, String id, String subject) {
        super(name, age, id);
        this.subject = subject;
    }

    @Override
    public void showDetails() {
        System.out.println("👩‍🏫 Teacher ID: " + id + ", Name: " + name + ", Age: " + age + ", Subject: " + subject);
    }
}

// ----------------------
// School Management System
// ----------------------
class SchoolSystem {
    private Map<String, Student> students;
    private Map<String, Teacher> teachers;

    public SchoolSystem() {
        students = new HashMap<>();
        teachers = new HashMap<>();
    }

    // Student operations
    public void addStudent(String name, int age, String id, String grade) {
        if (students.containsKey(id)) {
            System.out.println("❌ Student ID already exists.");
        } else {
            students.put(id, new Student(name, age, id, grade));
            System.out.println("✅ Student added successfully.");
        }
    }

    public void viewAllStudents() {
        if (students.isEmpty()) {
            System.out.println("📭 No students registered.");
            return;
        }
        for (Student s : students.values()) {
            s.showDetails();
        }
    }

    public void markAttendance(String id, String date) {
        Student student = students.get(id);
        if (student != null) {
            student.markAttendance(date);
            System.out.println("✅ Attendance marked for " + student.name);
        } else {
            System.out.println("❌ Student not found.");
        }
    }

    public void viewAttendance(String id) {
        Student student = students.get(id);
        if (student != null) {
            student.showAttendance();
        } else {
            System.out.println("❌ Student not found.");
        }
    }

    // Teacher operations
    public void addTeacher(String name, int age, String id, String subject) {
        if (teachers.containsKey(id)) {
            System.out.println("❌ Teacher ID already exists.");
        } else {
            teachers.put(id, new Teacher(name, age, id, subject));
            System.out.println("✅ Teacher added successfully.");
        }
    }

    public void viewAllTeachers() {
        if (teachers.isEmpty()) {
            System.out.println("📭 No teachers registered.");
            return;
        }
        for (Teacher t : teachers.values()) {
            t.showDetails();
        }
    }
}

// ----------------------
// Main Application
// ----------------------
public class SchoolManagementApp {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        SchoolSystem school = new SchoolSystem();

        while (true) {
            System.out.println("\n--- School Management System ---");
            System.out.println("1. Add Student");
            System.out.println("2. View All Students");
            System.out.println("3. Mark Student Attendance");
            System.out.println("4. View Student Attendance");
            System.out.println("5. Add Teacher");
            System.out.println("6. View All Teachers");
            System.out.println("7. Exit");
            System.out.print("Enter choice: ");
            String choice = sc.nextLine();

            switch (choice) {
                case "1":
                    System.out.print("Enter name: ");
                    String sname = sc.nextLine();
                    System.out.print("Enter age: ");
                    int sage = Integer.parseInt(sc.nextLine());
                    System.out.print("Enter ID: ");
                    String sid = sc.nextLine();
                    System.out.print("Enter grade: ");
                    String grade = sc.nextLine();
                    school.addStudent(sname, sage, sid, grade);
                    break;

                case "2":
                    school.viewAllStudents();
                    break;

                case "3":
                    System.out.print("Enter student ID: ");
                    String attId = sc.nextLine();
                    System.out.print("Enter date (YYYY-MM-DD): ");
                    String date = sc.nextLine();
                    school.markAttendance(attId, date);
                    break;

                case "4":
                    System.out.print("Enter student ID: ");
                    String viewId = sc.nextLine();
                    school.viewAttendance(viewId);
                    break;

                case "5":
                    System.out.print("Enter name: ");
                    String tname = sc.nextLine();
                    System.out.print("Enter age: ");
                    int tage = Integer.parseInt(sc.nextLine());
                    System.out.print("Enter ID: ");
                    String tid = sc.nextLine();
                    System.out.print("Enter subject: ");
                    String subject = sc.nextLine();
                    school.addTeacher(tname, tage, tid, subject);
                    break;

                case "6":
                    school.viewAllTeachers();
                    break;

                case "7":
                    System.out.println("👋 Exiting System...");
                    return;

                default:
                    System.out.println("⚠️ Invalid choice. Try again.");
            }
        }
    }
}
