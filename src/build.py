"""Gera as páginas legais de saibro.app.br a partir dos `.md` desta pasta.

Uma fonte, duas saídas: o HTML publicado pelo GitHub Pages (`<slug>/index.html`,
na raiz do repo) e, opcionalmente, o texto simples que o app Saibro embute em
`mobile/lib/features/identity/data/legal_content.dart` (`--dart <caminho>`).

    python src/build.py                 # só o site
    python src/build.py --dart ../apptenis-monorepo/mobile/lib/features/identity/data/legal_content.dart

Markdown suportado, de propósito mínimo: `# título`, `## seção`, parágrafos e
listas com `- `. E-mails e caminhos `saibro.app.br/...` viram link no HTML.
"""

from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(__file__).resolve().parent

@dataclass(frozen=True)
class Page:
    slug: str
    source: str  # arquivo em src/
    description: str  # <meta name="description">
    nav: str  # nome curto na navegação

    @property
    def url(self) -> str:
        return f"https://saibro.app.br/{self.slug}/"


PAGES = [
    Page("termos", "termos.md", "Termos de Uso do aplicativo Saibro.", "Termos"),
    Page("privacidade", "privacidade.md", "Política de Privacidade do aplicativo Saibro (LGPD).", "Privacidade"),
    Page("excluir-conta", "excluir-conta.md", "Como excluir a sua conta do Saibro e o que acontece com os dados.", "Excluir conta"),
]

VERSION_RE = re.compile(r"^Versão (\d{4}-\d{2}-\d{2})")


@dataclass
class Block:
    kind: str  # h1 | h2 | p | ul
    text: str = ""
    items: list[str] = field(default_factory=list)


@dataclass
class Doc:
    title: str
    version: str | None
    blocks: list[Block]


def parse(text: str) -> Doc:
    blocks: list[Block] = []
    title = ""
    version = None
    para: list[str] = []

    def flush() -> None:
        nonlocal para
        if para:
            blocks.append(Block("p", " ".join(para)))
            para = []

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line:
            flush()
            continue
        if line.startswith("# "):
            flush()
            title = line[2:].strip()
        elif line.startswith("## "):
            flush()
            blocks.append(Block("h2", line[3:].strip()))
        elif line.startswith("- "):
            flush()
            if blocks and blocks[-1].kind == "ul":
                blocks[-1].items.append(line[2:].strip())
            else:
                blocks.append(Block("ul", items=[line[2:].strip()]))
        else:
            m = VERSION_RE.match(line)
            if m and version is None:
                version = m.group(1)
            para.append(line.strip())
    flush()
    if not title:
        raise SystemExit("fonte sem `# título`")
    return Doc(title, version, blocks)


# --- HTML ---------------------------------------------------------------------

EMAIL_RE = re.compile(r"[\w.+-]+@saibro\.app\.br")
PATH_RE = re.compile(r"saibro\.app\.br(/[\w-]+)")


def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = EMAIL_RE.sub(lambda m: f'<a href="mailto:{m.group(0)}">{m.group(0)}</a>', out)
    out = PATH_RE.sub(lambda m: f'<a href="{m.group(1)}/">saibro.app.br{m.group(1)}</a>', out)
    return out


def render_blocks(doc: Doc) -> str:
    parts: list[str] = []
    section = 0
    for b in doc.blocks:
        if b.kind == "h2":
            section += 1
            parts.append(f'<h2 id="s{section}">{inline(b.text)}</h2>')
        elif b.kind == "p":
            if VERSION_RE.match(b.text):
                parts.append(f'<p class="version">{inline(b.text)}</p>')
            else:
                parts.append(f"<p>{inline(b.text)}</p>")
        elif b.kind == "ul":
            items = "".join(f"<li>{inline(i)}</li>" for i in b.items)
            parts.append(f"<ul>{items}</ul>")
    return "\n".join(parts)


FAVICON = (
    "data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%20100%20100%22%3E"
    "%3Crect%20width%3D%22100%22%20height%3D%22100%22%20rx%3D%2220%22%20fill%3D%22%2333473A%22%2F%3E"
    "%3Cg%20transform%3D%22translate(15%2015)%20scale(0.7)%22%3E"
    "%3Cpath%20d%3D%22M50%208%20A42%2042%200%200%200%2050%2092%20C14%2057%2086%2043%2050%208%20Z%22%20fill%3D%22%23D8C9AC%22%20transform%3D%22translate(-4%20-5.5)%22%2F%3E"
    "%3Cpath%20d%3D%22M50%208%20A42%2042%200%200%201%2050%2092%20C14%2057%2086%2043%2050%208%20Z%22%20fill%3D%22%23CDBE9F%22%20transform%3D%22translate(4%205.5)%22%2F%3E"
    "%3C%2Fg%3E%3C%2Fsvg%3E"
)

