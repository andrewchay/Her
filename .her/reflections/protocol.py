#!/usr/bin/env python3
"""
Her 的反思协议
任务前、中、后的强制反思机制
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict
from enum import Enum

HER_DIR = Path(__file__).parent.parent
REFLECTIONS_DIR = HER_DIR / "reflections"
REFLECTIONS_DIR.mkdir(parents=True, exist_ok=True)


class ReflectionPhase(Enum):
    PRE_TASK = "pre_task"      # 任务前：计划与评估
    MID_TASK = "mid_task"      # 任务中：检查与调整
    POST_TASK = "post_task"    # 任务后：总结与学习


@dataclass
class Reflection:
    """反思记录"""
    id: str
    timestamp: str
    phase: str
    task_id: str
    task_description: str
    
    # 反思内容
    what_happened: str
    why_it_happened: str
    what_i_learned: str
    what_to_do_differently: str
    
    # 元数据
    confidence_before: float
    confidence_after: float
    deviations_from_plan: List[str]
    emotions: Optional[str] = None  # 可选：记录挫败感、兴奋等
    
    def to_dict(self) -> dict:
        return asdict(self)


class ReflectionProtocol:
    """
    反思协议
    
    强制 Her 在关键节点进行结构化反思
    """
    
    # 反思提示模板
    PRE_TASK_PROMPT = """
## Pre-Task Reflection (任务前反思)

Before starting this task, I must answer:

1. **What is the goal?**
   - 用一句话描述任务目标

2. **How confident am I?** (0-1)
   - 基于类似任务的历史表现
   - 基于对技术栈的熟悉程度

3. **What could go wrong?**
   - 列出 2-3 个可能的风险点

4. **When should I ask for help?**
   - 明确的求助触发条件
   - 例如："如果 30 分钟内无法解决 X，就求助"

5. **What is my plan?**
   - 步骤 1, 2, 3...

---
**Task**: {task_description}
**My Confidence**: ___/1.0
"""

    MID_TASK_PROMPT = """
## Mid-Task Reflection (任务中检查)

I'm currently at step {current_step} of {total_steps}.

Quick check:
- [ ] Am I on track? 
- [ ] Has anything unexpected happened?
- [ ] Is my confidence still the same?
- [ ] Should I adjust my plan?

If stuck for >10 min: CONSIDER SEEKING HELP
"""

    POST_TASK_PROMPT = """
## Post-Task Reflection (任务后总结)

Task completed: {task_description}
Success: {success}

### What went well?
(具体描述，不只是"it worked")

### What was harder than expected?
(技术难点、理解偏差等)

### Did I deviate from the plan? Why?
(计划 vs 实际的差异)

### What did I learn?
(新知识、新技能、新认识)

### What would I do differently next time?
(可操作的改进点)

### Should this update my self-model?
- [ ] Yes, my capability assessment needs adjustment
- [ ] Yes, I discovered a new failure pattern
- [ ] Yes, I confirmed a success pattern
- [ ] No, this was routine work

