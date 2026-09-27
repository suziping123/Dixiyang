package com.dixiyang.server.Service.My;

/**
 * @author SuZiPing
 * @version 1.0
 */
public class MyDate {
    private int year;
    private int month;
    private int day;

    public int getYear() {
        return year;
    }

    public int getMonth() {
        return month;
    }

    public int getDay() {
        return day;
    }

    public void setYear(int year) {
        this.year = year;
    }

    public void setMonth(int month) {
        this.month = month;
    }

    public void setDay(int day) {
        this.day = day;
    }

    public MyDate(int year, int month, int day) {
        this.year = year;
        this.month = month;
        this.day = day;
    }
    public MyDate() {
        this(2020, 1, 1);
    }

    public String toString() {
        return "MyDate{" +
                "year=" + year +
                ", month=" + month +
                ", day=" + day +
                '}';
    }

    public Boolean Sort(MyDate date) {
        if (this.year > date.getYear()) {
            return true;
        } else if (this.year == date.getYear()) {
            if (this.month > date.getMonth()) {
                return true;
            } else if (this.month == date.getMonth()) {
                if (this.day > date.getDay()) {
                    return true;
                }
            }
        }
        return false;
    }
}
