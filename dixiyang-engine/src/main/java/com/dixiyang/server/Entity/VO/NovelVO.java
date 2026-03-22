package com.dixiyang.server.Entity.VO;

import com.fasterxml.jackson.annotation.JsonFormat;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;
import java.util.Date;

/**
 * @author SuZiPing
 * @version 1.0
 */


@Data
public class NovelVO {
    private Long id;
    private String title;

    @JsonProperty("pen_name") // 匹配前端示例中的 pen_name
    private String penName;

    private String description;

    @JsonProperty("cover_url")
    private String coverUrl;

    @JsonProperty("char_count") // 匹配前端示例
    private int charCount;

    @JsonProperty("node_count")
    private int nodeCount;

    @JsonProperty("relation_count")
    private int relationCount;

    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss'Z'")
    private Date createTime;

    @JsonFormat(pattern = "yyyy-MM-dd'T'HH:mm:ss'Z'")
    private Date updateTime;
}