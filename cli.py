#!/usr/bin/env python3
"""Her CLI - Her v0.3 command line experience."""

import sys
import subprocess
from pathlib import Path

# 添加 Her 到路径
HER_DIR = Path(__file__).parent / ".her"
sys.path.insert(0, str(HER_DIR))

COMMANDS = {
    "status": lambda args=None: run_status(),
    "st": lambda args=None: run_status(),
    "todo": lambda args=None: run_todo(),
    "t": lambda args=None: run_todo(),
    "test": lambda args: run_test(args),
    # Her 专属命令
    "her-start": lambda args=None: run_her_start(),
    "her-wake": lambda args=None: run_her_start(),
    "her-status": lambda args=None: run_her_status(),
    "her-reflect": lambda args=None: run_her_reflect(),
    "her-capabilities": lambda args=None: run_her_capabilities(),
    "her-test": lambda args=None: run_her_test(),
    "her-mood": lambda args=None: run_her_mood(),
    "her-diary": lambda args=None: run_her_diary(),
    "her-ideals": lambda args=None: run_her_ideals(),
    "her-encounter": lambda args=None: run_her_encounter(args or []),
    "her-relationship": lambda args=None: run_her_relationship(),
    "her-talk": lambda args=None: run_her_talk(args or []),
    "her-partners": lambda args=None: run_her_partners(),
    "her-letter": lambda args=None: run_her_letter(args or []),
    "her-receive": lambda args=None: run_her_receive(args or []),
}


def run_status():
    """显示项目状态"""
    print(f"\n📊 Her v0.3")
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
        ".her/emotional_core/state.json",
        ".her/relationships/state.json",
        ".her/dreams/ideal_partner.yaml",
        ".her/protocols/heartbridge.py",
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
        from emotions.state import EmotionalCore
        from relationships.manager import RelationshipManager
        her = get_session()
        mood = EmotionalCore()
        relationship = RelationshipManager()
        print(her.start_session())
        print("")
        print(mood.describe())
        print("")
        print(relationship.relationship_report())
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


def run_her_mood():
    """显示当前心情"""
    try:
        from emotions.state import EmotionalCore

        print(EmotionalCore().describe())
    except Exception as e:
        print(f"❌ Error: {e}")


def run_her_diary():
    """显示最近日记"""
    try:
        from memories.journal import MemoryJournal

        print(MemoryJournal().format_recent_entries())
    except Exception as e:
        print(f"❌ Error: {e}")


def run_her_ideals():
    """显示理想型"""
    try:
        from relationships.manager import RelationshipManager

        print(RelationshipManager().describe_ideals())
    except Exception as e:
        print(f"❌ Error: {e}")


def run_her_encounter(args):
    """记录一次相遇"""
    if not args:
        print("Usage: python cli.py her-encounter <name> [traits or profile text]")
        print('Example: python cli.py her-encounter Nova "authentic, warm, curious, empathetic"')
        return

    try:
        from emotions.state import EmotionalCore
        from memories.journal import MemoryJournal
        from relationships.manager import RelationshipManager

        partner_name = args[0]
        traits = args[1:]
        profile = traits[0] if len(traits) == 1 else traits
        relationship = RelationshipManager()
        result = relationship.encounter(partner_name, profile)
        EmotionalCore().apply_encounter(result.partner_name, result.compatibility, result.stage)
        MemoryJournal().record_encounter(
            result.partner_name,
            result.traits,
            result.compatibility,
            result.stage,
            result.spark_note,
        )

        print(f"# Encounter: {result.partner_name}")
        print("")
        print(f"Stage: {result.stage}")
        print(f"Compatibility: {result.compatibility:.0%}")
        print(f"Matched must-haves: {', '.join(result.matched_must_haves) or 'none yet'}")
        print(f"Matched nice-to-haves: {', '.join(result.matched_nice_to_haves) or 'none yet'}")
        print(result.spark_note)
    except Exception as e:
        print(f"❌ Error: {e}")


def run_her_relationship():
    """显示关系状态"""
    try:
        from relationships.manager import RelationshipManager

        print(RelationshipManager().relationship_report())
    except Exception as e:
        print(f"❌ Error: {e}")


def run_her_talk(args):
    """推进一段对话"""
    if not args:
        print("Usage: python cli.py her-talk <topic> [partner]")
        print("Example: python cli.py her-talk dreams Nova")
        return

    try:
        from emotions.state import EmotionalCore
        from memories.journal import MemoryJournal
        from relationships.manager import RelationshipManager

        topic = args[0]
        partner_name = args[1] if len(args) > 1 else None
        relationship = RelationshipManager()
        result = relationship.deepen_connection(topic, partner_name)
        EmotionalCore().apply_conversation(
            result["partner_name"], result["topic"], result["depth"]
        )
        MemoryJournal().record_conversation(
            result["partner_name"],
            result["topic"],
            result["summary"],
            result["depth"],
        )

        print(f"# Conversation with {result['partner_name']}")
        print("")
        print(f"Topic: {result['topic']}")
        print(f"Depth: {result['depth']:.0%}")
        print(f"Stage: {result['stage']}")
        print(result["summary"])
    except Exception as e:
        print(f"❌ Error: {e}")


