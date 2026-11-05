#!/usr/bin/env python3
"""
Ralph · Segundo Cérebro CLI
Ferramenta de linha de comando para gerenciar notas P.A.R.A., validar integridade,
gerar o visualizador HTML do grafo e sincronizar com o GitHub.

Uso:
  python ralph.py new <category> <title>
  python ralph.py check
  python ralph.py build
  python ralph.py serve [--port 8000]
  python ralph.py sync [mensagem de commit]
"""

import argparse
import datetime
import http.server
import json
import os
import re
import socketserver
import subprocess
import sys
from pathlib import Path

# Adiciona scripts ao path para importar parser
sys.path.insert(0, str(Path(__file__).parent / "scripts"))
try:
    from parser import VaultScanner, PARA_CATEGORIES
except ImportError:
    print("[!] Erro: scripts/parser.py não foi encontrado.")
    sys.exit(1)

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
DOCS_DIR = BASE_DIR / "docs"
TEMPLATE_HTML = BASE_DIR / "scripts" / "visualizer_template.html"

CATEGORY_MAP = {
    "inbox": ("00_Inbox", "inbox.md"),
    "project": ("01_Projects", "project.md"),
    "projects": ("01_Projects", "project.md"),
    "area": ("02_Areas", "area.md"),
    "areas": ("02_Areas", "area.md"),
    "resource": ("03_Resources", "resource.md"),
    "resources": ("03_Resources", "resource.md"),
    "archive": ("04_Archives", "resource.md"),
    "archives": ("04_Archives", "resource.md")
}

def slugify(text: str) -> str:
    """Converte um título para formato de slug de arquivo (ex: 'Meu Novo Projeto' -> 'meu-novo-projeto')."""
    text = text.lower().strip()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')

def cmd_new(args):
    """Cria uma nova nota a partir do template correspondente."""
    cat_key = args.category.lower()
    if cat_key not in CATEGORY_MAP:
        print(f"[!] Categoria inválida: '{args.category}'. Opções válidas: inbox, project, area, resource, archive.")
        sys.exit(1)

    folder_name, template_name = CATEGORY_MAP[cat_key]
    template_file = TEMPLATES_DIR / template_name
    if not template_file.exists():
        print(f"[!] Template não encontrado: {template_file}")
        sys.exit(1)

    title = args.title.strip()
    slug = slugify(title)
    target_dir = BASE_DIR / folder_name
    target_dir.mkdir(parents=True, exist_ok=True)

    target_file = target_dir / f"{slug}.md"
    if target_file.exists():
        print(f"[!] A nota já existe em: {target_file}")
        sys.exit(1)

    template_content = template_file.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()

    content = template_content.replace("{{title}}", title).replace("{{date}}", today)
    target_file.write_text(content, encoding="utf-8")

    print(f"[+] Nova nota criada com sucesso!")
    print(f"    Arquivo: {target_file.relative_to(BASE_DIR)}")
    print(f"    Categoria: {folder_name} (OKF padronizado)")

def cmd_check(args):
    """Verifica a integridade das notas, links órfãos e metadados."""
    print("[*] Escaneando a base de conhecimento Ralph...")
    scanner = VaultScanner(BASE_DIR).scan()
    report = scanner.check_integrity()

    print(f"    Total de notas indexadas: {report['total_notes']}")
    has_issues = False

    if report["broken_links"]:
        has_issues = True
        print(f"\n[!] Links quebrados encontrados ({len(report['broken_links'])}):")
        for bl in report["broken_links"]:
            print(f"    - {bl['source_file']} aponta para [[{bl['target_clean']}]] (inexistente)")

    if report["orphan_notes"]:
        print(f"\n[?] Notas sem nenhuma conexão (órfãs) ({len(report['orphan_notes'])}):")
        for o in report["orphan_notes"]:
            print(f"    - {o['path']} ({o['title']})")

    if report["missing_metadata"]:
        has_issues = True
        print(f"\n[!] Notas sem frontmatter OKF ({len(report['missing_metadata'])}):")
        for mm in report["missing_metadata"]:
            print(f"    - {mm}")

    if not has_issues and not report["orphan_notes"]:
        print("\n[OK] Base 100% íntegra! Sem links quebrados e todos os metadados OKF válidos.")
    elif not has_issues:
        print("\n[OK] Sem links quebrados ou erros críticos de metadados.")

    return 1 if has_issues else 0

