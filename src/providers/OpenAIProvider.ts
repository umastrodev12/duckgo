import { AIProvider } from "./Provider.js";
import { Message, ToolDefinition, CompletionResult } from "../core/types.js";

export class OpenAICompatibleProvider implements AIProvider {
  constructor(
    public readonly name: string,
    private apiKey: string,
    private baseUrl: string
  ) {}

  async complete(
    messages: Message[],
    tools: ToolDefinition[],
    model: string
  ): Promise<CompletionResult> {
    const body = {
      model,
      messages: messages.map(this.toOpenAIFormat),
      tools: tools.map((t) => ({
        type: "function",
        function: {
          name: t.name,
          description: t.description,
          parameters: t.parameters,
        },
      })),
      tool_choice: "auto",
    };

    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const err = await response.text();
      throw new Error(`Groq API error: ${response.status} - ${err}`);
    }

    const json = await response.json();
    const message = json.choices[0].message;

    const toolCalls = (message.tool_calls ?? []).map((tc: any) => ({
      id: tc.id,
      name: tc.function.name,
      arguments: JSON.parse(tc.function.arguments || "{}"),
    }));

    return {
      content: message.content ?? null,
      toolCalls,
      promptTokens: json.usage?.prompt_tokens ?? 0,
      completionTokens: json.usage?.completion_tokens ?? 0,
    };
  }

  private toOpenAIFormat(msg: Message) {
    if (msg.role === "tool") {
      return {
        role: "tool",
        tool_call_id: msg.toolCallId,
        content: msg.content,
      };
    }

    if (msg.toolCalls && msg.toolCalls.length > 0) {
      return {
        role: "assistant",
        content: msg.content,
        tool_calls: msg.toolCalls.map((tc) => ({
          id: tc.id,
          type: "function",
          function: {
            name: tc.name,
            arguments: JSON.stringify(tc.arguments),
          },
        })),
      };
    }

    return { role: msg.role, content: msg.content };
  }
}