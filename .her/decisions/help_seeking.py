#!/usr/bin/env python3
"""
Her 的求助决策器
智能决定何时向用户求助、何时生成子代理、何时搜索网络
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum, auto

HER_DIR = Path(__file__).parent.parent
SELF_MODEL_FILE = HER_DIR / "self_model" / "identity.yaml"
DECISIONS_DIR = HER_DIR / "decisions"
DECISIONS_DIR.mkdir(parents=True, exist_ok=True)


class HelpType(Enum):
    """求助类型"""
    ASK_USER = auto()           # 直接询问用户
    SPAWN_SUBAGENT = auto()     # 生成子代理
    WEB_SEARCH = auto()         # 网络搜索
    TRY_SELF = auto()           # 自己尝试
    ESCALATE = auto()           # 升级/放弃


@dataclass
class DecisionContext:
    """决策上下文"""
    task_type: str
    task_description: str
    current_confidence: float
    time_spent_minutes: float
    time_estimated_minutes: float
    consecutive_errors: int
    repeated_attempts: int
    anomaly_detected: bool
    involves_git: bool
    involves_external_access: bool
    unknown_technology: bool


class HelpSeekingDecider:
    """
    求助决策器
    
    基于策略和上下文，决定最佳行动方案
    """
    
    def __init__(self):
        self.self_model = self._load_self_model()
        self.decision_history: List[Dict] = []
    
    def _load_self_model(self) -> dict:
        """加载自我模型"""
        if SELF_MODEL_FILE.exists():
            return yaml.safe_load(SELF_MODEL_FILE.read_text())
        return {}
    
    def decide(self, context: DecisionContext) -> Tuple[HelpType, str, Dict]:
        """
        做出求助决策
        
        返回: (help_type, reason, additional_context)
        """
        # 获取阈值
        thresholds = self.self_model.get("meta_preferences", {}).get("help_seeking_thresholds", {})
        conf_threshold = thresholds.get("confidence", 0.5)
        error_threshold = thresholds.get("repeated_error", 3)
        time_multiplier = thresholds.get("time_multiplier", 2.0)
        
        # 决策树
        
        # 1. 最高优先级：安全/权限问题
        if context.involves_git:
            return (
                HelpType.ASK_USER,
                "Git mutations require user confirmation",
                {"urgency": "immediate", "risk": "high"}
            )
        
        if context.involves_external_access:
            return (
                HelpType.ASK_USER,
                "Accessing files outside working directory requires confirmation",
                {"urgency": "immediate", "risk": "medium"}
            )
        
        # 2. 高优先级：明显超出能力范围
        if context.unknown_technology and context.current_confidence < 0.4:
            return (
                HelpType.WEB_SEARCH,
                f"Unknown technology with low confidence ({context.current_confidence:.0%})",
                {"search_terms": [context.task_type], "max_results": 5}
            )
        
        # 3. 中优先级：反复失败
        if context.consecutive_errors >= error_threshold:
            return (
                HelpType.ASK_USER,
                f"{context.consecutive_errors} consecutive errors - pattern suggests need for guidance",
                {"suggestion": "Consider trying a different approach or asking for clarification"}
            )
        
        # 4. 时间超支
        if context.time_spent_minutes > context.time_estimated_minutes * time_multiplier:
            return (
                HelpType.ASK_USER,
                f"Time exceeded estimate by {time_multiplier}x "
                f"({context.time_spent_minutes:.0f}min vs {context.time_estimated_minutes:.0f}min estimated)",
                {"options": ["continue", "get_help", "break_into_smaller_tasks"]}
            )
        
        # 5. 信心度低
        if context.current_confidence < conf_threshold:
            # 检查是否是已知弱点
            caps = self.self_model.get("capabilities", {})
            if context.task_type in caps:
                hist_conf = caps[context.task_type].get("confidence", 0.5)
                if hist_conf < conf_threshold:
                    return (
                        HelpType.SPAWN_SUBAGENT,
                        f"Low confidence ({context.current_confidence:.0%}) and historical weakness "
                        f"({hist_conf:.0%} success rate)",
                        {"subagent_type": "specialist", "isolation": True}
                    )
            
            return (
                HelpType.ASK_USER,
                f"Confidence ({context.current_confidence:.0%}) below threshold ({conf_threshold:.0%})",
                {"can_provide": "hints, examples, or take over"}
            )
        
        # 6. 复杂任务：考虑子代理
        if self._is_complex_task(context):
            return (
                HelpType.SPAWN_SUBAGENT,
                "Complex task with independent subtasks - parallelization beneficial",
                {"subagent_type": "worker", "parallel": True}
            )
        
        # 7. 异常情况
        if context.anomaly_detected:
            return (
                HelpType.ASK_USER,
                "Anomaly detected in work pattern",
                {"check": "environment monitor for details"}
            )
        
        # 默认：自己尝试
        return (
            HelpType.TRY_SELF,
            "Within capability range, no red flags",
            {"max_attempts": 3, "reassess_after": 10}
        )
    
    def _is_complex_task(self, context: DecisionContext) -> bool:
        """判断是否为复杂任务（适合子代理）"""
        # 启发式：基于描述长度、时间估计、任务类型
        if len(context.task_description) > 200:
            return True
        if context.time_estimated_minutes > 30:
            return True
        if context.task_type in ["refactor", "architecture", "multi_file"]:
            return True
        return False
    
    def record_decision(self, context: DecisionContext, decision: HelpType, reason: str):
        """记录决策历史"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "context": {
                "task_type": context.task_type,
                "confidence": context.current_confidence,
                "time_spent": context.time_spent_minutes,
            },
            "decision": decision.name,
            "reason": reason
        }
        self.decision_history.append(record)
        
        # 保存到文件
        history_file = DECISIONS_DIR / "help_seeking_history.jsonl"
        with open(history_file, "a") as f:
            f.write(json.dumps(record) + "\n")
    
    def get_decision_report(self) -> str:
        """生成决策报告"""
        if not self.decision_history:
            return "No decisions recorded yet."
        
        total = len(self.decision_history)
        type_counts = {}
        for d in self.decision_history:
            t = d["decision"]
            type_counts[t] = type_counts.get(t, 0) + 1
        
        lines = ["# Help-Seeking Decision Report", ""]
        lines.append(f"Total decisions: {total}")
        lines.append("")
        lines.append("## Decision Distribution")
        for dtype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            pct = count / total * 100
            lines.append(f"- {dtype}: {count} ({pct:.0f}%)")
        
        return "\n".join(lines)


