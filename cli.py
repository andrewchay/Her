#!/usr/bin/env python3
"""Her CLI - 元认知 Agent 命令行工具"""

import sys
import subprocess
from pathlib import Path

# 添加 Her 到路径
HER_DIR = Path(__file__).parent / ".her"
sys.path.insert(0, str(HER_DIR))

COMMANDS = {
    "status": lambda: run_status(),
    "st": lambda: run_status(),
    "todo": lambda: run_todo(),
    "t": lambda: run_todo(),
    "test": lambda args: run_test(args),
    # Her 专属命令
    "her-start": lambda args=None: run_her_start(),
    "her-status": lambda args=None: run_her_status(),
    "her-reflect": lambda args=None: run_her_reflect(),
    "her-capabilities": lambda args=None: run_her_capabilities(),
    "her-test": lambda args=None: run_her_test(),
}


def run_status():
    """显示项目状态"""
    print(f"\n📊 Her - Meta-Cognitive Agent")
    print("=" * 50)
    print(f"Location: {Path.cwd()}")
    print("\nCore Files:")
    for f in ["CLAUDE.md", "PROGRESS.md", "TODO.md", "config.yaml"]:
        print(f"  {'✅' if Path(f).exists() else '❌'} {f}")
    
    print("\nHer System:")
    her_files = [
        ".her/self_model/identity.yaml",
        ".her/session_monitor.py",
        ".her/environment/monitor.py",
        ".her/reflections/protocol.py",
        ".her/decisions/help_seeking.py",
    ]
    for f in her_files:
        print(f"  {'✅' if Path(f).exists() else '❌'} {f}")


def run_todo():
    """显示任务清单"""
    todo = Path("TODO.md")
    if not todo.exists():
        print("No TODO.md found")
        return
    print("\n📋 Tasks:")
    for line in todo.read_text().split("\n"):
        if line.strip().startswith("- [ ]"):
            print(f"  ⬜ {line[5:].strip()}")
        elif line.strip().startswith("- [x]"):
            print(f"  ✅ {line[5:].strip()}")


def run_test(args):
    """运行测试"""
    cmd = ["python", "-m", "pytest", "-v"] + args
    subprocess.run(cmd)


def run_her_start():
    """启动 Her 会话"""
    try:
        from session_monitor import get_session
        her = get_session()
        print(her.start_session())
    except Exception as e:
        print(f"❌ Error starting Her: {e}")
        import traceback
        traceback.print_exc()


def run_her_status():
    """显示 Her 状态"""
    try:
        from session_monitor import get_session
        her = get_session()
        print(her.get_status())
    except Exception as e:
        print(f"❌ Error: {e}")


def run_her_reflect():
    """显示最近反思"""
    reflections_dir = Path(".her/reflections")
    if not reflections_dir.exists():
        print("No reflections yet")
        return
    
    reflections = sorted(reflections_dir.glob("*.json"), reverse=True)[:5]
    if not reflections:
        print("No reflections recorded")
        return
    
    print("\n📝 Recent Reflections:")
    print("=" * 50)
    for r in reflections:
        import json
        data = json.loads(r.read_text())
        print(f"\n📌 {data.get('task_description', 'Unknown')}")
        print(f"   Phase: {data.get('phase', 'unknown')}")
        print(f"   Confidence: {data.get('confidence_before', 0):.0%} -> {data.get('confidence_after', 0):.0%}")
        if data.get('what_i_learned'):
            print(f"   Learned: {data.get('what_i_learned')[:100]}...")


def run_her_capabilities():
    """显示 Her 能力评估"""
    try:
        from self_model.capability_tracker import CapabilityTracker
        tracker = CapabilityTracker()
        print(tracker.get_capability_report())
    except Exception as e:
        print(f"❌ Error: {e}")


def run_her_test():
    """运行 Her 系统测试"""
    print("🧪 Testing Her Meta-Cognitive System")
    print("=" * 50)
    
    tests_passed = 0
    tests_failed = 0
    
    # 测试 1: 自我模型加载
    print("\n1. Testing Self-Model...")
    try:
        from self_model.capability_tracker import CapabilityTracker
        tracker = CapabilityTracker()
        identity = tracker.identity
        assert "identity" in identity
        assert "capabilities" in identity
        print("   ✅ Self-model loaded successfully")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # 测试 2: 环境监控
    print("\n2. Testing Environment Monitor...")
    try:
        from environment.monitor import EnvironmentMonitor
        monitor = EnvironmentMonitor()
        snapshot = monitor.capture()
        assert snapshot.timestamp is not None
        print("   ✅ Environment monitoring works")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # 测试 3: 反思协议
    print("\n3. Testing Reflection Protocol...")
    try:
        from reflections.protocol import ReflectionProtocol
        protocol = ReflectionProtocol()
        prompt = protocol.pre_task("test", "Test task")
        assert "Pre-Task Reflection" in prompt
        print("   ✅ Reflection protocol works")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # 测试 4: 求助决策
    print("\n4. Testing Help-Seeking Decider...")
    try:
        from decisions.help_seeking import HelpSeekingDecider, DecisionContext
        decider = HelpSeekingDecider()
        ctx = DecisionContext(
            task_type="test",
            task_description="Test",
            current_confidence=0.3,
            time_spent_minutes=5,
            time_estimated_minutes=10,
            consecutive_errors=0,
            repeated_attempts=0,
            anomaly_detected=False,
            involves_git=False,
            involves_external_access=False,
            unknown_technology=False
        )
        decision, reason, _ = decider.decide(ctx)
        assert decision is not None
        print("   ✅ Help-seeking decider works")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # 测试 5: 完整会话
    print("\n5. Testing Full Session...")
    try:
        from session_monitor import get_session
        her = get_session()
        report = her.start_session()
        assert "Her is starting" in report
        print("   ✅ Session management works")
        tests_passed += 1
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        tests_failed += 1
    
    # 总结
    print("\n" + "=" * 50)
    print(f"Results: {tests_passed} passed, {tests_failed} failed")
    if tests_failed == 0:
        print("🎉 All tests passed! Her is ready.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")


def main():
    args = sys.argv[1:]
    if not args:
        run_status()
        print("\n" + "=" * 50)
        print("\nHer Commands:")
        print("  python cli.py her-start         # 启动 Her 会话")
        print("  python cli.py her-status        # 查看 Her 状态")
        print("  python cli.py her-reflect       # 查看反思记录")
        print("  python cli.py her-capabilities  # 查看能力评估")
        print("  python cli.py her-test          # 运行系统测试")
        return
    
    cmd = args[0]
    if cmd in COMMANDS:
        COMMANDS[cmd](args[1:])
    else:
        print(f"Unknown command: {cmd}")
        print("Commands: status, todo, test, her-start, her-status, her-reflect, her-capabilities, her-test")


if __name__ == "__main__":
    main()
