package com.dixiyang.server.Service;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.dixiyang.server.Entity.AppUser;
import com.dixiyang.server.Entity.VO.UserVO;
import com.dixiyang.server.Mapper.AppUserMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.ai.chat.client.ChatClient;

import static org.junit.jupiter.api.Assertions.assertNotNull;

@SpringBootTest
class AITest {

    @Autowired
    private AppUserMapper appUserMapper;

    @Autowired
    private ChatClient.Builder chatClientBuilder;

    @Test
    void testChat() {
        // 构建客户端并发送一个简单的消息
        ChatClient chatClient = chatClientBuilder.build();
        String response = chatClient.prompt("你好，请回复1").call().content();

        System.out.println("AI 回复: " + response);
        assertNotNull(response);
    }

    @Test
    void updateaaa() {
        AppUser appUser= new AppUser();
        appUser.setId(2L);
        appUser.setNickname("张三");
        LambdaQueryWrapper<AppUser> queryWrapper = new LambdaQueryWrapper<>();
        queryWrapper.eq(AppUser::getId, appUser.getId());
        appUserMapper.update(appUser, queryWrapper);

    }
}