MARK = (
    '<svg class="mark" viewBox="0 0 100 100" aria-hidden="true">'
    '<rect width="100" height="100" rx="20" fill="var(--mark-bg)"/>'
    '<g transform="translate(15 15) scale(0.7)">'
    '<path d="M50 8 A42 42 0 0 0 50 92 C14 57 86 43 50 8 Z" fill="#D8C9AC" transform="translate(-4 -5.5)"/>'
    '<path d="M50 8 A42 42 0 0 1 50 92 C14 57 86 43 50 8 Z" fill="#CDBE9F" transform="translate(4 5.5)"/>'
    "</g></svg>"
)

CSS = """
:root {
  --bg: #EFEAE1; --surface: #F7F4EC; --ink: #1F2C24; --ink2: #3F5648; --ink3: #6B7A6F;
  --line: rgba(31, 44, 36, 0.14); --accent: #33473A; --sand: #D8C9AC; --mark-bg: #33473A;
  --focus: #33473A;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0E1710; --surface: #15221A; --ink: #EFEAE1; --ink2: #CDBE9F; --ink3: #9BA898;
    --line: rgba(239, 234, 225, 0.16); --accent: #D8C9AC; --sand: #D8C9AC; --mark-bg: #1F2C24;
    --focus: #D8C9AC;
  }
}
:root[data-theme="dark"] {
  --bg: #0E1710; --surface: #15221A; --ink: #EFEAE1; --ink2: #CDBE9F; --ink3: #9BA898;
  --line: rgba(239, 234, 225, 0.16); --accent: #D8C9AC; --sand: #D8C9AC; --mark-bg: #1F2C24;
  --focus: #D8C9AC;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font-family: 'Archivo', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  font-size: 17px; line-height: 1.6; -webkit-font-smoothing: antialiased;
}
a { color: var(--accent); text-decoration: underline; text-underline-offset: 3px; text-decoration-thickness: 1px; }
a:hover { text-decoration-thickness: 2px; }
a:focus-visible, .nav a:focus-visible { outline: 2px solid var(--focus); outline-offset: 3px; border-radius: 4px; }
.wrap { max-width: 720px; margin: 0 auto; padding: 0 16px; }
.top { border-bottom: 1px solid var(--line); }
.top .wrap { display: flex; align-items: center; justify-content: space-between; gap: 16px; min-height: 64px; flex-wrap: wrap; }
.brand { display: inline-flex; align-items: center; gap: 10px; color: var(--ink); text-decoration: none; font-weight: 600; letter-spacing: 0.01em; }
.brand .mark { width: 28px; height: 28px; border-radius: 7px; }
.nav { display: flex; gap: 4px; flex-wrap: wrap; margin: 0; padding: 0; list-style: none; }
.nav a { display: inline-block; padding: 8px 12px; border-radius: 999px; color: var(--ink2); text-decoration: none; font-size: 15px; font-weight: 500; }
.nav a:hover { background: var(--surface); }
.nav a[aria-current="page"] { background: var(--accent); color: var(--bg); }
main { padding: 40px 0 64px; }
article h1 { font-size: 36px; line-height: 1.15; letter-spacing: -0.02em; font-weight: 700; margin: 0 0 8px; }
article .version { color: var(--ink3); font-size: 15px; margin: 0 0 32px; }
article h2 { font-size: 22px; line-height: 1.3; letter-spacing: -0.01em; font-weight: 600; margin: 40px 0 12px; padding-top: 20px; border-top: 1px solid var(--line); }
article p { margin: 0 0 16px; }
article ul { margin: 0 0 16px; padding-left: 22px; }
article li { margin: 0 0 8px; }
article li::marker { color: var(--ink3); }
.foot { border-top: 1px solid var(--line); padding: 24px 0 40px; color: var(--ink3); font-size: 14px; }
.foot .wrap { display: flex; gap: 8px 24px; flex-wrap: wrap; justify-content: space-between; }
@media (max-width: 480px) {
  body { font-size: 16px; }
  article h1 { font-size: 30px; }
  main { padding-top: 28px; }
}
@media print {
  .top, .foot { display: none; }
  body { background: #fff; color: #000; font-size: 12pt; }
  a { color: #000; }
}
"""


