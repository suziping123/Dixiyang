package com.dixiyang.server.Service.chat.pipeline;

import java.util.List;

public record EditMemory(
    List<EditRecord> records
) {
    public record EditRecord(
        int index,
        String errorType,
        String correct,
        String original
    ) {}

    public static EditMemory empty() {
        return new EditMemory(List.of());
    }
}