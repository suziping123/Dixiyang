package com.dixiyang.server.Controller;


import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.Novels;
import com.dixiyang.server.Entity.VO.NovelVO;
import com.dixiyang.server.Service.NovelService;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

/**
 * @author SuZiPing
 * @version 1.0
 */
@RestController
@RequestMapping("/novel")
@Tag( name = "小说相关模块")
public class NovelController {
    @Autowired
    private NovelService novelService;

    /**
     * 获取当前用户的小说列表
     * GET /api/novel/listall?page=1&pageSize=10
     */
    @GetMapping("/listall")
    public Result<Page<NovelVO>> list(@RequestAttribute(value = "userId", required = false) Long userId, // 改为非必填
                                      @RequestParam(defaultValue = "1") int page,
                                      @RequestParam(defaultValue = "10") int pageSize) {
        // 如果 userId 为空，可以给个默认值测试
        if (userId == null) userId = 1L;
        // 调用 Service，传入从 Token 解析出的真实 userId
        Page<NovelVO> novelPage = novelService.getUserNovelList(userId, page, pageSize);
        return Result.success("获取成功", novelPage);
    }

    @PostMapping("/create")
    public Result<NovelVO> create(@RequestAttribute(value = "userId", required = false) Long userId, // 改为非必填
                                  @RequestBody Novels novel) {
        // 如果 userId 为空，可以给个默认值测试
        if (userId == null) userId = 1L;
        // 调用 Service，传入从 Token 解析出的真实 userId
        NovelVO novelVO = novelService.createNovel(userId, novel, null);
        return Result.success("创建成功", novelVO);
    }

    @PostMapping("delete/{novelId}")
    public Result<String> delete(@RequestAttribute(value = "userId", required = false) Long userId, // 改为非必填
                                  @PathVariable Long novelId) {
        // 如果 userId 为空，可以给个默认值测试
        if (userId == null) userId = 1L;
        // 调用 Service，传入从 Token 解析出的真实 userId
        boolean result = novelService.deleteNovel(novelId, userId);
        return result ? Result.success("删除成功") : Result.error("删除失败");
    }

    @PostMapping("/update/{novelId}")
    public Result<NovelVO> update(@RequestAttribute(value = "userId", required = false) Long userId, // 改为非必填
                                  @PathVariable Long novelId,
                                  @RequestBody Novels novel) {
        // 如果 userId 为空，可以给个默认值测试
        if (userId == null) userId = 1L;
        // 调用 Service，传入从 Token 解析出的真实 userId
        NovelVO novelVO = novelService.updateNovel(userId, novelId, novel, null);
        return Result.success("更新成功", novelVO);
     }
}
