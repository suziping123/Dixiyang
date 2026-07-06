package com.dixiyang.server.Controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.NovelCharacter;
import com.dixiyang.server.Service.INovelCharacterService;
import com.dixiyang.server.Utils.StorageService;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/novelCharacter")
@Tag(name = "角色管理模块")
public class NovelCharacterController {

    private static final Logger log = LoggerFactory.getLogger(NovelCharacterController.class);
    private static final String SUBDIR = "character";
    private final ObjectMapper jsonMapper = new ObjectMapper();

    @Autowired
    private INovelCharacterService novelCharacterService;

    @Autowired
    private StorageService storageService;

    /**
     * 根据小说ID获取角色列表
     */
    @GetMapping("/list/{novelId}")
    public Result<Map<String, Object>> list(
            @PathVariable Long novelId,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "10") int pageSize) {
        LambdaQueryWrapper<NovelCharacter> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(NovelCharacter::getNovelId, novelId)
               .orderByDesc(NovelCharacter::getCreateTime);
        Page<NovelCharacter> characterPage = novelCharacterService.page(new Page<>(page, pageSize), wrapper);
        // 转换 extra 为实际 JSON 数据
        List<Map<String, Object>> records = characterPage.getRecords().stream()
                .map(this::toVO)
                .toList();
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("records", records);
        result.put("total", characterPage.getTotal());
        result.put("size", characterPage.getSize());
        result.put("current", characterPage.getCurrent());
        result.put("pages", characterPage.getPages());
        return Result.success("获取成功", result);
    }

    /**
     * 获取小说所有角色列表
     */
    @GetMapping("/all/{novelId}")
    public Result<List<Map<String, Object>>> listAll(@PathVariable Long novelId) {
        LambdaQueryWrapper<NovelCharacter> wrapper = new LambdaQueryWrapper<>();
        wrapper.eq(NovelCharacter::getNovelId, novelId)
               .orderByDesc(NovelCharacter::getCreateTime);
        List<NovelCharacter> characters = novelCharacterService.list(wrapper);
        List<Map<String, Object>> voList = characters.stream().map(this::toVO).toList();
        return Result.success("获取成功", voList);
    }

    /**
     * 根据ID获取角色详情
     */
    @GetMapping("/{id}")
    public Result<Map<String, Object>> getById(@PathVariable Long id) {
        NovelCharacter character = novelCharacterService.getById(id);
        return character != null ? Result.success("获取成功", toVO(character)) : Result.error("角色不存在");
    }

    /**
     * 创建角色
     */
    @PostMapping("/create")
    public Result<Map<String, Object>> create(@RequestBody NovelCharacter character) {
        // extra 先不存，等 save 后再存文件
        String rawExtra = character.getExtra();
        character.setExtra(null);
        boolean result = novelCharacterService.save(character);
        if (result && rawExtra != null && !rawExtra.isBlank()) {
            String ref = storageService.saveJsonString(SUBDIR, character.getId(), rawExtra);
            character.setExtra(ref);
            novelCharacterService.updateById(character);
        }
        return result ? Result.success("创建成功", toVO(character)) : Result.error("创建失败");
    }

    /**
     * 更新角色
     */
    @PostMapping("/update/{id}")
    public Result<Map<String, Object>> update(@PathVariable Long id, @RequestBody NovelCharacter character) {
        character.setId(id);
        // 处理 extra：删除旧文件，存新文件
        if (character.getExtra() != null) {
            NovelCharacter old = novelCharacterService.getById(id);
            if (old != null && old.getExtra() != null) {
                storageService.deleteJson(old.getExtra());
            }
            String ref = storageService.saveJsonString(SUBDIR, id, character.getExtra());
            character.setExtra(ref);
        }
        boolean result = novelCharacterService.updateById(character);
        return result ? Result.success("更新成功", toVO(character)) : Result.error("更新失败");
    }

    /**
     * 删除角色
     */
    @PostMapping("/delete/{id}")
    public Result<String> delete(@PathVariable Long id) {
        NovelCharacter old = novelCharacterService.getById(id);
        if (old != null && old.getExtra() != null) {
            storageService.deleteJson(old.getExtra());
        }
        boolean result = novelCharacterService.removeById(id);
        return result ? Result.success("删除成功", null) : Result.error("删除失败");
    }

    /**
     * 从对话内容中提取角色设定
     */
    @PostMapping("/extractSettings")
    public Result<Map<String, Object>> extractSettings(@RequestBody Map<String, String> body) {
        String conversation = body.getOrDefault("conversation", "").trim();
        if (conversation.isEmpty()) {
            return Result.error("对话内容不能为空");
        }
        // 注意：extractSettings 需要调用 LLM，这里由 Python 端提供
        // Java 端作为代理，调用 Python 端的接口
        // 或者在前端直接调用 Python 端
        return Result.error("请使用 Python 端的 /api/novelCharacter/extractSettings");
    }

    /**
     * 保存角色设定到 extra 字段
     */
    @PostMapping("/saveSettings")
    public Result<Map<String, Object>> saveSettings(@RequestBody Map<String, Object> body) {
        Object charIdObj = body.get("characterId");
        Object settingsObj = body.get("settings");
        if (charIdObj == null || settingsObj == null) {
            return Result.error("参数不完整");
        }
        Long charId = Long.valueOf(charIdObj.toString());

        @SuppressWarnings("unchecked")
        Map<String, Object> settings = (Map<String, Object>) settingsObj;

        // 加载已有设定并合并（不覆盖）
        NovelCharacter character = novelCharacterService.getById(charId);
        if (character == null) return Result.error("角色不存在");

        @SuppressWarnings("unchecked")
        Map<String, Object> existing = (Map<String, Object>) storageService.loadJson(SUBDIR, character.getId(), character.getExtra());
        if (existing == null) {
            existing = new LinkedHashMap<>();
        }
        // 合并：已有字段保留，新字段追加，同名字段用新值覆盖
        existing.putAll(settings);

        String ref = storageService.saveJson(SUBDIR, charId, existing);
        character.setExtra(ref);
        novelCharacterService.updateById(character);
        return Result.success("设定保存成功", toVO(character));
    }

    /**
     * NovelCharacter → VO（extra 从文件加载）
     */
    private Map<String, Object> toVO(NovelCharacter c) {
        Map<String, Object> vo = new LinkedHashMap<>();
        vo.put("id", c.getId());
        vo.put("novelId", c.getNovelId());
        vo.put("name", c.getName());
        vo.put("gender", c.getGender());
        vo.put("age", c.getAge());
        vo.put("appearance", c.getAppearance());
        vo.put("background", c.getBackground());
        vo.put("personality", c.getPersonality());
        vo.put("extra", storageService.loadJson(SUBDIR, c.getId(), c.getExtra()));
        vo.put("createTime", c.getCreateTime());
        return vo;
    }
}
