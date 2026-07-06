package com.dixiyang.server;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.context.annotation.Bean;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication(exclude = {
    org.springframework.ai.autoconfigure.vectorstore.qdrant.QdrantVectorStoreAutoConfiguration.class
})
@ConfigurationPropertiesScan
@MapperScan("com.dixiyang.server.Mapper")
@EnableAsync

public class DixiyangEngineApplication {

    public static void main(String[] args) {
        SpringApplication.run(DixiyangEngineApplication.class, args);
    }
}
