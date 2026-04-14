# LLM Wiki Skill

A Claude Code Skill for managing LLM paper knowledge base, based on Karpathy's "LLM Wiki" pattern.

## What is This?

LLM Wiki is a personal knowledge management tool where **LLM acts as the "compiler" and "administrator"** of your knowledge base. You just ask questions, and the wiki maintains itself in the background.

## Core Features

| Feature | Description |
|---------|-------------|
| **Ingest** | Read PDF papers → Extract structured info → Generate wiki entries |
| **Query** | Ask questions about papers, get answers with citations |
| **Maintain** | Check cross-references, detect contradictions, update index |
| **Search** | Full-text search across all papers and concepts |

## Quick Start

### 1. Install the Skill

You can install the skill and its scripts using the install script:

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

Or manually:
```bash
mkdir -p ~/.claude/skills/llm-wiki
cp SKILL.md ~/.claude/skills/llm-wiki/
```

### 2. Initialize Wiki

Tell Claude Code:
> "帮我建一个 wiki 来管理论文" (Help me set up a wiki to manage papers)

Claude will use the `scripts/init_wiki.sh` script to set up the directory structure.

### 3. Configure (Optional)

Create `~/Documents/wikis/config.yaml`:

```yaml
wiki_path: ~/Documents/wikis
marker_api_key: your_marker_api_key  # Optional, for GPU acceleration

ingest:
  auto_detect_raw_dir: true
  raw_dir: ~/Documents/wikis/raw

maintain:
  auto_maintain: false
```

### 4. Start Using

**Ingest a paper:**
> "帮我把这篇论文加到wiki" (Add this paper to wiki)

**Batch Ingest:**
> "帮我管理这个目录下的论文" (Help me manage the papers in this directory)
> Claude can use `scripts/ingest_papers.py` to generate a summary report.

**Ingest a Codebase:**
> "帮我分析这个代码库" (Help me analyze this codebase)
> Claude will use `scripts/ingest_repo.py` to scan the codebase and create a code wiki.

**Query:**
> "这个领域最近有什么进展?" (What's new in this field?)
> "这个项目的鉴权逻辑是怎么串起来的？" (How does the authentication flow work in this project?)

**Search:**
> "搜索 anomaly detection" (Search for anomaly detection)

**Maintain:**
> "检查一下wiki" (Check the wiki)

## Wiki Structure

```
~/Documents/wikis/
├── config.yaml      # Configuration
├── index.md         # Global index
├── sources/         # Paper sources (one .md per paper)
│   └── <paper-slug>.md
├── concepts/        # Concept pages
│   └── <concept-slug>.md
├── raw/             # Raw PDFs
│   └── *.pdf
└── docs/           # Documentation (optional)
```

## Architecture

```
┌─────────────────────────────────────────┐
│  User (asks questions)                   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  SKILL.md (workflow definitions)         │
│  ├── Ingest: PDF/Code → Wiki entry      │
│  ├── Query: Question → Answer          │
│  ├── Search: Keyword → Results          │
│  └── Maintain: Check & Fix              │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Wiki Content                           │
│  ├── sources/ (papers)                 │
│  ├── concepts/ (topics)                 │
│  └── index.md (navigation)             │
└─────────────────────────────────────────┘
```

## Dependencies

### Optional: Marker API (GPU-accelerated PDF parsing)

For faster PDF parsing, deploy Marker on a GPU server. The skill is configured to use a local server at `http://localhost:5203/v1/parse/file` by default.

```bash
# Install
pip install marker-pdf fastapi uvicorn python-multipart

# Run server
python scripts/marker_server.py --port 5203 --gpu 0
```

If Marker is not available, the skill intelligently falls back to Claude's native PDF parsing.

## Customization

### Adding Custom Tags

Edit the tag list in `config.yaml`:

```yaml
default_tags:
  - llm
  - your-custom-tag
```

### Custom Templates

Modify the source/concept templates in `SKILL.md` to match your preferred format.

## License

MIT License
