package com.dixiyang.server.Service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.exceptions.MybatisPlusException;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.Novels;
import com.dixiyang.server.Entity.StoryNode;
import com.dixiyang.server.Entity.NovelCharacter;
import com.dixiyang.server.Entity.NovelRelation;
import com.dixiyang.server.Entity.Timeline;
import com.dixiyang.server.Entity.VO.NovelVO;
import com.dixiyang.server.Mapper.NovelMapper;
import com.dixiyang.server.Mapper.StoryNodeMapper;
import com.dixiyang.server.Mapper.NovelCharacterMapper;
import com.dixiyang.server.Mapper.NovelRelationMapper;
import com.dixiyang.server.Mapper.TimelineMapper;
import com.dixiyang.server.Service.NovelService;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.dao.DuplicateKeyException;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

/**
 * @author SuZiPing
 * @version 1.0
 */
@Service//和Controller一起使用（这个东西其实和Controller一模一样）
public class NovelServiceImpl implements NovelService {
    @Autowired // 必须注入 Mapper
    private NovelMapper novelMapper;
    
    // 注入关联表Mapper，用于级联删除
    @Autowired
    private StoryNodeMapper storyNodeMapper;
    @Autowired
    private NovelCharacterMapper novelCharacterMapper;
    @Autowired
    private NovelRelationMapper novelRelationMapper;
    @Autowired
    private TimelineMapper timelineMapper;
    @Override
    public Page<NovelVO> getUserNovelList(Long userId, int page, int pageSize) {
//        创建分页对象
        Page<NovelVO> pageParam = new Page<>(page, pageSize);
//        调用Mapper层的自定义查询（需要再Mapper接口定义该方法）
//        但要在资源包内的xml文件中left join左链接实现
        return novelMapper.selectUserNovelsWithStats(pageParam, userId);
    }


    @Override
    public NovelVO createNovel(Long userId, Novels novel, String coverUrl) {
        // 1. 关键修复：先检查当前用户是否已存在相同标题的小说
        LambdaQueryWrapper<Novels> checkWrapper = new LambdaQueryWrapper<Novels>()
                .eq(Novels::getUserId, userId)  // 同一个用户
                .eq(Novels::getTitle, novel.getTitle());  // 相同标题

        Novels existNovel = novelMapper.selectOne(checkWrapper);
        if (existNovel != null) {
            // 抛出自定义异常（或返回友好提示），避免触发数据库报错
            throw new RuntimeException("当前用户已存在标题为【" + novel.getTitle() + "】的小说，请勿重复创建");
        }

        // 2. 强制设置用户ID（防止越权）
        novel.setUserId(userId);

        // 3. 设置封面URL（优化空值判断，避免NPE）
        if (StringUtils.hasText(coverUrl)) {
            novel.setCoverUrl(coverUrl.trim());
        }

        // 4. 保存小说（添加异常兜底处理）
        try {
            novelMapper.insert(novel);
        } catch (DuplicateKeyException e) {
            // 兜底：防止并发场景下的重复插入（比如两个请求同时过了上面的检查）
            throw new RuntimeException("创建失败：小说标题已存在", e);
        } catch (MybatisPlusException e) {
            throw new RuntimeException("创建小说失败：数据库操作异常", e);
        }

        // 5. 转换为VO返回
        NovelVO vo = new NovelVO();
        BeanUtils.copyProperties(novel, vo);
        vo.setCharCount(0);
        vo.setNodeCount(0);
        vo.setRelationCount(0);

        return vo;
    }

    @Override
    public Map<String, Object> getNovelFullDetail(Long userId, Long novelId) {
        return Map.of("novelId", novelId,"userId", userId,"msg","待实现");
    }

    @Override
    @Transactional
    public NovelVO updateNovel(Long userId, Long novelId, Novels novel, String coverUrl) {
        // 1. 严格权限检查
        Novels existing = novelMapper.selectOne(new LambdaQueryWrapper<Novels>()
                .eq(Novels::getId, novelId)
                .eq(Novels::getUserId, userId));

        if (existing == null) return null;

        // 2. 字段“补丁”模式：只更新前端传了的非空字段
        // 这样可以防止 description 等字段被意外置空
        if (novel.getTitle() != null) existing.setTitle(novel.getTitle());
        if (novel.getDescription() != null) existing.setDescription(novel.getDescription());
        if (novel.getPenName() != null) existing.setPenName(novel.getPenName());
        if (novel.getCoverUrl() != null) existing.setCoverUrl(novel.getCoverUrl());
        // 更新时间通常由数据库自动填充或手动设置
        // existing.setUpdateTime(LocalDateTime.now());

        // 3. 执行更新
        novelMapper.updateById(existing);

        // 4. 封装完整的 VO 返回
        NovelVO vo = new NovelVO();
        BeanUtils.copyProperties(existing, vo);

        return vo;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteNovel(Long novelId, Long userId) {
        // 先验证小说是否属于该用户
        LambdaQueryWrapper<Novels> queryWrapper = new LambdaQueryWrapper<Novels>()
                .eq(Novels::getId, novelId)
                .eq(Novels::getUserId, userId);
        Novels novel = novelMapper.selectOne(queryWrapper);
        if (novel == null) {
            return false; // 小说不存在或不属于该用户
        }
        
        // 构造删除条件（用于所有关联表）
        LambdaQueryWrapper<StoryNode> storyNodeWrapper = new LambdaQueryWrapper<StoryNode>()
                .eq(StoryNode::getNovelId, novelId);
        LambdaQueryWrapper<NovelCharacter> characterWrapper = new LambdaQueryWrapper<NovelCharacter>()
                .eq(NovelCharacter::getNovelId, novelId);
        LambdaQueryWrapper<NovelRelation> relationWrapper = new LambdaQueryWrapper<NovelRelation>()
                .eq(NovelRelation::getNovelId, novelId);
        LambdaQueryWrapper<Timeline> timelineWrapper = new LambdaQueryWrapper<Timeline>()
                .eq(Timeline::getNovelId, novelId);

        // 按依赖顺序删除：故事节点 -> 角色 -> 关系 -> 时间线 -> 小说
        storyNodeMapper.delete(storyNodeWrapper);
        novelCharacterMapper.delete(characterWrapper);
        novelRelationMapper.delete(relationWrapper);
        timelineMapper.delete(timelineWrapper);
        int result = novelMapper.delete(queryWrapper);

        return result > 0;
    }

    @Override
    public NovelVO getById(Long novelId) {
        Novels novel = novelMapper.selectById(novelId);
        if (novel == null) return null;
        NovelVO vo = new NovelVO();
        BeanUtils.copyProperties(novel, vo);
        return vo;
    }
}
