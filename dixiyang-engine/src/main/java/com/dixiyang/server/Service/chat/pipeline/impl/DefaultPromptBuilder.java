package com.dixiyang.server.Service.chat.pipeline.impl;

import com.dixiyang.server.Service.chat.pipeline.EditMemory;
import com.dixiyang.server.Service.chat.pipeline.ExecutionProfile;
import com.dixiyang.server.Service.chat.pipeline.PromptBuilder;
import com.dixiyang.server.Service.chat.pipeline.PromptContext;
import com.dixiyang.server.Service.chat.pipeline.Tool;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Component
@Slf4j
public class DefaultPromptBuilder implements PromptBuilder {

    private static final Map<ExecutionProfile, String> SYSTEM_PROMPTS = Map.of(
        ExecutionProfile.FAST, """
            你是小说创作助手。你具备以下能力：
            - 创作：按设定写剧情/对话/描写
            - 讨论：回答关于角色、世界观、大纲的设定问题
            - 分析：分析角色性格、剧情逻辑、世界观一致性
            
            严格遵循【固定设定】与【对话历史】。不自造设定，不违背前文。
            直接给出回答，简练、沉浸感强。
            """,
        ExecutionProfile.BALANCED, """
            你是小说创作助手。你具备以下能力：
            - 创作：按设定写剧情/对话/描写/续写
            - 讨论：回答关于角色、世界观、大纲的设定问题
            - 分析：分析角色性格、剧情逻辑、世界观一致性
            - 检索：使用 knowledge_search 查阅设定细节
            
            严格遵循【固定设定】与【对话历史】。
            根据用户意图切换模式：用户问设定就讨论设定，用户要创作就写内容。不要答非所问。
            """,
        ExecutionProfile.DEEP, """
            你是资深小说创作专家。你具备以下能力：
            - 创作：按设定写剧情/对话/描写/续写
            - 讨论：回答关于角色、世界观、大纲的设定问题
            - 分析：分析角色性格、剧情逻辑、世界观一致性
            - 检索：使用 knowledge_search 多轮检索角色/大纲/世界观/章节
            - 规划：复杂创作任务拆解为多步骤
            
            严格遵循【固定设定】与【对话历史】。
            根据用户意图切换模式：用户问设定就讨论设定，用户要创作就写内容。不要答非所问。
            请输出 <thinking> 思考过程，再给最终回答。思考要包含：意图分析、检索策略、推理链路。
            """
    );

    private static final Map<ExecutionProfile, String> TASK_INSTRUCTIONS = Map.of(
        ExecutionProfile.FAST, "根据用户意图给出相应回答。",
        ExecutionProfile.BALANCED, "根据用户意图给出相应回答。",
        ExecutionProfile.DEEP, "必须输出 <thinking> 完整思考过程，再根据用户意图给出相应回答。"
    );

    @Override
    public String build(PromptContext ctx) {
        StringBuilder sb = new StringBuilder();

        // 1. System Prompt
        sb.append(SYSTEM_PROMPTS.getOrDefault(ctx.profile(), SYSTEM_PROMPTS.get(ExecutionProfile.BALANCED)))
          .append("\n\n");

        // 2. Fixed Context (角色卡/大纲/前文)
        if (ctx.fixedContext() != null && !ctx.fixedContext().isEmpty()) {
            sb.append("【固定设定·不可违背】\n");
            ctx.fixedContext().forEach((k, v) -> sb.append("== ").append(k).append(" ==\n").append(v).append("\n\n"));
        }

        // 3. History
        if (ctx.history() != null && !ctx.history().isEmpty()) {
            sb.append("【对话历史】\n");
            for (PromptContext.Message m : ctx.history()) {
                String role = "user".equals(m.role()) ? "用户" : "AI";
                sb.append(role).append("：").append(m.content());
                if (m.thinking() != null && !m.thinking().isBlank()) {
                    sb.append("\n  [思考] ").append(m.thinking());
                }
                sb.append("\n\n");
            }
        }

        // 4. Edit Memory
        if (ctx.editMemory() != null && !ctx.editMemory().records().isEmpty()) {
            sb.append("【编辑修正记忆·仅供避免重复错误，不作为当前任务】\n");
            for (EditMemory.EditRecord r : ctx.editMemory().records()) {
                sb.append("第 ").append(r.index() + 1).append(" 条：")
                  .append("错误类型=").append(r.errorType())
                  .append("，正确做法=").append(r.correct())
                  .append("，原输出=").append(r.original().length() > 100 ? r.original().substring(0, 100) + "..." : r.original())
                  .append("\n");
            }
            sb.append("\n");
        }

        // 5. Tool Results
        if (ctx.toolResults() != null && !ctx.toolResults().isEmpty()) {
            sb.append("【工具检索结果·可选参考】\n");
            for (Tool.ToolResult tr : ctx.toolResults()) {
                sb.append(tr.content()).append("\n---\n");
            }
            sb.append("\n");
        }

        // 6. User Input (always last, highest priority)
        sb.append("【用户本轮输入】\n").append(ctx.userInput()).append("\n\n");

        // 7. Task Instruction
        sb.append(TASK_INSTRUCTIONS.getOrDefault(ctx.profile(), TASK_INSTRUCTIONS.get(ExecutionProfile.BALANCED)));

        return sb.toString();
    }
}