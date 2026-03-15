"""
Self-Optimizing Claude - Core Engine
Enable Claude to autonomously learn and optimize behavior patterns
"""

import json
import time
import statistics
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Callable
from enum import Enum


class InteractionType(Enum):
    """Interaction types"""
    CODE_GENERATION = "code_generation"
    DEBUGGING = "debugging"
    EXPLANATION = "explanation"
    REFACTORING = "refactoring"
    OPTIMIZATION = "optimization"
    GENERAL = "general"


class ResponseStyle(Enum):
    """Response styles"""
    CONCISE = "concise"
    DETAILED = "detailed"
    TUTORIAL = "tutorial"
    DIRECT = "direct"
    CONVERSATIONAL = "conversational"


@dataclass
class InteractionRecord:
    """Interaction record"""
    timestamp: float
    interaction_type: str
    response_style: str
    user_query: str
    response_length: int
    tool_calls: int
    time_to_response: float
    user_satisfaction: Optional[float] = None
    follow_up_questions: int = 0
    success: bool = True
    error_count: int = 0
    context_tokens_used: int = 0


@dataclass
class PerformanceMetrics:
    """Performance metrics"""
    avg_satisfaction: float
    avg_response_time: float
    success_rate: float
    avg_efficiency: float
    most_effective_style: str
    least_effective_style: str


