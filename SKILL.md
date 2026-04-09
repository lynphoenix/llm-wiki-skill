---
name: llm-wiki
description: LLM论文Wiki知识库管理工具。帮你整理、阅读、总结论文，建立个人知识wiki，支持多领域标签。
version: 1.0.0
---

# LLM Wiki Skill

## 概念
这是一个基于 Karpathy "LLM Wiki" 模式的知识管理工具。LLM 作为知识库的"编译器"和"管理员"，用户只管问问题，wiki 在后台自动维护。

## 核心能力
- Ingest: 读取PDF论文，提取内容，生成结构化wiki条目
- Query: 根据wiki内容回答关于论文的问题
- Maintain: 检查交叉引用，标记矛盾，更新索引
- Search: 搜索wiki中的相关内容

## Ingest 工作流

### 触发方式
用户说"帮我管理这个目录下的论文"或"把这篇论文加到wiki"

### 处理流程
1. **定位 PDF**
   - 用户指定路径或使用默认 ~/Documents/wikis/raw/
   - 识别所有 PDF 文件

2. **提取文本**
   优先调用 Marker API（如配置了本地服务器或 API key）：
   ```
   POST https://api.marker.cloud/v1/document
   Headers: Authorization: Bearer <marker_api_key>
   Content-Type: multipart/form-data
   Body: file=<pdf_binary>
   ```

   **Fallback — Claude 原生 PDF 解析：**
   当 Marker 服务不可用时（连接超时/未配置），使用 Claude 的 PDF 解析能力：
   - 将 PDF 文件路径或内容发给 Claude
   - 提示词引导提取结构化信息：
     ```
     请阅读这篇 PDF 论文，提取并返回以下结构化信息（仅返回信息，不要解释）：

     title: <论文标题>
     authors: [<作者1>, <作者2>]
     date: <发表年份>
     tags: [<领域标签1>, <标签2>]
     summary: <3-5句摘要>
     key_concepts: <3-5个关键概念，格式：概念名: 一句话描述>
     contributions: <主要贡献，格式：1. ... 2. ...>
     full_markdown: <完整 Markdown 内容>
     ```
   - 将 `full_markdown` 字段内容保存到 Source 文件的 `## Full Markdown` 区块

3. **LLM 分析内容**
   提取以下信息:
   - title: 论文标题
   - authors: 作者列表
   - date: 发表日期（如有）
   - tags: 自动打标签（llm, embodied-ai, anomaly-detection, graph-neural-network, transformer, gnn, reinforcement-learning, self-supervised, reasoning, planning, control, classification, time-series 等）
   - summary: 3-5句摘要
   - key_concepts: 3-5个关键概念
   - contributions: 主要贡献

4. **写入 Wiki**
   - 创建 source 文件: /wiki_path/sources/<slug>.md
   - 如有关联 concept，更新 concept 文件或创建新 concept
   - 更新 index.md

### Source 文件模板
```markdown
---
title: <title>
authors: [<author1>, <author2>]
date: <date>
tags: [<tag1>, <tag2>]
source_file: <原始PDF路径>
pages: <页码>
---

## Full Markdown

<Marker API 返回的完整 Markdown 内容>

## Summary

<LLM生成的论文摘要，3-5句>

## Key Concepts

- <概念1>: <一句话描述>
- <概念2>: <一句话描述>

## Main Contributions

1. <贡献1>
2. <贡献2>

## Related Concepts

- [[concept-slug]]

## Key Quotes

> "<可引用的重要观点>"
```

### Concept 文件模板
```markdown
---
title: <概念名称>
tags: [<tag1>, <tag2>]
confidence: <0-1>
last_updated: <YYYY-MM-DD>
---

## Definition

<综合多篇论文的定义>

## Key Papers

- [[source-slug]] - <该论文中的描述>
- [[source-slug2]] - <另一论文中的描述>

## Related Concepts

- [[other-concept]]

## Open Questions

<不同论文中矛盾或未达成共识的观点>
```

## Wiki 目录结构
/wiki_path/           # 默认 ~/Documents/wikis
├── config.yaml      # 配置
├── index.md         # 全局索引
├── sources/         # 论文源文件
│   └── <slug>.md
└── concepts/        # 概念页面
    └── <slug>.md

