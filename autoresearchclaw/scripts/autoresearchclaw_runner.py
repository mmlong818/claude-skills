# scripts/autoresearchclaw_runner.py
# 示例脚本：演示如何通过 Python API 驱动 AutoResearchClaw 流水线
# 实际使用时需安装: pip install autoresearchclaw

import json
import time
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ResearchDecision(Enum):
    PROCEED = "proceed"
    REFINE = "refine"
    PIVOT = "pivot"


class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_APPROVAL = "awaiting_approval"


APPROVAL_GATES = {5, 9, 20}  # Stages requiring human approval


@dataclass
class StageResult:
    stage_id: int
    stage_name: str
    status: StageStatus
    output: dict
    duration_seconds: float
    error: Optional[str] = None


@dataclass
class ResearchConfig:
    """最小配置数据类，对应 config.researchclaw.yaml"""
    project_name: str
    research_topic: str
    llm_base_url: str
    llm_api_key: str
    primary_model: str = "claude-sonnet-4-6"
    fallback_models: list = field(default_factory=lambda: ["claude-haiku-4-5-20251001"])
    experiment_mode: str = "sandbox"
    auto_approve: bool = False
    max_refine_iterations: int = 3
    max_pivot_iterations: int = 2


class AutoResearchClawRunner:
    """
    AutoResearchClaw 流水线编排器（示例实现）
    展示 23 个阶段的执行逻辑、人工审批门和自主决策机制
    """

    STAGES = [
        (1,  "TOPIC_INIT"),
        (2,  "PROBLEM_DECOMPOSE"),
        (3,  "SEARCH_STRATEGY"),
        (4,  "LITERATURE_COLLECT"),
        (5,  "LITERATURE_SCREEN"),       # 人工审批门 1
        (6,  "KNOWLEDGE_EXTRACT"),
        (7,  "SYNTHESIS"),
        (8,  "HYPOTHESIS_GEN"),
        (9,  "EXPERIMENT_DESIGN"),       # 人工审批门 2
        (10, "CODE_GENERATION"),
        (11, "RESOURCE_PLANNING"),
        (12, "EXPERIMENT_RUN"),
        (13, "ITERATIVE_REFINE"),
        (14, "RESULT_ANALYSIS"),
        (15, "RESEARCH_DECISION"),
        (16, "PAPER_OUTLINE"),
        (17, "PAPER_DRAFT"),
        (18, "PEER_REVIEW"),
        (19, "PAPER_REVISION"),
        (20, "QUALITY_GATE"),            # 人工审批门 3
        (21, "KNOWLEDGE_ARCHIVE"),
        (22, "EXPORT_PUBLISH"),
        (23, "CITATION_VERIFY"),
    ]

    def __init__(self, config: ResearchConfig):
        self.config = config
        self.stage_results: list[StageResult] = []
        self.knowledge_base: dict = {}
        self.refine_count = 0
        self.pivot_count = 0
        print(f"[AutoResearchClaw] Initialized for topic: '{config.research_topic}'")

    def _detect_hardware(self) -> str:
        """检测可用硬件，生成适配的实验代码设备配置"""
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
        except ImportError:
            pass
        return "cpu"

    def _request_human_approval(self, stage_id: int, stage_name: str, context: dict) -> bool:
        """
        在人工审批门处暂停，等待用户确认
        auto_approve 模式下自动通过
        """
        if self.config.auto_approve:
            print(f"[Gate {stage_id}] AUTO-APPROVE: {stage_name} passed automatically.")
            return True

        print(f"\n{'='*60}")
        print(f"[APPROVAL GATE] Stage {stage_id}: {stage_name}")
        print(f"Context summary: {json.dumps(context, indent=2, ensure_ascii=False)[:500]}...")
        print(f"{'='*60}")
        response = input("Approve? (yes/no/rollback): ").strip().lower()
        return response == "yes"

    def _run_stage(self, stage_id: int, stage_name: str, input_data: dict) -> StageResult:
        """执行单个阶段（示例：实际调用 LLM 完成各阶段任务）"""
        start = time.time()
        print(f"[Stage {stage_id:02d}] Running {stage_name}...")

        # 人工审批门检查
        if stage_id in APPROVAL_GATES:
            approved = self._request_human_approval(stage_id, stage_name, input_data)
            if not approved:
                return StageResult(
                    stage_id=stage_id,
                    stage_name=stage_name,
                    status=StageStatus.FAILED,
                    output={},
                    duration_seconds=time.time() - start,
                    error="Rejected at human approval gate"
                )

        # 模拟阶段执行（实际实现调用 LLM API）
        output = self._simulate_stage_output(stage_id, stage_name, input_data)

        duration = time.time() - start
        print(f"[Stage {stage_id:02d}] {stage_name} completed in {duration:.2f}s")

        return StageResult(
            stage_id=stage_id,
            stage_name=stage_name,
            status=StageStatus.COMPLETED,
            output=output,
            duration_seconds=duration
        )

    def _simulate_stage_output(self, stage_id: int, stage_name: str, input_data: dict) -> dict:
        """模拟各阶段产出（实际实现替换为真实 LLM 调用）"""
        outputs = {
            "TOPIC_INIT": {"keywords": ["keyword1", "keyword2"], "domain": "computer science"},
            "PROBLEM_DECOMPOSE": {"problem_tree": {"main": "Main problem", "sub": ["Sub1", "Sub2"]}},
            "SEARCH_STRATEGY": {"queries": ["query1 arxiv", "query2 semantic scholar"]},
            "LITERATURE_COLLECT": {"papers": [{"title": "Paper A", "arxiv_id": "2401.00001"}]},
            "LITERATURE_SCREEN": {"selected_papers": [{"title": "Paper A", "relevance": 0.95}]},
            "KNOWLEDGE_EXTRACT": {"findings": ["Finding 1", "Finding 2"], "gaps": ["Gap 1"]},
            "SYNTHESIS": {"consensus": "Key insight", "disagreements": [], "research_gaps": ["Gap 1"]},
            "HYPOTHESIS_GEN": {"hypotheses": [{"text": "H1: ...", "confidence": 0.8}]},
            "EXPERIMENT_DESIGN": {"baselines": ["Baseline A"], "metrics": ["accuracy", "F1"]},
            "CODE_GENERATION": {"code": f"# Hardware: {self._detect_hardware()}\nimport torch\n..."},
            "RESOURCE_PLANNING": {"gpu_memory_gb": 8, "estimated_runtime_hours": 2},
            "EXPERIMENT_RUN": {"results": {"accuracy": 0.92, "f1": 0.89}, "logs": "..."},
            "ITERATIVE_REFINE": {"fixed_code": "# Fixed version", "retry_count": 0},
            "RESULT_ANALYSIS": {"summary": "Model achieves SOTA", "confidence_interval": [0.90, 0.94]},
            "RESEARCH_DECISION": {"decision": ResearchDecision.PROCEED.value, "rationale": "Results exceed baseline"},
            "PAPER_OUTLINE": {"sections": ["Abstract", "Introduction", "Method", "Experiments", "Conclusion"]},
            "PAPER_DRAFT": {"word_count": 5800, "paper_text": "# Title\n## Abstract\n..."},
            "PEER_REVIEW": {"reviews": [{"reviewer": "R1", "score": 7, "comments": "Good work"}]},
            "PAPER_REVISION": {"revision_log": ["Addressed R1 comment 1"], "revised_text": "..."},
            "QUALITY_GATE": {"quality_score": 0.91, "checks_passed": 5, "checks_failed": 0},
            "KNOWLEDGE_ARCHIVE": {"archived_entries": 42, "categories": ["decisions", "experiments"]},
            "EXPORT_PUBLISH": {"paper_tex": "paper.tex", "references_bib": "references.bib", "pdf": "paper.pdf"},
            "CITATION_VERIFY": {"total_citations": 28, "verified": 28, "fabricated_detected": 0},
        }
        return outputs.get(stage_name, {"status": "completed"})

    def _handle_research_decision(self, decision_output: dict) -> Optional[int]:
        """
        处理阶段 15 的自主决策结果
        返回需要返回的阶段 ID（None 表示继续前进）
        """
        decision = decision_output.get("decision", ResearchDecision.PROCEED.value)

        if decision == ResearchDecision.PROCEED.value:
            print("[Decision] PROCEED → Continuing to paper writing phase.")
            return None

        elif decision == ResearchDecision.REFINE.value:
            self.refine_count += 1
            if self.refine_count <= self.config.max_refine_iterations:
                print(f"[Decision] REFINE ({self.refine_count}/{self.config.max_refine_iterations}) → Returning to EXPERIMENT_RUN.")
                return 12  # 返回到阶段 12
            else:
                print("[Decision] REFINE limit reached → Forcing PROCEED.")
                return None

        elif decision == ResearchDecision.PIVOT.value:
            self.pivot_count += 1
            if self.pivot_count <= self.config.max_pivot_iterations:
                print(f"[Decision] PIVOT ({self.pivot_count}/{self.config.max_pivot_iterations}) → Returning to HYPOTHESIS_GEN.")
                return 8  # 返回到阶段 8
            else:
                print("[Decision] PIVOT limit reached → Forcing PROCEED.")
                return None

        return None

    def run(self) -> dict:
        """
        执行完整的 23 阶段研究流水线
        返回所有产出物的路径和摘要
        """
        print(f"\n{'='*60}")
        print(f"AutoResearchClaw Pipeline Starting")
        print(f"Topic: {self.config.research_topic}")
        print(f"Model: {self.config.primary_model}")
        print(f"Auto-approve: {self.config.auto_approve}")
        print(f"{'='*60}\n")

        pipeline_start = time.time()
        current_data = {"topic": self.config.research_topic}
        stage_index = 0

        while stage_index < len(self.STAGES):
            stage_id, stage_name = self.STAGES[stage_index]

            result = self._run_stage(stage_id, stage_name, current_data)
            self.stage_results.append(result)

            if result.status == StageStatus.FAILED:
                print(f"[PIPELINE HALTED] Stage {stage_id} failed: {result.error}")
                return {"success": False, "failed_stage": stage_name, "error": result.error}

            # 合并阶段输出到流水线数据流
            current_data.update(result.output)

            # 阶段 15：处理自主决策（可能跳回前序阶段）
            if stage_name == "RESEARCH_DECISION":
                jump_to = self._handle_research_decision(result.output)
                if jump_to is not None:
                    # 跳回指定阶段
                    stage_index = next(
                        i for i, (sid, _) in enumerate(self.STAGES) if sid == jump_to
                    )
                    continue

            stage_index += 1

        total_duration = time.time() - pipeline_start
        print(f"\n{'='*60}")
        print(f"Pipeline COMPLETED in {total_duration:.1f}s")
        print(f"Outputs: paper.pdf, paper.tex, references.bib")
        print(f"{'='*60}\n")

        return {
            "success": True,
            "paper_pdf": current_data.get("pdf"),
            "paper_tex": current_data.get("paper_tex"),
            "references_bib": current_data.get("references_bib"),
            "total_stages": len(self.stage_results),
            "total_duration_seconds": total_duration,
            "citations_verified": current_data.get("verified", 0),
            "word_count": current_data.get("word_count", 0),
        }

    def export_run_summary(self, output_path: str = "run_summary.json"):
        """将本次运行的完整记录导出为 JSON"""
        summary = {
            "config": {
                "topic": self.config.research_topic,
                "model": self.config.primary_model,
                "auto_approve": self.config.auto_approve,
            },
            "stages": [
                {
                    "id": r.stage_id,
                    "name": r.stage_name,
                    "status": r.status.value,
                    "duration_seconds": r.duration_seconds,
                    "error": r.error,
                }
                for r in self.stage_results
            ],
            "decision_stats": {
                "refine_iterations": self.refine_count,
                "pivot_iterations": self.pivot_count,
            }
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"Run summary exported to {output_path}")


# 示例用法
if __name__ == "__main__":
    # 配置研究任务
    config = ResearchConfig(
        project_name="my_research_project",
        research_topic="Efficient attention mechanisms for long-context language models",
        llm_base_url="https://api.anthropic.com/v1",
        llm_api_key="your-api-key-here",
        primary_model="claude-sonnet-4-6",
        fallback_models=["claude-haiku-4-5-20251001"],
        experiment_mode="sandbox",
        auto_approve=False,  # 设为 True 以跳过所有人工审批门
    )

    # 初始化并运行流水线
    runner = AutoResearchClawRunner(config)
    result = runner.run()

    # 输出结果
    if result["success"]:
        print(f"Paper generated: {result['paper_pdf']}")
        print(f"Word count: {result['word_count']}")
        print(f"Citations verified: {result['citations_verified']}")
    else:
        print(f"Pipeline failed at stage: {result['failed_stage']}")
        print(f"Error: {result['error']}")

    # 导出运行摘要
    runner.export_run_summary("run_summary.json")
