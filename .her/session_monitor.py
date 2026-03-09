#!/usr/bin/env python3
"""
Her 的会话监控器
整合所有元认知组件，管理完整会话生命周期
"""

import json
import yaml
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass, field

# 导入 Her 的组件
import sys
HER_DIR = Path(__file__).parent
sys.path.insert(0, str(HER_DIR))

from self_model.capability_tracker import CapabilityTracker, TaskOutcome
from environment.monitor import EnvironmentMonitor, EnvironmentSnapshot
from reflections.protocol import ReflectionProtocol, ReflectionPhase, MetaCognitivePrompts
from decisions.help_seeking import HelpSeekingDecider, DecisionContext, HelpType

SESSIONS_DIR = HER_DIR / "sessions"
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class SessionState:
    """会话状态"""
    session_id: str
    started_at: str
    task_id: Optional[str] = None
    task_description: Optional[str] = None
    phase: str = "initializing"  # initializing | planning | executing | reflecting | completed
    
    # 时间追踪
    phase_start_time: Optional[float] = None
    task_start_time: Optional[float] = None
    
    # 评估
    confidence_at_start: float = 0.5
    current_confidence: float = 0.5
    
    # 统计
    tools_used: Dict[str, int] = field(default_factory=dict)
    errors_encountered: int = 0
    help_seeking_events: int = 0
    
    # 反思
    pre_task_reflection: Optional[str] = None
    post_task_reflection: Optional[str] = None


