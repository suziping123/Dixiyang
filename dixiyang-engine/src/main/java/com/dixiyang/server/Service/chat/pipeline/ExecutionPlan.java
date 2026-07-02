package com.dixiyang.server.Service.chat.pipeline;

import java.util.List;

public record ExecutionPlan(
    List<PlanStep> steps
) {
    public record PlanStep(
        int order,
        String tool,
        Tool.ToolInput input,
        String rationale
    ) {}
}