## Query 工作流

### 触发方式
用户直接提问，Skill 自动判断需要查 wiki

### 处理流程
1. **分析问题**
   - 提取问题中的关键概念和标签
   - 判断需要查询哪些 source/concept

2. **加载 Wiki 内容**
   - 读取 index.md 了解整体结构
   - 加载相关的 source 文件（根据 tag 或概念匹配）
   - 加载相关的 concept 文件

3. **生成回答**
   - 基于 wiki 内容回答
   - 标注来源: `来源: [[source-slug]]`
   - 如信息不足，明确告知用户

### 回答格式
```
根据 wiki 中的资料：

<回答内容>

**来源**：
- [[source-slug]] - <相关描述>
- [[source-slug2]] - <另一相关描述>

**相关概念**：
- [[related-concept]]

---
💡 要深入了解，可以查看 [[concept-slug]]
```

## Maintain 工作流

### 触发方式
用户说"检查一下wiki"或"/llm-wiki maintain"

### 检查内容
1. **交叉引用完整性**
   - 检查所有 [[wiki-link]] 是否指向存在的页面
   - 列出 dangling references

2. **矛盾检测**
   - 同一 concept 在不同 source 中的描述是否矛盾
   - 标记可疑内容供人工确认

3. **孤立页面**
   - 没有任何引用指向的页面
   - 建议删除或补充引用

4. **index.md 同步**
   - 检查 index.md 是否反映实际内容

### 自动修复
- 补充缺失的交叉引用
- 删除确认孤立的页面
- 更新 index.md

## Search 工作流

### 触发方式
用户说"搜索 <关键词>"或"/llm-wiki search <关键词>"

### 搜索范围
- 所有 source 和 concept 页面的 title、tags、summary
- 支持 tag 过滤: "搜索 <关键词> --tag llm"

### 返回格式
```
找到 N 个匹配：

1. **[[source-slug]]** (tags: [tag1, tag2])
   摘要: <前两行摘要>

2. **[[concept-slug]]** (tags: [tag1])
   定义: <一句话定义>
```

## 初始设置流程

### 首次使用
1. 用户激活 skill: "帮我建一个 wiki 来管理论文"
2. Skill 确认 wiki 路径（默认 ~/Documents/wikis）
3. 创建目录结构
4. 询问 Marker API key 或引导用户获取
5. 创建 config.yaml

### config.yaml 模板
```yaml
wiki_path: ~/Documents/wikis
marker_api_key: <用户填入>
default_tags: []

ingest:
  auto_detect_raw_dir: true
  raw_dir: ~/Documents/wikis/raw

maintain:
  auto_maintain: false
  interval_hours: 24
```

### 验证设置
- 读取 config.yaml 确认配置正确
- 如无 API key，提示用户获取

## index.md 模板

```markdown
# Wiki Index

最后更新: <YYYY-MM-DD>

## 概览

- 论文数量: N
- 概念数量: N
- 标签: <tag1> (N), <tag2> (N)

## 按标签索引

### llm (N)
- [[source-slug]] - <标题>

### embodied-ai (N)
- [[source-slug]] - <标题>

## 概念索引

### [[concept-slug]]
<一句话定义>

## 最近更新

- <YYYY-MM-DD>: [[source-slug]] - <更新内容>
```

## Wiki 状态追踪

Skill 需要追踪以下状态（存储在 config.yaml 或单独状态文件）:

```yaml
state:
  initialized: true
  last_maintain: <YYYY-MM-DD>
  paper_count: N
  concept_count: N
  recent_ingest:
    - paper: <slug>
      date: <YYYY-MM-DD>
```

### 状态更新时机
- Ingest 后更新 paper_count、recent_ingest
- Maintain 后更新 last_maintain
- 删除 source/concept 后更新计数
```

## 错误处理

### PDF 解析失败
- API 返回错误时，提示用户检查 API key 或 PDF 文件
- 建议备选方案：让用户手动复制文本

### Wiki 文件损坏
- 检测到文件格式异常时，标记并提示修复
- 提供修复建议

### API Key 缺失
- 在需要调用 Marker API 时，检查 config.yaml
- 如缺失，引导用户获取并配置

### 空 Wiki 查询
- 首次查询时如无任何 source，提示用户先 ingest 论文
```