class HerSession:
    """
    Her 的会话管理器
    
    这是 Her 的"大脑"，协调所有元认知功能：
    - 自我模型追踪
    - 环境监控
    - 反思协议
    - 求助决策
    """
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        
        # 初始化组件
        self.capability_tracker = CapabilityTracker()
        self.environment_monitor = EnvironmentMonitor(project_root)
        self.reflection_protocol = ReflectionProtocol()
        self.help_decider = HelpSeekingDecider()
        
        # 会话状态
        self.state: Optional[SessionState] = None
        self.session_file: Optional[Path] = None
    
    def start_session(self, task_id: Optional[str] = None, task_description: Optional[str] = None) -> str:
        """
        开始新会话
        
        返回：会话启动报告
        """
        session_id = f"her_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.state = SessionState(
            session_id=session_id,
            started_at=datetime.now().isoformat(),
            task_id=task_id,
            task_description=task_description
        )
        
        self.session_file = SESSIONS_DIR / f"{session_id}.json"
        self._save_state()
        
        # 捕获初始环境快照
        self.environment_monitor.session_id = session_id
        self.environment_monitor.save_snapshot()
        
        # 生成启动报告
        report = self._generate_start_report()
        return report
    
    def start_task(self, task_id: str, task_description: str) -> str:
        """
        开始新任务
        
        触发：任务前反思
        """
        if self.state is None:
            self.start_session(task_id, task_description)
        
        self.state.task_id = task_id
        self.state.task_description = task_description
        self.state.phase = "planning"
        self.state.task_start_time = time.time()
        self.state.phase_start_time = time.time()
        
        # 评估初始信心度
        self.state.confidence_at_start = self._assess_initial_confidence(task_description)
        self.state.current_confidence = self.state.confidence_at_start
        
        self._save_state()
        
        # 返回任务前反思提示
        return self.reflection_protocol.pre_task(task_id, task_description)
    
    def check_should_seek_help(self) -> Optional[str]:
        """
        检查是否应该寻求帮助
        
        返回：如果需要帮助，返回建议消息；否则返回 None
        """
        if self.state is None:
            return None
        
        # 构建决策上下文
        time_spent = (time.time() - self.state.task_start_time) / 60 if self.state.task_start_time else 0
        time_estimated = self._estimate_time(self.state.task_description)
        
        context = DecisionContext(
            task_type=self._classify_task(self.state.task_description),
            task_description=self.state.task_description,
            current_confidence=self.state.current_confidence,
            time_spent_minutes=time_spent,
            time_estimated_minutes=time_estimated,
            consecutive_errors=self.state.errors_encountered,
            repeated_attempts=self.state.help_seeking_events,
            anomaly_detected=len(self.environment_monitor.detect_anomalies()) > 0,
            involves_git=False,  # 由具体工具检测
            involves_external_access=False,
            unknown_technology=self._is_unknown_technology(self.state.task_description)
        )
        
        decision, reason, extra = self.help_decider.decide(context)
        
        if decision != HelpType.TRY_SELF:
            self.help_decider.record_decision(context, decision, reason)
            self.state.help_seeking_events += 1
            self._save_state()
            
            return self._format_help_suggestion(decision, reason, extra)
        
        return None
    
    def record_tool_use(self, tool_name: str):
        """记录工具使用"""
        if self.state:
            self.state.tools_used[tool_name] = self.state.tools_used.get(tool_name, 0) + 1
            self.environment_monitor.record_tool_use(tool_name)
            self._save_state()
    
    def record_error(self):
        """记录错误"""
        if self.state:
            self.state.errors_encountered += 1
            self.environment_monitor.record_error()
            self._save_state()
    
    def record_success(self):
        """记录成功"""
        self.environment_monitor.record_success()
    
    def record_file_edit(self, filepath: str):
        """记录文件编辑"""
        self.environment_monitor.record_file_edit(filepath)
    
    def update_confidence(self, new_confidence: float):
        """更新当前信心度"""
        if self.state:
            self.state.current_confidence = new_confidence
            self._save_state()
    
    def end_task(self, success: bool, what_happened: str, learnings: str, deviations: List[str]) -> str:
        """
        结束任务
        
        触发：任务后反思、能力更新
        """
        if self.state is None:
            return "No active task"
        
        duration = (time.time() - self.state.task_start_time) / 60 if self.state.task_start_time else 0
        
        # 记录任务结果
        outcome = TaskOutcome(
            task_type=self._classify_task(self.state.task_description),
            success=success,
            duration_minutes=duration,
            confidence_before=self.state.confidence_at_start,
            confidence_after=self.state.current_confidence,
            errors_encountered=self.state.errors_encountered,
            help_seeking_events=self.state.help_seeking_events,
            notes=learnings
        )
        self.capability_tracker.record_task(outcome)
        
        # 创建反思记录
        reflection = self.reflection_protocol.post_task(
            task_id=self.state.task_id,
            task_description=self.state.task_description,
            success=success,
            confidence_before=self.state.confidence_at_start,
            confidence_after=self.state.current_confidence,
            duration_minutes=duration,
            what_happened=what_happened,
            deviations=deviations,
            learnings=learnings
        )
        
        self.state.phase = "completed"
        self.state.post_task_reflection = reflection.id
        self._save_state()
        
        # 生成总结报告
        return self._generate_end_report(success, duration, reflection.id)
    
    def get_status(self) -> str:
        """获取当前状态报告"""
        if self.state is None:
            return "No active session"
        
        lines = ["# Her Session Status", ""]
        lines.append(f"Session: {self.state.session_id}")
        lines.append(f"Phase: {self.state.phase}")
        lines.append(f"Task: {self.state.task_description or 'None'}")
        lines.append("")
        lines.append(f"Confidence: {self.state.current_confidence:.0%} (started at {self.state.confidence_at_start:.0%})")
        lines.append(f"Errors: {self.state.errors_encountered}")
        lines.append(f"Help sought: {self.state.help_seeking_events} times")
        lines.append("")
        lines.append("## Tools Used")
        for tool, count in self.state.tools_used.items():
            lines.append(f"- {tool}: {count}")
        
        # 添加环境异常
        anomalies = self.environment_monitor.detect_anomalies()
        if anomalies:
            lines.append("")
            lines.append("## ⚠️ Anomalies Detected")
            for a in anomalies:
                lines.append(f"- [{a['severity'].upper()}] {a['message']}")
        
        return "\n".join(lines)
    
    def _save_state(self):
        """保存会话状态"""
        if self.state and self.session_file:
            self.session_file.write_text(json.dumps(self.state.__dict__, indent=2, default=str))
    
    def _generate_start_report(self) -> str:
        """生成会话启动报告"""
        lines = ["🌸 Her is starting...", ""]
        lines.append(f"Session ID: {self.state.session_id}")
        lines.append("")
        lines.append("## Self-Model Loaded")
        lines.append(self.capability_tracker.get_capability_report())
        lines.append("")
        lines.append("## Meta-Cognitive Protocols Active")
        lines.append("- ✅ Pre-task reflection")
        lines.append("- ✅ Mid-task monitoring")
        lines.append("- ✅ Post-task reflection")
        lines.append("- ✅ Help-seeking decisions")
        lines.append("")
        lines.append("I'm ready. What would you like me to do?")
        
        return "\n".join(lines)
    
    def _generate_end_report(self, success: bool, duration: float, reflection_id: str) -> str:
        """生成任务结束报告"""
        lines = [f"{'✅' if success else '❌'} Task Complete", ""]
        lines.append(f"Duration: {duration:.1f} minutes")
        lines.append(f"Reflection recorded: {reflection_id}")
        lines.append("")
        lines.append("## Session Summary")
        lines.append(self.get_status())
        
        return "\n".join(lines)
    
    def _assess_initial_confidence(self, task_description: str) -> float:
        """评估初始信心度"""
        # 基于任务类型和历史表现
        task_type = self._classify_task(task_description)
        caps = self.capability_tracker.identity.get("capabilities", {})
        
        if task_type in caps:
            return caps[task_type].get("confidence", 0.5)
        
        # 默认中等信心
        return 0.6
    
    def _classify_task(self, description: str) -> str:
        """简单任务分类"""
        desc = description.lower()
        if any(w in desc for w in ["test", "spec"]):
            return "testing"
        if any(w in desc for w in ["debug", "fix", "error"]):
            return "debugging"
        if any(w in desc for w in ["refactor", "restructure"]):
            return "architecture_design"
        if any(w in desc for w in ["implement", "create", "add"]):
            return "code_writing"
        return "code_reading"
    
    def _estimate_time(self, description: str) -> float:
        """预估任务时间（分钟）"""
        # 简单启发式
        desc = description.lower()
        if any(w in desc for w in ["simple", "quick", "typo"]):
            return 5
        if any(w in desc for w in ["implement", "feature"]):
            return 30
        if any(w in desc for w in ["refactor", "architecture"]):
            return 60
        return 15  # 默认
    
    def _is_unknown_technology(self, description: str) -> bool:
        """检测是否涉及未知技术"""
        # 检查描述中是否包含 Her 不熟悉的技术
        unknown_techs = ["rust", "go", "kotlin", "swift"]
        desc = description.lower()
        return any(t in desc for t in unknown_techs)
    
    def _format_help_suggestion(self, decision: HelpType, reason: str, extra: Dict) -> str:
        """格式化求助建议"""
        lines = ["🤔 Her suggests seeking help:", ""]
        lines.append(f"**Reason**: {reason}")
        lines.append("")
        
        if decision == HelpType.ASK_USER:
            lines.append("**Action**: Ask user for guidance")
        elif decision == HelpType.SPAWN_SUBAGENT:
            lines.append("**Action**: Spawn a specialized subagent")
        elif decision == HelpType.WEB_SEARCH:
            lines.append("**Action**: Search the web for information")
        elif decision == HelpType.ESCALATE:
            lines.append("**Action**: Escalate or consider abandoning")
        
        if extra:
            lines.append("")
            lines.append("**Additional context**:")
            for k, v in extra.items():
                lines.append(f"- {k}: {v}")
        
        return "\n".join(lines)


