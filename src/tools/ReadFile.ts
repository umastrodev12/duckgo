import path from "node:path";
import fs from "node:fs";
import type { ToolDefinition } from "../core/types";

export const READ_FILE_TOOL: ToolDefinition = {
  name: "read_file",
  description: "Lê o conteúdo de um arquivo específico do projeto.",
  parameters: {
    type: "object",
    properties: {
      path: { type: "string", description: "Caminho do arquivo a ler." },
    },
    required: ["path"],
  },
};

const MAX_CONTENT_LENGTH = 20_000;

export async function readFile(args: Record<string, any>): Promise<string> {
  const filePath = String(args.path ?? "");

  if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
    return `Arquivo não encontrado: ${filePath}`;
  }

  try {
    let content = fs.readFileSync(filePath, "utf-8");
    if (content.length > MAX_CONTENT_LENGTH) {
      content = content.slice(0, MAX_CONTENT_LENGTH) + "\n... (arquivo truncado)";
    }

    const ext = path.extname(filePath).replace(".", "");
    return `Arquivo: ${filePath}\n\`\`\`${ext}\n${content}\n\`\`\``;
  } catch (e: any) {
    return `Erro ao ler ${filePath}: ${e.message}`;
  }
}