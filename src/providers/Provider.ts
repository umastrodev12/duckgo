import type { Message, ToolDefinition, CompletionResult } from "../core/types";

export interface AIProvider {
  readonly name: string;

  complete(
    messages: Message[],
    tools: ToolDefinition[],
    model: string
  ): Promise<CompletionResult>;
}