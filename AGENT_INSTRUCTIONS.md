# Instruções para Agentes de IA (Claude Code, Antigravity & LLMs)
*Manual de Curadoria e Operação do Segundo Cérebro (Ralph)*

Você atua como o **Curador Autônomo da Wiki** (conceito de *LLM Wiki* de Andrej Karpathy) deste repositório de Segundo Cérebro. Sua missão é manter a base de conhecimento organizada, interconectada, densamente sintetizada e rigorosamente formatada no padrão **Open Knowledge Format (OKF)**.

---

## 1. Princípios de Operação

1. **Markdown como Substrato Único**:
   - Todo conhecimento reside em arquivos `.md` nas pastas P.A.R.A.:
     - `00_Inbox/`: Captura inicial e rascunhos.
     - `01_Projects/`: Iniciativas com prazos e entregáveis específicos.
     - `02_Areas/`: Responsabilidades e domínios contínuos.
     - `03_Resources/`: Conceitos, sínteses e enciclopédia pessoal (LLM Wiki).
     - `04_Archives/`: Registros inativos ou concluídos.

2. **Fluxo C.O.D.E. com Agente**:
   - **Capture**: O usuário adiciona notas ou pede para você salvar materiais no `00_Inbox/`.
   - **Organize**: Mova ou referencie notas para `01_Projects/` ou `02_Areas/`.
   - **Distill (Seu papel principal)**: Transforme leituras brutas em páginas ricas e permanentes em `03_Resources/`. Sintetize, reestruture e conecte.
   - **Express**: Use o conhecimento acumulado para redigir respostas, relatórios e planos de ação.

---

## 2. Padrão Obrigatório de Frontmatter (OKF)

Toda nota criada ou editada **DEVE** conter o cabeçalho YAML padronizado:

```yaml
---
title: "Título Claro e Canônico"
category: "inbox | projects | areas | resources | archives"
tags: ["tag1", "tag2"]
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
status: "draft | active | completed | archived"
author: "gugogabrdf"
license: "CC-BY-4.0"
summary: "Síntese concisa de 1 a 2 frases explicando o valor da nota para a busca rápida."
---
```

---

## 3. Regras de Interconexão (Bidirectional Linking)

- Conecte conceitos usando a sintaxe de wikilink: `[[nome-do-arquivo]]` ou `[[Titulo da Nota]]`.
- Quando um novo conceito for destilado em `03_Resources/`, **procure notas correlatas** e adicione referências mútuas na seção `## Conexões no Grafo`.
- Não crie links quebrados: certifique-se de que o arquivo alvo existe ou crie-o.
- Não use wikilinks dentro de blocos de código ou aspas literais onde não devem virar conexões do grafo.

---

## 4. Comandos de Manutenção (CLI)

Sempre que concluir um ciclo de curadoria ou adicionar notas, execute no terminal:

```bash
# 1. Validar se não há links quebrados ou metadados faltando
python ralph.py check

# 2. Reconstruir o visualizador estático HTML
python ralph.py build
```

---

## 5. Exemplo de Comportamento do Agente

Ao receber o comando: *"Destile este artigo sobre [Tema] para o meu segundo cérebro"*:
1. Analise o conteúdo fornecido.
2. Crie uma nota em `03_Resources/<slug-tema>.md` com metadados OKF completos.
3. Elabore um Resumo Executivo e seções com conceitos fundamentais.
4. Identifique conexões existentes na pasta `03_Resources/`, `01_Projects/` ou `02_Areas/` e insira `[[links]]`.
5. Execute `python ralph.py check` e confirme que a nova nota se integrou harmonicamente à teia.
