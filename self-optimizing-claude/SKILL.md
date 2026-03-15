---
name: self-optimizing-claude
description: Enable Claude to autonomously learn and optimize its own behavior patterns through interaction tracking, performance analysis, and automatic style preference adjustment. Use when Claude needs to: (1) Track and analyze interaction performance metrics (satisfaction, response time, success rate), (2) Automatically learn optimal response styles for different query types (code generation, debugging, explanation, refactoring, optimization), (3) Continuously improve responses based on historical data, (4) Export and import optimization configurations across sessions. This skill transforms Claude from a static assistant into an adaptive system that learns from every interaction.
---

# Self-Optimizing Claude

Enable Claude to autonomously learn and optimize behavior patterns through continuous interaction tracking and performance analysis.

## Core Workflow

```
User Query → Detect Type → Select Optimal Style → Generate Response → Track Performance
                                                          ↓
                                                    Analyze Metrics
                                                          ↓
                                                    Update Preferences
                                                          ↓
                                                Improve Future Responses
```

## Quick Start

### Initialize Optimizer

```python
from self_optimizing_claude import SelfOptimizingClaude, ClaudeResponseOptimizer

claude = SelfOptimizingClaude(log_file="interactions.jsonl")
optimizer = ClaudeResponseOptimizer(claude)
```

### Process Interactions

```python
optimized, metadata = optimizer.optimize_response(
    query="Create a sorting algorithm",
    draft_response="```python\ndef sort(arr):...\n```",
    context={
        "tool_calls": 0,
        "tokens": 300,
        "success": True,
        "errors": 0
    }
)
```

### Generate Performance Report

```python
report = claude.generate_performance_report()
print(f"Satisfaction: {report['overall_performance']['avg_satisfaction']}")
print(f"Success rate: {report['overall_performance']['success_rate']}")
```

## Query Type Detection

The system automatically detects these interaction types:

- **code_generation** → `detailed` style (complete code + explanations)
- **debugging** → `direct` style (quick solutions)
- **explanation** → `tutorial` style (step-by-step learning)
- **refactoring** → `concise` style (clean improvements)
- **optimization** → `detailed` style (performance analysis)
- **general** → `conversational` style (natural dialogue)

## Response Styles

- **concise**: Minimal, essential information only
- **detailed**: Complete with extensive context
- **tutorial**: Step-by-step, educational approach
- **direct**: Immediate solution, minimal explanation
- **conversational**: Natural, dialogue-like

## Performance Metrics

Tracked automatically:
- **Satisfaction** (1-5): User rating
- **Response time**: Objective performance
- **Success rate**: Problem resolution rate
- **Efficiency**: Success / Token usage
- **Style effectiveness**: Per-style satisfaction

## Auto-Optimization

Every 10 interactions, the system:
1. Analyzes satisfaction by style
2. Updates style preferences
3. Generates optimization insights
4. Saves learning progress

## Export Configuration

```python
config = claude.export_optimization_config()
# Save for future sessions
```

## Advanced Patterns

For detailed usage patterns, integration strategies, and performance optimization techniques, see [references/usage_patterns.md](references/usage_patterns.md).

## Implementation Notes

The core engine is in `scripts/self_optimizing_claude.py`. Execute directly without loading into context for optimal token efficiency.
