# scripts/self_optimizing_claude.py
# 自优化 Claude 核心实现脚本
# 实现交互追踪、性能分析、风格优化和配置持久化

import json
import time
import os
import shutil
from collections import defaultdict
from datetime import datetime


def _default_config():
    """返回默认优化配置。"""
    return {
        "default_style": "balanced",
        "style_preferences": {
            "code_generation": {"detail_level": "medium", "comment_density": "high"},
            "debugging": {"explanation_depth": "medium", "step_by_step": True},
            "explanation": {"clarity_priority": "high", "conciseness_priority": "medium"},
            "refactoring": {"safety_checks": True, "performance_considerations": True},
            "optimization": {"aggressiveness": "medium", "risk_assessment": "medium"},
            "general": {"tone": "helpful", "formality": "medium"}
        },
        "performance_thresholds": {
            "satisfaction_min": 0.7,
            "response_time_max_ms": 5000,
            "success_rate_min": 0.8
        },
        "last_optimized_at": None
    }


# 查询类型关键词映射，用于自动识别查询类型
QUERY_TYPE_KEYWORDS = {
    "code_generation": ["生成", "写", "创建", "实现", "generate", "write", "create", "implement"],
    "debugging": ["调试", "错误", "报错", "bug", "修复", "debug", "error", "fix", "exception"],
    "explanation": ["解释", "什么是", "如何理解", "explain", "what is", "how does", "understand"],
    "refactoring": ["重构", "优化结构", "重写", "refactor", "restructure", "rewrite", "clean up"],
    "optimization": ["性能", "速度", "优化", "performance", "optimize", "faster", "efficient"],
}


