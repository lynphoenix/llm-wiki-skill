#!/bin/bash

# Simple install script for llm-wiki-skill

SKILL_DIR="$HOME/.claude/skills/llm-wiki"

echo "Installing LLM Wiki Skill..."

mkdir -p "$SKILL_DIR"
cp SKILL.md "$SKILL_DIR/"

echo "Installation complete!"
echo "You can now use the skill in Claude Code."
echo "Try: '帮我建一个 wiki 来管理论文' or '/llm-wiki-skill'"
