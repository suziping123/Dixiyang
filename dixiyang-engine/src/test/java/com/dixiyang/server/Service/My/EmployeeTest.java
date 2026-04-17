package com.dixiyang.server.Service.My;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Comparator;

/**
 * @author SuZiPing
 * @version 1.0
 */
public class EmployeeTest {
    private String name;
    private int sal;
    private MyDate birthday;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getSal() {
        return sal;
    }

    public void setSal(int sal) {
        this.sal = sal;
    }

    public MyDate getBirthday() {
        return birthday;
    }

    public void setBirthday(MyDate birthday) {
        this.birthday = birthday;
    }

    public EmployeeTest(String name, int sal, MyDate birthday) {
        this.name = name;
        this.sal = sal;
        this.birthday = birthday;
    }

    public String toString() {
        return "EmployeeTest{" +
                "name='" + name + '\'' +
                ", sal=" + sal +
                ", birthday=" + birthday +
                '}';
    }

    public static void main(String[] args) {
        EmployeeTest e1 = new EmployeeTest("张三", 5000, new MyDate(1990, 5, 1));
        EmployeeTest e2 = new EmployeeTest("张三", 5000, new MyDate(2020, 5, 1));
        EmployeeTest e3 = new EmployeeTest("张三", 2000, new MyDate(1990, 5, 1));
        EmployeeTest e4 = new EmployeeTest("李思", 5000, new MyDate(1990, 5, 1));
        ArrayList<EmployeeTest> list = new ArrayList<>();
        list.add(e1);
        list.add(e2);
        list.add(e3);
        list.add(e4);
        list.sort((emp1, emp2) -> {
            try{
                if (emp1.getName().equals(emp2.getName())) {
                    return emp1.getBirthday().Sort(emp2.getBirthday()) ? -1 : 1;
                }
                return emp1.getName().compareTo(emp2.getName());
            } catch (Exception e) {
                e.printStackTrace();
                return 0;
            }
        });
        for (Object o :list) {
            EmployeeTest emp = (EmployeeTest) o;
            System.out.println(emp);
        }

    }
}