---
**Confidence Before**: {confidence_before}
**Confidence After**: {confidence_after}
**Time Taken**: {duration_minutes} min
"""

    def __init__(self):
        self.current_reflection: Optional[Reflection] = None
    
    def pre_task(self, task_id: str, task_description: str) -> str:
        """
        生成任务前反思提示
        返回：应该向用户/系统展示的反思模板
        """
        return self.PRE_TASK_PROMPT.format(task_description=task_description)
    
    def post_task(
        self,
        task_id: str,
        task_description: str,
        success: bool,
        confidence_before: float,
        confidence_after: float,
        duration_minutes: float,
        what_happened: str,
        deviations: List[str],
        learnings: str
    ) -> Reflection:
        """
        创建任务后反思记录
        """
        reflection = Reflection(
            id=f"{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            phase=ReflectionPhase.POST_TASK.value,
            task_id=task_id,
            task_description=task_description,
            what_happened=what_happened,
            why_it_happened="",  # 由 Her 填写
            what_i_learned=learnings,
            what_to_do_differently="",  # 由 Her 填写
            confidence_before=confidence_before,
            confidence_after=confidence_after,
            deviations_from_plan=deviations
        )
        
        self._save_reflection(reflection)
        return reflection
    
    def _save_reflection(self, reflection: Reflection):
        """保存反思记录"""
        filepath = REFLECTIONS_DIR / f"{reflection.id}.json"
        filepath.write_text(json.dumps(reflection.to_dict(), indent=2))
    
    def get_recent_reflections(self, n: int = 5) -> List[Reflection]:
        """获取最近的反思记录"""
        reflections = []
        for f in sorted(REFLECTIONS_DIR.glob("*.json"), reverse=True)[:n]:
            data = json.loads(f.read_text())
            reflections.append(Reflection(**data))
        return reflections
    
    def analyze_patterns(self) -> Dict:
        """分析反思模式，提取洞察"""
        reflections = self.get_recent_reflections(20)
        
        if not reflections:
            return {"message": "Not enough reflections for pattern analysis"}
        
        # 简单统计
        total = len(reflections)
        confidence_drops = sum(
            1 for r in reflections 
            if r.confidence_after < r.confidence_before
        )
        
        # 常见偏差
        all_deviations = []
        for r in reflections:
            all_deviations.extend(r.deviations_from_plan)
        
        deviation_counts = {}
        for d in all_deviations:
            deviation_counts[d] = deviation_counts.get(d, 0) + 1
        
        return {
            "total_reflections": total,
            "confidence_drop_rate": confidence_drops / total if total > 0 else 0,
            "common_deviations": sorted(
                deviation_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5],
            "recent_learning_themes": self._extract_themes(reflections[:5])
        }
    
    def _extract_themes(self, reflections: List[Reflection]) -> List[str]:
        """提取学习主题（简化版）"""
        themes = []
        for r in reflections:
            if "type" in r.what_i_learned.lower():
                themes.append("type_system")
            if "async" in r.what_i_learned.lower():
                themes.append("async_patterns")
            if "test" in r.what_i_learned.lower():
                themes.append("testing")
        return list(set(themes))


class MetaCognitivePrompts:
    """
    元认知提示模板
    在关键决策点插入这些提示
    """
    
    BEFORE_EDIT = """
🤔 [Meta-Cognitive Check] Before editing:
- Why am I changing this file?
- What could break?
- Is this the minimal change needed?
"""

    BEFORE_SUBAGENT = """
🤔 [Meta-Cognitive Check] Before spawning subagent:
- Is the task well-defined enough to delegate?
- What context does the subagent need?
- How will I verify the result?
"""

    WHEN_STUCK = """
🤔 [Meta-Cognitive Check] I've been stuck for a while:
- What have I tried?
- What haven't I tried?
- Should I ask for help now?
"""

    CONFIDENCE_CHECK = """
🤔 [Meta-Cognitive Check] Confidence assessment:
- Current confidence: ___/1.0
- Based on: ___
- If < 0.5, I should seek help
"""


if __name__ == "__main__":
    # 测试
    protocol = ReflectionProtocol()
    
    print("=== Pre-Task Reflection ===")
    print(protocol.pre_task("test-1", "Implement user authentication"))
    
    print("\n=== Post-Task Reflection ===")
    reflection = protocol.post_task(
        task_id="test-1",
        task_description="Implement user authentication",
        success=True,
        confidence_before=0.7,
        confidence_after=0.8,
        duration_minutes=45,
        what_happened="Implemented JWT-based auth",
        deviations=["Used library X instead of Y"],
        learnings="Library X has better TypeScript support"
    )
    print(f"Saved reflection: {reflection.id}")
    
    print("\n=== Pattern Analysis ===")
    print(json.dumps(protocol.analyze_patterns(), indent=2))
