"""
Ralph PKM - Parser & Graph Builder
Processa arquivos Markdown com metadados OKF e extrai grafo de conexões bidirecionais [[wikilinks]].
Compatível com Python 3.10+ sem dependências externas obrigatórias.
"""

from __future__ import annotations
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

PARA_CATEGORIES = {
    "00_Inbox": "inbox",
    "01_Projects": "projects",
    "02_Areas": "areas",
    "03_Resources": "resources",
    "04_Archives": "archives"
}

CATEGORY_COLORS = {
    "projects": "#38bdf8",   # Sky Blue
    "areas": "#34d399",      # Emerald Green
    "resources": "#a78bfa",  # Violet
    "archives": "#94a3b8",   # Slate Gray
    "inbox": "#fbbf24"       # Amber
}

def parse_yaml_frontmatter(text: str) -> Tuple[Dict[str, Any], str]:
    """Extrai metadados do bloco YAML frontmatter e retorna (metadados, corpo_markdown)."""
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    yaml_block = parts[1].strip()
    body = parts[2].strip()
    metadata: Dict[str, Any] = {}

    current_list_key = None

    for line in yaml_block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Item de lista: - item
        if line.startswith("- ") and current_list_key:
            item_val = line[2:].strip().strip('"').strip("'")
            if current_list_key in metadata and isinstance(metadata[current_list_key], list):
                metadata[current_list_key].append(item_val)
            continue

        # Chave-valor
        if ":" in line:
            current_list_key = None
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()

            if val == "":
                # Pode ser início de lista
                metadata[key] = []
                current_list_key = key
            elif val.startswith("[") and val.endswith("]"):
                # Lista inline: ["a", "b"]
                inner = val[1:-1].strip()
                if not inner:
                    metadata[key] = []
                else:
                    items = [item.strip().strip('"').strip("'") for item in inner.split(",") if item.strip()]
                    metadata[key] = items
            else:
                # String ou número
                clean_val = val.strip('"').strip("'")
                metadata[key] = clean_val

    return metadata, body

def extract_wikilinks(text: str) -> List[Dict[str, str]]:
    """
    Encontra todos os links no formato [[target]], [[target|alias]] ou [[target#section|alias]].
    Ignora links dentro de blocos de código (```) e spans de código (`...`).
    """
    # Remove blocos de código cercados por ```
    clean_text = re.sub(r'```[\s\S]*?```', '', text)
    # Remove código inline cercado por `
    clean_text = re.sub(r'`[^`]*`', '', clean_text)

    pattern = re.compile(r'\[\[(.*?)\]\]')
    links = []
    for match in pattern.finditer(clean_text):
        raw = match.group(1).strip()
        if not raw:
            continue
        
        alias = None
        target = raw
        if "|" in raw:
            target, alias = raw.split("|", 1)
            target = target.strip()
            alias = alias.strip()
        
        # Remove ancoras de seção se houver
        clean_target = target.split("#")[0].strip()
        if clean_target:
            links.append({
                "raw": raw,
                "target": clean_target,
                "alias": alias or clean_target
            })
    return links

def normalize_key(s: str) -> str:
    """Normaliza nomes para matching de links (minúsculas, sem extensão, sem espaços)."""
    s = s.strip()
    if s.endswith(".md"):
        s = s[:-3]
    return s.lower().replace(" ", "-").replace("_", "-")