def cmd_build(args=None):
    """Compila as notas para docs/index.html e exporta graph_data.json."""
    print("[*] Construindo visualizador HTML do Segundo Cérebro...")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    scanner = VaultScanner(BASE_DIR).scan()
    graph_data = scanner.build_graph()

    # Salva JSON do grafo
    json_path = DOCS_DIR / "graph_data.json"
    json_path.write_text(json.dumps(graph_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"    Dados exportados: {json_path.relative_to(BASE_DIR)}")

    # Gera HTML completo
    if not TEMPLATE_HTML.exists():
        print(f"[!] Template HTML não encontrado em: {TEMPLATE_HTML}")
        sys.exit(1)

    template_str = TEMPLATE_HTML.read_text(encoding="utf-8")
    json_compact = json.dumps(graph_data, ensure_ascii=False)
    final_html = template_str.replace("__VAULT_DATA_PLACEHOLDER__", json_compact)

    html_path = DOCS_DIR / "index.html"
    html_path.write_text(final_html, encoding="utf-8")
    print(f"    Visualizador gerado: {html_path.relative_to(BASE_DIR)}")

    # Garante arquivo .nojekyll para o GitHub Pages ignorar o processamento do Jekyll
    nojekyll_path = DOCS_DIR / ".nojekyll"
    if not nojekyll_path.exists():
        nojekyll_path.write_text("", encoding="utf-8")

    print(f"[+] Build concluído com sucesso!")
    print(f"    Notas: {graph_data['stats']['total_notes']} | Conexões: {graph_data['stats']['total_links']}")
    return 0

def cmd_serve(args):
    """Compila e inicia um servidor web local para visualizar o grafo."""
    cmd_build()
    port = args.port
    docs_str = str(DOCS_DIR)

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=docs_str, **k)

    print(f"\n[*] Servidor local iniciado em: http://localhost:{port}")
    print("    Pressione Ctrl+C para encerrar.")

    with socketserver.TCPServer(("", port), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Servidor encerrado.")

def cmd_sync(args):
    """Compila o site, comita as alterações no Git e envia para o GitHub."""
    cmd_build()

    today = datetime.date.today().isoformat()
    msg = args.message if args.message else f"chore(brain): update second brain notes & graph [{today}]"

    print("\n[*] Preparando sincronização com o GitHub...")
    try:
        subprocess.run(["git", "add", "."], check=True, cwd=str(BASE_DIR))
        
        # Verifica se há alterações para commitar
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=str(BASE_DIR))
        if not status.stdout.strip():
            print("[-] Nenhuma alteração pendente para commit.")
        else:
            subprocess.run(["git", "commit", "-m", msg], check=True, cwd=str(BASE_DIR))
            print(f"[+] Commit realizado: '{msg}'")

        print("[*] Enviando alterações para origin main...")
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True, cwd=str(BASE_DIR))
        print("[+] Sincronização concluída com sucesso com o repositório remoto!")
    except subprocess.CalledProcessError as e:
        print(f"[!] Erro durante o comando git: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        prog="ralph",
        description="Ralph · CLI para o Segundo Cérebro (Karpathy LLM Wiki + Tiago Forte P.A.R.A. + OKF)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Comandos disponíveis")

    # new
    p_new = subparsers.add_parser("new", help="Cria uma nova nota a partir de template OKF")
    p_new.add_argument("category", help="Categoria: inbox, project, area, resource, archive")
    p_new.add_argument("title", help="Título da nota (entre aspas)")
    p_new.set_defaults(func=cmd_new)

    # check
    p_check = subparsers.add_parser("check", help="Verifica integridade, links quebrados e metadados")
    p_check.set_defaults(func=cmd_check)

    # build
    p_build = subparsers.add_parser("build", help="Gera o visualizador estático HTML em docs/index.html")
    p_build.set_defaults(func=cmd_build)

    # serve
    p_serve = subparsers.add_parser("serve", help="Inicia servidor local em docs/")
    p_serve.add_argument("--port", type=int, default=8000, help="Porta do servidor (padrão: 8000)")
    p_serve.set_defaults(func=cmd_serve)

    # sync
    p_sync = subparsers.add_parser("sync", help="Compila, comita no git e faz push para o GitHub")
    p_sync.add_argument("message", nargs="?", default=None, help="Mensagem do commit (opcional)")
    p_sync.set_defaults(func=cmd_sync)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)

if __name__ == "__main__":
    main()

