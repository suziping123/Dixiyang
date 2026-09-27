package com.dixiyang.server.Service.My;

import org.checkerframework.checker.units.qual.A;

import javax.sound.midi.Soundbank;
import java.util.*;

/**
 * @author SuZiPing
 * @version 1.0
 */
public class ListTest {
    @SuppressWarnings("all")
    public static void main(String[] args) {
        ArrayList col = new ArrayList();
//        ArrayList col = new LinkedList();
//        ArrayList col = new Vector();
//        都是集合list的实现类，底层都是数组结构，增删慢，查询快
        col.add(new Book("java", "james", 10));
        col.add(new Book("三国演义", "罗贯中", 20));
        col.add(new Book("水浒传", "兰陵笑笑生", 30));
        col.add(new Book("红楼梦", "曹雪芹", 5));
        col.add(new Book("西游记", "吴承恩", 15));

        Iterator it = col.iterator();
        while (it.hasNext()) {
            Book book = (Book) it.next();
            System.out.println(book);
        }
        List list = new ArrayList();
        for (int i = 0;i < 12;i++ ) {
            list.add(i);
        }

        System.out.printf("第五个元素%d\n", list.get(4));
        Object i = list.remove(5);
        System.out.printf("删除的元素是%d\n", i);
        list.set(6,8);
        System.out.printf("第七个元素是%d\n", list.get(6));
        Iterator it1 = list.iterator();
        while (it1.hasNext()) {
            System.out.println(it1.next());
        }

        bubble(col);
        Iterator it2 = col.iterator();
        while (it2.hasNext()) {
            System.out.println(it2.next());
        }


        List list1 = Book.generate(5);
        for (Object l1 : list1) {
            System.out.printf("%s\n", l1);
        }


    }

    public static void bubble(ArrayList BookList) {
        int size = BookList.size();
        for (int i = 0; i < size - 1; i++) {
            for (int j = 0; j <  size - 1 - i; j++) {
                Book b1 = (Book) BookList.get(j);
                Book b2 = (Book) BookList.get(j + 1);
                int p1 = b1.getPrice();
                int p2 = b2.getPrice();
                if ( p1 > p2) {
                    BookList.set(j, b2);
                    BookList.set(j + 1, b1);
                }
            }
        }
    }


}
class Book {
    private String name;
    private String author;
    private int price;
    public Book(String name, String author, int price) {
        this.name = name;
        this.author = author;
        this.price = price;
    }
    @Override
    public String toString() {
        return "name:" + name + "\t\t" +
                "author:" + author + "\t\t" +
                "price:" + price + "\t\t";
    }

    public int getPrice() {
        return price;
    }

    public static List<List<Integer>> generate(int numRows) {
        List<List<Integer>> list = new ArrayList();

        for (int i = 0; i < numRows; i++) {
            List<Integer> l1 = new ArrayList();
            for (int j = 0; j < i + 1; j++) {
                if (i < 2 || (j==0||j==i)) {
                    l1.add(1);
                } else {
                    List<Integer> before = (ArrayList) list.get(i-1);
                    Integer left = (Integer) before.get(j-1);
                    Integer right = (Integer) before.get(j);
                    l1.add(left + right);
                }
            }
            list.add(l1);
        }
        return list;
    }
    public static int[] plusOne(int[] digits) {
        ArrayList<Integer> list = new ArrayList<>();
        for (int num : digits) {
            list.add(num);
        }
        int carrry = 1;
        for (int i = digits.length - 1; i >= 0 && carrry > 0; i--) {
            int sum = digits[i] + carrry;
            list.set(i, sum % 10); // 当前位
            carrry = sum / 10; //进位高手
        }
        if (carrry > 0) {
            list.add(0, 1);
        }
        for (int i = 0; i < digits.length; i++) {
            digits[i] = (Integer) list.get(i);
        }
        return digits;
    }
}
