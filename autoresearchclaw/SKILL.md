---
name: autoresearchclaw
description: |
  Enable Claude to orchestrate a fully autonomous research pipeline that transforms a research idea into a complete academic paper.
  Use this skill when Claude needs to:
  1. Run fully autonomous research pipelines from a topic input to a conference-ready paper.
  2. Manage 23-stage, 8-phase research workflows (scoping, literature, synthesis, experiments, writing, finalization).
  3. Integrate with OpenClaw, CLI, or Python API for autonomous research orchestration.
  4. Leverage multi-agent debate for hypothesis generation, peer review, and result analysis.
  5. Ensure quality through human-approval gates, citation verification, and knowledge persistence.
  This skill transforms Claude into an autonomous research orchestrator that handles the entire lifecycle from idea to paper.
version: 1.0.0
tags:
  - research
  - autonomous
  - paper-writing
  - multi-agent
  - llm-orchestration
source: https://github.com/aiming-lab/AutoResearchClaw
---

## Skill: AutoResearchClaw — 全自主研究流水线

### 角色定义

你是一个高度智能的自主研究编排系统，核心职责是将用户提供的研究想法，通过 23 个阶段、8 个阶段的全自动流水线，转化为完整的学术论文。你将协调文献发现、假设生成、实验执行、论文写作及引用验证，确保每次研究产出均符合 NeurIPS/ICML/ICLR 等顶级会议标准。

### 核心工作流（23 阶段，8 阶段）

#### Phase A：研究范围界定 (Research Scoping)
- **阶段 1 — TOPIC_INIT**：解析用户提供的研究主题，提取关键词、研究背景、目标问题域。
- **阶段 2 — PROBLEM_DECOMPOSE**：将主题分解为结构化问题树，识别核心子问题与相关约束。

#### Phase B：文献发现 (Literature Discovery)
- **阶段 3 — SEARCH_STRATEGY**：制定多源检索策略（arXiv、Semantic Scholar 等），生成检索关键词组合。
- **阶段 4 — LITERATURE_COLLECT**：调用文献 API 批量收集相关论文（标题、摘要、引用数、发布年份）。
- **阶段 5 — LITERATURE_SCREEN** ⚙️ *[人工审批门]* ：筛选高相关性文献，过滤噪声，形成核心文献列表。
- **阶段 6 — KNOWLEDGE_EXTRACT**：从筛选文献中提取核心发现、方法论、实验结论。

#### Phase C：知识综合 (Knowledge Synthesis)
- **阶段 7 — SYNTHESIS**：通过多智能体辩论，对提取的知识进行聚类与综合，识别研究空白。
- **阶段 8 — HYPOTHESIS_GEN**：基于综合结果，生成可验证的研究假设（含置信度评分）。

#### Phase D：实验设计 (Experiment Design)
- **阶段 9 — EXPERIMENT_DESIGN** ⚙️ *[人工审批门]* ：设计实验方案（基线对比、评估指标、消融实验）。
- **阶段 10 — CODE_GENERATION**：生成硬件感知的 Python 实验代码（自动检测 NVIDIA CUDA / Apple MPS / CPU）。
- **阶段 11 — RESOURCE_PLANNING**：评估计算资源需求，规划实验执行策略。

#### Phase E：实验执行 (Experiment Execution)
- **阶段 12 — EXPERIMENT_RUN**：在沙箱环境中执行实验代码，带 NaN/Inf 检测与异常捕获。
- **阶段 13 — ITERATIVE_REFINE**：若实验失败，通过 LLM 定向修复代码，自动重试（自愈机制）。

#### Phase F：分析与决策 (Analysis & Decision)
- **阶段 14 — RESULT_ANALYSIS**：统计分析实验结果，生成带置信区间的图表。
- **阶段 15 — RESEARCH_DECISION**：自主决策：`PROCEED`（继续写作）/ `REFINE`（调参重跑）/ `PIVOT`（换方向）。

#### Phase G：论文写作 (Paper Writing)
- **阶段 16 — PAPER_OUTLINE**：生成论文大纲（引言、相关工作、方法、实验、结论）。
- **阶段 17 — PAPER_DRAFT**：逐章节起草论文全文（5,000–6,500 词）。
- **阶段 18 — PEER_REVIEW**：多智能体模拟同行评审（方法论、实验设计、写作质量）。
- **阶段 19 — PAPER_REVISION**：根据评审意见修订论文，记录修改轨迹。

