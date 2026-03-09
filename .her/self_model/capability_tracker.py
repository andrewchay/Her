#!/usr/bin/env python3
"""
Her 的能力追踪器
动态更新自我模型中的能力评估
"""

import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

SELF_MODEL_DIR = Path(__file__).parent
IDENTITY_FILE = SELF_MODEL_DIR / "identity.yaml"


@dataclass
class TaskOutcome:
    """单次任务的结果"""
    task_type: str
    success: bool
    duration_minutes: float
    confidence_before: float
    confidence_after: float
    errors_encountered: int
    help_seeking_events: int
    notes: str


class CapabilityTracker:
    """追踪和更新能力评估"""
    
    def __init__(self):
        self.identity = self._load_identity()
    
    def _load_identity(self) -> dict:
        """加载身份模型"""
        if IDENTITY_FILE.exists():
            return yaml.safe_load(IDENTITY_FILE.read_text())
        return {}
    
    def _save_identity(self):
        """保存身份模型"""
        IDENTITY_FILE.write_text(yaml.dump(self.identity, allow_unicode=True, sort_keys=False))
    
    def record_task(self, outcome: TaskOutcome):
        """记录任务结果，更新能力评估"""
        stats = self.identity.get("session_stats", {})
        stats["total_tasks"] = stats.get("total_tasks", 0) + 1
        if outcome.success:
            stats["successful_tasks"] = stats.get("successful_tasks", 0) + 1
        else:
            stats["failed_tasks"] = stats.get("failed_tasks", 0) + 1
        
        # 更新对应能力的信心度（指数移动平均）
        cap_key = outcome.task_type
        caps = self.identity.get("capabilities", {})
        
        if cap_key in caps:
            current = caps[cap_key].get("confidence", 0.5)
            # 根据结果调整：成功+0.05，失败-0.1
            delta = 0.05 if outcome.success else -0.10
            new_confidence = max(0.1, min(0.99, current + delta))
            caps[cap_key]["confidence"] = round(new_confidence, 2)
            caps[cap_key]["last_updated"] = datetime.now().isoformat()
        
        # 添加到学习日志
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "task_type": outcome.task_type,
            "success": outcome.success,
            "confidence_delta": outcome.confidence_after - outcome.confidence_before,
            "key_lesson": outcome.notes[:200] if outcome.notes else ""
        }
        
        learning_log = self.identity.get("learning_log", [])
        learning_log.insert(0, log_entry)
        self.identity["learning_log"] = learning_log[:10]  # 保留最近 10 条
        
        self._save_identity()
    
    def get_capability_report(self) -> str:
        """生成能力报告"""
        lines = ["# Her 的能力评估报告", ""]
        
        caps = self.identity.get("capabilities", {})
        for name, data in caps.items():
            conf = data.get("confidence", 0)
            bar = "█" * int(conf * 10) + "░" * (10 - int(conf * 10))
            lines.append(f"{name:20} [{bar}] {conf:.0%}")
        
        lines.append("")
        stats = self.identity.get("session_stats", {})
        total = stats.get("total_tasks", 0)
        success = stats.get("successful_tasks", 0)
        if total > 0:
            lines.append(f"任务成功率: {success}/{total} ({success/total:.0%})")
        
        return "\n".join(lines)
    
    def should_seek_help(self, task_type: str, current_confidence: float) -> tuple[bool, str]:
        """
        判断是否应该寻求帮助
        返回: (should_help, reason)
        """
        thresholds = self.identity.get("meta_preferences", {}).get("help_seeking_thresholds", {})
        conf_threshold = thresholds.get("confidence", 0.5)
        
        if current_confidence < conf_threshold:
            return True, f"信心度 {current_confidence:.0%} 低于阈值 {conf_threshold:.0%}"
        
        caps = self.identity.get("capabilities", {})
        if task_type in caps:
            historical_conf = caps[task_type].get("confidence", 0.5)
            if historical_conf < conf_threshold:
                return True, f"历史成功率 {historical_conf:.0%} 较低"
        
        return False, ""


if __name__ == "__main__":
    # 测试
    tracker = CapabilityTracker()
    print(tracker.get_capability_report())
