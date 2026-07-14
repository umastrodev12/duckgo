# 🦆 Duck Go

Um assistente de IA de terminal, rápido e leve, rodando com a API da [Groq](https://groq.com).

Duck Go traz um chat com IA direto no seu terminal — sem depender de navegador, com respostas em Markdown renderizado, análise de arquivos do seu projeto e configuração persistente entre sessões.

## ✨ Recursos

- 💬 Chat com IA direto no terminal, com histórico de conversa
- 🎨 Respostas renderizadas em Markdown (negrito, código, listas, etc)
- 📄 Leitura e análise de arquivos do seu projeto com `/read <arquivo>`
- ⚙️ Configuração persistente (modelo padrão e API key) salva em `.duck/`
- 🚀 Rápido, graças à inferência da Groq (LPU)
- 🇧🇷 Fluente em Português Brasileiro

## 🔑 Configuração

Duck Go usa a API da Groq, que possui um **free tier** generoso.

1. Crie uma conta gratuita em [console.groq.com](https://console.groq.com)
2. Gere uma API key
3. Na primeira execução, o Duck Go vai pedir para você colar sua chave — ela é salva localmente em um  `.env` e não é enviada para nenhum lugar além da própria Groq

## 🚀 Uso

Rode o comando no terminal:

```bash
python main.py
```

Você verá o menu principal:

```
🦆 Duck Go

Selecione uma opção
1. Iniciar Duck AI
2. Sair
```

Escolha `1` para iniciar o chat. Dentro do chat:

| Comando | Descrição |
|---|---|
| `/read <arquivo>` | Analisa um arquivo do seu projeto |
| `/clear` | Limpa o histórico da conversa atual |
| `/help` | Mostra os comandos disponíveis |
| `sair` | Encerra a sessão |

### Exemplo

```
> /read main.py
Lendo main.py...

Esse arquivo implementa o loop principal do programa...
```

## 🧱 Stack

- **Python** — linguagem principal
- **Groq API** — inferência de IA
- **Rich** — renderização no terminal (Markdown, painéis, spinners, cores)

## 📁 Estrutura de configuração

```
.duck/
└── config.json   # onde fica o modelo padrão
```

## 🤝 Contribuindo

Pull requests são bem-vindos! Se encontrar um bug ou tiver uma ideia, abra uma issue.

## 📄 Licença

Este projeto está licenciado sob a [Apache License 2.0](LICENSE).
