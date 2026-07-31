import { spawn } from "node:child_process";
import type { ToolDefinition } from "../core/types";

export const RUN_COMMAND_TOOL: ToolDefinition = {
  name: "run_command",
  description: "Executa um comando no terminal do sistema operacional do usuário.",
  parameters: {
    type: "object",
    properties: {
      command: { type: "string", description: "O comando de shell a ser executado." },
      reason: { type: "string", description: "Breve explicação do motivo de executar esse comando." },
    },
    required: ["command", "reason"],
  },
};

const DANGEROUS_PATTERNS = ["rm -rf", "del /f", "format", "shutdown", "mkfs", ":(){:|:&};:"];

const DEV_SERVER_KEYWORDS = [
  "flask run", "runserver", "uvicorn", "gunicorn",
  "npm run dev", "bun dev", "yarn dev", "next dev", "vite",
];

export type ConfirmCallback = (command: string, reason: string) => Promise<boolean> | boolean;

function isDangerous(command: string): boolean {
  const lowered = command.toLowerCase();
  return DANGEROUS_PATTERNS.some((p) => lowered.includes(p));
}

function looksLikeDevServer(command: string): boolean {
  const lowered = command.toLowerCase();
  return DEV_SERVER_KEYWORDS.some((k) => lowered.includes(k));
}

function runShellCommand(command: string, timeoutMs: number): Promise<{ code: number; output: string }> {
  return new Promise((resolve) => {
    const isWindows = process.platform === "win32";
    const shell = isWindows ? "cmd.exe" : "bash";
    const args = isWindows ? ["/c", command] : ["-c", command];

    const child = spawn(shell, args, { windowsHide: true });

    let output = "";
    let settled = false;

    const timer = setTimeout(() => {
      if (!settled) {
        settled = true;
        child.kill();
        resolve({ code: -1, output: "Comando excedeu o tempo limite." });
      }
    }, timeoutMs);

    child.stdout.on("data", (data) => (output += data.toString()));
    child.stderr.on("data", (data) => (output += data.toString()));

    child.on("close", (code) => {
      if (!settled) {
        settled = true;
        clearTimeout(timer);
        resolve({ code: code ?? 0, output });
      }
    });
  });
}

export function createRunCommandTool(confirm: ConfirmCallback) {
  return async function runCommand(args: Record<string, any>): Promise<string> {
    const command = String(args.command ?? "");
    const reason = String(args.reason ?? "");

    if (isDangerous(command)) {
      return "Comando bloqueado por segurança.";
    }

    const allowed = await confirm(command, reason);
    if (!allowed) {
      return "Usuário negou a execução do comando.";
    }

    if (looksLikeDevServer(command)) {
      const isWindows = process.platform === "win32";
      const shell = isWindows ? "cmd.exe" : "bash";
      const shellArgs = isWindows ? ["/c", command] : ["-c", command];

      const child = spawn(shell, shellArgs, {
        detached: true,
        stdio: "ignore",
        windowsHide: true,
      });
      child.unref();

      return `Comando iniciado em background: ${command}. Verifique o terminal/navegador para os logs.`;
    }

    const { code, output } = await runShellCommand(command, 180_000);
    const truncated = output.length > 2000 ? output.slice(0, 2000) : output;

    return `Código de saída: ${code}\n${truncated}`;
  };
}