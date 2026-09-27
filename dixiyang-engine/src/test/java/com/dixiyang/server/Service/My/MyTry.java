/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-24 19:04:53
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-25 17:09:48
 * @FilePath: \Dixiyang\dixiyang-engine\src\test\java\com\dixiyang\MyTry.java
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
package com.dixiyang.server.Service.My;

import java.util.Scanner;

import org.checkerframework.checker.units.qual.s;

public class MyTry {
    public static void main(String[] args) {
        // recursion();
        String str_parse = "123";
        // 字符串转整数1
        // Integer i = Integer.parseInt(str_parse);
        // // 字符串转整数2
        // Integer i2 = new Integer(str_parse);
        // System.out.println(i);
        // System.out.println(i2);

        Integer m = Integer.valueOf(1);
        Integer n = Integer.valueOf(1);
        m = 2;
        System.out.println(m);
        System.out.println(m == n);
        

        String name = "手机";
        String price = "999999999999.99999999";
        int index = price.indexOf(".");
        StringBuffer sb = new StringBuffer(price);
        // if ((int)(index / 3) >= 1) {

        //     for (int i = 1; i <= (int)(index / 3); i++) {

        //         sb.insert(index - i * 3, ",");

        //     }

        // }
        for (int i = index - 3; i > 0; i -= 3) {
            sb.insert(i, ",");
        }
        System.out.println("名称\t\t价格");
        System.out.println(name+"\t\t"+sb.toString());
    }

    public static void recursion(){
        Scanner sc = new Scanner(System.in);
        
        // while( true ){
        //     try {
        //         System.out.println("请输入数字：");
        //         int i = sc.nextInt();
        //         System.out.println("你输入的数字是：" + i);
        //         break;
        //     } catch(Exception e) {
        //         System.out.println("输入错误，请输入整数");
        //     } finally {
        //         System.out.println("程序继续");
        //     }
            
        // }
        // sc.close();
        // 上面是我写的，下面是韩老师写的
        String input = "";
        while(true) { 
            System.out.println("请输入：");
            input = sc.nextLine();
            try {
                int i = Integer.parseInt(input);
                System.out.println("你输入的数字是：" + i);
                break;
            } catch(Exception e) {
                System.out.println("输入错误，请输入整数");
            }
        }
        System.out.println("你输入的值是：" + input);
        sc.close();
    }
    
}
