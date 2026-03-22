package com.dixiyang.server.Common;
//前后端通信的协议，Vue 3 拿报错信息。
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * @author SuZiPing
 * @version 1.0
 */
@Data
@AllArgsConstructor
@NoArgsConstructor
public class Result<T> {
    private Integer code; //200成功，500失败，以后还有更多
    private String msg;   //提示信息
    private T data;       //数据主体（比如用户信息、Token等）
    // 成功时候的静态方法
    public static <T> Result<T> success(T data) {
        System.out.println("success");
        return new Result<T>(200, "操作成功", data);
    }
    // 支持自定义 msg，用于返回“小说创建成功”
    public static <T> Result<T> success(String msg, T data) {
        return new Result<T>(200, msg, data);
    }
    //失败时的静态方法
    public static <T> Result<T> error(String msg) {
        System.out.println("error");
        return new Result<T>(500, msg, null);
    }
}
