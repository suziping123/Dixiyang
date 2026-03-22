package com.dixiyang.server.Mapper;


import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.dixiyang.server.Entity.AppUser;
import org.apache.ibatis.annotations.Mapper;

/**
 * @author SuZiPing
 * @version 1.0
 */



@Mapper // Spring 这是一个 Mapper 接口
public interface AppUserMapper extends BaseMapper<AppUser> {
    // BaseMapper 已经写好了 insert, delete, selectById 等所有方法

    // 如果一定要用资源文件下的 XML 里的自定义查询，才可以在这里写一行声明：
    // AppUser getByUsername(String username);
}