def render_page(slug: str, doc: Doc, description: str) -> str:
    nav = "".join(
        f'<li><a href="/{p.slug}/"{" aria-current=\"page\"" if p.slug == slug else ""}>{p.nav}</a></li>'
        for p in PAGES
    )
    version_meta = f' · versão {doc.version}' if doc.version else ""
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(doc.title)} · Saibro</title>
  <meta name="description" content="{html.escape(description, quote=True)}">
  <meta name="color-scheme" content="light dark">
  <link rel="canonical" href="https://saibro.app.br/{slug}/">
  <link rel="icon" type="image/svg+xml" href="{FAVICON}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&display=swap">
  <style>{CSS}</style>
</head>
<body>
  <header class="top">
    <div class="wrap">
      <a class="brand" href="/">{MARK}<span>Saibro</span></a>
      <nav aria-label="Páginas legais"><ul class="nav">{nav}</ul></nav>
    </div>
  </header>
  <main class="wrap">
    <article>
      <h1>{html.escape(doc.title)}</h1>
{render_blocks(doc)}
    </article>
  </main>
  <footer class="foot">
    <div class="wrap">
      <span>Saibro · mantido por Vitor Starling Castro · saibro.app.br{version_meta}</span>
      <a href="mailto:privacidade@saibro.app.br">privacidade@saibro.app.br</a>
    </div>
  </footer>
</body>
</html>
"""


# --- texto simples para o app ------------------------------------------------


def render_plain(doc: Doc) -> str:
    lines: list[str] = []
    for b in doc.blocks:
        if b.kind == "h2":
            lines.append("")
            lines.append(b.text)
            lines.append("")
        elif b.kind == "p":
            lines.append(b.text)
            lines.append("")
        elif b.kind == "ul":
            lines.extend(f"- {i}" for i in b.items)
            lines.append("")
    text = "\n".join(lines).strip("\n") + "\n"
    return re.sub(r"\n{3,}", "\n\n", text)


DART_TEMPLATE = """/// Textos de Termos de Uso e Política de Privacidade — o mesmo conteúdo que
/// está publicado em https://saibro.app.br (repo `saibro-site`, #37/#80).
///
/// **Gerado**: não editar à mão. A fonte é `src/*.md` no repo `saibro-site`;
/// `python src/build.py --dart <este arquivo>` regenera o site e este arquivo
/// de uma vez, para os dois nunca divergirem.
///
/// A versão em [LegalContent.policyVersion] tem que casar com
/// `SupabaseConfig.policyVersion` (define do app) e `SAIBRO_POLICY_VERSION`
/// do backend — `legal_pages_test` cobra o par do app.
library;

class LegalContent {
  LegalContent._();

  static const String policyVersion = '{version}';

  /// Canal do Encarregado (DPO), o mesmo de `SAIBRO_DPO_EMAIL` no backend.
  static const String dpoEmail = 'privacidade@saibro.app.br';

  static const String termsUrl = '{termsUrl}';
  static const String privacyUrl = '{privacyUrl}';
  static const String deleteAccountUrl = '{deleteAccountUrl}';

  static const String terms = r'''
{terms}''';

  static const String privacy = r'''
{privacy}''';
}
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dart", type=Path, help="regenera também o legal_content.dart do app")
    args = ap.parse_args()

    docs: dict[str, Doc] = {}
    for page in PAGES:
        doc = parse((SRC / page.source).read_text(encoding="utf-8"))
        docs[page.slug] = doc
        out = ROOT / page.slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_page(page.slug, doc, page.description), encoding="utf-8", newline="\n")
        print(f"{out.relative_to(ROOT)}  ({doc.title}, versão {doc.version})")

    versions = {docs["termos"].version, docs["privacidade"].version}
    if len(versions) != 1 or None in versions:
        raise SystemExit(f"Termos e Política precisam da mesma `Versão AAAA-MM-DD`: {versions}")

    if args.dart:
        by_slug = {p.slug: p for p in PAGES}
        version = docs["termos"].version
        dart = (
            DART_TEMPLATE.replace("{version}", version)
            .replace("{termsUrl}", by_slug["termos"].url)
            .replace("{privacyUrl}", by_slug["privacidade"].url)
            .replace("{deleteAccountUrl}", by_slug["excluir-conta"].url)
            .replace("{terms}", render_plain(docs["termos"]))
            .replace("{privacy}", render_plain(docs["privacidade"]))
        )
        if "'''" in render_plain(docs["termos"]) + render_plain(docs["privacidade"]):
            raise SystemExit("texto contém ''' — quebraria a raw string do Dart")
        args.dart.write_text(dart, encoding="utf-8", newline="\n")
        print(f"{args.dart}  (versão {version})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
