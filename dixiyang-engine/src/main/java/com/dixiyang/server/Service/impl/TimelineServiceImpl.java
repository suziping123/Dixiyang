package com.dixiyang.server.Service.impl;

import com.dixiyang.server.Entity.Timeline;
import com.dixiyang.server.Mapper.TimelineMapper;
import com.dixiyang.server.Service.ITimelineService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import java.util.List;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;

/**
 * <p>
 *  服务实现类
 * </p>
 *
 * @author SuZiPing
 * @since 2026-03-23
 */
@Service
public class TimelineServiceImpl extends ServiceImpl<TimelineMapper, Timeline> implements ITimelineService {
    @Override
    public boolean createTimeline(Timeline timeline) {
        return saveOrUpdate(timeline);
    }
    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateTimeline(Long id, Timeline timeline) {
        try {
            timeline.setId(id);
            return this.updateById(timeline);
        } catch (Exception e) {
            log.error("更新时间线失败: {}", e);
            throw new RuntimeException("更新时间线失败: " + e.getMessage());
        }
    }
    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteTimeline(Long id) {
        try {
            return this.removeById(id);
        } catch (Exception e) {
            log.error("删除时间线失败: {}", e);
            throw new RuntimeException("删除时间线失败: " + e.getMessage());
        }
    }
    @Override
    @Transactional()
    public Timeline getTimelineById(Long id) {
        return getById(id);
    }
    @Override
    public List<Timeline> getAllTimeline(Long novelId) {
        LambdaQueryWrapper<Timeline> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Timeline::getNovelId, novelId)
                .orderByDesc(Timeline::getCreateTime);
        return this.list(wrapper);
    }
    @Override
    public Page<Timeline> getTimelinePage(Long novelId, int page, int pageSize) {
        LambdaQueryWrapper<Timeline> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(Timeline::getNovelId, novelId)
               .orderByDesc(Timeline::getCreateTime);//按创建时间降序排序
        return this.page(new Page<>(page, pageSize), wrapper);
    }
}
