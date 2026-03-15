# Self-Optimizing Claude - Usage Patterns

Advanced usage patterns for integrating and maximizing the self-optimizing system.

## Integration Patterns

### Pattern 1: Session-Based Learning

```python
# Initialize at session start
claude = SelfOptimizingClaude(log_file="session_2024_03_15.jsonl")
optimizer = ClaudeResponseOptimizer(claude)

# Use throughout session
for query in user_queries:
    response = generate_response(query)
    optimized, metadata = optimizer.optimize_response(
        query=query,
        draft_response=response,
        context=get_context()
    )
    send_to_user(optimized)

# Review performance at end
report = claude.generate_performance_report()
save_report(report, "performance_report.json")
```

### Pattern 2: Cross-Session Persistence

```python
# Session 1: Initial learning
claude_v1 = SelfOptimizingClaude(log_file="user123_interactions.jsonl")
# ... interactions ...
config = claude_v1.export_optimization_config()

# Session 2: Load learned preferences
claude_v2 = SelfOptimizingClaude(log_file="user123_interactions.jsonl")
claude_v2.style_preferences = {
    InteractionType(k): ResponseStyle(v)
    for k, v in config['style_preferences'].items()
}
# Starts with learned preferences!
```

### Pattern 3: Multi-User Personalization

```python
# Each user gets separate learning
user_claudes = {}

def get_user_claude(user_id: str) -> SelfOptimizingClaude:
    if user_id not in user_claudes:
        user_claudes[user_id] = SelfOptimizingClaude(
            log_file=f"users/{user_id}/interactions.jsonl"
        )
    return user_claudes[user_id]

# User-specific optimization
claude = get_user_claude(user_id)
# ... interactions ...
```

## Performance Analysis Patterns

### Pattern 1: Satisfaction Trend Analysis

```python
report = claude.generate_performance_report()
trends = report['recent_trends']

if trends['satisfaction_trend'] == 'improving':
    print(f"Improvement: {trends['improvement']:.2f} points")
elif trends['satisfaction_trend'] == 'declining':
    print(f"Decline: {trends['improvement']:.2f} points - adjust strategy")
```

### Pattern 2: Style Effectiveness Comparison

```python
style_stats = report['response_style_stats']

# Find best performing style
best_style = max(
    style_stats.items(),
    key=lambda x: x[1]['avg_satisfaction'] if x[1]['avg_satisfaction'] else 0
)

print(f"Best style: {best_style[0]}")
print(f"Average satisfaction: {best_style[1]['avg_satisfaction']:.2f}")
```

### Pattern 3: Type-Specific Performance

```python
type_stats = report['interaction_type_stats']

# Identify weak areas
weak_areas = [
    (int_type, stats)
    for int_type, stats in type_stats.items()
    if stats['avg_satisfaction'] and stats['avg_satisfaction'] < 3.5
]

for int_type, stats in weak_areas:
    print(f"Needs improvement: {int_type}")
    print(f"  Current satisfaction: {stats['avg_satisfaction']:.2f}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
```

## Optimization Strategies

### Strategy 1: Active Learning

```python
# Occasionally test alternative styles
import random

def should_experiment():
    return random.random() < 0.1  # 10% of the time

def get_response_style(query: str) -> ResponseStyle:
    if should_experiment():
        # Try random style to gather data
        return random.choice(list(ResponseStyle))
    else:
        # Use learned preference
        return claude.get_optimal_response_style(query)
```

### Strategy 2: Context-Aware Optimization

```python
# Adjust style based on additional context
def get_context_aware_style(query: str, urgency: str) -> ResponseStyle:
    base_style = claude.get_optimal_response_style(query)

    if urgency == "high":
        # Override to direct for urgent queries
        return ResponseStyle.DIRECT
    elif urgency == "low":
        # Use more detailed style for learning
        return ResponseStyle.DETAILED
    else:
        return base_style
```

### Strategy 3: Feedback-Driven Tuning

```python
# After each interaction, collect feedback
def collect_and_apply_feedback(query: str, response: str, rating: int):
    # Record with satisfaction score
    claude.record_interaction(
        user_query=query,
        response=response,
        tool_calls=0,
        context_tokens=1000,
        satisfaction=rating
    )

    # If low rating, trigger immediate optimization
    if rating < 3.0:
        claude._optimize_style_preferences()
        print("Preferences updated based on feedback")
```

## Data Export Patterns

### Pattern 1: Performance Dashboard

```python
def create_dashboard_data(claude: SelfOptimizingClaude) -> dict:
    report = claude.generate_performance_report()

    return {
        "overview": {
            "total_interactions": report['total_interactions'],
            "avg_satisfaction": report['overall_performance']['avg_satisfaction'],
            "success_rate": report['overall_performance']['success_rate']
        },
        "by_type": report['interaction_type_stats'],
        "by_style": report['response_style_stats'],
        "trends": report['recent_trends'],
        "preferences": report['current_style_preferences']
    }

# Export for visualization
dashboard_data = create_dashboard_data(claude)
with open("dashboard.json", "w") as f:
    json.dump(dashboard_data, f, indent=2)
```