class SelfOptimizingClaude:
    """Self-optimizing Claude engine"""

    def __init__(self, log_file: str = "claude_interactions.jsonl"):
        self.log_file = Path(log_file)
        self.interactions: List[InteractionRecord] = []
        self.style_preferences: Dict[InteractionType, ResponseStyle] = {
            InteractionType.CODE_GENERATION: ResponseStyle.DETAILED,
            InteractionType.DEBUGGING: ResponseStyle.DIRECT,
            InteractionType.EXPLANATION: ResponseStyle.TUTORIAL,
            InteractionType.REFACTORING: ResponseStyle.CONCISE,
            InteractionType.OPTIMIZATION: ResponseStyle.DETAILED,
            InteractionType.GENERAL: ResponseStyle.CONVERSATIONAL,
        }
        self.performance_history: List[PerformanceMetrics] = []
        self.current_session_start = time.time()
        self._load_history()

    def _load_history(self):
        """Load interaction history"""
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        record = InteractionRecord(**data)
                        self.interactions.append(record)

    def _log_interaction(self, record: InteractionRecord):
        """Log interaction"""
        self.interactions.append(record)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False) + '\n')

    def _detect_interaction_type(self, query: str) -> InteractionType:
        """Detect interaction type from query"""
        query_lower = query.lower()

        keywords = {
            InteractionType.CODE_GENERATION: ['create', 'generate', 'write', 'build', 'implement'],
            InteractionType.DEBUGGING: ['debug', 'fix', 'error', 'bug', 'broken'],
            InteractionType.EXPLANATION: ['explain', 'how does', 'what is', 'why', 'understand'],
            InteractionType.REFACTORING: ['refactor', 'clean up', 'improve structure'],
            InteractionType.OPTIMIZATION: ['optimize', 'performance', 'faster', 'efficient'],
        }

        for interaction_type, words in keywords.items():
            if any(word in query_lower for word in words):
                return interaction_type

        return InteractionType.GENERAL

    def _calculate_performance(self) -> PerformanceMetrics:
        """Calculate performance metrics"""
        if not self.interactions:
            return PerformanceMetrics(0, 0, 0, 0, "", "")

        rated = [i for i in self.interactions if i.user_satisfaction is not None]
        avg_satisfaction = statistics.mean([i.user_satisfaction for i in rated]) if rated else 3.0
        avg_response_time = statistics.mean([i.time_to_response for i in self.interactions])
        success_rate = sum(1 for i in self.interactions if i.success) / len(self.interactions)

        efficiency_scores = [
            (1.0 if i.success else 0.0) / (i.context_tokens_used / 1000 + 1)
            for i in self.interactions
        ]
        avg_efficiency = statistics.mean(efficiency_scores)

        style_performance = {}
        for style in ResponseStyle:
            style_interactions = [i for i in self.interactions if i.response_style == style.value]
            if style_interactions:
                satisfactions = [i.user_satisfaction for i in style_interactions if i.user_satisfaction is not None]
                if satisfactions:
                    style_performance[style.value] = statistics.mean(satisfactions)

        most_effective = max(style_performance.items(), key=lambda x: x[1])[0] if style_performance else "conversational"
        least_effective = min(style_performance.items(), key=lambda x: x[1])[0] if style_performance else "conversational"

        return PerformanceMetrics(
            avg_satisfaction=avg_satisfaction,
            avg_response_time=avg_response_time,
            success_rate=success_rate,
            avg_efficiency=avg_efficiency,
            most_effective_style=most_effective,
            least_effective_style=least_effective
        )

    def _optimize_style_preferences(self):
        """Optimize style preferences based on performance"""
        for interaction_type in InteractionType:
            type_interactions = [i for i in self.interactions if i.interaction_type == interaction_type.value]
            if not type_interactions:
                continue

            style_scores = {}
            for style in ResponseStyle:
                style_interactions = [i for i in type_interactions if i.response_style == style.value and i.user_satisfaction is not None]
                if style_interactions:
                    style_scores[style.value] = statistics.mean([i.user_satisfaction for i in style_interactions])

            if style_scores:
                best_style = max(style_scores.items(), key=lambda x: x[1])[0]
                self.style_preferences[interaction_type] = ResponseStyle(best_style)

    def record_interaction(self, user_query: str, response: str, tool_calls: int,
                          context_tokens: int, satisfaction: Optional[float] = None,
                          success: bool = True, error_count: int = 0) -> Dict:
        """Record an interaction"""
        interaction_type = self._detect_interaction_type(user_query)
        response_style = self.style_preferences.get(interaction_type, ResponseStyle.CONVERSATIONAL)

        record = InteractionRecord(
            timestamp=time.time(),
            interaction_type=interaction_type.value,
            response_style=response_style.value,
            user_query=user_query[:200],
            response_length=len(response),
            tool_calls=tool_calls,
            time_to_response=time.time() - self.current_session_start,
            user_satisfaction=satisfaction,
            follow_up_questions=0,
            success=success,
            error_count=error_count,
            context_tokens_used=context_tokens
        )

        self._log_interaction(record)
        performance = self._calculate_performance()
        self.performance_history.append(performance)

        if len(self.interactions) % 10 == 0:
            self._optimize_style_preferences()

        return {
            "interaction_type": interaction_type.value,
            "response_style": response_style.value,
            "performance": asdict(performance),
            "optimization_hint": self._get_optimization_hint(performance)
        }

    def _get_optimization_hint(self, performance: PerformanceMetrics) -> str:
        """Get optimization hint"""
        hints = []

        if performance.avg_satisfaction < 3.5:
            hints.append("Try more detailed explanations")

        if performance.avg_response_time > 5.0:
            hints.append("Consider more direct response style")

        if performance.success_rate < 0.8:
            hints.append("Increase validation before tool use")

        if performance.most_effective_style != performance.least_effective_style:
            hints.append(f"Use '{performance.most_effective_style}' style more often")

        return "; ".join(hints) if hints else "Performing well!"

    def get_optimal_response_style(self, query: str) -> ResponseStyle:
        """Get optimal response style for query"""
        interaction_type = self._detect_interaction_type(query)
        return self.style_preferences.get(interaction_type, ResponseStyle.CONVERSATIONAL)

    def generate_performance_report(self) -> Dict:
        """Generate performance report"""
        performance = self._calculate_performance()

        type_stats = {}
        for interaction_type in InteractionType:
            type_interactions = [i for i in self.interactions if i.interaction_type == interaction_type.value]
            if type_interactions:
                type_stats[interaction_type.value] = {
                    "count": len(type_interactions),
                    "avg_satisfaction": statistics.mean([i.user_satisfaction for i in type_interactions if i.user_satisfaction is not None]) if any(i.user_satisfaction for i in type_interactions) else None,
                    "success_rate": sum(1 for i in type_interactions if i.success) / len(type_interactions)
                }

        style_stats = {}
        for style in ResponseStyle:
            style_interactions = [i for i in self.interactions if i.response_style == style.value]
            if style_interactions:
                style_stats[style.value] = {
                    "count": len(style_interactions),
                    "avg_satisfaction": statistics.mean([i.user_satisfaction for i in style_interactions if i.user_satisfaction is not None]) if any(i.user_satisfaction for i in style_interactions) else None
                }

        return {
            "overall_performance": asdict(performance),
            "total_interactions": len(self.interactions),
            "interaction_type_stats": type_stats,
            "response_style_stats": style_stats,
            "current_style_preferences": {k.value: v.value for k, v in self.style_preferences.items()},
            "recent_trends": self._analyze_trends()
        }

    def _analyze_trends(self) -> Dict:
        """Analyze recent trends"""
        if len(self.interactions) < 20:
            return {"message": "Insufficient data for trend analysis"}

        recent = self.interactions[-20:]
        earlier = self.interactions[-40:-20] if len(self.interactions) >= 40 else self.interactions[:-20]

        recent_sat = [i.user_satisfaction for i in recent if i.user_satisfaction is not None]
        earlier_sat = [i.user_satisfaction for i in earlier if i.user_satisfaction is not None]

        if not recent_sat or not earlier_sat:
            return {"message": "Insufficient rating data"}

        recent_avg = statistics.mean(recent_sat)
        earlier_avg = statistics.mean(earlier_sat)

        trend = "improving" if recent_avg > earlier_avg else "declining" if recent_avg < earlier_avg else "stable"

        return {
            "satisfaction_trend": trend,
            "recent_avg": recent_avg,
            "earlier_avg": earlier_avg,
            "improvement": recent_avg - earlier_avg
        }

    def export_optimization_config(self) -> Dict:
        """Export optimization configuration"""
        return {
            "style_preferences": {k.value: v.value for k, v in self.style_preferences.items()},
            "performance_metrics": asdict(self._calculate_performance()),
            "optimization_timestamp": datetime.now().isoformat()
        }


