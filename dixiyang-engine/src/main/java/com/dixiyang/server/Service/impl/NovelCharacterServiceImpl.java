package com.dixiyang.server.Service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.dixiyang.server.Entity.NovelCharacter;
import com.dixiyang.server.Mapper.NovelCharacterMapper;
import com.dixiyang.server.Service.INovelCharacterService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;

/**
 * <p>
 *  角色服务实现类
 * </p>
 *
 * @author SuZiPing
 * @since 2026-03-23
 */
@Service
public class NovelCharacterServiceImpl extends ServiceImpl<NovelCharacterMapper, NovelCharacter> implements INovelCharacterService {

    private static final Logger log = LoggerFactory.getLogger(NovelCharacterServiceImpl.class);

    @Override
    public Page<NovelCharacter> getCharacterPage(Long novelId, int page, int pageSize) {
        LambdaQueryWrapper<NovelCharacter> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(NovelCharacter::getNovelId, novelId)
               .orderByDesc(NovelCharacter::getCreateTime);
        return this.page(new Page<>(page, pageSize), wrapper);
    }

    @Override
    public List<NovelCharacter> getAllCharacters(Long novelId) {
        LambdaQueryWrapper<NovelCharacter> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(NovelCharacter::getNovelId, novelId)
               .orderByDesc(NovelCharacter::getCreateTime);
        return this.list(wrapper);
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean createCharacter(NovelCharacter character) {
        try {
            // 手动设置创建时间（解决自动填充问题）
            if (character.getCreateTime() == null) {
                character.setCreateTime(LocalDateTime.now());
            }
            return this.save(character);
        } catch (Exception e) {
            log.error("创建角色失败: {}", e.getMessage(), e);
            throw new RuntimeException("创建角色失败: " + e.getMessage());
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean updateCharacter(Long id, NovelCharacter character) {
        try {
            character.setId(id);
            return this.updateById(character);
        } catch (Exception e) {
            log.error("更新角色失败: {}", e.getMessage(), e);
            throw new RuntimeException("更新角色失败: " + e.getMessage());
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean deleteCharacter(Long id) {
        try {
            return this.removeById(id);
        } catch (Exception e) {
            log.error("删除角色失败: {}", e.getMessage(), e);
            throw new RuntimeException("删除角色失败: " + e.getMessage());
        }
    }
}
