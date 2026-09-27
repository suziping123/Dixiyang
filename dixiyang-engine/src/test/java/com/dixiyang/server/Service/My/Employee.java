package com.dixiyang.server.Service.My;

import java.util.HashSet;

/**
 * @author SuZiPing
 * @version 1.0
 */
public class Employee {
    public static void main(String[] args) {
        HashSet<Employee> set = new HashSet<>();
        set.add(new Employee("张三", 18));
        set.add(new Employee("张三", 18));
        System.out.println(set.size());

    }
    private String name;
    private int age;
//    只写 hashCode 而不重写 equals：
//    落到数组中同一个桶里。此时，HashSet 会发现这里已经有元素了，于是调用 equals 来确认是不是真的重复。
//    HashSet 认为它们只是恰好哈希值碰撞了，但内容不同，于是会在同一个桶里通过链表或红黑树把它们都存下来。
//    由于没有重写 equals，它会调用 Object 默认的 equals（即比较 == 内存地址）。
//    @Override
//    public boolean equals(Object obj) {
//        if (obj == null || getClass() != obj.getClass()) {
//            return false;
//        }
//        if (this.age == ((Employee) obj).age && this.name.equals(((Employee) obj).name)) {
//            return true;
//        } else {
//            return false;
//        }
//    }
    Employee(String name, int age) {
        this.name = name;
        this.age = age;
    }

    @Override
    public int hashCode() {
        int result = name != null ? name.hashCode() : 0;
        result = 31 * result + age; // 引入 31
        return result;
    }
}
