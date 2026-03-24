/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-23 13:14:02
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-23 17:33:55
 * @FilePath: \Dixiyang\dixiyang-engine\src\main\java\com\dixiyang\server\Service\ITimelineService.java
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
package com.dixiyang.server.Service;

import com.dixiyang.server.Entity.Timeline;
import com.baomidou.mybatisplus.extension.service.IService;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import java.util.List;

/**
 * <p>
 *  服务类
 * </p>
 *
 * @author SuZiPing
 * @since 2026-03-23
 */
public interface ITimelineService extends IService<Timeline> {
    Page<Timeline> getTimelinePage(Long novelId, int page, int pageSize);
    List<Timeline> getAllTimeline(Long novelId);
    Timeline getTimelineById(Long id);
    boolean createTimeline(Timeline timeline);
    boolean updateTimeline(Long id, Timeline timeline);
    boolean deleteTimeline(Long id);
}
