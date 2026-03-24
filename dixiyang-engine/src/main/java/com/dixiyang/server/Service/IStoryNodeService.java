/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-23 13:14:02
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-23 18:08:40
 * @FilePath: \Dixiyang\dixiyang-engine\src\main\java\com\dixiyang\server\Service\IStoryNodeService.java
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
package com.dixiyang.server.Service;

import com.dixiyang.server.Entity.StoryNode;
import com.dixiyang.server.Mapper.StoryNodeMapper;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.baomidou.mybatisplus.extension.service.IService;
import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;

/**
 * <p>
 *  服务类
 * </p>
 *
 * @author SuZiPing
 * @since 2026-03-23
 */
public interface IStoryNodeService extends IService<StoryNode> {
    public Page<StoryNode> getNodePage(Long novelId, Long timelineId, int page, int pageSize);
    public boolean createNode(StoryNode node);
    public boolean updateNode(Long id, StoryNode node);

    public boolean deleteNode(Long id);

}
