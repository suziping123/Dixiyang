package com.dixiyang.server.Controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.Timeline;
import com.dixiyang.server.Service.ITimelineService;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * <p>
 *  时间线控制器
 * </p>
 *
 * @author SuZiPing
 * @since 2026-03-23
 */
@RestController
@RequestMapping("/timeline")
@Tag(name = "时间线管理模块")
public class TimelineController {

    @Autowired
    private ITimelineService timelineService;

    /**
     * 根据小说ID获取时间线列表（分页）
     * GET /api/timeline/list/{novelId}?page=1&pageSize=10
     */
    @GetMapping("/list/{novelId}")
    public Result<Page<Timeline>> list(
            @PathVariable Long novelId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int pageSize) {
        LambdaQueryWrapper<Timeline> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Timeline::getNovelId, novelId)
               .orderByAsc(Timeline::getCreateTime);
        Page<Timeline> timelinePage = timelineService.page(new Page<>(page, pageSize), wrapper);
        return Result.success("获取成功", timelinePage);
    }

    /**
     * 获取小说所有时间线列表（不分页）
     * GET /api/timeline/all/{novelId}
     */
    @GetMapping("/all/{novelId}")
    public Result<List<Timeline>> listAll(@PathVariable Long novelId) {
        LambdaQueryWrapper<Timeline> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Timeline::getNovelId, novelId)
               .orderByAsc(Timeline::getCreateTime);
        List<Timeline> timelines = timelineService.list(wrapper);
        return Result.success("获取成功", timelines);
    }

    /**
     * 根据ID获取时间线详情
     * GET /api/timeline/{id}
     */
    @GetMapping("/{id}")
    public Result<Timeline> getById(@PathVariable Long id) {
        Timeline timeline = timelineService.getById(id);
        return timeline != null ? Result.success("获取成功", timeline) : Result.error("时间线不存在");
    }

    /**
     * 创建时间线
     * POST /api/timeline/create
     */
    @PostMapping("/create")
    public Result<Timeline> create(@RequestBody Timeline timeline) {
        boolean result = timelineService.save(timeline);
        return result ? Result.success("创建成功", timeline) : Result.error("创建失败");
    }

    /**
     * 更新时间线
     * POST /api/timeline/update/{id}
     */
    @PostMapping("/update/{id}")
    public Result<Timeline> update(@PathVariable Long id, @RequestBody Timeline timeline) {
        timeline.setId(id);
        boolean result = timelineService.updateById(timeline);
        return result ? Result.success("更新成功", timeline) : Result.error("更新失败");
    }

    /**
     * 删除时间线
     * POST /api/timeline/delete/{id}
     */
    @PostMapping("/delete/{id}")
    public Result<String> delete(@PathVariable Long id) {
        boolean result = timelineService.removeById(id);
        return result ? Result.success("删除成功", null) : Result.error("删除失败");
    }
}
