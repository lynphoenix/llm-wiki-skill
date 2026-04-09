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

Copy `SKILL.md` to your Claude Code skills directory:

```bash
mkdir -p ~/.claude/skills/llm-wiki
cp SKILL.md ~/.claude/skills/llm-wiki/
```

### 2. Initialize Wiki

Tell Claude Code:
> "帮我建一个 wiki 来管理论文" (Help me set up a wiki to manage papers)

Or manually:
```bash
mkdir -p ~/Documents/wikis
```

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

**Query:**
> "这个领域最近有什么进展?" (What's new in this field?)

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
│  ├── Ingest: PDF → Wiki entry           │
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

## Workflow Details

### Ingest

1. **Locate PDF** - User specifies path or uses default
2. **Extract Text** - Marker API (GPU-accelerated) or Claude native PDF parsing
3. **LLM Analysis** - Extract title, authors, tags, summary, key concepts
4. **Write Wiki** - Create source file + update concepts + update index

### Query

1. **Analyze Question** - Extract key concepts and tags
2. **Load Wiki** - Read relevant source and concept files
3. **Generate Answer** - Based on wiki content, cite sources

### Maintain

1. **Cross-reference integrity** - Check all `[[wiki-links]]` exist
2. **Contradiction detection** - Flag conflicting definitions
3. **Orphan pages** - Find unreferenced pages
4. **Index sync** - Ensure index.md reflects actual content

## Dependencies

### Optional: Marker API (GPU-accelerated PDF parsing)

For faster PDF parsing, deploy Marker on a GPU server:

```bash
# Install
pip install marker-pdf

# Run server
marker_server.py --port 5203 --gpu 7
```

Without Marker, the skill falls back to Claude's native PDF parsing.

## Customization

### Adding Custom Tags

Edit the tag list in `SKILL.md` or add to `config.yaml`:

```yaml
default_tags:
  - llm
  - your-custom-tag
```

### Custom Templates

Modify the source/concept templates in `SKILL.md` to match your preferred format.

## License

MIT License

## References

- [Karpathy's LLM Wiki](https://github.com/karpathy/llm-wiki) - The inspiration for this pattern
- [Marker PDF Parser](https://github.com/VikParuchuri/marker) - GPU-accelerated PDF to Markdown