class ClaudeOptimizer:
    def __init__(self, config_path="optimization_config.json", log_path="interaction_logs.json"):
        self.config_path = config_path
        self.log_path = log_path
        self.optimization_config = self._load_config()
        self.interaction_logs = self._load_logs()
        print(f"Claude Optimizer initialized. Current config: {self.optimization_config}")

    # -------------------------
    # 配置管理
    # -------------------------

    def _load_config(self):
        """加载优化配置，如果不存在或损坏则使用默认配置。"""
        if not os.path.exists(self.config_path):
            print("Optimization config not found, using default.")
            return _default_config()
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error: {self.config_path} is corrupted. Using default config.")
            return _default_config()

    def _save_config(self):
        """保存当前优化配置，并在保存前备份旧配置（支持回滚）。"""
        # 备份旧配置
        if os.path.exists(self.config_path):
            backup_path = self.config_path + ".bak"
            shutil.copy2(self.config_path, backup_path)

        self.optimization_config["last_optimized_at"] = time.time()
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_config, f, indent=4, ensure_ascii=False)
        print(f"Optimization config saved to {self.config_path}")

    def rollback_config(self):
        """回滚到上一个备份的配置。"""
        backup_path = self.config_path + ".bak"
        if not os.path.exists(backup_path):
            print("No backup config found, cannot rollback.")
            return "No backup config found."
        try:
            shutil.copy2(backup_path, self.config_path)
            self.optimization_config = self._load_config()
            print(f"Config rolled back from {backup_path}.")
            return "Rollback successful."
        except Exception as e:
            print(f"Rollback failed: {e}")
            return f"Rollback failed: {e}"

    def export_config(self, filename="exported_optimization_config.json"):
        """导出当前优化配置。"""
        self.optimization_config["last_exported_at"] = time.time()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_config, f, indent=4, ensure_ascii=False)
        print(f"Configuration exported to {filename}")
        return f"Configuration exported to {filename}"

    def import_config(self, filename="exported_optimization_config.json"):
        """从文件导入优化配置，导入前备份当前配置。"""
        if not os.path.exists(filename):
            print(f"Error: Import file {filename} not found.")
            return f"Error: Import file {filename} not found."
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            # 备份当前配置后再覆盖
            self._save_config()
            self.optimization_config.update(imported_config)
            self._save_config()
            print(f"Configuration imported from {filename} and applied.")
            return f"Configuration imported from {filename} and applied."
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in {filename}.")
            return f"Error: Invalid JSON in {filename}."

    # -------------------------
    # 交互日志持久化
    # -------------------------

    def _load_logs(self):
        """从磁盘加载历史交互日志。"""
        if not os.path.exists(self.log_path):
            return []
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            print(f"Warning: Could not load logs from {self.log_path}, starting fresh.")
            return []

    def _save_logs(self):
        """将交互日志持久化到磁盘。"""
        with open(self.log_path, 'w', encoding='utf-8') as f:
            json.dump(self.interaction_logs, f, indent=4, ensure_ascii=False)

    # -------------------------
    # 查询类型自动识别
    # -------------------------

    @staticmethod
    def detect_query_type(user_input: str) -> str:
        """
        根据用户输入自动识别查询类型。
        :param user_input: 用户的原始输入文本
        :return: 查询类型字符串
        """
        text = user_input.lower()
        for query_type, keywords in QUERY_TYPE_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                return query_type
        return "general"

    # -------------------------
    # 交互追踪
    # -------------------------

    def track_interaction(self, query_type: str, response_time_ms: int,
                          user_satisfaction: float, task_success: bool,
                          applied_style: dict):
        """
        追踪单次用户交互的性能数据并持久化。
        :param query_type: 查询类型
        :param response_time_ms: 响应时间（毫秒）
        :param user_satisfaction: 用户满意度 (0.0 - 1.0)
        :param task_success: 任务是否成功完成
        :param applied_style: 本次交互应用的风格配置
        """
        log_entry = {
            "timestamp": time.time(),
            "datetime": datetime.now().isoformat(),
            "query_type": query_type,
            "response_time_ms": response_time_ms,
            "user_satisfaction": user_satisfaction,
            "task_success": task_success,
            "applied_style": applied_style
        }
        self.interaction_logs.append(log_entry)
        self._save_logs()
        print(f"Interaction logged: {log_entry}")

    # -------------------------
    # 性能分析
    # -------------------------

    def analyze_performance(self):
        """分析收集到的交互数据，识别模式和优化机会。"""
        if not self.interaction_logs:
            print("No interaction logs to analyze.")
            return {}

        analysis_results = defaultdict(lambda: defaultdict(list))
        for log in self.interaction_logs:
            q_type = log["query_type"]
            analysis_results[q_type]["satisfaction"].append(log["user_satisfaction"])
            analysis_results[q_type]["response_time"].append(log["response_time_ms"])
            analysis_results[q_type]["success_rate"].append(1 if log["task_success"] else 0)
            analysis_results[q_type]["styles"].append(log["applied_style"])

        summary = {}
        for q_type, data in analysis_results.items():
            summary[q_type] = {
                "avg_satisfaction": sum(data["satisfaction"]) / len(data["satisfaction"]),
                "avg_response_time": sum(data["response_time"]) / len(data["response_time"]),
                "avg_success_rate": sum(data["success_rate"]) / len(data["success_rate"]),
                "sample_count": len(data["satisfaction"]),
                "styles_used": data["styles"]
            }
        print("Performance analysis complete.")
        return summary

    # -------------------------
    # 优化策略生成与应用
    # -------------------------

    def generate_optimization_strategy(self, analysis_summary: dict):
        """根据分析结果生成优化策略。"""
        new_style_preferences = {
            k: dict(v) for k, v in self.optimization_config["style_preferences"].items()
        }
        optimization_report = []

        thresholds = self.optimization_config["performance_thresholds"]

        for q_type, metrics in analysis_summary.items():
            current_pref = new_style_preferences.get(q_type, {})
            report_entry = {"query_type": q_type, "changes": []}

            # 满意度低于阈值
            if metrics["avg_satisfaction"] < thresholds["satisfaction_min"]:
                if q_type == "code_generation" and current_pref.get("comment_density") != "very_high":
                    current_pref["comment_density"] = "very_high"
                    report_entry["changes"].append("Increased comment density due to low satisfaction.")
                elif q_type == "explanation" and current_pref.get("conciseness_priority") != "high":
                    current_pref["conciseness_priority"] = "high"
                    report_entry["changes"].append("Increased conciseness priority due to low satisfaction.")
                elif q_type == "debugging" and not current_pref.get("step_by_step"):
                    current_pref["step_by_step"] = True
                    report_entry["changes"].append("Enabled step_by_step due to low satisfaction.")

            # 响应时间过长
            if metrics["avg_response_time"] > thresholds["response_time_max_ms"]:
                if q_type == "code_generation" and current_pref.get("detail_level") != "low":
                    current_pref["detail_level"] = "low"
                    report_entry["changes"].append("Decreased detail level due to high response time.")
                elif q_type == "explanation" and current_pref.get("clarity_priority") != "medium":
                    current_pref["clarity_priority"] = "medium"
                    report_entry["changes"].append("Adjusted clarity priority due to high response time.")

            # 成功率低
            if metrics["avg_success_rate"] < thresholds["success_rate_min"]:
                if q_type == "refactoring":
                    current_pref["safety_checks"] = True
                    report_entry["changes"].append("Enforced safety checks due to low success rate.")

            if report_entry["changes"]:
                new_style_preferences[q_type] = current_pref
                optimization_report.append(report_entry)

        self.optimization_config["style_preferences"] = new_style_preferences
        return optimization_report

    def apply_optimization(self):
        """应用生成的优化策略并保存配置（自动支持回滚）。"""
        analysis_summary = self.analyze_performance()
        if not analysis_summary:
            print("No analysis summary to apply optimizations.")
            return "No changes applied."

        optimization_report = self.generate_optimization_strategy(analysis_summary)

        if optimization_report:
            self._save_config()  # 内部会先备份旧配置
            report_str = "Optimization applied successfully. Changes:\n"
            for entry in optimization_report:
                report_str += f"- {entry['query_type']}: {', '.join(entry['changes'])}\n"
            print(report_str)
            return report_str
        else:
            print("No significant changes needed based on current performance.")
            return "No significant changes needed."

    # -------------------------
    # 工具方法
    # -------------------------

    def get_current_style(self, query_type: str):
        """根据查询类型获取当前应用的响应风格。"""
        prefs = self.optimization_config["style_preferences"]
        return prefs.get(query_type, prefs["general"])

    def generate_report(self):
        """生成 Markdown 格式的优化总结报告。"""
        summary = self.analyze_performance()
        if not summary:
            return "# 优化报告\n\n暂无交互数据。"

        lines = [
            "# 自优化 Claude 优化报告",
            f"\n**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n**总交互数**: {sum(v['sample_count'] for v in summary.values())}",
            "\n## 各查询类型性能指标\n",
            "| 查询类型 | 平均满意度 | 平均响应时间(ms) | 平均成功率 | 样本数 |",
            "| --- | --- | --- | --- | --- |",
        ]
        for q_type, m in summary.items():
            lines.append(
                f"| {q_type} | {m['avg_satisfaction']:.2f} | "
                f"{m['avg_response_time']:.0f} | {m['avg_success_rate']:.2f} | {m['sample_count']} |"
            )

        lines.append("\n## 当前风格偏好\n```json")
        lines.append(json.dumps(self.optimization_config["style_preferences"], indent=2, ensure_ascii=False))
        lines.append("```")

        return "\n".join(lines)


