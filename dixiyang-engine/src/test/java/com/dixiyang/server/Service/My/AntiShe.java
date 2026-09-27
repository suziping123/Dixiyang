package com.dixiyang.server.Service.My;

import java.util.HashMap;
import java.util.Iterator;

/**
 * @author SuZiPing
 * @version 1.0
 */
public class AntiShe {
    static class Animal { } // 父类
    static class Dog extends Animal { } // 子类
    static class Student {
        public String name;

        public Student(String name) {
            this.name = name;
        }

        public Student() {
            this.name = "ljj";
        }

        public void setName(String name) {
            this.name = name;
        }
    }
    public static void main(String[] args) {
        Animal animal = new Animal(); // 创建一个父类实例
        Dog dog = new Dog(); // 创建一个子类实例

        String animalClassName = animal.getClass().getName();
        String dogClassName = dog.getClass().getName();
        try {
            Class<?> animalClass = Class.forName(animalClassName);
            if (animalClass.equals(Animal.class)) {
                System.out.println("animal 是 Animal 类型");
            } else if (animalClass.equals(Dog.class)) {
                System.out.println("animal 是 Dog 类型");
            }

            Class<?> dogClass = Class.forName(dogClassName);
            if (dogClass.equals(Animal.class)) {
                System.out.println("dog 是 Animal 类型");
            } else if (dogClass.equals(Dog.class)) {
                System.out.println("dog 是 Dog 类型");
            }
        } catch (ClassNotFoundException e) {
            e.printStackTrace();
        }

        Student student1 = new Student("jack");
        Student  student2 = new Student("rose");
        HashMap<String, Student> map = new HashMap<>();
        map.put(student1.name, student1);
        map.put(student2.name, student2);

        for (Object o :map.values()) {
            Student student = (Student) o;
            System.out.println(student.name+" "+Student.class);
        }
        Iterator iterator = map.values().iterator();
        while (iterator.hasNext()) {
            Object next =  iterator.next();
            Student student = (Student) next;
            System.out.println(student.name+" "+Student.class);
        }


    }
}