class VaultScanner:
    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)
        self.notes: Dict[str, Dict[str, Any]] = {}
        self.alias_map: Dict[str, str] = {} # normalizado -> note_id

    def scan(self) -> VaultScanner:
        self.notes.clear()
        self.alias_map.clear()

        # Pastas monitoradas
        for folder, cat in PARA_CATEGORIES.items():
            folder_path = self.root_dir / folder
            if not folder_path.exists():
                continue

            for md_file in folder_path.rglob("*.md"):
                rel_path = md_file.relative_to(self.root_dir).as_posix()
                stem = md_file.stem
                note_id = stem

                try:
                    content = md_file.read_text(encoding="utf-8")
                except Exception as e:
                    print(f"[!] Erro ao ler {rel_path}: {e}")
                    continue

                meta, body = parse_yaml_frontmatter(content)
                wikilinks = extract_wikilinks(body)

                title = meta.get("title") or stem.replace("-", " ").replace("_", " ").title()
                category = meta.get("category") or cat
                tags = meta.get("tags") or []
                if isinstance(tags, str):
                    tags = [tags]

                note_data = {
                    "id": note_id,
                    "title": title,
                    "stem": stem,
                    "path": rel_path,
                    "folder": folder,
                    "category": category,
                    "tags": tags,
                    "created": str(meta.get("created", "")),
                    "updated": str(meta.get("updated", "")),
                    "status": str(meta.get("status", "active")),
                    "author": str(meta.get("author", "")),
                    "summary": str(meta.get("summary", "")),
                    "raw_links": wikilinks,
                    "body": body,
                    "full_content": content,
                    "has_frontmatter": bool(meta)
                }

                self.notes[note_id] = note_data

                # Mapeia chaves para resolução flexível de links
                self.alias_map[normalize_key(stem)] = note_id
                self.alias_map[normalize_key(title)] = note_id
                self.alias_map[normalize_key(rel_path)] = note_id

        return self

    def build_graph(self) -> Dict[str, Any]:
        nodes = []
        links = []
        connections_count: Dict[str, int] = {nid: 0 for nid in self.notes}
        seen_links: Set[Tuple[str, str]] = set()

        for note_id, note in self.notes.items():
            for link in note["raw_links"]:
                target_raw = link["target"]
                norm_target = normalize_key(target_raw)

                target_id = self.alias_map.get(norm_target)
                if target_id and target_id != note_id:
                    link_pair = tuple(sorted([note_id, target_id]))
                    if link_pair not in seen_links:
                        seen_links.add(link_pair)
                        links.append({
                            "source": note_id,
                            "target": target_id,
                            "label": link.get("alias") or ""
                        })
                    connections_count[note_id] = connections_count.get(note_id, 0) + 1
                    connections_count[target_id] = connections_count.get(target_id, 0) + 1

        for note_id, note in self.notes.items():
            cat = note["category"]
            color = CATEGORY_COLORS.get(cat, "#64748b")
            degree = connections_count.get(note_id, 0)
            
            nodes.append({
                "id": note["id"],
                "title": note["title"],
                "path": note["path"],
                "folder": note["folder"],
                "category": cat,
                "color": color,
                "tags": note["tags"],
                "created": note["created"],
                "updated": note["updated"],
                "status": note["status"],
                "summary": note["summary"],
                "degree": degree,
                "content": note["body"]
            })

        return {
            "nodes": nodes,
            "links": links,
            "stats": {
                "total_notes": len(nodes),
                "total_links": len(links),
                "categories": {cat: sum(1 for n in nodes if n["category"] == cat) for cat in CATEGORY_COLORS}
            }
        }

    def check_integrity(self) -> Dict[str, Any]:
        broken_links = []
        orphan_notes = []
        missing_metadata = []

        graph_data = self.build_graph()
        connected_ids = set()
        for link in graph_data["links"]:
            connected_ids.add(link["source"])
            connected_ids.add(link["target"])

        for note_id, note in self.notes.items():
            if not note["has_frontmatter"]:
                missing_metadata.append(note["path"])

            if note_id not in connected_ids and len(self.notes) > 1:
                orphan_notes.append({"id": note_id, "title": note["title"], "path": note["path"]})

            for link in note["raw_links"]:
                norm_target = normalize_key(link["target"])
                if norm_target not in self.alias_map:
                    broken_links.append({
                        "source_file": note["path"],
                        "target_raw": link["raw"],
                        "target_clean": link["target"]
                    })

        return {
            "broken_links": broken_links,
            "orphan_notes": orphan_notes,
            "missing_metadata": missing_metadata,
            "total_notes": len(self.notes)
        }
