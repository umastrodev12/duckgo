import type { AIProvider } from "../providers/Provider";
import type { Message, ToolDefinition } from "./types";

type ToolFunction = (args: Record<string, any>) => string | Promise<string>;

export class AIClient {
  private history: Message[] = [];
  private readonly maxIterations = 15;

  constructor(
    private provider: AIProvider,
    private model: string,
    private tools: ToolDefinition[],
    private toolFunctions: Record<string, ToolFunction>
  ) {}

  setSystemPrompt(prompt: string) {
    if (this.history.length === 0) {
      this.history.push({ role: "system", content: prompt });
    }
  }

  async ask(prompt: string): Promise<string> {
    this.history.push({ role: "user", content: prompt });

    for (let i = 0; i < this.maxIterations; i++) {
      const result = await this.provider.complete(this.history, this.tools, this.model);

      if (result.toolCalls.length === 0) {
        this.history.push({ role: "assistant", content: result.content });
        return result.content ?? "";
      }

      this.history.push({
        role: "assistant",
        content: result.content,
        toolCalls: result.toolCalls,
      });

      for (const call of result.toolCalls) {
        const func = this.toolFunctions[call.name];
        const toolResult = func ? await func(call.arguments) : "Ferramenta não encontrada.";

        this.history.push({
          role: "tool",
          content: toolResult,
          toolCallId: call.id,
        });
      }
    }

    return "Limite de iterações atingido.";
  }

  clearHistory() {
    const systemMsg = this.history.find((m) => m.role === "system");
    this.history = systemMsg ? [systemMsg] : [];
  }
}