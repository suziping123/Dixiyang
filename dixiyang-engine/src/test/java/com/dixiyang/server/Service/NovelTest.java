package com.dixiyang.server.Service;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.dixiyang.server.Entity.Novels;
import com.dixiyang.server.Entity.VO.NovelVO;
import com.dixiyang.server.Service.impl.NovelServiceImpl;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.junit4.SpringRunner;

import javax.management.Query;

/**
 * @author SuZiPing
 * @version 1.0
 */
@SpringBootTest
@RunWith(SpringRunner.class)
public class NovelTest {
    // 由 Spring 容器注入 NovelService 实例（而非手动 new）
    @Autowired
    private NovelService novelService;
    @Test
    public void testCreateNovel() {
        Novels novel = new Novels();
        novel.setTitle("测试小说");
        novel.setDescription("这是测试小说");
        novel.setPenName("测试作者");
        novel.setCoverUrl("https://example.com/cover.jpg");
        novel.setUserId(1L);
        NovelVO novelVO = novelService.createNovel(1L, novel, null);
        System.out.println(novelVO);
    }
    @Test
    public void testDeleteAllNovel() {
//        由于安装了 BlockAttackInnerInterceptor() 拦截器，所以这里会报错
        Novels novels = new Novels();
        novels.delete(new QueryWrapper<Novels>());
    }

}
