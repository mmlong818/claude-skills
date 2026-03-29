# Claude Skills Collection · Claude Skills 合集

> A curated collection of Claude Code skills for specialized creative and professional tasks.
> 精选 Claude Code Skills 合集，覆盖创意写作、专业工具等垂直领域。

---

## English

### What Are Claude Skills?

Claude Skills are modular knowledge packages that extend Claude Code's capabilities. Each skill provides Claude with specialized workflows, domain expertise, templates, and reference materials — transforming it from a general assistant into a domain expert for specific tasks.

Skills are loaded automatically when Claude detects a relevant task. They follow a progressive disclosure model: only the necessary context is loaded, keeping your conversation efficient.

### Available Skills

| Skill | Category | Description |
|-------|----------|-------------|
| [micro-drama-writer](./micro-drama-writer/) | Creative Writing | Professional micro-drama screenwriting for female-oriented emotional content. Covers modern romance, historical fantasy, time travel, revenge & rebirth genres. |

*More skills coming soon.*

### How to Install a Skill

1. Download or clone this repository
2. Copy the skill folder you want to your Claude Code skills directory:
   - **macOS / Linux:** `~/.claude/skills/`
   - **Windows:** `C:\Users\<username>\.claude\skills\`
3. The skill is immediately available — no restart needed

### How to Use

Simply describe your task naturally. Claude will detect the intent and load the appropriate skill:

```
# Triggers micro-drama-writer
"Help me write a 60-episode micro-drama about revenge"
"Design a face-slap scene for my short drama"
"Write dialogue for the male lead's confession"
```

### Skill Structure

Each skill follows this standard structure:

```
skill-name/
├── README.md        # Bilingual documentation (EN + ZH)
├── SKILL.md         # Core instructions loaded by Claude
└── references/      # Detailed reference files loaded on demand
    └── *.md
```

### Contributing

Feel free to submit a pull request to add your own skill. Please follow the structure above and include a bilingual README.

---

## 中文说明

### 什么是 Claude Skill？

Claude Skill 是为 Claude Code 设计的模块化知识包，为 Claude 提供专项领域的工作流程、领域知识、模板和参考资料——让通用助手变成特定领域的专家。

Skill 在 Claude 检测到相关任务时自动触发，采用渐进式加载机制：只加载必要内容，不占用多余上下文。

### 当前可用 Skills

| Skill | 分类 | 说明 |
|-------|------|------|
| [micro-drama-writer](./micro-drama-writer/) | 创意写作 | 专业微短剧编剧助手，面向女性情感向内容。覆盖都市甜宠、古装虐恋、穿越重生、复仇逆袭等主流题材。 |

*更多 Skills 持续更新中。*

### 安装方法

1. 下载或克隆本仓库
2. 将想要的 skill 文件夹复制到 Claude Code 的 skills 目录：
   - **macOS / Linux：** `~/.claude/skills/`
   - **Windows：** `C:\Users\<用户名>\.claude\skills\`
3. 无需重启，立即生效

### 使用方式

直接用自然语言描述任务，Claude 会自动识别并加载对应 skill：

```
# 触发 micro-drama-writer
"帮我写一个60集的复仇微短剧"
"设计第30集的打脸场景"
"写男主表白的台词"
```

### Skill 结构规范

每个 skill 遵循以下标准结构：

```
skill-name/
├── README.md        # 中英文双语说明
├── SKILL.md         # Claude 加载的核心指令
└── references/      # 按需加载的详细参考文件
    └── *.md
```

### 贡献

欢迎提交 PR 添加你的 skill，请遵循上方结构规范并附带中英文双语 README。

---

## License

MIT