# -------------------------
# 示例用法
# -------------------------
if __name__ == "__main__":
    optimizer = ClaudeOptimizer()

    # 自动识别查询类型示例
    print("\n--- 查询类型自动识别 ---")
    samples = [
        "帮我写一个排序函数",
        "这段代码报错了怎么修复",
        "解释一下什么是递归",
        "重构这段代码",
        "优化这个循环的性能",
        "你好",
    ]
    for s in samples:
        print(f"  '{s}' -> {ClaudeOptimizer.detect_query_type(s)}")

    # 模拟交互追踪
    print("\n--- 模拟交互 ---")
    optimizer.track_interaction("code_generation", 3500, 0.85, True,
                                optimizer.get_current_style("code_generation"))
    optimizer.track_interaction("debugging", 6000, 0.6, False,
                                optimizer.get_current_style("debugging"))
    optimizer.track_interaction("explanation", 2000, 0.9, True,
                                optimizer.get_current_style("explanation"))
    optimizer.track_interaction("code_generation", 4000, 0.65, True,
                                optimizer.get_current_style("code_generation"))

    # 应用优化
    print("\n--- 应用优化 ---")
    result = optimizer.apply_optimization()
    print(result)

    # 生成报告
    print("\n--- 优化报告 ---")
    print(optimizer.generate_report())

    # 测试回滚
    print("\n--- 测试回滚 ---")
    print(optimizer.rollback_config())

    # 导出/导入配置
    print("\n--- 导出配置 ---")
    optimizer.export_config("my_claude_optimizations.json")

    # 新会话中导入配置
    print("\n--- 新会话导入配置 ---")
    new_optimizer = ClaudeOptimizer(config_path="my_claude_optimizations.json")
    print(new_optimizer.optimization_config)
