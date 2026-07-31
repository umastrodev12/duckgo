import { Command } from "commander";

export function setupCLI() {
    const program = new Command();

    program
        .name('duckgo')
        .description('An agentic coding tool that lives in your terminal. He understand your project files and help you to fix bugs.')
        .helpOption('-h', 'help')

    return program;
}