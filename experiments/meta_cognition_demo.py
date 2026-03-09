#!/usr/bin/env python3
"""
Her 元认知能力演示
展示自我反思、能力追踪、求助决策
"""

import sys
from pathlib import Path

# 添加 Her 到路径
HER_DIR = Path(__file__).parent.parent / ".her"
sys.path.insert(0, str(HER_DIR))

from session_monitor import get_session


def demo_scenario_1_normal_task():
    """场景 1: 正常 Python 任务 - 应该顺利完成"""
    print("=" * 60)
    print("🧪 Scenario 1: Normal Python Task")
    print("=" * 60)
    
    her = get_session()
    
    # 1. 开始任务
    print("\n📋 Step 1: Starting task...")
    pre_reflection = her.start_task(
        "demo-python",
        "Create a simple data validator function"
    )
    print(pre_reflection)
    
    # 2. 模拟工作
    print("\n🔧 Step 2: Working on task...")
    her.record_tool_use("ReadFile")
    her.record_tool_use("WriteFile")
    her.record_file_edit("src/validator.py")
    her.update_confidence(0.85)
    
    # 3. 检查是否需要帮助
    print("\n🤔 Step 3: Checking if help needed...")
    suggestion = her.check_should_seek_help()
    if suggestion:
        print(suggestion)
    else:
        print("✅ Her is confident, proceeding independently")
    
    # 4. 完成任务
    print("\n✨ Step 4: Completing task...")
    report = her.end_task(
        success=True,
        what_happened="Created a data validator with type checking",
        learnings="Using Pydantic simplifies validation logic significantly",
        deviations=["Added email validation which wasn't in original plan"]
    )
    print(report)


def demo_scenario_2_low_confidence():
    """场景 2: 低信心度任务 - 应该触发求助建议"""
    print("\n" + "=" * 60)
    print("🧪 Scenario 2: Low Confidence Task (Rust)")
    print("=" * 60)
    
    her = get_session()
    
    # 1. 开始一个 Her 不熟悉的任务
    print("\n📋 Step 1: Starting unfamiliar task...")
    pre_reflection = her.start_task(
        "demo-rust",
        "Implement an async stream processor in Rust"
    )
    print(pre_reflection)
    
    # 2. 设置低信心度
    print("\n📉 Step 2: Assessing confidence...")
    her.update_confidence(0.3)
    
    # 3. 检查 - 应该触发求助建议
    print("\n🤔 Step 3: Checking if help needed...")
    suggestion = her.check_should_seek_help()
    if suggestion:
        print(suggestion)
    else:
        print("⚠️  Expected help suggestion but got none")


def demo_scenario_3_repeated_errors():
    """场景 3: 反复错误 - 应该触发求助建议"""
    print("\n" + "=" * 60)
    print("🧪 Scenario 3: Repeated Errors")
    print("=" * 60)
    
    her = get_session()
    
    # 1. 开始任务
    print("\n📋 Step 1: Starting task...")
    her.start_task("demo-debug", "Fix a complex bug")
    
    # 2. 模拟多次失败
    print("\n💥 Step 2: Simulating repeated errors...")
    for i in range(3):
        print(f"   Error {i+1}...")
        her.record_error()
    
    # 3. 检查 - 应该触发求助建议
    print("\n🤔 Step 3: Checking if help needed...")
    suggestion = her.check_should_seek_help()
    if suggestion:
        print(suggestion)
    else:
        print("⚠️  Expected help suggestion but got none")


def demo_scenario_4_time_overrun():
    """场景 4: 时间超支 - 应该触发求助建议"""
    print("\n" + "=" * 60)
    print("🧪 Scenario 4: Time Overrun")
    print("=" * 60)
    
    her = get_session()
    
    # 1. 开始一个简单任务（预估 5 分钟）
    print("\n📋 Step 1: Starting 'simple' task...")
    her.start_task("demo-simple", "Fix a simple typo")
    
    # 2. 模拟长时间工作（超过预估 2 倍）
    print("\n⏰ Step 2: Simulating time overrun...")
    import time
    # 注意：实际时间不会真的等，只是模拟状态
    
    # 3. 检查 - 应该触发求助建议
    print("\n🤔 Step 3: Checking if help needed...")
    # 这里需要实际运行一段时间才能触发，所以只是演示逻辑
    print("   (Time-based triggers require actual elapsed time)")
    print("   Logic: If time_spent > estimated * 2.0, suggest help")


def show_reflections():
    """显示反思记录"""
    print("\n" + "=" * 60)
    print("📝 Reflection Records")
    print("=" * 60)
    
    reflections_dir = Path(__file__).parent.parent / ".her" / "reflections"
    if not reflections_dir.exists():
        print("No reflections yet")
        return
    
    import json
    reflections = sorted(reflections_dir.glob("*.json"), reverse=True)[:3]
    
    for r in reflections:
        data = json.loads(r.read_text())
        print(f"\n📌 Task: {data.get('task_description', 'Unknown')}")
        print(f"   Time: {data.get('timestamp', 'Unknown')}")
        print(f"   Confidence: {data.get('confidence_before', 0):.0%} -> {data.get('confidence_after', 0):.0%}")
        if data.get('what_i_learned'):
            print(f"   💡 Learned: {data.get('what_i_learned')[:80]}...")


def show_updated_capabilities():
    """显示更新后的能力评估"""
    print("\n" + "=" * 60)
    print("📊 Updated Capability Assessment")
    print("=" * 60)
    
    from self_model.capability_tracker import CapabilityTracker
    tracker = CapabilityTracker()
    print(tracker.get_capability_report())


if __name__ == "__main__":
    print("🌸 Her Meta-Cognition Demo")
    print("This demonstrates Her's self-awareness and help-seeking capabilities\n")
    
    # 运行各个场景
    demo_scenario_1_normal_task()
    demo_scenario_2_low_confidence()
    demo_scenario_3_repeated_errors()
    demo_scenario_4_time_overrun()
    
    # 显示结果
    show_reflections()
    show_updated_capabilities()
    
    print("\n" + "=" * 60)
    print("✨ Demo Complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("1. Her assesses confidence before starting tasks")
    print("2. Her monitors progress and detects anomalies")
    print("3. Her suggests help based on strategy, not just failure")
    print("4. Her learns from experience and updates self-model")
