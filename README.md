# Ralph · Segundo Cérebro Digital
> **Inspirado no conceito de LLM Wiki de Andrej Karpathy, metodologia C.O.D.E. e P.A.R.A. de Tiago Forte e Open Knowledge Format (OKF).**

Repositório pessoal de gestão de conhecimento baseado em **Markdown puro**, mantido e enriquecido com auxílio de Modelos de Linguagem (LLMs), estruturado com metadados abertos e visualizável através de um **dashboard interativo em D3.js estilo Obsidian Publish** publicado automaticamente no **GitHub Pages**.

---

## 🧭 Pilares do Sistema

### 1. O Fluxo C.O.D.E. & Estrutura P.A.R.A. (Tiago Forte)
- `00_Inbox/` — **Capture**: notas rápidas, links e pensamentos brutos.
- `01_Projects/` — **Organize**: iniciativas ativas com prazos e entregáveis definidos.
- `02_Areas/` — **Organize**: responsabilidades e domínios contínuos de longo prazo (saúde, finanças, PKM).
- `03_Resources/` — **Distill**: enciclopédia pessoal permanente, guias e conceitos sintetizados.
- `04_Archives/` — Itens inativos ou concluídos preservados para histórico.

### 2. A Filosofia de LLM Wiki (Andrej Karpathy)
Em vez de bancos de dados opacos ou sistemas fragmentados, o conhecimento vive em arquivos Markdown interconectados via `[[wikilinks]]`. Agentes de IA (Claude Code, Antigravity, etc.) atuam como **curadores da wiki**, lendo entradas brutas, destilando conceitos centrais, unificando referências e mantendo as conexões vivas e sem contradições.

### 3. Open Knowledge Format (OKF)
Todas as notas possuem cabeçalho YAML padronizado:
```yaml
---
title: "Título da Nota"
category: "projects | areas | resources | archives | inbox"
tags: ["ia", "segundo-cerebro"]
created: "2026-11-05"
updated: "2026-11-05"
status: "active"
author: "gugogabrdf"
license: "CC-BY-4.0"
summary: "Síntese concisa de 1 a 2 frases para indexação rápida e busca."
---
```

### 4. Visualizador HTML Autônomo (Obsidian Publish Style)
O comando `python ralph.py build` compila a base inteira para um único arquivo estático em `docs/index.html` com:
- **Grafo 2D Interativo em D3.js**: nós coloridos por categoria P.A.R.A., tamanho baseado na centralidade/conexões, zoom/pan e destaque de nós vizinhos ao passar o mouse.
- **Painel Lateral de Leitura**: leitor de Markdown integrado (Marked.js), suporte a links bidirecionais clicáveis (`[[Nota]]`), metadados OKF e resumo executivo.
- **Busca Instantânea**: filtragem por categoria, tags, títulos e corpo do texto.
- **Zero Servidor Necessário**: funciona direto no navegador ou publicado no GitHub Pages.

---

## 🚀 Como Usar a CLI (`ralph.py`)

A ferramenta CLI foi desenvolvida em Python padrão (sem necessidade de instalar dependências via pip):

```bash
# 1. Criar uma nova nota usando o template OKF padronizado
python ralph.py new resource "Aprendizado por Reforço com Feedback Humano"
python ralph.py new project "Migração do Servidor"
python ralph.py new inbox "Ideias de Podcast"

# 2. Verificar a saúde da base (detecta links quebrados, notas órfãs e metadados faltantes)
python ralph.py check

# 3. Compilar o visualizador HTML e exportar os dados do grafo
python ralph.py build

# 4. Iniciar um servidor local para testar a visualização
python ralph.py serve
# Acesse: http://localhost:8000

# 5. Sincronizar tudo com o GitHub com um único comando
python ralph.py sync "feat: adiciona novas sínteses de IA"
```

---

## 🌐 Publicação no GitHub Pages

Este repositório possui um workflow automatizado em `.github/workflows/deploy.yml`.

Para ativar a visualização pública no seu repositório:
1. Vá até as configurações do repositório no GitHub: `Settings` > `Pages`.
2. Em **Build and deployment** > **Source**, escolha **GitHub Actions**.
3. A cada `git push` na branch `main` (ou via `python ralph.py sync`), o visualizador será construído e publicado automaticamente em:
   ```
   https://gugogabrdf.github.io/ralph/
   ```

---

## 🤖 Uso com Agentes de IA (Claude Code, Antigravity, Cursor)

O arquivo [`AGENT_INSTRUCTIONS.md`](AGENT_INSTRUCTIONS.md) contém o manual operacional completo para os agentes inteligentes. 

Basta pedir ao seu agente:
> *"Leia o AGENT_INSTRUCTIONS.md e destile o rascunho em 00_Inbox/ideias-iniciais.md para uma nova página em 03_Resources, conectando com as notas existentes."*

---

## 📂 Compatibilidade com Obsidian

Esta pasta pode ser aberta diretamente como um **Vault do Obsidian**:
- Pastas P.A.R.A. são reconhecidas nativamente.
- Links `[[wikilinks]]` funcionam perfeitamente nos dois sentidos.
- Frontmatter YAML é lido pelas propriedades nativas do Obsidian.
