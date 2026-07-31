import path from "node:path";
import fs from "fs-extra";
import os from "node:os";
import { SYSTEM_PROMPT } from "../prompts/system-prompt.js";

const CONFIG_DIR = path.join(os.homedir(), '.duck');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

interface Config {
    apiKey: string
    model: string
    maxTokens: number
    temperature: number
    systemPrompt: string
    password: string
}

const ProviderAPIiKey = process.env.AI_API_KEY;

const DEFAULT_CONFIG: Config = {
    apiKey: "", 
    model: "qwen/qwen3.6-27b",

    maxTokens: 2048,
    temperature: 0.6,

    systemPrompt: SYSTEM_PROMPT,
    password: ""
}

export class ConfigManager {
    private config: Config;

    constructor() {
        this.config = { ...DEFAULT_CONFIG };
    }

    async init() {
        await fs.ensureDir(CONFIG_DIR)

        if (await fs.pathExists(CONFIG_FILE)) {
            try {
                const savedConfig = fs.readJson(CONFIG_FILE)
                this.config = { ...this.config, ...savedConfig }
            } catch {

            }
        }

        if (process.env.AI_API_KEY) {
            this.config.apiKey = process.env.AI_API_KEY;
        }

        process.env.AI_API_KEY = this.config.apiKey;
    }

    validate(): boolean {
        return true;
    }

    async save(): Promise<void> {
        await fs.ensureDir(CONFIG_DIR);
        await fs.writeJson(CONFIG_FILE, this.config, { spaces: 2 });
      }
    
      /**
       * Get a copy of current configuration
       */
      get(): Config {
        return { ...this.config };
      }

      getConfigPath(): string {
        return CONFIG_FILE;
      }
}

export const configManager = new ConfigManager()