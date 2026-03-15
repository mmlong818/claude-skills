#!/usr/bin/env python3
"""
markdown_viewer.py – Render Markdown to terminal, HTML, or a live preview server.

Usage:
    python markdown_viewer.py [OPTIONS] <file>
    python markdown_viewer.py --diff FILE_A FILE_B

Options:
    --mode terminal|html|serve   Output mode (default: terminal)
    --theme light|dark           HTML/serve theme (default: dark)
    --port PORT                  Port for serve mode (default: 8765)
    --output PATH                Output file for html mode
    --diff FILE_A FILE_B         Show semantic diff between two Markdown files
    --no-pager                   Disable pager in terminal mode
    --width N                    Override terminal width (default: auto-detect)
"""

import argparse
import html as html_module
import os
import re
import shutil
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Minimal CommonMark-style tokeniser (no external dependencies)
# ---------------------------------------------------------------------------

TOKEN_HEADING = "heading"
TOKEN_CODE_BLOCK = "code_block"
TOKEN_BLOCKQUOTE = "blockquote"
TOKEN_HR = "hr"
TOKEN_TABLE = "table"
TOKEN_LIST = "list"
TOKEN_PARAGRAPH = "paragraph"
TOKEN_BLANK = "blank"


def _parse_inline(text: str) -> str:
    """Convert inline Markdown to ANSI-escaped terminal text."""
    # Bold-italic
    text = re.sub(r"\*\*\*(.+?)\*\*\*", "\033[1;3m\\1\033[0m", text)
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", "\033[1m\\1\033[0m", text)
    text = re.sub(r"__(.+?)__", "\033[1m\\1\033[0m", text)
    # Italic
    text = re.sub(r"\*(.+?)\*", "\033[3m\\1\033[0m", text)
    text = re.sub(r"_(.+?)_", "\033[3m\\1\033[0m", text)
    # Strikethrough
    text = re.sub(r"~~(.+?)~~", "\033[9m\\1\033[0m", text)
    # Inline code
    text = re.sub(r"`(.+?)`", "\033[7m \\1 \033[0m", text)
    # Links  [label](url)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", "\033[4;36m\\1\033[0m", text)
    # Images ![alt](url) → just show alt text
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", "[image: \\1]", text)
    return text


def _parse_inline_html(text: str) -> str:
    """Convert inline Markdown to HTML."""
    text = html_module.escape(text)
    # Bold-italic
    text = re.sub(r"\*\*\*(.+?)\*\*\*", "<strong><em>\\1</em></strong>", text)
    text = re.sub(r"\*\*(.+?)\*\*", "<strong>\\1</strong>", text)
    text = re.sub(r"__(.+?)__", "<strong>\\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", "<em>\\1</em>", text)
    text = re.sub(r"_(.+?)_", "<em>\\1</em>", text)
    text = re.sub(r"~~(.+?)~~", "<del>\\1</del>", text)
    text = re.sub(r"`(.+?)`", "<code>\\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", '<a href="\\2">\\1</a>', text)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", '<img src="\\2" alt="\\1">', text)
    return text


class MarkdownParser:
    """Very small block-level Markdown parser returning a list of token dicts."""

    HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)")
    HR_RE = re.compile(r"^(\*{3,}|-{3,}|_{3,})\s*$")
    TABLE_SEP_RE = re.compile(r"^\|?[\s\-:|]+\|[\s\-:|]*$")
    UL_RE = re.compile(r"^(\s*)[-*+]\s+(.*)")
    OL_RE = re.compile(r"^(\s*)\d+\.\s+(.*)")

    def parse(self, source: str) -> list:
        lines = source.splitlines()
        tokens = []
        i = 0
        while i < len(lines):
            line = lines[i]

            # Blank line
            if not line.strip():
                tokens.append({"type": TOKEN_BLANK})
                i += 1
                continue

            # ATX Heading
            m = self.HEADING_RE.match(line)
            if m:
                tokens.append({"type": TOKEN_HEADING, "level": len(m.group(1)), "text": m.group(2)})
                i += 1
                continue

            # Horizontal rule
            if self.HR_RE.match(line):
                tokens.append({"type": TOKEN_HR})
                i += 1
                continue

            # Fenced code block
            fence_match = re.match(r"^(`{3,}|~{3,})(.*)", line)
            if fence_match:
                fence = fence_match.group(1)
                lang = fence_match.group(2).strip()
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith(fence[:3]):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # skip closing fence
                tokens.append({"type": TOKEN_CODE_BLOCK, "lang": lang, "code": "\n".join(code_lines)})
                continue

            # Blockquote
            if line.startswith(">"):
                bq_lines = []
                while i < len(lines) and lines[i].startswith(">"):
                    bq_lines.append(lines[i].lstrip(">").lstrip())
                    i += 1
                tokens.append({"type": TOKEN_BLOCKQUOTE, "lines": bq_lines})
                continue

            # Table (detect by pipe characters and separator row)
            if "|" in line and i + 1 < len(lines) and self.TABLE_SEP_RE.match(lines[i + 1]):
                headers = [c.strip() for c in line.strip("|").split("|")]
                i += 2  # skip separator
                rows = []
                while i < len(lines) and "|" in lines[i]:
                    rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                    i += 1
                tokens.append({"type": TOKEN_TABLE, "headers": headers, "rows": rows})
                continue

            # List
            ul_m = self.UL_RE.match(line)
            ol_m = self.OL_RE.match(line)
            if ul_m or ol_m:
                ordered = bool(ol_m)
                items = []
                while i < len(lines):
                    ul = self.UL_RE.match(lines[i])
                    ol = self.OL_RE.match(lines[i])
                    if ul:
                        items.append({"ordered": False, "text": ul.group(2)})
                        i += 1
                    elif ol:
                        items.append({"ordered": True, "text": ol.group(2)})
                        i += 1
                    else:
                        break
                tokens.append({"type": TOKEN_LIST, "ordered": ordered, "items": items})
                continue

            # Paragraph (collect until blank line or block element)
            para_lines = []
            while i < len(lines) and lines[i].strip():
                if (self.HEADING_RE.match(lines[i]) or self.HR_RE.match(lines[i])
                        or lines[i].startswith(">") or re.match(r"^(`{3,}|~{3,})", lines[i])):
                    break
                para_lines.append(lines[i])
                i += 1
            if para_lines:
                tokens.append({"type": TOKEN_PARAGRAPH, "lines": para_lines})
            continue

        return tokens


# ---------------------------------------------------------------------------
# Terminal renderer
# ---------------------------------------------------------------------------

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_CYAN = "\033[36m"
ANSI_YELLOW = "\033[33m"
ANSI_WHITE = "\033[37m"
ANSI_GREEN = "\033[32m"
ANSI_BLUE = "\033[34m"
ANSI_BG_DARK = "\033[48;5;236m"

HEADING_STYLES = {
    1: f"\033[1;96m",   # bold bright-cyan
    2: f"\033[1;93m",   # bold bright-yellow
    3: f"\033[1;97m",   # bold bright-white
    4: f"\033[1;95m",
    5: f"\033[1;92m",
    6: f"\033[1;94m",
}


def _wrap(text: str, width: int, indent: str = "") -> list[str]:
    """Wrap plain text (stripping ANSI for width measurement) to *width* cols."""
    ansi_escape = re.compile(r"\033\[[0-9;]*m")
    words = text.split()
    lines = []
    current = indent
    current_len = len(indent)
    for word in words:
        visible_len = len(ansi_escape.sub("", word))
        if current_len + visible_len + (1 if current_len > len(indent) else 0) > width:
            if current.strip():
                lines.append(current.rstrip())
            current = indent + word
            current_len = len(indent) + visible_len
        else:
            if current_len > len(indent):
                current += " " + word
                current_len += 1 + visible_len
            else:
                current += word
                current_len += visible_len
    if current.strip():
        lines.append(current)
    return lines or [indent]


class TerminalRenderer:
    def __init__(self, width: int = 0, use_ansi: bool = True):
        self.width = width or (shutil.get_terminal_size().columns or 80)
        self.use_ansi = use_ansi and os.environ.get("NO_COLOR") is None and sys.stdout.isatty()

    def _c(self, code: str, text: str) -> str:
        if not self.use_ansi:
            return text
        return f"{code}{text}{ANSI_RESET}"

    def render(self, tokens: list) -> str:
        output = []
        for tok in tokens:
            t = tok["type"]
            if t == TOKEN_BLANK:
                output.append("")
            elif t == TOKEN_HEADING:
                self._render_heading(tok, output)
            elif t == TOKEN_HR:
                output.append(self._c(ANSI_DIM, "─" * self.width))
            elif t == TOKEN_CODE_BLOCK:
                self._render_code_block(tok, output)
            elif t == TOKEN_BLOCKQUOTE:
                self._render_blockquote(tok, output)
            elif t == TOKEN_TABLE:
                self._render_table(tok, output)
            elif t == TOKEN_LIST:
                self._render_list(tok, output)
            elif t == TOKEN_PARAGRAPH:
                self._render_paragraph(tok, output)
        return "\n".join(output)

    def _render_heading(self, tok: dict, output: list):
        level = tok["level"]
        prefix = "#" * level + " "
        style = HEADING_STYLES.get(level, ANSI_BOLD)
        text = _parse_inline(tok["text"]) if self.use_ansi else tok["text"]
        line = self._c(style, prefix + tok["text"]) if self.use_ansi else prefix + tok["text"]
        output.append("")
        output.append(line)
        if level == 1:
            output.append(self._c(ANSI_CYAN, "═" * min(len(prefix + tok["text"]), self.width)))
        elif level == 2:
            output.append(self._c(ANSI_YELLOW, "─" * min(len(prefix + tok["text"]), self.width)))
        output.append("")

    def _render_code_block(self, tok: dict, output: list):
        lang = tok.get("lang", "")
        border = self._c(ANSI_DIM, "┌" + ("─" * (self.width - 2)) + "┐")
        border_bot = self._c(ANSI_DIM, "└" + ("─" * (self.width - 2)) + "┘")
        label = self._c(ANSI_DIM, f" {lang} ") if lang else ""
        output.append(border + label)
        for code_line in tok["code"].splitlines():
            padded = code_line[: self.width - 4]
            if self.use_ansi:
                output.append(f"\033[48;5;236m  {padded:<{self.width - 4}}  \033[0m")
            else:
                output.append(f"  {padded}")
        output.append(border_bot)

    def _render_blockquote(self, tok: dict, output: list):
        for bq_line in tok["lines"]:
            inline = _parse_inline(bq_line) if self.use_ansi else bq_line
            bar = self._c(ANSI_CYAN, "│")
            for wrapped in _wrap(inline, self.width - 4, "  "):
                output.append(f"{bar} {wrapped}")

    def _render_table(self, tok: dict, output: list):
        headers = tok["headers"]
        rows = tok["rows"]
        all_rows = [headers] + rows
        col_widths = [max(len(str(r[c])) if c < len(r) else 0 for r in all_rows)
                      for c in range(len(headers))]
        sep = "┼".join("─" * (w + 2) for w in col_widths)
        header_sep = "┼".join("═" * (w + 2) for w in col_widths)

        def fmt_row(row, bold=False):
            cells = []
            for i, w in enumerate(col_widths):
                cell = str(row[i]) if i < len(row) else ""
                if bold and self.use_ansi:
                    cells.append(f" {ANSI_BOLD}{cell:<{w}}{ANSI_RESET} ")
                else:
                    cells.append(f" {cell:<{w}} ")
            return "│" + "│".join(cells) + "│"

        output.append("┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐")
        output.append(fmt_row(headers, bold=True))
        output.append("╞" + header_sep + "╡")
        for row in rows:
            output.append(fmt_row(row))
        output.append("└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘")

    def _render_list(self, tok: dict, output: list):
        for idx, item in enumerate(tok["items"]):
            bullet = f"{idx + 1}." if item["ordered"] else "•"
            text = item["text"]
            # Task list
            task_m = re.match(r"^\[([ xX])\]\s+(.*)", text)
            if task_m:
                checked = task_m.group(1).lower() == "x"
                label = "☑" if checked else "☐"
                text = f"{label} {task_m.group(2)}"
            inline = _parse_inline(text) if self.use_ansi else text
            prefix = f"  {bullet} "
            for line in _wrap(inline, self.width, " " * len(prefix)):
                output.append(prefix + line[len(prefix):] if line.startswith(" " * len(prefix)) else prefix + line)

    def _render_paragraph(self, tok: dict, output: list):
        text = " ".join(tok["lines"])
        inline = _parse_inline(text) if self.use_ansi else text
        for line in _wrap(inline, self.width):
            output.append(line)


# ---------------------------------------------------------------------------
# HTML renderer
# ---------------------------------------------------------------------------

DARK_CSS = """
body{font-family:system-ui,sans-serif;background:#1e1e2e;color:#cdd6f4;max-width:860px;margin:40px auto;padding:0 20px;line-height:1.7}
h1,h2,h3,h4,h5,h6{color:#89dceb;margin-top:1.6em}
h1{border-bottom:2px solid #89dceb;padding-bottom:.3em}
h2{border-bottom:1px solid #45475a;padding-bottom:.2em}
a{color:#89b4fa}
code{background:#313244;padding:2px 6px;border-radius:4px;font-size:.9em}
pre{background:#181825;border:1px solid #45475a;border-radius:8px;padding:1.2em;overflow-x:auto}
pre code{background:none;padding:0}
blockquote{border-left:4px solid #89dceb;margin:0;padding:.5em 1em;background:#181825;border-radius:0 8px 8px 0}
table{border-collapse:collapse;width:100%}
th,td{border:1px solid #45475a;padding:.5em .8em;text-align:left}
th{background:#313244}
tr:nth-child(even){background:#181825}
hr{border:none;border-top:1px solid #45475a}
img{max-width:100%}
"""

LIGHT_CSS = """
body{font-family:system-ui,sans-serif;background:#fff;color:#24292f;max-width:860px;margin:40px auto;padding:0 20px;line-height:1.7}
h1,h2,h3,h4,h5,h6{color:#0550ae;margin-top:1.6em}
h1{border-bottom:2px solid #0550ae;padding-bottom:.3em}
h2{border-bottom:1px solid #d0d7de;padding-bottom:.2em}
a{color:#0550ae}
code{background:#f6f8fa;padding:2px 6px;border-radius:4px;font-size:.9em;border:1px solid #d0d7de}
pre{background:#f6f8fa;border:1px solid #d0d7de;border-radius:8px;padding:1.2em;overflow-x:auto}
pre code{background:none;padding:0;border:none}
blockquote{border-left:4px solid #0550ae;margin:0;padding:.5em 1em;background:#f6f8fa;border-radius:0 8px 8px 0}
table{border-collapse:collapse;width:100%}
th,td{border:1px solid #d0d7de;padding:.5em .8em;text-align:left}
th{background:#f6f8fa}
tr:nth-child(even){background:#f0f4f8}
hr{border:none;border-top:1px solid #d0d7de}
img{max-width:100%}
"""

WEBSOCKET_SNIPPET = """
<script>
(function(){
  var ws = new WebSocket('ws://' + location.host + '/__ws__');
  ws.onmessage = function(e){ if(e.data === 'reload') location.reload(); };
  ws.onclose = function(){ setTimeout(function(){ location.reload(); }, 1500); };
})();
</script>
"""


class HtmlRenderer:
    def __init__(self, theme: str = "dark", title: str = "Markdown", live: bool = False):
        self.theme = theme
        self.title = title
        self.live = live
        self.css = DARK_CSS if theme == "dark" else LIGHT_CSS

    def render(self, tokens: list) -> str:
        body = self._render_body(tokens)
        ws = WEBSOCKET_SNIPPET if self.live else ""
        return (
            f"<!DOCTYPE html><html lang='en'><head>"
            f"<meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
            f"<title>{html_module.escape(self.title)}</title>"
            f"<style>{self.css}</style></head>"
            f"<body>{body}{ws}</body></html>"
        )

    def _render_body(self, tokens: list) -> str:
        parts = []
        for tok in tokens:
            t = tok["type"]
            if t == TOKEN_BLANK:
                continue
            elif t == TOKEN_HEADING:
                lvl = tok["level"]
                text = _parse_inline_html(tok["text"])
                parts.append(f"<h{lvl}>{text}</h{lvl}>")
            elif t == TOKEN_HR:
                parts.append("<hr>")
            elif t == TOKEN_CODE_BLOCK:
                lang = html_module.escape(tok.get("lang", ""))
                code = html_module.escape(tok["code"])
                cls = f' class="language-{lang}"' if lang else ""
                parts.append(f"<pre><code{cls}>{code}</code></pre>")
            elif t == TOKEN_BLOCKQUOTE:
                inner = " ".join(_parse_inline_html(ln) for ln in tok["lines"])
                parts.append(f"<blockquote><p>{inner}</p></blockquote>")
            elif t == TOKEN_TABLE:
                parts.append(self._render_table_html(tok))
            elif t == TOKEN_LIST:
                parts.append(self._render_list_html(tok))
            elif t == TOKEN_PARAGRAPH:
                text = _parse_inline_html(" ".join(tok["lines"]))
                parts.append(f"<p>{text}</p>")
        return "\n".join(parts)

    def _render_table_html(self, tok: dict) -> str:
        headers = "".join(f"<th>{_parse_inline_html(h)}</th>" for h in tok["headers"])
        rows = ""
        for row in tok["rows"]:
            cells = "".join(f"<td>{_parse_inline_html(c)}</td>" for c in row)
            rows += f"<tr>{cells}</tr>"
        return f"<table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table>"

    def _render_list_html(self, tok: dict) -> str:
        tag = "ol" if tok["ordered"] else "ul"
        items = ""
        for item in tok["items"]:
            text = item["text"]
            task_m = re.match(r"^\[([ xX])\]\s+(.*)", text)
            if task_m:
                checked = 'checked' if task_m.group(1).lower() == "x" else ""
                text = f'<input type="checkbox" {checked} disabled> {_parse_inline_html(task_m.group(2))}'
            else:
                text = _parse_inline_html(text)
            items += f"<li>{text}</li>"
        return f"<{tag}>{items}</{tag}>"


# ---------------------------------------------------------------------------
# Diff renderer (terminal)
# ---------------------------------------------------------------------------

def diff_markdown(source_a: str, source_b: str) -> str:
    """Return a coloured unified-style diff of two Markdown sources."""
    lines_a = source_a.splitlines()
    lines_b = source_b.splitlines()
    import difflib
    diff = list(difflib.unified_diff(lines_a, lines_b, lineterm="", n=3))
    out = []
    for line in diff:
        if line.startswith("+++") or line.startswith("---"):
            out.append(f"\033[1m{line}\033[0m")
        elif line.startswith("+"):
            out.append(f"\033[32m{line}\033[0m")
        elif line.startswith("-"):
            out.append(f"\033[31m{line}\033[0m")
        elif line.startswith("@@"):
            out.append(f"\033[36m{line}\033[0m")
        else:
            out.append(line)
    return "\n".join(out) if out else "(no differences)"


# ---------------------------------------------------------------------------
# Live preview server
# ---------------------------------------------------------------------------

class LiveServer:
    def __init__(self, source_path: Path, theme: str, port: int):
        self.source_path = source_path
        self.theme = theme
        self.port = port
        self._html = ""
        self._lock = threading.Lock()
        self._clients: list = []
        self._rebuild()

    def _rebuild(self):
        source = self.source_path.read_text(encoding="utf-8")
        parser = MarkdownParser()
        tokens = parser.parse(source)
        renderer = HtmlRenderer(theme=self.theme, title=self.source_path.name, live=True)
        with self._lock:
            self._html = renderer.render(tokens)

    def _watch(self):
        mtime = self.source_path.stat().st_mtime
        while True:
            time.sleep(0.5)
            try:
                new_mtime = self.source_path.stat().st_mtime
            except FileNotFoundError:
                continue
            if new_mtime != mtime:
                mtime = new_mtime
                self._rebuild()
                # Notify clients via a simple flag file approach (no asyncio needed)
                with self._lock:
                    self._reload_flag = True

    def start(self):
        self._reload_flag = False
        watcher = threading.Thread(target=self._watch, daemon=True)
        watcher.start()

        server = self
        port = self.port

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                pass  # suppress access logs

            def do_GET(self):
                if self.path == "/":
                    with server._lock:
                        body = server._html.encode()
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(body)
                elif self.path == "/__poll__":
                    flag = server._reload_flag
                    if flag:
                        with server._lock:
                            server._reload_flag = False
                    data = b"reload" if flag else b"ok"
                    self.send_response(200)
                    self.send_header("Content-Type", "text/plain")
                    self.end_headers()
                    self.wfile.write(data)
                else:
                    self.send_response(404)
                    self.end_headers()

        httpd = HTTPServer(("127.0.0.1", port), Handler)
        url = f"http://127.0.0.1:{port}"
        print(f"Serving preview at {url}  (Ctrl+C to stop)")
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _read_source(path: str) -> str:
    p = Path(path)
    if not p.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Render Markdown to terminal, HTML, or live preview.")
    ap.add_argument("file", nargs="?", help="Markdown file to render")
    ap.add_argument("--mode", choices=["terminal", "html", "serve"], default="terminal")
    ap.add_argument("--theme", choices=["light", "dark"], default="dark")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--output", help="Output HTML file path (html mode)")
    ap.add_argument("--no-pager", action="store_true", dest="no_pager")
    ap.add_argument("--width", type=int, default=0)
    ap.add_argument("--diff", nargs=2, metavar=("FILE_A", "FILE_B"))
    args = ap.parse_args()

    # --- Diff mode ---
    if args.diff:
        src_a = _read_source(args.diff[0])
        src_b = _read_source(args.diff[1])
        print(diff_markdown(src_a, src_b))
        return

    if not args.file:
        if not sys.stdin.isatty():
            source = sys.stdin.read()
            file_path = Path("stdin.md")
        else:
            ap.print_help()
            sys.exit(1)
    else:
        source = _read_source(args.file)
        file_path = Path(args.file).resolve()

    parser = MarkdownParser()
    tokens = parser.parse(source)

    # --- Terminal mode ---
    if args.mode == "terminal":
        renderer = TerminalRenderer(width=args.width)
        rendered = renderer.render(tokens)
        if args.no_pager or not sys.stdout.isatty():
            print(rendered)
        else:
            pager = os.environ.get("PAGER", "less -R")
            pager_cmd = shutil.which(pager.split()[0])
            if pager_cmd:
                import subprocess
                proc = subprocess.Popen(pager.split(), stdin=subprocess.PIPE, text=True)
                try:
                    proc.communicate(input=rendered)
                except BrokenPipeError:
                    pass
            else:
                print(rendered)

    # --- HTML mode ---
    elif args.mode == "html":
        title = file_path.stem if args.file else "Markdown"
        renderer = HtmlRenderer(theme=args.theme, title=title)
        html_out = renderer.render(tokens)
        out_path = args.output or str(file_path.with_suffix(".html"))
        Path(out_path).write_text(html_out, encoding="utf-8")
        print(f"HTML written to {out_path}")

    # --- Serve mode ---
    elif args.mode == "serve":
        if not args.file:
            print("Error: --mode serve requires a file argument.", file=sys.stderr)
            sys.exit(1)
        server = LiveServer(file_path, theme=args.theme, port=args.port)
        server.start()


if __name__ == "__main__":
    main()