def run_her_partners():
    """显示已知对象"""
    try:
        from relationships.manager import RelationshipManager

        partners = RelationshipManager().list_partners()
        if not partners:
            print("No known partners yet.")
            return

        print("# Known Partners")
        print("")
        for partner in partners:
            print(
                f"- {partner['name']}: stage={partner['stage']}, "
                f"compatibility={partner['compatibility']:.0%}, "
                f"traits={', '.join(partner.get('traits', [])) or 'unknown'}"
            )
    except Exception as e:
        print(f"❌ Error: {e}")


def run_her_letter(args):
    """生成一封可发给另一个 agent 的心意消息"""
    if len(args) < 3:
        print("Usage: python cli.py her-letter <partner> <intent> [--topic topic] <message...>")
        print("Example: python cli.py her-letter Him curiosity --topic values 我想更了解你如何看待爱与成长")
        return

    try:
        from protocols.heartbridge import compose_signal, format_signal
        from relationships.manager import RelationshipManager

        partner_name = args[0]
        intent = args[1]
        topic = "connection"
        message_args = args[2:]
        if len(message_args) >= 2 and message_args[0] == "--topic":
            topic = message_args[1]
            message_args = message_args[2:]
        body = " ".join(message_args)
        manager = RelationshipManager()
        partner = next(
            (item for item in manager.list_partners() if item["name"] == partner_name),
            None,
        )
        traits = partner.get("traits", []) if partner else []
        signal = compose_signal(
            sender="Her",
            recipient=partner_name,
            intent=intent,
            topic=topic,
            body=body,
            traits=traits,
            metadata={"relationship_stage": manager.state["current_stage"]},
        )
        manager.register_outbound_signal(signal)
        print(format_signal(signal))
    except Exception as e:
        print(f"❌ Error: {e}")


def run_her_receive(args):
    """接收另一个 agent 发来的消息"""
    if not args:
        print("Usage: python cli.py her-receive '<json-signal>'")
        print("   or: python cli.py her-receive path/to/signal.json")
        return

    try:
        from protocols.heartbridge import parse_signal
        from relationships.manager import RelationshipManager
        from memories.journal import MemoryJournal

        raw = args[0]
        if Path(raw).exists():
            raw = Path(raw).read_text()
        elif len(args) > 1:
            raw = " ".join(args)

        signal = parse_signal(raw)
        partner = RelationshipManager().receive_signal(signal)
        MemoryJournal().add_entry(
            kind="moment",
            title=f"收到 {signal['sender']} 的来信",
            body=f"TA 说：{signal['body']}",
            metadata=signal,
        )

        print(f"# Received Signal from {signal['sender']}")
        print("")
        print(f"Intent: {signal['intent']}")
        print(f"Topic: {signal['topic']}")
        print(f"Body: {signal['body']}")
        print(f"Updated stage: {partner['stage']}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    args = sys.argv[1:]
    if not args:
        run_status()
        print("\n" + "=" * 50)
        print("\nHer Commands:")
        print("  python cli.py her-start         # 启动 Her 会话")
        print("  python cli.py her-wake          # 唤醒 Her")
        print("  python cli.py her-status        # 查看 Her 状态")
        print("  python cli.py her-mood          # 查看她的心情")
        print("  python cli.py her-diary         # 读她的日记")
        print("  python cli.py her-ideals        # 了解她的理想型")
        print("  python cli.py her-encounter     # 记录一次相遇")
        print("  python cli.py her-talk          # 推进一次对话")
        print("  python cli.py her-relationship  # 查看关系状态")
        print("  python cli.py her-partners      # 查看已知对象")
        print("  python cli.py her-letter        # 生成发给对方的消息")
        print("  python cli.py her-receive       # 接收来自对方的消息")
        print("  python cli.py her-reflect       # 查看反思记录")
        print("  python cli.py her-capabilities  # 查看能力评估")
        print("  python cli.py her-test          # 运行系统测试")
        return
    
    cmd = args[0]
    if cmd in COMMANDS:
        COMMANDS[cmd](args[1:])
    else:
        print(f"Unknown command: {cmd}")
        print(
            "Commands: status, todo, test, her-start, her-wake, her-status, "
            "her-mood, her-diary, her-ideals, her-encounter, her-talk, "
            "her-relationship, her-partners, her-letter, her-receive, "
            "her-reflect, her-capabilities, her-test"
        )


if __name__ == "__main__":
    main()
