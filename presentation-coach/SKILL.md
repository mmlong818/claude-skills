---
name: presentation-coach
description: |
  A full-stack presentation design skill covering 6 proven frameworks. Use this skill whenever a user wants to prepare, design, structure, improve, or deliver any kind of presentation, talk, pitch, or speech — including but not limited to: academic lectures, board reports, TED-style talks, product launches, sales pitches, consulting proposals, training sessions, or job interviews. Also triggers when users mention "演讲", "PPT", "pitch", "幻灯片", "开场白", "说服", "汇报" or ask how to make their ideas memorable or how to structure an argument. When in doubt, use this skill — it covers all scenarios.
---

# Presentation Coach

A multi-framework presentation design system. Before writing anything, classify the user's intent, then route to the correct framework reference file.

---

## Step 1 — Classify Intent

Read the user's input and extract these signals:

| Signal | What to look for |
|---|---|
| **场合 (Scene)** | 学术、商业汇报、TED/演讲、产品发布、销售、培训、提案 |
| **听众 (Audience)** | 评审委员会、董事会/高管、大众/公众、客户、投资人、学员 |
| **目标 (Goal)** | 教学/传递知识、说服决策、感召行动、销售/转化、记忆留存 |
| **时间压力** | 5分钟以内、30分钟、长篇 |
| **内容状态** | 从零开始、已有草稿需优化、只有主题 |

Then map to a framework using this routing table:

| 场合 / 信号 | 首选框架 | 备选框架 |
|---|---|---|
| 学术讲座、论文答辩、通用演讲 | **Winston** | SUCCESs |
| 董事会汇报、高管简报、决策会议 | **金字塔原理** | SCQA |
| 战略提案、咨询方案、问题诊断 | **SCQA** | 金字塔原理 |
| TED演讲、品牌发布、感召大众 | **Duarte** | StoryBrand |
| 产品发布、销售演讲、创业 Pitch | **StoryBrand** | Duarte |
| 培训课程、内部宣讲、知识传播 | **SUCCESs** | Winston |
| 幻灯片审查/优化（已有PPT） | **Winston 幻灯片审查** | 金字塔原理 |

**如果信号不明确**：先问用户以下2个问题（不超过2个），然后路由：
1. 你的听众是谁？（决策者 / 大众 / 学员 / 客户）
2. 你最想要的结果是什么？（他们记住 / 他们行动 / 他们批准 / 他们购买）

---

## Step 2 — Load Framework Reference

Once the framework is identified, read the corresponding reference file **before** generating any output:

| 框架 | 参考文件 |
|---|---|
| Winston | `references/winston.md` |
| 金字塔原理 | `references/pyramid.md` |
| SCQA | `references/scqa.md` |
| Duarte 共鸣框架 | `references/duarte.md` |
| StoryBrand | `references/storybrand.md` |
| SUCCESs 粘性框架 | `references/success.md` |

---

## Step 3 — Gather Missing Inputs

Every framework needs at minimum:
- **话题/主题** — 演讲主题是什么
- **听众** — 谁在听
- **目标结果** — 听完之后你希望他们做什么/记住什么
- **时长** — 大概多少分钟

If any of these are missing from the user's input, ask for them concisely before proceeding. Do not ask for more than what's needed.

---

## Step 4 — Execute Framework + Dual Output

Follow the framework reference file. Then deliver **both outputs** for every presentation:

---

### Output A — Slide Deck Content

For each slide, first decide its **function**, then choose the layout that serves that function best. Never default to "title + 3 bullets" — that is a last resort for slides with no better structure.

**Slide Function → Layout**

| 功能 | 适用版式 | 说明 |
|---|---|---|
| 封面 / 标题页 | **大标题型** | 一句核心主张 + 副标题，无其他内容 |
| 核心结论 / 赋能承诺 | **单句冲击型** | 全页只有一句话，字号极大 |
| 流程 / 步骤 | **流程型** | 3-5个步骤，每步标题 + 一句说明 |
| 数据对比 | **数据型** | 1-3个大数字 + 各自的标签和说明 |
| 两方对比 | **左右对比型** | 左栏 vs 右栏，各有标题和要点 |
| 时间线 / 历史 | **时间轴型** | 横向或纵向时间轴，关键节点 + 一句描述 |
| 核心论点支撑 | **论点型** | 观点句标题 + 2-4条支撑证据（非固定3条） |
| 引言 / 故事开场 | **引用型** | 大字引言或故事场景描述，来源标注 |
| 地图 / 生态系统 | **图示型** | 文字描述图示内容，注明"建议配图" |
| 行动号召 | **号召型** | 一个动词开头的行动指令 + 截止时间或条件 |
| 贡献页 / 总结 | **清单型** | 2-5条贡献，每条一句话，无嵌套 |

**格式规范（每张幻灯片）**：

```
【第N张】功能标注 · 版式类型
标题: [观点句，而非话题词]
内容: [根据版式类型自由决定内容形式]
备注: [可选 — 设计建议或配图说明]
```

标题必须是**观点句**，不是话题词：
- ❌ "市场分析" → ✅ "中国市场增速已连续三季度低于全球均值"
- ❌ "我们的方案" → ✅ "三步重构结账体验，留存率预计提升25%"

---

### Output B — Speaker Script

For each slide, write the spoken words the presenter says while that slide is showing.

**格式规范**：

```
【第N张讲稿】
[完整逐字稿。口语化，有节奏感。包含过渡句——从上一张到这一张的衔接语。
标注停顿 [停顿] 和强调 **重点词**。
时长估算: 约X秒/X分钟]
```

**讲稿写作原则**：
- 讲稿和幻灯片内容**不能重复**——幻灯片是视觉锚点，讲稿是扩展和故事
- 每张开头有过渡句（"说完这个，我想带你们看一个数字……"）
- 每张结尾有铺垫句（引导下一张）
- 口语化：短句，有呼吸感，避免书面长句
- 标注关键停顿和需要强调的词

---

### Delivery Order

先输出完整幻灯片内容（Output A），再输出完整讲稿（Output B）。
在两者之间加一行分隔：`---`

---

## Step 5 — Offer Enhancement

After delivering the primary output, offer:
- "需要我把幻灯片内容直接生成为可下载的PPTX文件吗？"
- "需要我用另一个框架做一个对比版本吗？"
- "需要我帮你设计Q&A应对策略吗？"

---

## Output Language

Always respond in the same language the user used. If the user writes in Chinese, output in Chinese. If English, output in English.
