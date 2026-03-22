package com.dixiyang.server;
import com.baomidou.mybatisplus.generator.FastAutoGenerator;
import com.baomidou.mybatisplus.generator.config.OutputFile;
import com.baomidou.mybatisplus.generator.engine.VelocityTemplateEngine;

import java.util.Collections;
/**
 * @author SuZiPing
 * @version 1.0
 */

public class CodeGenerator {
    public static void main(String[] args) {
        // 1. 数据库配置（改成你自己的）
        String url = "jdbc:mysql://localhost:3306/dixiyang";
        String username = "root";
        String password = "123456";

        // 2. 全局配置
        FastAutoGenerator.create(url, username, password)
                // 全局配置（fileOverride 废弃 → 用 disableOpenDir() + 全局覆盖逻辑）
                .globalConfig(builder -> {
                    builder.author("SuZiPing") // 作者
                            .outputDir(System.getProperty("user.dir") + "/src/main/java") // 输出目录
                            .enableSwagger() // 开启 Swagger 注解（可选）
                            .commentDate("yyyy-MM-dd")
                            .disableOpenDir(); // 生成后不打开文件夹（替代 fileOverride 的辅助优化）
                    // 关键：3.5.x 版本的「覆盖已生成文件」是默认开启的！不用手动配置
                })
                // 3. 包配置
                .packageConfig(builder -> {
                    builder.parent("com.dixiyang.server") // 父包名
                            .moduleName("") // 模块名（你没有就空着）
                            .entity("Entity") // Entity 包
                            .mapper("Mapper") // Mapper 包
                            .service("Service") // Service 包
                            .serviceImpl("Service.impl") // Serviceimpl 包
                            .controller("Controller") // Controller 包
                            .pathInfo(Collections.singletonMap(OutputFile.xml,
                                    System.getProperty("user.dir") + "/src/main/resources/mapper")); // XML 位置
                })
                // 策略配置（enableMapperAnnotation 废弃 → 用 mapperAnnotation()）
                .strategyConfig(builder -> {
                    builder
                            // 要生成的表（可以写多个，用逗号分隔）
                            .addInclude("app_user",
                                    "novels",
                                    "user_config",
                                    "file",
                                    "novel_character",
                                    "novel_relation",
                                    "story_node",
                                    "timeline")
                            // 实体类策略
                            .entityBuilder()
                            .enableLombok() // 开启 @Data
                            .enableTableFieldAnnotation() // 开启 @TableField
                            .logicDeleteColumnName("is_deleted") // 逻辑删除字段（如果有）
                            // Mapper 策略（核心修正：enableMapperAnnotation → mapperAnnotation()）
                            .mapperBuilder()
                            .mapperAnnotation(org.apache.ibatis.annotations.Mapper.class) // 自动加 @Mapper
                            // Controller 策略
                            .controllerBuilder()
                            .enableRestStyle(); // 开启 @RestController
                })
                // 5. 使用 Velocity 模板引擎
                .templateEngine(new VelocityTemplateEngine())
                .execute();
    }
}