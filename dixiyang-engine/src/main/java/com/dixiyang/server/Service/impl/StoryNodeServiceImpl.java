package com.dixiyang.server.Service.impl;

import com.dixiyang.server.Entity.StoryNode;
import com.dixiyang.server.Mapper.StoryNodeMapper;
import com.dixiyang.server.Service.IStoryNodeService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import com.dixiyang.server.Service.EmbeddingService;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import org.springframework.transaction.annotation.Transactional;
import lombok.extern.slf4j.Slf4j;
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
public class StoryNodeServiceImpl extends ServiceImpl<StoryNodeMapper, StoryNode> implements IStoryNodeService {

    @Autowired
    private EmbeddingService embeddingService;

    @Override
    public Page<StoryNode> getNodePage(Long novelId, Long timelineId, int page, int pageSize) {
        LambdaQueryWrapper<StoryNode> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(StoryNode::getNovelId, novelId);
        if (timelineId != null) {
            wrapper.eq(StoryNode::getTimelineId, timelineId);
        }
        wrapper.orderByDesc(StoryNode::getCreateTime);
        return this.page(new Page<>(page, pageSize), wrapper);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean createNode(StoryNode node) {
        try {
            // 生成向量嵌入
            if (node.getContent() != null && !node.getContent().isEmpty()) {
                String vectorId = embeddingService.generateEmbedding(node.getContent());
                node.setVectorId(vectorId);
            }
            return this.save(node);
        } catch (Exception e) {
            log.error("创建节点失败: {}", e);
            throw new RuntimeException("创建节点失败: " + e.getMessage());
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateNode(Long id, StoryNode node) {
        try {
            node.setId(id);
            // 更新向量嵌入
            if (node.getContent() != null && !node.getContent().isEmpty()) {
                String vectorId = embeddingService.generateEmbedding(node.getContent());
                node.setVectorId(vectorId);
            }
            return this.updateById(node);
        } catch (Exception e) {
            log.error("更新节点失败: {}", e);
            throw new RuntimeException("更新节点失败: " + e.getMessage());
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteNode(Long id) {
        try {
            // 删除向量嵌入
            StoryNode node = this.getById(id);
            if (node != null && node.getVectorId() != null) {
                embeddingService.deleteEmbedding(node.getVectorId());
            }
            return this.removeById(id);
        } catch (Exception e) {
            log.error("删除节点失败: {}", e);
            throw new RuntimeException("删除节点失败: " + e.getMessage());
        }
    }
}
