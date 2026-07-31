import type { AIProvider } from "./Provider";
import type { Message, ToolDefinition, CompletionResult } from "../core/types";

export class AnthropicProvider implements AIProvider {
  readonly name = "anthropic";

  constructor(private apiKey: string) {}

  async complete(messages: Message[], tools: ToolDefinition[], model: string): Promise<CompletionResult> {
    const systemMsg = messages.find((m) => m.role === "system");
    const rest = messages.filter((m) => m.role !== "system");

    const body = {
      model,
      max_tokens: 4096,
      system: systemMsg?.content ?? undefined,
      messages: rest.map(this.toAnthropicFormat),
      tools: tools.map((t) => ({
        name: t.name,
        description: t.description,
        input_schema: t.parameters,
      })),
    };

    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": this.apiKey,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const err = await response.text();
      throw new Error(`Anthropic API error: ${response.status} - ${err}`);
    }

    const json = await response.json();

    let content: string | null = null;
    const toolCalls = [];

    for (const block of json.content) {
      if (block.type === "text") {
        content = (content ?? "") + block.text;
      } else if (block.type === "tool_use") {
        toolCalls.push({ id: block.id, name: block.name, arguments: block.input });
      }
    }

    return {
      content,
      toolCalls,
      promptTokens: json.usage?.input_tokens ?? 0,
      completionTokens: json.usage?.output_tokens ?? 0,
    };
  }

  private toAnthropicFormat(msg: Message) {
    if (msg.role === "tool") {
      return {
        role: "user",
        content: [
          { type: "tool_result", tool_use_id: msg.toolCallId, content: msg.content },
        ],
      };
    }

    if (msg.toolCalls && msg.toolCalls.length > 0) {
      return {
        role: "assistant",
        content: msg.toolCalls.map((tc) => ({
          type: "tool_use",
          id: tc.id,
          name: tc.name,
          input: tc.arguments,
        })),
      };
    }

    return { role: msg.role, content: msg.content };
  }
}