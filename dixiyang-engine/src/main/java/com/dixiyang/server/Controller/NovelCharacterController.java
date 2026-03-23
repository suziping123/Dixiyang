package com.dixiyang.server.Controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.NovelCharacter;
import com.dixiyang.server.Service.INovelCharacterService;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * <p>
 *  前端控制器
 * </p>
 *
 * @author SuZiPing
 * @since 2026-03-23
 */
@RestController
@RequestMapping("/novelCharacter")
@Tag( name = "角色管理模块")
public class NovelCharacterController {

    @Autowired
    private INovelCharacterService novelCharacterService;

    /**
     * 根据小说ID获取角色列表
     * GET /api/novelCharacter/list/{novelId}?page=1&pageSize=10
     */
    @GetMapping("/list/{novelId}")
    public Result<Page<NovelCharacter>> list(
            @PathVariable Long novelId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int pageSize) {
        LambdaQueryWrapper<NovelCharacter> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(NovelCharacter::getNovelId, novelId)
               .orderByDesc(NovelCharacter::getCreateTime);
        Page<NovelCharacter> characterPage = novelCharacterService.page(new Page<>(page, pageSize), wrapper);
        return Result.success("获取成功", characterPage);
    }

    /**
     * 获取小说所有角色列表（不分页）
     * GET /api/novelCharacter/all/{novelId}
     */
    @GetMapping("/all/{novelId}")
    public Result<List<NovelCharacter>> listAll(@PathVariable Long novelId) {
        LambdaQueryWrapper<NovelCharacter> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(NovelCharacter::getNovelId, novelId)
               .orderByDesc(NovelCharacter::getCreateTime);
        List<NovelCharacter> characters = novelCharacterService.list(wrapper);
        return Result.success("获取成功", characters);
    }

    /**
     * 根据ID获取角色详情
     * GET /api/novelCharacter/{id}
     */
    @GetMapping("/{id}")
    public Result<NovelCharacter> getById(@PathVariable Long id) {
        NovelCharacter character = novelCharacterService.getById(id);
        return character != null ? Result.success("获取成功", character) : Result.error("角色不存在");
    }

    /**
     * 创建角色
     * POST /api/novelCharacter/create
     */
    @PostMapping("/create")
    public Result<NovelCharacter> create(@RequestBody NovelCharacter character) {
        boolean result = novelCharacterService.save(character);
        return result ? Result.success("创建成功", character) : Result.error("创建失败");
    }

    /**
     * 更新角色
     * POST /api/novelCharacter/update/{id}
     */
    @PostMapping("/update/{id}")
    public Result<NovelCharacter> update(@PathVariable Long id, @RequestBody NovelCharacter character) {
        character.setId(id);
        boolean result = novelCharacterService.updateById(character);
        return result ? Result.success("更新成功", character) : Result.error("更新失败");
    }

    /**
     * 删除角色
     * POST /api/novelCharacter/delete/{id}
     */
    @PostMapping("/delete/{id}")
    public Result<String> delete(@PathVariable Long id) {
        boolean result = novelCharacterService.removeById(id);
        return result ? Result.success("删除成功", null) : Result.error("删除失败");
    }
}