### Pattern 2: CSV Export for Analysis

```python
import csv

def export_interactions_to_csv(claude: SelfOptimizingClaude, output_file: str):
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'type', 'style', 'satisfaction',
                        'response_time', 'success', 'tokens'])

        for record in claude.interactions:
            writer.writerow([
                record.timestamp,
                record.interaction_type,
                record.response_style,
                record.user_satisfaction,
                record.time_to_response,
                record.success,
                record.context_tokens_used
            ])

export_interactions_to_csv(claude, "analysis.csv")
```

### Pattern 3: Config Backup and Restore

```python
def backup_config(claude: SelfOptimizingClaude, backup_path: str):
    config = claude.export_optimization_config()
    with open(backup_path, 'w') as f:
        json.dump(config, f, indent=2)

def restore_config(claude: SelfOptimizingClaude, backup_path: str):
    with open(backup_path, 'r') as f:
        config = json.load(f)

    claude.style_preferences = {
        InteractionType(k): ResponseStyle(v)
        for k, v in config['style_preferences'].items()
    }

# Usage
backup_config(claude, "config_backup_2024_03_15.json")
# Later...
restore_config(claude, "config_backup_2024_03_15.json")
```

## Best Practices

### 1. Data Collection

- Collect satisfaction scores consistently
- Log every interaction, even failed ones
- Include context about the environment

### 2. Optimization Frequency

- Default: Every 10 interactions
- High-volume: Every 50-100 interactions
- Low-volume: After 5 interactions

### 3. Config Management

- Backup configs before major changes
- Version control your configs
- Label configs with dates/contexts

### 4. Performance Monitoring

- Review reports weekly
- Track trends over time
- Compare before/after experiments

### 5. Privacy Considerations

- Sanitize sensitive data before logging
- Encrypt log files if needed
- Comply with data retention policies

## Troubleshooting

### Issue: Low satisfaction scores

**Diagnosis:**
```python
report = claude.generate_performance_report()
print(f"Overall: {report['overall_performance']['avg_satisfaction']}")
```

**Solutions:**
- Review which types have lowest satisfaction
- Experiment with different styles for those types
- Collect more feedback to validate trends

### Issue: No learning happening

**Diagnosis:**
```python
print(f"Total interactions: {len(claude.interactions)}")
print(f"Style preferences: {claude.style_preferences}")
```

**Solutions:**
- Ensure satisfaction scores are being recorded
- Check that optimization is triggering (every 10 interactions)
- Verify interaction types are detected correctly

### Issue: High memory usage

**Solution:**
```python
# Archive old interactions
def archive_interactions(claude: SelfOptimizingClaude, cutoff_days: int):
    cutoff_time = time.time() - (cutoff_days * 86400)
    recent = [i for i in claude.interactions if i.timestamp > cutoff_time]
    archived = [i for i in claude.interactions if i.timestamp <= cutoff_time]

    # Save archived
    with open(f"archived_{cutoff_days}days.jsonl", 'w') as f:
        for record in archived:
            f.write(json.dumps(asdict(record)) + '\n')

    # Keep only recent
    claude.interactions = recent
```

## Advanced Topics

### Custom Interaction Types

```python
class CustomInteractionType(InteractionType):
    CODE_REVIEW = "code_review"
    DOCUMENTATION = "documentation"

# Extend detection logic
def _detect_interaction_type(self, query: str) -> InteractionType:
    query_lower = query.lower()

    if "review" in query_lower and "code" in query_lower:
        return CustomInteractionType.CODE_REVIEW
    elif "document" in query_lower:
        return CustomInteractionType.DOCUMENTATION

    # ... rest of detection logic
```

### Multi-Objective Optimization

```python
def calculate_weighted_score(record: InteractionRecord) -> float:
    satisfaction_weight = 0.5
    speed_weight = 0.3
    efficiency_weight = 0.2

    score = (
        (record.user_satisfaction or 3.0) * satisfaction_weight +
        (1.0 / (record.time_to_response + 1)) * speed_weight +
        (1.0 / (record.context_tokens_used / 1000 + 1)) * efficiency_weight
    )
    return score
```

### A/B Testing Framework

```python
def run_ab_test(claude: SelfOptimizingClaude, query: str, style_a: ResponseStyle, style_b: ResponseStyle):
    # Force both styles
    response_a = apply_style(generate_response(query), style_a)
    response_b = apply_style(generate_response(query), style_b)

    # Present both and collect ratings
    rating_a = collect_rating(query, response_a)
    rating_b = collect_rating(query, response_b)

    return {
        "style_a": {"style": style_a.value, "rating": rating_a},
        "style_b": {"style": style_b.value, "rating": rating_b},
        "winner": style_a if rating_a > rating_b else style_b
    }
```
