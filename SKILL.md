---
name: llm-wiki
description: LLM双栖Wiki工具（论文+代码库）。帮你阅读总结论文、分析代码架构，建立跨域知识wiki，支持多领域标签。
version: 1.0.0
---

# LLM Wiki Skill

## 概念
这是一个基于 Karpathy "LLM Wiki" 模式的知识管理工具。LLM 作为知识库的"编译器"和"管理员"，用户只管问问题，wiki 在后台自动维护。

## 核心能力
- Ingest (PDF): 读取学术论文，提取内容，生成结构化条目。
- Ingest (Code): 扫描并读取代码库源文件，生成系统架构与代码逻辑的 Wiki。
- Query: 根据wiki内容回答关于论文或代码架构的问题。
- Maintain: 检查交叉引用，检测矛盾，更新全局索引。
- Search: 全文搜索论文和代码的相关内容。

## Ingest 工作流

### 触发方式
用户说"帮我管理这个目录下的论文"或"把这篇论文加到wiki"

### 处理流程
1. **定位 PDF**
   - 用户指定路径或使用默认 ~/Documents/wikis/raw/
   - 识别所有 PDF 文件

2. **提取文本**
   - 对于批量导入场景，可建议用户使用或直接代为执行 `scripts/ingest_papers.py --dir <目录>` 生成概览报告。
   优先调用 Marker API（智能路由：判断如果是理工科论文、包含大量公式图表，强烈建议使用 Marker；否则可直接使用 Claude 原生解析以提高速度）：
   ```
   优先使用本地部署的 Marker Server: POST http://localhost:5203/v1/parse/file (或其他配置的本地地址)
   如果本地不可用，则尝试使用官方 API: POST https://api.marker.cloud/v1/document
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
     macro_analysis:
       1. 核心问题: <这篇论文具体在解决什么核心问题或业务痛点？>
       2. 具体方法: <论文提出了什么具体的解决方案、算法或创新设计来解决上述问题？>
       3. 实验与验证: <该方法是如何被验证的？取得了哪些关键突破或性能提升？>
       4. 局限与不足: <该研究目前存在哪些局限性或尚未解决的问题？>
       5. 启发与价值: <这项工作对后续研究或实际工程应用有什么重要启发？>
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
   - tags: 自动打标签（请先读取 wiki 目录下的 config.yaml 中的 default_tags，优先使用这些预设标签，如有必要再创建新标签）
   - summary: 3-5句摘要
   - macro_analysis: 回答关于核心问题、具体方法、实验验证、局限性、启发与价值的5个宏观问题
   - key_concepts: 3-5个关键概念
   - contributions: 主要贡献

4. **写入 Wiki (CRITICAL)**
   - **强制要求：你必须使用 `Write` 工具将生成的内容直接写入到对应的 Markdown 文件中，绝对不能仅仅在聊天框中输出。**
   - 创建 source 文件: /wiki_path/sources/<slug>.md
   - 如有关联 concept，更新 concept 文件或创建新 concept
   - 更新 index.md
   - 只有在确认文件写入成功后，才能向用户总结你的工作。

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

## 核心分析 (Macro Analysis)

### 1. 核心问题 (Core Problem)
<这篇论文具体在解决什么核心问题或业务痛点？>

### 2. 具体方法 (Proposed Method)
<论文提出了什么具体的解决方案、算法或创新设计来解决上述问题？>

### 3. 实验与验证 (Evaluation & Results)
<该方法是如何被验证的？取得了哪些关键突破或性能提升？>

### 4. 局限与不足 (Limitations)
<该研究目前存在哪些局限性或尚未解决的问题？>

### 5. 启发与价值 (Insights & Value)
<这项工作对后续研究或实际工程应用有什么重要启发？>

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


## 扩展：代码库 Ingest 工作流 (Code Wiki)

除了论文，Wiki 同样支持对代码库（Repo）进行知识索引和总结。两者共存，论文记录"理论"，代码库记录"实现"。

**⚠️ 防偷懒强制约束 (ANTI-LAZINESS CONSTRAINT)**: 
作为 Agent，你**绝对不被允许**跳过步骤或直奔最终结论。你必须严格按照 1 -> 2 -> 3 -> 4 的顺序执行。
**特别是第 2 步**：你必须对核心源码逐一阅读，并**立即使用 `Write` 工具**将分析结果写入 `/wiki_path/sources/` 目录。
如果发现你只输出了第 3 步的宏观架构而没有生成 `sources/` 目录下的单文件分析，这将被视为严重失败！

### 触发方式
用户说"帮我分析这个代码库"、"将这个目录的代码加到wiki"

### 处理流程
1. **扫描代码结构**
   - 执行 `scripts/ingest_repo.py --dir <代码路径>`，自动读取 .gitignore 并列出核心源文件。
   
2. **提取与分析 (逐文件或按模块) - MUST WRITE TO DISK FIRST**
   - Claude 逐一读取核心源码文件，提取结构化信息：
     ```
     请阅读这段代码，提取并返回以下结构化信息：
     module_name: <模块/文件名称>
     file_path: <相对路径>
     language: <编程语言>
     dependencies: [<依赖的内部模块或外部库>]
     core_logic: <3-5句核心职责总结>
     exports: [<导出的关键类/接口/函数>]
     ```
   - **紧接着这一步，立刻使用 `Write` 工具创建源文件**：`/wiki_path/sources/code_<repo>_<slug>.md`。所有核心文件必须被分析并写入磁盘后，才能进入下一步。

3. **宏观架构分析 (预设问题)**
   - 在确认所有核心单文件都已经成功存入 `sources/` 后，Claude 必须基于已阅读的代码，回答以下 5 个核心架构问题，并生成一个概念页面：
     1. **宏观定位 (Macro positioning)**: 这个项目是什么？解决什么业务场景？
     2. **核心入口 (Core entry points)**: 系统的启动入口或核心 API 在哪？（例如 main 函数、对外暴露的类）
     3. **数据流向 (Data flow)**: 核心数据是如何在系统中流转的？
     4. **扩展性机制 (Extensibility)**: 系统提供了哪些接口/基类供二次开发或插件化扩展？
     5. **复杂机制 (Tricky mechanisms)**: 代码中是否有特殊的并发处理、硬件通信协议（如 CAN、RS485）或复杂的业务状态机？

4. **写入 Wiki (Concept - CRITICAL)**
   - **强制要求：分析完成后，你必须使用 `Write` 工具将架构报告直接写入以下指定的文件路径中。不要只在聊天框里口头汇报！**
   - 根据宏观架构分析，创建或更新概念页面：`/wiki_path/concepts/architecture_<repo_name>.md`
   - 将业务概念（如 `Auth_Flow`, `Data_Pipeline`）链接到 Concept 页面。
   - 写入完成后，再向用户简短汇报已存入的路径。

### Code Source 文件模板
```markdown
---
type: code_module
title: <module_name>
file_path: <file_path>
language: <language>
tags: [code, <语言tag>, <业务模块tag>]
---

## Core Logic
<LLM总结的核心职责>

## Exports (Key Interfaces)
- `Function/Class`: <一句话说明>

## Dependencies
- <外部库/内部模块>

## Related Concepts / Architecture
- [[concept-slug]] (关联的架构设计或业务概念)
- [[architecture_<repo_name>]] (宏观架构页面)
```

### Repo Architecture Concept 模板
```markdown
---
title: <Repo Name> Architecture Overview
tags: [architecture, code]
---

## 宏观定位
<该项目是什么，解决什么业务场景>

## 核心入口
<系统的启动入口或核心 API 列表及说明>

## 数据流向
<核心数据的流转过程>

## 扩展性机制
<支持二次开发或插件化的接口/基类>

## 复杂机制
<并发、特殊硬件协议、状态机等核心难点解析>
```

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
   - 当用户要求初始化时，请优先尝试执行项目目录下的 `scripts/init_wiki.sh <wiki_path>` 脚本。
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