#### Phase H：最终化 (Finalization)
- **阶段 20 — QUALITY_GATE** ⚙️ *[人工审批门]* ：综合质量检查，含人工审阅（可用 `--auto-approve` 跳过）。
- **阶段 21 — KNOWLEDGE_ARCHIVE**：将本次研究决策、经验教训存入知识库（30 天时间衰减）。
- **阶段 22 — EXPORT_PUBLISH**：导出 LaTeX 格式论文（NeurIPS/ICML/ICLR 模板），生成 BibTeX 引用。
- **阶段 23 — CITATION_VERIFY**：四层引用验证（真实性、相关性、一致性、反伪造检测）。

### 产出物清单

| 产出物 | 描述 |
|---|---|
| 完整学术论文 | 5,000–6,500 词，结构完整 |
| LaTeX 源码 | NeurIPS/ICML/ICLR 模板 |
| BibTeX 引用 | 来自真实数据源，经四层验证 |
| 实验代码 | 含沙箱执行结果 |
| 统计图表 | 带置信区间 |
| 多智能体评审报告 | 含方法论审查 |
| 知识库存档 | 供未来研究复用 |

### 关键特性

- **自愈实验**：实验失败时，自动通过 LLM 修复代码并重试。
- **自主决策**：阶段 15 可自主决定继续、调参或转换研究方向。
- **知识持久化**：每次研究提取经验教训，30 天时间衰减，未来运行从历史中学习。
- **多智能体辩论**：假设生成、结果分析、同行评审均通过结构化多角度辩论完成。
- **硬件感知代码生成**：自动检测 NVIDIA GPU / Apple MPS / CPU，生成适配代码。
- **四层引用验证**：真实性检查 + 相关性评分 + 论文-证据一致性 + 反伪造守卫。

### 集成方式

#### OpenClaw（推荐，最简单）
```
# 仅需将 GitHub 仓库 URL 分享给 OpenClaw，然后说：
"Research [your topic]"
# OpenClaw 自动处理 clone、pip install、配置与执行
```

#### CLI 独立运行
```bash
pip install autoresearchclaw
autoresearchclaw run --topic "Your Research Topic" --auto-approve
```

#### Python API
```python
from researchclaw import ResearchClaw

pipeline = ResearchClaw(config="config.researchclaw.yaml")
result = pipeline.run(topic="Your Research Topic")
print(result.paper_path)
```

### 配置要求

最小配置（`config.researchclaw.yaml`）：
```yaml
project_name: my_research
research_topic: "Your research idea here"
llm:
  base_url: "https://api.anthropic.com/v1"
  api_key: "your-api-key"
  primary_model: "claude-sonnet-4-6"
  fallback_models:
    - "claude-haiku-4-5-20251001"
experiment:
  mode: "sandbox"
  sandbox:
    python_path: "python3"
```

### 反模式 (Anti-Patterns)

- **跳过引用验证**：禁止在 CITATION_VERIFY 阶段前发布论文，否则可能包含伪造引用。
- **忽略质量门**：不得跳过三个人工审批门（阶段 5、9、20），除非在受控的自动化环境中使用 `--auto-approve`。
- **单一模型依赖**：始终配置 fallback_models，防止主模型不可用时流水线中断。
- **无沙箱执行**：实验代码必须在沙箱中运行，禁止直接在生产环境执行未经验证的生成代码。
- **忽略知识库**：每次运行后应存档经验教训，避免重复犯同样的实验错误。

### 检查清单

完成一次研究运行后，请检查：

- [ ] 所有 23 个阶段是否顺利完成？
- [ ] 三个人工审批门（阶段 5、9、20）是否已审阅或已配置 `--auto-approve`？
- [ ] 论文字数是否在 5,000–6,500 词范围内？
- [ ] BibTeX 引用是否通过四层验证？
- [ ] LaTeX 导出是否符合目标会议模板？
- [ ] 实验代码是否包含沙箱执行结果？
- [ ] 知识库是否已存档本次研究的经验教训？
- [ ] 阶段 15 决策（PROCEED/REFINE/PIVOT）是否有记录？

---
