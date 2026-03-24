/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-23 13:14:02
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-23 18:17:18
 * @FilePath: \Dixiyang\dixiyang-engine\src\main\java\com\dixiyang\server\Controller\StoryNodeController.java
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
package com.dixiyang.server.Controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.StoryNode;
import com.dixiyang.server.Service.IStoryNodeService;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * <p>
 *  故事节点前端控制器
 * </p>
 *
 * @author SuZiPing
 * @since 2026-03-23
 */
@RestController
@RequestMapping("/storyNode")
@Tag(name = "故事节点管理模块")
public class StoryNodeController {
    
    @Autowired
    private IStoryNodeService storyNodeService;
    
    /**
     * 根据小说ID获取所有故事节点列表
     * GET /api/storyNode/all/{novelId}
     */
    @GetMapping("/all/{novelId}")
    public Result<List<StoryNode>> listAll(@PathVariable Long novelId) {
        LambdaQueryWrapper<StoryNode> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StoryNode::getNovelId, novelId)
               .orderByDesc(StoryNode::getCreateTime);
        List<StoryNode> nodes = storyNodeService.list(wrapper);
        return Result.success("获取成功", nodes);
    }
}
