#!/usr/bin/env python3
"""
Her 的环境监控器
持续感知工作环境和上下文状态
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from dataclasses import dataclass, asdict

HER_DIR = Path(__file__).parent.parent
SNAPSHOTS_DIR = HER_DIR / "environment" / "snapshots"
SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class EnvironmentSnapshot:
    """环境快照"""
    timestamp: str
    session_id: Optional[str]
    
    # 项目状态
    project_root: str
    git_branch: Optional[str]
    git_status: str  # clean | dirty
    uncommitted_files: List[str]
    
    # 任务状态
    current_task: Optional[str]
    task_phase: Optional[str]  # planning | implementing | checking | reflecting
    
    # 文件活动
    recently_modified_files: List[str]
    open_files: List[str]  # 最近读取的文件
    
    # 工具使用统计
    tools_used_this_session: Dict[str, int]
    
    # 异常指标
    consecutive_errors: int
    repeated_file_edits: List[str]  # 被多次编辑的同一文件
    
    def to_dict(self) -> dict:
        return asdict(self)


class EnvironmentMonitor:
    """监控工作环境的传感器"""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.session_id = None
        self._error_count = 0
        self._file_edit_count: Dict[str, int] = {}
        self._tools_used: Dict[str, int] = {}
    
    def capture(self) -> EnvironmentSnapshot:
        """捕获当前环境快照"""
        return EnvironmentSnapshot(
            timestamp=datetime.now().isoformat(),
            session_id=self.session_id,
            project_root=str(self.project_root),
            git_branch=self._get_git_branch(),
            git_status=self._get_git_status(),
            uncommitted_files=self._get_uncommitted_files(),
            current_task=self._get_current_task(),
            task_phase=None,  # 由会话管理器设置
            recently_modified_files=self._get_recently_modified(),
            open_files=[],  # 由工具钩子更新
            tools_used_this_session=self._tools_used.copy(),
            consecutive_errors=self._error_count,
            repeated_file_edits=self._get_repeated_edits()
        )
    
    def save_snapshot(self, snapshot: Optional[EnvironmentSnapshot] = None):
        """保存快照到文件"""
        if snapshot is None:
            snapshot = self.capture()
        
        filename = f"{snapshot.timestamp.replace(':', '-')}.json"
        filepath = SNAPSHOTS_DIR / filename
        filepath.write_text(json.dumps(snapshot.to_dict(), indent=2))
        
        # 清理旧快照（保留最近 20 个）
        self._cleanup_old_snapshots(20)
        
        return filepath
    
    def detect_anomalies(self) -> List[Dict]:
        """检测环境异常"""
        anomalies = []
        snapshot = self.capture()
        
        # 异常 1: 连续错误过多
        if snapshot.consecutive_errors >= 3:
            anomalies.append({
                "type": "consecutive_errors",
                "severity": "high",
                "message": f"连续 {snapshot.consecutive_errors} 次错误",
                "suggestion": "考虑寻求帮助或改变策略"
            })
        
        # 异常 2: 同一文件反复编辑
        for file, count in self._file_edit_count.items():
            if count >= 5:
                anomalies.append({
                    "type": "repeated_edits",
                    "severity": "medium",
                    "message": f"文件 {file} 被编辑 {count} 次",
                    "suggestion": "可能陷入局部优化，考虑整体重构"
                })
        
        # 异常 3: 长时间无进展（需要外部时间戳）
        # 由会话管理器检测
        
        # 异常 4: 大量未提交更改
        if len(snapshot.uncommitted_files) > 10:
            anomalies.append({
                "type": "too_many_changes",
                "severity": "low",
                "message": f"有 {len(snapshot.uncommitted_files)} 个未提交文件",
                "suggestion": "考虑提交当前进度"
            })
        
        return anomalies
    
    def record_tool_use(self, tool_name: str):
        """记录工具使用"""
        self._tools_used[tool_name] = self._tools_used.get(tool_name, 0) + 1
    
    def record_error(self):
        """记录错误发生"""
        self._error_count += 1
    
    def record_success(self):
        """记录成功，重置错误计数"""
        self._error_count = 0
    
    def record_file_edit(self, filepath: str):
        """记录文件编辑"""
        self._file_edit_count[filepath] = self._file_edit_count.get(filepath, 0) + 1
    
    def _get_git_branch(self) -> Optional[str]:
        """获取当前 git 分支"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None
    
    def _get_git_status(self) -> str:
        """获取 git 状态"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            return "dirty" if result.stdout.strip() else "clean"
        except:
            return "unknown"
    
    def _get_uncommitted_files(self) -> List[str]:
        """获取未提交文件列表"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            files = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    # 格式: XY filename 或 XY "filename with spaces"
                    files.append(line[3:].strip().strip('"'))
            return files
        except:
            return []
    
    def _get_current_task(self) -> Optional[str]:
        """获取当前任务"""
        # 检查 .current-task 文件或类似机制
        current_task_file = self.project_root / ".current-task"
        if current_task_file.exists():
            return current_task_file.read_text().strip()
        return None
    
    def _get_recently_modified(self, minutes: int = 30) -> List[str]:
        """获取最近修改的文件"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", f"--since={minutes}.minutes"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            return [f for f in result.stdout.strip().split("\n") if f]
        except:
            return []
    
    def _get_repeated_edits(self) -> List[str]:
        """获取被多次编辑的文件"""
        return [f for f, c in self._file_edit_count.items() if c >= 3]
    
    def _cleanup_old_snapshots(self, keep: int):
        """清理旧快照"""
        snapshots = sorted(SNAPSHOTS_DIR.glob("*.json"), reverse=True)
        for old in snapshots[keep:]:
            old.unlink()


if __name__ == "__main__":
    # 测试
    monitor = EnvironmentMonitor()
    snapshot = monitor.capture()
    print(json.dumps(snapshot.to_dict(), indent=2))
    
    print("\n--- Anomalies ---")
    for a in monitor.detect_anomalies():
        print(f"[{a['severity'].upper()}] {a['message']}")
