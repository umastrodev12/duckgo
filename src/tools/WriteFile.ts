import path from "node:path";
import fs from "node:fs";
import type { ToolDefinition } from "../core/types";

export const WRITE_FILE_TOOL: ToolDefinition = {
  name: "write_file",
  description: "Cria ou sobrescreve um arquivo com o conteúdo especificado.",
  parameters: {
    type: "object",
    properties: {
      path: { type: "string", description: "Caminho do arquivo a ser criado." },
      content: { type: "string", description: "Conteúdo completo a ser escrito no arquivo." },
    },
    required: ["path", "content"],
  },
};

export type ConfirmCallback = (path: string, content: string) => Promise<boolean> | boolean;

export function createWriteFileTool(confirm: ConfirmCallback) {
  return async function writeFile(args: Record<string, any>): Promise<string> {
    const filePath = String(args.path ?? "");
    const content = String(args.content ?? "");

    const allowed = await confirm(filePath, content);
    if (!allowed) {
      return "Usuário negou a criação do arquivo.";
    }

    try {
      const dir = path.dirname(filePath);
      if (dir) {
        fs.mkdirSync(dir, { recursive: true });
      }
      fs.writeFileSync(filePath, content, "utf-8");
      return `Arquivo '${filePath}' criado com sucesso.`;
    } catch (e: any) {
      return `Erro ao criar '${filePath}': ${e.message}`;
    }
  };
}