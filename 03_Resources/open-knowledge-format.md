---
title: "Open Knowledge Format (OKF)"
category: "resources"
tags: ["okf", "padrao", "metadados", "interoperabilidade"]
created: "2026-11-05"
updated: "2026-11-05"
status: "active"
author: "gugogabrdf"
license: "CC-BY-4.0"
summary: "Especificação de metadados abertos em YAML frontmatter para anotações em Markdown, garantindo portabilidade entre Obsidian, scripts CLI e páginas web."
source: "Open Knowledge Standards"
---

# Open Knowledge Format (OKF)

> **Resumo Executivo**: O OKF estabelece um contrato de metadados previsível para cada documento Markdown no Segundo Cérebro. Isso permite que parsers, agentes inteligentes e ferramentas de visualização em grafo naveguem e indexem a base sem ambiguidade.

---

## 1. Campos Padrão do Frontmatter

```yaml
---
title: "Nome Canônico da Nota"
category: "projects | areas | resources | archives | inbox"
tags: ["tag1", "tag2"]
created: "YYYY-MM-DD"
updated: "YYYY-MM-DD"
status: "draft | active | completed | archived"
author: "gugogabrdf"
license: "CC-BY-4.0"
summary: "Resumo em 1-2 frases para pré-visualização e busca rápida."
---
```

---

## 2. Vantagens na Prática

1. **Interoperabilidade Total**: Compatível nativamente com Obsidian, VS Code, Antigravity, Claude Code e geradores estáticos.
2. **Filtragem no Visualizador**: O dashboard HTML usa os campos `category` e `tags` para colorir e filtrar nós dinamicamente.
3. **Consistência para Agentes**: As IAs leem o bloco YAML para entender imediatamente o contexto antes de processar o corpo da nota.

---

## 3. Conexões no Grafo
- [[llm-wiki-karpathy]]: Utiliza os metadados para construir índices e checar integridade.
- [[metodo-para-tiago-forte]]: Define as categorias aceitas no campo `category`.
- [[lancamento-segundo-cerebro]]: Implementa a validação do formato via script de checagem.
