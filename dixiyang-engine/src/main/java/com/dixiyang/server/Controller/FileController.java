package com.dixiyang.server.Controller;

import com.dixiyang.server.Common.Result;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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

    private static final String UPLOAD_ROOT = "/home/lijiajia/项目/Dixiyang/uploads";
    private static final String COVERS_DIR = UPLOAD_ROOT + "/covers";
    private static final String BACKGROUNDS_DIR = UPLOAD_ROOT + "/backgrounds";

    private static final Set<String> COVER_TYPES = Set.of(
            "image/jpeg", "image/png", "image/webp", "image/gif"
    );
    private static final Set<String> BG_TYPES = Set.of(
            "image/jpeg", "image/png", "image/webp"
    );

    // ==================== 封面上传 ====================

    @PostMapping("/novel-cover")
    public Result<String> uploadNovelCover(@RequestParam("file") MultipartFile file) {
        return doUpload(file, "cover", COVER_TYPES, 10 * 1024 * 1024);
    }

    @DeleteMapping("/novel-cover")
    public Result<Void> deleteNovelCover(@RequestParam("url") String url) {
        return doDelete(url, "cover");
    }

    // ==================== 背景图上传 ====================

    @PostMapping("/background")
    public Result<String> uploadBackground(@RequestParam("file") MultipartFile file) {
        return doUpload(file, "background", BG_TYPES, 10 * 1024 * 1024);
    }

    @DeleteMapping("/background")
    public Result<Void> deleteBackground(@RequestParam("url") String url) {
        return doDelete(url, "background");
    }

    // ==================== 内部方法 ====================

    private Result<String> doUpload(MultipartFile file, String type,
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
            String subDir = "cover".equals(type) ? COVERS_DIR : BACKGROUNDS_DIR;
            Path uploadPath = Paths.get(subDir);
            Files.createDirectories(uploadPath);

            byte[] fileBytes = file.getBytes();
            String md5 = org.apache.commons.codec.digest.DigestUtils.md5Hex(fileBytes);

            // MD5 去重
            Path md5File = uploadPath.resolve(md5 + ".md5");
            if (Files.exists(md5File)) {
                String existingUrl = Files.readString(md5File);
                return Result.success("文件已存在，已复用之前的文件", existingUrl);
            }

            // 生成文件名
            String ext = switch (contentType) {
                case "image/jpeg" -> ".jpg";
                case "image/png" -> ".png";
                case "image/webp" -> ".webp";
                case "image/gif" -> ".gif";
                default -> ".bin";
            };
            String filename = UUID.randomUUID().toString().replace("-", "") + ext;

            // 写入文件
            Path filePath = uploadPath.resolve(filename);
            file.transferTo(filePath.toFile());

            // 保存 MD5 映射
            String fileUrl = "/api/uploads/" + type + "s/" + filename;
            Files.writeString(md5File, fileUrl);

            log.info("上传{}成功: {}", type, filename);
            return Result.success("上传成功", fileUrl);
        } catch (IOException e) {
            log.error("上传{}失败", type, e);
            return Result.error("上传失败: " + e.getMessage());
        }
    }

    private Result<Void> doDelete(String url, String type) {
        if (url == null || url.isBlank()) {
            return Result.error("URL不能为空");
        }

        // 只允许删除本系统上传的文件
        String prefix = "/api/uploads/" + type + "s/";
        if (!url.startsWith(prefix)) {
            return Result.error("无法删除非本系统文件");
        }

        try {
            String subDir = "cover".equals(type) ? COVERS_DIR : BACKGROUNDS_DIR;
            Path uploadPath = Paths.get(subDir);

            // 从 URL 提取文件名
            String filename = url.substring(prefix.length());
            Path filePath = uploadPath.resolve(filename);

            // 删除物理文件
            boolean deleted = Files.deleteIfExists(filePath);
            if (deleted) {
                log.info("删除{}文件: {}", type, filename);
            }

            // 清理 MD5 映射文件（遍历查找指向该 URL 的 md5 文件）
            try (var stream = Files.list(uploadPath)) {
                stream.filter(p -> p.toString().endsWith(".md5"))
                      .forEach(md5File -> {
                          try {
                              String mappedUrl = Files.readString(md5File);
                              if (url.equals(mappedUrl)) {
                                  Files.deleteIfExists(md5File);
                                  log.info("清理MD5映射: {}", md5File.getFileName());
                              }
                          } catch (IOException ignored) {}
                      });
            }

            return Result.success(null);
        } catch (IOException e) {
            log.error("删除{}文件失败", type, e);
            return Result.error("删除失败: " + e.getMessage());
        }
    }

    // ==================== 工具方法（供其他 Service 调用） ====================

    /**
     * 根据 URL 删除物理文件（供 NovelServiceImpl 等调用）
     */
    public static void deleteFileByUrl(String url) {
        if (url == null || url.isBlank()) return;

        Path filePath = null;
        if (url.startsWith("/api/uploads/covers/")) {
            String filename = url.substring("/api/uploads/covers/".length());
            filePath = Paths.get(COVERS_DIR, filename);
        } else if (url.startsWith("/api/uploads/backgrounds/")) {
            String filename = url.substring("/api/uploads/backgrounds/".length());
            filePath = Paths.get(BACKGROUNDS_DIR, filename);
        }

        if (filePath != null) {
            try {
                boolean deleted = Files.deleteIfExists(filePath);
                if (deleted) {
                    log.info("级联删除文件: {}", filePath.getFileName());
                }
            } catch (IOException e) {
                log.warn("删除文件失败: {}", url, e);
            }
        }
    }
}
