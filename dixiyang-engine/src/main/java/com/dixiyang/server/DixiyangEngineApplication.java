package com.dixiyang.server;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;
import org.springframework.ai.vectorstore.VectorStore;

@SpringBootApplication(exclude = {
    org.springframework.ai.autoconfigure.vectorstore.qdrant.QdrantVectorStoreAutoConfiguration.class
})
@MapperScan("com.dixiyang.server.Mapper") // 这个注解告诉 Spring Boot 扫描 Mapper 接口所在的包

public class DixiyangEngineApplication {

    public static void main(String[] args) {
        SpringApplication.run(DixiyangEngineApplication.class, args);
    }
}
