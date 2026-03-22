package com.dixiyang.server.Mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.dixiyang.server.Entity.Novels;
import com.dixiyang.server.Entity.VO.NovelVO;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

/**
 * @author SuZiPing
 * @version 1.0
 */
@Mapper
public interface NovelMapper extends BaseMapper<Novels> {
    Page<NovelVO> selectUserNovelsWithStats(Page<NovelVO> pageParam, @Param("userId") Long userId);
}
