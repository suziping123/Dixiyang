package com.dixiyang.server.Controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
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
     * 根据小说ID获取所有故事节点列表（不分页）
     * GET /api/storyNode/all/{novelId}
     */
    @GetMapping("/all/{novelId}")
    public Result<List<StoryNode>> listAll(@PathVariable Long novelId) {
        LambdaQueryWrapper<StoryNode> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StoryNode::getNovelId, novelId)
               .orderByAsc(StoryNode::getEventDate);
        List<StoryNode> nodes = storyNodeService.list(wrapper);
        return Result.success("获取成功", nodes);
    }

    /**
     * 根据小说ID获取故事节点列表（分页）
     * GET /api/storyNode/list/{novelId}?page=1&pageSize=10
     */
    @GetMapping("/list/{novelId}")
    public Result<Page<StoryNode>> list(
            @PathVariable Long novelId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int pageSize) {
        LambdaQueryWrapper<StoryNode> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StoryNode::getNovelId, novelId)
               .orderByAsc(StoryNode::getEventDate);
        Page<StoryNode> nodePage = storyNodeService.page(new Page<>(page, pageSize), wrapper);
        return Result.success("获取成功", nodePage);
    }

    /**
     * 根据时间线ID获取故事节点列表
     * GET /api/storyNode/timeline/{timelineId}
     */
    @GetMapping("/timeline/{timelineId}")
    public Result<List<StoryNode>> listByTimeline(@PathVariable Long timelineId) {
        LambdaQueryWrapper<StoryNode> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StoryNode::getTimelineId, timelineId)
               .orderByAsc(StoryNode::getEventDate);
        List<StoryNode> nodes = storyNodeService.list(wrapper);
        return Result.success("获取成功", nodes);
    }

    /**
     * 根据ID获取故事节点详情
     * GET /api/storyNode/{id}
     */
    @GetMapping("/{id}")
    public Result<StoryNode> getById(@PathVariable Long id) {
        StoryNode node = storyNodeService.getById(id);
        return node != null ? Result.success("获取成功", node) : Result.error("节点不存在");
    }

    /**
     * 创建故事节点
     * POST /api/storyNode/create
     */
    @PostMapping("/create")
    public Result<StoryNode> create(@RequestBody StoryNode node) {
        boolean result = storyNodeService.save(node);
        return result ? Result.success("创建成功", node) : Result.error("创建失败");
    }

    /**
     * 更新故事节点
     * POST /api/storyNode/update/{id}
     */
    @PostMapping("/update/{id}")
    public Result<StoryNode> update(@PathVariable Long id, @RequestBody StoryNode node) {
        node.setId(id);
        boolean result = storyNodeService.updateById(node);
        return result ? Result.success("更新成功", node) : Result.error("更新失败");
    }

    /**
     * 删除故事节点
     * POST /api/storyNode/delete/{id}
     */
    @PostMapping("/delete/{id}")
    public Result<String> delete(@PathVariable Long id) {
        boolean result = storyNodeService.removeById(id);
        return result ? Result.success("删除成功", null) : Result.error("删除失败");
    }
}
