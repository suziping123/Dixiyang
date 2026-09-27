package com.dixiyang.server.Service.impl;

import com.dixiyang.server.Entity.AppUser;
import com.dixiyang.server.Mapper.AppUserMapper;
import com.dixiyang.server.Service.IAppUserService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import org.springframework.stereotype.Service;

/**
 * <p>
 *  服务实现类
 * </p>
 *
 * @author SuZiPing
 * @since 2026-03-23
 */
@Service
public class AppUserServiceImpl extends ServiceImpl<AppUserMapper, AppUser> implements IAppUserService {

}
