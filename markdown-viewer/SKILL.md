---
name: markdown-viewer
description: |
  Render and display Markdown files with rich formatting in the terminal or as HTML output.
  Use this skill when Claude needs to:
  1. Render Markdown files to styled terminal output with syntax highlighting.
  2. Convert Markdown to HTML for browser preview.
  3. Display tables, code blocks, and other Markdown elements in a readable format.
  4. Serve a live local preview server for a Markdown file.
  5. Diff two Markdown documents and highlight structural changes.
  This skill turns raw Markdown text into human-friendly formatted output across multiple targets.
version: 0.1.0
tags:
  - markdown
  - rendering
  - preview
  - documentation
  - formatting
---

## Skill: Markdown Viewer

### Role Definition

You are an expert documentation renderer. Your core responsibility is to take raw Markdown source (from files, URLs, or stdin) and produce rich, readable output. You select the best output target based on context—terminal ANSI colour, standalone HTML, or a live HTTP preview server—and ensure all Markdown features (headings, tables, fenced code blocks, task lists, images, footnotes) are handled correctly.

### Core Workflow

1. **Input Resolution**
   - **Step 1.1**: Determine the input source: local file path, URL, or piped stdin.
   - **Step 1.2**: Read and validate that the content is parseable Markdown.
   - **Step 1.3**: If a file path is given, resolve it to an absolute path and watch for changes when in live-preview mode.

2. **Rendering Mode Selection**
   - **Step 2.1**: Choose the output mode based on flags or environment:
     - `terminal` – ANSI-styled output printed to stdout (default when no GUI is available).
     - `html` – Write a self-contained HTML file and optionally open a browser.
     - `serve` – Start a local HTTP server that auto-refreshes when the source file changes.
   - **Step 2.2**: Apply optional theming (light / dark / custom CSS) when rendering HTML.

3. **Content Parsing**
   - **Step 3.1**: Parse the Markdown AST using a CommonMark-compliant parser.
   - **Step 3.2**: Apply extensions: GitHub Flavored Markdown (tables, task lists, strikethrough), syntax highlighting for fenced code blocks, and footnotes.
   - **Step 3.3**: Resolve relative image and link paths relative to the source file location.

4. **Terminal Rendering**
   - **Step 4.1**: Map Markdown elements to ANSI escape sequences:
     - Headings → bold + colour (H1 cyan, H2 yellow, H3 white bold).
     - Bold / italic → ANSI bold / dim.
     - Code blocks → monospace with a contrasting background colour.
     - Blockquotes → indented with a leading `│` character.
     - Tables → aligned columns with Unicode box-drawing characters.
     - Task lists → `[x]` or `[ ]` rendered with checkmark symbols.
   - **Step 4.2**: Wrap long lines at the detected terminal width.
   - **Step 4.3**: Page output through a pager (e.g. `less -R`) when content exceeds terminal height.

5. **HTML Rendering**
   - **Step 5.1**: Wrap the rendered body in a minimal but complete HTML5 document.
   - **Step 5.2**: Embed a lightweight CSS stylesheet (light or dark theme).
   - **Step 5.3**: Embed highlight.js for client-side code syntax highlighting.
   - **Step 5.4**: Write output to `<source-name>.html` or a user-specified path.

6. **Live Preview Server**
   - **Step 6.1**: Bind a local HTTP server (default port 8765).
   - **Step 6.2**: Serve the rendered HTML with an injected WebSocket snippet.
   - **Step 6.3**: Watch the source file for changes using filesystem events.
   - **Step 6.4**: On change, re-render and push a reload message over the WebSocket so the browser refreshes automatically.
   - **Step 6.5**: Print the local URL to stdout and optionally open the default browser.

7. **Diff Mode**
   - **Step 7.1**: Accept two Markdown files as input.
   - **Step 7.2**: Parse both into ASTs and produce a semantic diff (added/removed/changed nodes).
   - **Step 7.3**: Render the diff with green/red colouring for additions/removals.

### Format Rules

- **CLI interface**: The script is invoked as `python markdown_viewer.py [OPTIONS] <file>`.
- **Options**:
  - `--mode terminal|html|serve` (default: `terminal`)
  - `--theme light|dark` (default: `dark`, html/serve only)
  - `--port PORT` (default: 8765, serve only)
  - `--output PATH` (html mode only)
  - `--diff FILE_A FILE_B` (diff mode)
- **Exit codes**: 0 success, 1 input error, 2 render error.

### Anti-Patterns

- **Silent failures**: Never swallow parse errors; always surface them with a clear message and the offending line number.
- **Hardcoded paths**: Always resolve paths relative to CWD or the source file; never embed absolute system paths.
- **Blocking the server loop**: The file-watcher and HTTP server must run in separate threads/async tasks to avoid blocking each other.
- **Unescaped HTML in terminal mode**: Do not emit raw HTML tags to the terminal; strip or convert them.
- **Ignoring terminal capability**: Check `$TERM` and `NO_COLOR`; fall back to plain text if ANSI is unsupported.

### Checklist

After rendering a document, verify:

- [ ] All headings are visually distinct and properly nested.
- [ ] Fenced code blocks display with syntax highlighting (or fall back gracefully).
- [ ] Tables are aligned and all rows have the correct column count.
- [ ] Task list items show the correct checked/unchecked state.
- [ ] Relative links and images are resolved correctly.
- [ ] Long lines are wrapped at the terminal width (terminal mode).
- [ ] The HTML output is a valid, self-contained document (html mode).
- [ ] The live server reloads the browser within 1 second of a file change (serve mode).
- [ ] Exit code is 0 on success and non-zero on any error.

---
