import { OpenAICompatibleProvider } from "./providers/OpenAIProvider.js";
import { AnthropicProvider } from "./providers/AnthropicProvider.js";
import { AIClient } from "./core/AIClient.js";

const providers = {
  groq: () => new OpenAICompatibleProvider("groq", process.env.GROQ_API_KEY!, "https://api.groq.com/openai/v1/chat/completions"),
  openai: () => new OpenAICompatibleProvider("openai", process.env.OPENAI_API_KEY!, "https://api.openai.com/v1/chat/completions"),
  anthropic: () => new AnthropicProvider(process.env.ANTHROPIC_API_KEY!),
};

const chosenProvider = providers["groq"]();
const ai = new AIClient(chosenProvider, "llama-3.3-70b-versatile", [], {});