# 全局会话实例（单例模式）
_current_session: Optional[HerSession] = None


def get_session(project_root: Optional[str] = None) -> HerSession:
    """获取或创建会话"""
    global _current_session
    if _current_session is None:
        _current_session = HerSession(project_root)
    return _current_session


if __name__ == "__main__":
    # 测试完整流程
    print("=== Test: Her Session Lifecycle ===\n")
    
    her = get_session("/Users/chaihao/LLM/Her")
    
    # 1. 启动会话
    print(her.start_session())
    print("\n" + "="*50 + "\n")
    
    # 2. 开始任务
    print(her.start_task("test-auth", "Implement JWT authentication"))
    print("\n" + "="*50 + "\n")
    
    # 3. 模拟工作
    her.record_tool_use("ReadFile")
    her.record_tool_use("WriteFile")
    her.update_confidence(0.8)
    
    # 4. 检查是否需要帮助
    help_suggestion = her.check_should_seek_help()
    if help_suggestion:
        print(help_suggestion)
    else:
        print("✅ Her is confident, proceeding...")
    
    print("\n" + "="*50 + "\n")
    
    # 5. 状态报告
    print(her.get_status())
    print("\n" + "="*50 + "\n")
    
    # 6. 结束任务
    print(her.end_task(
        success=True,
        what_happened="Implemented JWT auth with refresh tokens",
        learnings="PyJWT is easier to use than python-jose",
        deviations=["Added refresh tokens which weren't in original plan"]
    ))