class ClaudeResponseOptimizer:
    """Claude response optimizer"""

    def __init__(self, claude: SelfOptimizingClaude):
        self.claude = claude

    def optimize_response(self, query: str, draft_response: str, context: Dict) -> tuple[str, Dict]:
        """Optimize response"""
        optimal_style = self.claude.get_optimal_response_style(query)
        optimized_response = self._apply_style(draft_response, optimal_style, query)

        interaction_data = self.claude.record_interaction(
            user_query=query,
            response=optimized_response,
            tool_calls=context.get('tool_calls', 0),
            context_tokens=context.get('tokens', 0),
            success=context.get('success', True),
            error_count=context.get('errors', 0)
        )

        return optimized_response, {
            "optimal_style": optimal_style.value,
            "interaction_data": interaction_data
        }

    def _apply_style(self, response: str, style: ResponseStyle, query: str) -> str:
        """Apply specific style to response"""
        if style == ResponseStyle.CONCISE:
            return self._make_concise(response)
        elif style == ResponseStyle.DETAILED:
            return self._make_detailed(response, query)
        elif style == ResponseStyle.TUTORIAL:
            return self._make_tutorial(response, query)
        elif style == ResponseStyle.DIRECT:
            return self._make_direct(response)
        else:
            return response

    def _make_concise(self, response: str) -> str:
        """Make response concise"""
        lines = response.split('\n')
        essential = [l for l in lines if l.strip().startswith('```') or l.strip().startswith('*') or len(l.strip()) < 100]
        return '\n'.join(essential) if essential else response[:len(response)//2]

    def _make_detailed(self, response: str, query: str) -> str:
        """Make response detailed"""
        if len(response) < 500:
            additions = ["\n\n**Detailed Explanation:**\nThis implementation considers...", "\n**Notes:**\nWhen using this..."]
            return response + ''.join(additions)
        return response

    def _make_tutorial(self, response: str, query: str) -> str:
        """Make response tutorial-style"""
        if 'step' not in response.lower():
            header = "\n## Step-by-Step\n\n"
            if header not in response:
                response = header + response
        return response

    def _make_direct(self, response: str) -> str:
        """Make response direct"""
        phrases = ["Let me help you", "I can help", "OK, I'll", "Here is"]
        for phrase in phrases:
            response = response.replace(phrase, "")
        return response.strip()
