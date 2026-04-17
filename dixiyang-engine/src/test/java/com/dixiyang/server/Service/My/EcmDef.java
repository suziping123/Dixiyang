package com.dixiyang.server.Service.My;

import java.util.*;

public class EcmDef {

    public static void main(String[] args) {

        int[] nums = {1, 2, 3};
        System.out.println(new Solution().subarraySum(nums, 3));
        try {
            // 第一道关卡：判断参数个数
            if (args.length != 2) {
                // 主动抛出异常，交给下面的 catch 块处理
                throw new ArrayIndexOutOfBoundsException("参数个数不对，请输入两个整数。");
            }

            // 第二道关卡：判断数据格式
            int n1 = Integer.parseInt(args[0]);
            int n2 = Integer.parseInt(args[1]);

            // 第三道关卡：计算并处理除0
            System.out.println("结果：" + cal(n1, n2));

        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("错误：你必须输入两个参数！" + e.getMessage());
        } catch (NumberFormatException e) {
            System.out.println("错误：输入的参数必须是整数！");
        } catch (ArithmeticException e) {
            System.out.println("错误：除数不能为0！");
        }
    }
    
    public static int cal(int n1, int n2) {
        return n1 / n2;
    }
}


class Solution {
    public int maxProfit(int[] prices) {
        int max = 0;
        int min = Integer.MAX_VALUE;
        for (int price : prices) {
            if (price < min) {
                min = price;
            } else if (price - min > max) {
                max = price - min;
            }
        }
        if (max == 0) {
            return 0;
        } else {
            return max - min;
        }
    }

    public boolean searchMatrix(int[][] matrix, int target) {
        // 边界处理：矩阵为空或行/列为0
        if (matrix == null || matrix.length == 0 || matrix[0].length == 0) {
            return false;
        }
        boolean flag =false;
        int m = matrix.length;
        int n = matrix[0].length;
        int left = 0;
        int right = m * n - 1;
        while (left <= right) {
            int mid = (left + right) / 2;
            int midVal = matrix[mid / n][mid % n];
            if (midVal == target) {
                flag = true;
                break;
            } else if (midVal < target) {
                left = mid + 1;
            } else {
                right = mid - 1;
            }
        }
        return flag;
    }
    public int subarraySum(int[] nums, int k) {
        int count = 0;
        Map<Integer,Integer> hashmap = new HashMap<Integer,Integer>();
        int prei = 0;
        hashmap.put(0,1);
        for (int num : nums) {
            prei += num;
            int temp = prei - k;
            if (hashmap.containsKey(temp)) {
                count += hashmap.get(temp);
            }
//            if (hashmap.containsKey(prei)) {
//                hashmap.put(prei, hashmap.get(prei) + 1);
//            } else {
//                hashmap.put(prei, 1);
//            }
//            上面的东西可以优化成下面一句话
            hashmap.put(prei,hashmap.getOrDefault(prei,0) +1);
        }
        return count;
    }

    public ListNode detectCycle(ListNode head) {
//        Set<ListNode> visited = new HashSet<>();
//        int len = 0;
//        ListNode cur = head;
//        while (cur != null) {
//            if (visited.contains(cur)) {
//                return cur;
//            }
//            visited.add(cur);
//            cur = cur.next;
//            len++;
//        }
//        return null;
        ListNode fast = head;
        ListNode slow = head;
        while (fast != null && fast.next != null) {
            fast = fast.next.next;
            slow = slow.next;
            if(fast == slow) {
                ListNode slow2 = head;
                while (slow != slow2) {
                    slow = slow.next;
                    slow2 = slow2.next;
                }
                return slow;
            }
        }
        return null;
    }

    public int findDuplicate(int[] nums) {
        int slow = 0;
        int fast = 0;
        do {
            slow = nums[slow];
            fast = nums[nums[fast]];
        } while (slow != fast);
        int slow2 = 0;
        while (slow != slow2) {
            slow = nums[slow];
            slow2 = nums[slow2];
        }
        return slow;
    }
}


//Definition for singly-linked list.
class ListNode {
    int val;
    ListNode next;
    ListNode(int x) {
        val = x;
        next = null;
    }
}