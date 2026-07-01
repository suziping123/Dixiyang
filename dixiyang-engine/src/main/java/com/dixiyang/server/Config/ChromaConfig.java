package com.dixiyang.server.Config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Data
@Configuration
@ConfigurationProperties(prefix = "app.chromadb")
public class ChromaConfig {
    private String host = "[::1]";
    private int port = 8000;
    private String collectionName = "dixiyang_knowledge";

    public String getBaseUrl() {
        return "http://" + host + ":" + port;
    }
}
