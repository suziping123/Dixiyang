package com.dixiyang.server.Service;

import com.dixiyang.server.Entity.Novels;
import com.dixiyang.server.Entity.VO.NovelVO;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;


/**
 * @author SuZiPing
 * @version 1.0
 */
public interface NovelService {
    /**
     * 1. 分页获取当前用户的小说列表 (带统计数据)
     * @param userId 当前登录用户ID
     * @param page 当前页码
     * @param pageSize 每页大小
     */
    Page<NovelVO> getUserNovelList(Long userId, int page , int pageSize);
    /**
     * 2. 创建新小说
     * @param userId 当前登录用户ID
     * @param novel 小说基本信息（title, penName, description）
     * @param cover 封面文件 (可选)
     */
    NovelVO createNovel(Long userId, Novels novel, String cover);
    /**
     * 3. 获取小说完整详情 (包含角色、节点、关系)
     * @param userId 用于权限检查：只有所有者可访问
     * @param novelId 小说ID
     */
    Map<String , Object> getNovelFullDetail(Long userId, Long novelId);

    /**
     * 4. 删除小说
     * @param userId 当前登录用户ID
     * @param novelId 小说ID
     */
    boolean deleteNovel(Long userId, Long novelId);
    /**
     * 5. 更新小说信息
     * @param userId 当前登录用户ID
     * @param novelId 小说ID
     * @param novel 小说信息（title, penName, description）
     * @param cover 封面文件 (可选)
     * @return 更新后的小说详情
     */
    NovelVO updateNovel(Long userId, Long novelId, Novels novel, String cover);
    
}
