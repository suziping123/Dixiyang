/*
 * @Author: suziping123 yunzhiming123@gmail.com
 * @Date: 2026-03-23 12:59:53
 * @LastEditors: suziping123 yunzhiming123@gmail.com
 * @LastEditTime: 2026-03-23 13:06:51
 * @FilePath: \dixiyang-engine\src\main\java\com\dixiyang\server\CodeGenerator.java
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
 */
package com.dixiyang.server;
import com.baomidou.mybatisplus.generator.FastAutoGenerator;
import com.baomidou.mybatisplus.generator.config.OutputFile;
import com.baomidou.mybatisplus.generator.config.rules.NamingStrategy;
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
                // 全局配置
                .globalConfig(builder -> {
                    builder.author("SuZiPing") // 作者
                            .outputDir(System.getProperty("user.dir") + "/src/main/java") // 输出目录
                            .commentDate("yyyy-MM-dd")
                            .disableOpenDir(); // 生成后不打开文件夹
                })
                // 3. 包配置
                .packageConfig(builder -> {
                    builder.parent("com.dixiyang.server") // 父包名
                            .moduleName("") // 模块名
                            .entity("Entity") // Entity 包
                            .mapper("Mapper") // Mapper 包
                            .service("Service") // Service 包
                            .serviceImpl("Service.impl") // ServiceImpl 包
                            .controller("Controller") // Controller 包
                            .pathInfo(Collections.singletonMap(OutputFile.xml,
                                    System.getProperty("user.dir") + "/src/main/resources/mapper")); // XML 位置
                })
                // 策略配置
                .strategyConfig(builder -> {
                    builder
                            // 要生成的表（注意：排除novel表，因为已有Novels.java手动维护）
                            .addInclude("app_user",
                                    "user_config",
                                    "file",
                                    "novel_character",
                                    "novel_relation",
                                    "story_node",
                                    "timeline")
                            // 实体类策略
                            .entityBuilder()
                            .enableLombok() // 开启 Lombok
                            .enableTableFieldAnnotation() // 开启 @TableField
                            .naming(NamingStrategy.underline_to_camel) // 下划线转驼峰
                            .columnNaming(NamingStrategy.underline_to_camel)
                            .logicDeleteColumnName("is_deleted") // 逻辑删除字段
                            // Mapper 策略
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