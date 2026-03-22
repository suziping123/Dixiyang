package com.dixiyang.server.Service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.exceptions.MybatisPlusException;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.Novels;
import com.dixiyang.server.Entity.VO.NovelVO;
import com.dixiyang.server.Mapper.NovelMapper;
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
        if (coverUrl != null) existing.setCoverUrl(coverUrl);
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
    @Transactional // 建议加上事务，虽然是单条删除，但养成习惯比较好
    public boolean deleteNovel(Long novelId, Long userId) {
        // 直接构造删除条件：id 匹配 且 userId 匹配
        LambdaQueryWrapper<Novels> queryWrapper = new LambdaQueryWrapper<Novels>()
                .eq(Novels::getId, novelId)     // 锁定这本小说
                .eq(Novels::getUserId, userId); // 确保是当前用户的小说

        // 执行删除
        int result = novelMapper.delete(queryWrapper);

        // 如果 result > 0 说明删除成功；如果为 0 说明条件不匹配（不存在或不属于该用户）
        return result > 0;
    }
}
