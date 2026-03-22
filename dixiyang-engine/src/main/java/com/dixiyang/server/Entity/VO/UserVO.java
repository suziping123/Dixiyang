package com.dixiyang.server.Entity.VO;

import lombok.Data;

/**
 * @author SuZiPing
 * @version 1.0
 */
@Data
public class UserVO {
    private Long id;
    private String username;
    private String nickname;
    private String email;
    // 绝对不写 password 和 createTime，这样前端永远看不见这两个字段
}
