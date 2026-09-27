package com.dixiyang.server.Service;

import com.dixiyang.server.Entity.NovelCharacter;
import com.baomidou.mybatisplus.extension.service.IService;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import java.util.List;

/**
 * <p>
 *  角色服务类
 * </p>
 *
 * @author SuZiPing
 * @since 2026-03-23
 */
public interface INovelCharacterService extends IService<NovelCharacter> {

    /**
     * 根据小说ID分页获取角色列表
     */
    Page<NovelCharacter> getCharacterPage(Long novelId, int page, int pageSize);

    /**
     * 根据小说ID获取所有角色列表
     */
    List<NovelCharacter> getAllCharacters(Long novelId);

    /**
     * 创建角色
     */
    boolean createCharacter(NovelCharacter character);

    /**
     * 更新角色
     */
    boolean updateCharacter(Long id, NovelCharacter character);

    /**
     * 删除角色
     */
    boolean deleteCharacter(Long id);
}