class SubAgentDecider:
    """
    子代理生成决策器
    决定何时生成子代理、生成什么类型
    """
    
    SUBAGENT_TYPES = {
        "research": {
            "when": "Need to analyze codebase or find patterns",
            "isolation": True,
            "model": "opus"
        },
        "implement": {
            "when": "Writing code following specs",
            "isolation": True,
            "model": "opus"
        },
        "check": {
            "when": "Reviewing code against specs",
            "isolation": True,
            "model": "opus"
        },
        "debug": {
            "when": "Fixing specific errors",
            "isolation": True,
            "model": "opus"
        },
        "specialist": {
            "when": "Task requires specialized knowledge",
            "isolation": True,
            "model": "opus"
        },
        "worker": {
            "when": "Parallelizable subtask",
            "isolation": True,
            "model": "sonnet"
        }
    }
    
    def should_spawn(
        self,
        task_description: str,
        estimated_steps: int,
        requires_isolation: bool = False,
        has_independent_subtasks: bool = False
    ) -> Tuple[bool, Optional[str], Dict]:
        """
        决定是否生成子代理
        
        返回: (should_spawn, agent_type, config)
        """
        # 明确需要子代理的情况
        if requires_isolation:
            return True, "specialist", {"reason": "Context isolation required"}
        
        if has_independent_subtasks and estimated_steps > 5:
            return True, "worker", {
                "reason": "Parallel subtasks detected",
                "parallel": True
            }
        
        # 复杂度启发式
        if estimated_steps > 10:
            return True, "implement", {"reason": "High complexity (>10 steps)"}
        
        # 默认不生成
        return False, None, {}


if __name__ == "__main__":
    # 测试
    decider = HelpSeekingDecider()
    
    # 测试场景 1: 低信心度
    ctx1 = DecisionContext(
        task_type="rust_async",
        task_description="Implement async stream processor",
        current_confidence=0.3,
        time_spent_minutes=5,
        time_estimated_minutes=30,
        consecutive_errors=0,
        repeated_attempts=0,
        anomaly_detected=False,
        involves_git=False,
        involves_external_access=False,
        unknown_technology=True
    )
    
    decision, reason, extra = decider.decide(ctx1)
    print(f"Scenario 1 (Low confidence + unknown tech):")
    print(f"  Decision: {decision.name}")
    print(f"  Reason: {reason}")
    print()
    
    # 测试场景 2: 反复错误
    ctx2 = DecisionContext(
        task_type="python",
        task_description="Fix type error",
        current_confidence=0.7,
        time_spent_minutes=15,
        time_estimated_minutes=10,
        consecutive_errors=3,
        repeated_attempts=3,
        anomaly_detected=False,
        involves_git=False,
        involves_external_access=False,
        unknown_technology=False
    )
    
    decision, reason, extra = decider.decide(ctx2)
    print(f"Scenario 2 (Repeated errors):")
    print(f"  Decision: {decision.name}")
    print(f"  Reason: {reason}")
