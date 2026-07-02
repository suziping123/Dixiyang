package com.dixiyang.server.Service.chat.pipeline;

public interface Planner {
    ExecutionPlan plan(PlannerInput input);
}