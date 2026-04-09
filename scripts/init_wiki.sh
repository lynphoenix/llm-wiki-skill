#!/bin/bash
# Initialize LLM Wiki directory structure

WIKI_PATH="${1:-$HOME/Documents/wikis}"

echo "Initializing LLM Wiki at: $WIKI_PATH"

mkdir -p "$WIKI_PATH"
mkdir -p "$WIKI_PATH/sources"
mkdir -p "$WIKI_PATH/concepts"
mkdir -p "$WIKI_PATH/raw"
mkdir -p "$WIKI_PATH/docs"

# Create config.yaml if it doesn't exist
if [ ! -f "$WIKI_PATH/config.yaml" ]; then
cat > "$WIKI_PATH/config.yaml" << EOF
wiki_path: $WIKI_PATH
marker_api_key: ""
default_tags: []

ingest:
  auto_detect_raw_dir: true
  raw_dir: $WIKI_PATH/raw

maintain:
  auto_maintain: false
  interval_hours: 24

state:
  initialized: true
  last_maintain: null
  paper_count: 0
  concept_count: 0
  recent_ingest: []
EOF
echo "Created config.yaml"
fi

# Create index.md if it doesn't exist
if [ ! -f "$WIKI_PATH/index.md" ]; then
cat > "$WIKI_PATH/index.md" << EOF
# Wiki Index

最后更新: $(date +%Y-%m-%d)

## 概览

- 论文数量: 0
- 概念数量: 0

## 最近更新

暂无

## 开始使用

使用 Claude Code，说 "帮我把这篇论文加到wiki"，或 "帮我管理这个目录下的论文"
EOF
echo "Created index.md"
fi

echo ""
echo "Wiki initialized at: $WIKI_PATH"
echo "Directory structure:"
ls -la "$WIKI_PATH"
