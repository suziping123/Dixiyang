package com.dixiyang.server.Controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.dixiyang.server.Common.Result;
import com.dixiyang.server.Entity.Novels;
import com.dixiyang.server.Entity.UserConfig;
import com.dixiyang.server.Mapper.NovelMapper;
import com.dixiyang.server.Mapper.UserConfigMapper;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Set;
import java.util.UUID;

@RestController
@RequestMapping("/upload")
@Tag(name = "文件上传模块")
public class FileController {

    private static final Logger log = LoggerFactory.getLogger(FileController.class);

    private static final String COVERS_DIR = "/home/lijiajia/项目/Dixiyang/uploads/covers";
    private static final String BACKGROUNDS_DIR = "/home/lijiajia/项目/Dixiyang/uploads/backgrounds";

    private static final Set<String> COVER_TYPES = Set.of("image/jpeg", "image/png", "image/webp", "image/gif");
    private static final Set<String> BG_TYPES = Set.of("image/jpeg", "image/png", "image/webp");

    @Autowired
    private NovelMapper novelMapper;
    @Autowired
    private UserConfigMapper userConfigMapper;

    @PostMapping("/novel-cover")
    public Result<String> uploadNovelCover(@RequestParam("file") MultipartFile file) {
        return doUpload(file, COVERS_DIR, "covers", COVER_TYPES, 10 * 1024 * 1024);
    }

    /**
     * 删除封面：删物理文件 + 清数据库 cover_url
     */
    @DeleteMapping("/novel-cover")
    public Result<Void> deleteNovelCover(@RequestParam("url") String url,
                                          @RequestParam("novelId") Long novelId) {
        Result<Void> fileResult = doDelete(url, COVERS_DIR);
        if (fileResult.getCode() != 200) return fileResult;

        // 清数据库引用
        Novels novel = novelMapper.selectById(novelId);
        if (novel != null && url.equals(novel.getCoverUrl())) {
            novel.setCoverUrl(null);
            novelMapper.updateById(novel);
        }
        return Result.success(null);
    }

    @PostMapping("/background")
    public Result<String> uploadBackground(@RequestParam("file") MultipartFile file) {
        return doUpload(file, BACKGROUNDS_DIR, "backgrounds", BG_TYPES, 10 * 1024 * 1024);
    }

    /**
     * 删除背景：删物理文件 + 清 user_config.custom_bgs 中对应项
     */
    @DeleteMapping("/background")
    public Result<Void> deleteBackground(@RequestParam("url") String url,
                                          @RequestParam("userId") Long userId) {
        Result<Void> fileResult = doDelete(url, BACKGROUNDS_DIR);
        if (fileResult.getCode() != 200) return fileResult;

        // 清数据库引用
        UserConfig config = userConfigMapper.selectOne(
                new LambdaQueryWrapper<UserConfig>().eq(UserConfig::getUserId, userId));
        if (config != null && config.getCustomBgs() != null) {
            String updated = config.getCustomBgs().replaceAll(
                    "\\{\"id\":\"[^\"]*\",\"url\":\"" + url.replace("/", "\\/") + "\",\"label\":\"[^\"]*\"\\},?",
                    "");
            if (updated.isEmpty()) updated = null;
            config.setCustomBgs(updated);
            userConfigMapper.updateById(config);
        }
        return Result.success(null);
    }

    private Result<String> doUpload(MultipartFile file, String dir, String urlPrefix,
                                     Set<String> allowedTypes, long maxSize) {
        if (file.isEmpty()) return Result.error("文件不能为空");

        String contentType = file.getContentType();
        if (contentType == null || !allowedTypes.contains(contentType)) {
            return Result.error("不支持的文件格式");
        }
        if (file.getSize() > maxSize) {
            return Result.error("文件大小超过限制");
        }

        try {
            Path uploadPath = Paths.get(dir);
            Files.createDirectories(uploadPath);

            String ext = switch (contentType) {
                case "image/jpeg" -> ".jpg";
                case "image/png" -> ".png";
                case "image/webp" -> ".webp";
                case "image/gif" -> ".gif";
                default -> ".bin";
            };

            String filename = UUID.randomUUID().toString().replace("-", "") + ext;
            file.transferTo(uploadPath.resolve(filename).toFile());

            String url = "/api/uploads/" + urlPrefix + "/" + filename;
            log.info("上传文件: {}", filename);
            return Result.success("上传成功", url);
        } catch (IOException e) {
            log.error("上传失败", e);
            return Result.error("上传失败: " + e.getMessage());
        }
    }

    private Result<Void> doDelete(String url, String dir) {
        if (url == null || url.isBlank()) return Result.error("URL不能为空");

        String prefix = "/api/uploads/";
        if (!url.startsWith(prefix)) return Result.error("无法删除非本系统文件");

        try {
            String relative = url.substring(prefix.length());
            Path filePath = Paths.get(dir, relative.substring(relative.indexOf('/') + 1));
            boolean deleted = Files.deleteIfExists(filePath);
            if (deleted) log.info("删除文件: {}", filePath.getFileName());
            return Result.success(null);
        } catch (IOException e) {
            log.error("删除失败", e);
            return Result.error("删除失败: " + e.getMessage());
        }
    }

    /** 供其他 Service 调用：根据 URL 删除物理文件（不改数据库，由调用方负责） */
    public static void deleteFileByUrl(String url) {
        if (url == null || !url.startsWith("/api/uploads/")) return;

        String relative = url.substring("/api/uploads/".length());
        String dir = relative.startsWith("covers/") ? COVERS_DIR : BACKGROUNDS_DIR;
        String filename = relative.substring(relative.indexOf('/') + 1);

        try {
            boolean deleted = Files.deleteIfExists(Paths.get(dir, filename));
            if (deleted) log.info("级联删除: {}", filename);
        } catch (IOException e) {
            log.warn("删除失败: {}", url, e);
        }
    }
}
