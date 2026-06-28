package com.dixiyang.server.Controller;

import com.dixiyang.server.Common.Result;
import io.swagger.v3.oas.annotations.tags.Tag;
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

    private static final String UPLOAD_DIR = "/home/lijiajia/项目/Dixiyang/uploads/";
    private static final Set<String> ALLOWED_TYPES = Set.of(
            "image/jpeg", "image/png", "image/webp", "image/gif"
    );
    private static final Set<String> BG_ALLOWED_TYPES = Set.of(
            "image/jpeg", "image/png", "image/webp"
    );

    @PostMapping("/novel-cover")
    public Result<String> uploadNovelCover(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) return Result.error("文件不能为空");

        String contentType = file.getContentType();
        if (contentType == null || !ALLOWED_TYPES.contains(contentType)) {
            return Result.error("仅支持 jpg/png/webp/gif 格式");
        }

        if (file.getSize() > 10 * 1024 * 1024) {
            return Result.error("文件大小不能超过10MB");
        }

        try {
            Path uploadPath = Paths.get(UPLOAD_DIR);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            // 1. 计算文件内容 MD5
            byte[] fileBytes = file.getBytes();
            String md5 = org.apache.commons.codec.digest.DigestUtils.md5Hex(fileBytes);

            // 2. 检查是否已有相同内容的文件
            Path existingFile = uploadPath.resolve(md5 + ".md5");
            if (Files.exists(existingFile)) {
                String existingUrl = Files.readString(existingFile);
                return Result.success("文件已存在，已复用之前的文件", existingUrl);
            }

            // 3. 保存文件
            String ext = switch (contentType) {
                case "image/jpeg" -> ".jpg";
                case "image/png" -> ".png";
                case "image/webp" -> ".webp";
                case "image/gif" -> ".gif";
                default -> ".bin";
            };

            String filename = UUID.randomUUID().toString().replace("-", "") + ext;
            Path filePath = uploadPath.resolve(filename);
            file.transferTo(filePath.toFile());


            // 4. 保存 MD5 → URL 映射
            String coverUrl = "/api/uploads/" + filename;
            Files.writeString(uploadPath.resolve(md5 + ".md5"), coverUrl);

            return Result.success("上传成功", coverUrl);
        } catch (IOException e) {
            return Result.error("上传失败: " + e.getMessage());
        }
    }

    @PostMapping("/background")
    public Result<String> uploadBackground(@RequestParam("file") MultipartFile file) {
        if (file.isEmpty()) return Result.error("文件不能为空");

        String contentType = file.getContentType();
        if (contentType == null || !BG_ALLOWED_TYPES.contains(contentType)) {
            return Result.error("仅支持 jpg/png/webp 格式");
        }

        if (file.getSize() > 8 * 1024 * 1024) {
            return Result.error("文件大小不能超过8MB");
        }

        try {
            Path uploadPath = Paths.get(UPLOAD_DIR);
            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            byte[] fileBytes = file.getBytes();
            String md5 = org.apache.commons.codec.digest.DigestUtils.md5Hex(fileBytes);

            Path existingFile = uploadPath.resolve(md5 + ".md5");
            if (Files.exists(existingFile)) {
                String existingUrl = Files.readString(existingFile);
                return Result.success("文件已存在，已复用之前的文件", existingUrl);
            }

            String ext = switch (contentType) {
                case "image/jpeg" -> ".jpg";
                case "image/png" -> ".png";
                case "image/webp" -> ".webp";
                default -> ".bin";
            };

            String filename = UUID.randomUUID().toString().replace("-", "") + ext;
            Path filePath = uploadPath.resolve(filename);
            file.transferTo(filePath.toFile());

            String bgUrl = "/api/uploads/" + filename;
            Files.writeString(uploadPath.resolve(md5 + ".md5"), bgUrl);

            return Result.success("上传成功", bgUrl);
        } catch (IOException e) {
            return Result.error("上传失败: " + e.getMessage());
        }
    }
}
