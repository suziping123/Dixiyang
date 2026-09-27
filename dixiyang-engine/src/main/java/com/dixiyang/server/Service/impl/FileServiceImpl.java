package com.dixiyang.server.Service.impl;

import com.dixiyang.server.Entity.File;
import com.dixiyang.server.Mapper.FileMapper;
import com.dixiyang.server.Service.IFileService;
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
public class FileServiceImpl extends ServiceImpl<FileMapper, File> implements IFileService {

}
