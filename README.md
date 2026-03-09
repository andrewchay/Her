# Her - Meta-Cognitive AI Agent

> "Know thyself" - 一个具有自我反思能力的 AI Agent 实验项目

![Her Demo](https://img.shields.io/badge/Her-v1.0.0-pink)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Status](https://img.shields.io/badge/Status-Experimental-orange)

## 什么是 Her？

Her 是一个实验性的 AI Agent 架构，核心特性是**元认知（Meta-Cognition）**——对自己的认知过程进行认知。

与普通 Agent 不同，Her 能够：

- 🧠 **自我模型**: 持续更新的能力评估和失败模式识别
- 👁️ **环境感知**: 实时监控工作状态和异常检测  
- 🤔 **反思协议**: 任务前、中、后的强制反思
- 🆘 **求助决策**: 智能判断何时寻求帮助

## 快速开始

```bash
# 1. 启动 Her
python3 cli.py her-start

# 2. 运行系统测试
python3 cli.py her-test

# 3. 运行元认知演示
python3 experiments/meta_cognition_demo.py

# 4. 查看状态
python3 cli.py her-status
```

## 核心特性演示

### 1. 任务前反思

```python
from .her.session_monitor import get_session

her = get_session()
print(her.start_task("task-1", "Implement user authentication"))

# 输出：
## Pre-Task Reflection (任务前反思)
# 1. What is the goal?
# 2. How confident am I? (0-1)
# 3. What could go wrong?
# 4. When should I ask for help?
# 5. What is my plan?
```

### 2. 智能求助决策

```python
# 场景：Her 遇到不熟悉的 Rust 任务
her.update_confidence(0.3)
suggestion = her.check_should_seek_help()

# 输出：
# 🤔 Her suggests seeking help:
# Reason: Unknown technology with low confidence (30%)
# Action: Search the web for information
```

### 3. 能力学习

```python
# 完成任务后，Her 自动更新能力评估
her.end_task(
    success=True,
    what_happened="Implemented JWT auth",
    learnings="PyJWT is easier than python-jose",
    deviations=["Added refresh tokens"]
)

# identity.yaml 自动更新：
# code_writing.confidence: 0.85 -> 0.90
```

## 系统架构

```
Her/
├── .her/                          # Her 的核心系统
│   ├── self_model/
│   │   ├── identity.yaml          # 自我模型（能力、偏好、历史）
│   │   └── capability_tracker.py  # 能力追踪器
│   ├── environment/
│   │   └── monitor.py             # 环境监控器
│   ├── reflections/
│   │   └── protocol.py            # 反思协议
│   ├── decisions/
│   │   └── help_seeking.py        # 求助决策器
│   └── session_monitor.py         # 会话管理器
│
├── src/                           # Her 的源代码
├── tests/                         # 测试
├── experiments/                   # 实验和演示
└── CLAUDE.md                      # 详细文档
```

## 元认知协议

### 任务前反思

每次开始任务前，Her 必须回答：

1. **What is the goal?** - 一句话描述目标
2. **How confident am I?** - 基于历史表现评估信心度
3. **What could go wrong?** - 列出 2-3 个风险点
4. **When should I ask for help?** - 明确的求助触发条件
5. **What is my plan?** - 执行步骤

### 任务中检查

关键决策点插入元认知检查：

```
🤔 [Meta-Cognitive Check] Before editing:
- Why am I changing this file?
- What could break?
- Is this the minimal change?
```

### 任务后反思

任务完成后必须回答：

- What went well?
- What was harder than expected?
- Did I deviate from the plan? Why?
- What did I learn?
- Should this update my self-model?

## 求助决策策略

Her 在以下情况会建议寻求帮助：

| 触发条件 | 决策 | 说明 |
|---------|------|------|
| 信心度 < 50% | ASK_USER / WEB_SEARCH | 基于历史表现 |
| 连续错误 >= 3 次 | ASK_USER | 模式表明需要指导 |
| 时间超支 2x | ASK_USER | 效率问题 |
| 涉及 git 操作 | ASK_USER | 需要用户确认 |
| 未知技术 | WEB_SEARCH | 先研究再尝试 |
| 复杂任务 (>10 步) | SPAWN_SUBAGENT | 并行化 |

## 实验结果

运行 `python3 experiments/meta_cognition_demo.py`：

```
🧪 Scenario 1: Normal Python Task
   ✅ Her is confident, proceeding independently

🧪 Scenario 2: Low Confidence Task (Rust)
   🤔 Her suggests: Search the web for information

🧪 Scenario 3: Repeated Errors
   🤔 Her suggests: Ask user for guidance

📊 Updated Capability Assessment
   code_writing: 85% -> 90% (learned from success)
```

## 设计哲学

### 为什么元认知很重要？

**普通 Agent:**
```
用户: 做这个
Agent: 好的 -> 尝试 -> 失败 -> 再尝试 -> 失败 -> 放弃/瞎猜
```

**Her (元认知 Agent):**
```
用户: 做这个
Her: 
  1. 评估信心度: 60%
  2. 制定计划: A -> B -> C
  3. 设定求助条件: 如果 30 分钟没解决 X，就求助
  4. 执行 A... 遇到问题
  5. 反思: 为什么 A 失败了？模式是什么？
  6. 更新自我模型: "我在 Y 方面需要加强"
  7. 求助/调整策略
```

### 关键洞察

1. **自我模型是动态的**: 不是硬编码的，而是从经验中学习
2. **反思是强制的**: 不是可选的，是协议的一部分
3. **求助是策略**: 不是失败，是明智的资源管理
4. **环境是感知的**: 不只是代码，还有工作模式

## CLI 命令

```bash
python3 cli.py her-start         # 启动 Her 会话
python3 cli.py her-status        # 查看 Her 状态
python3 cli.py her-reflect       # 查看反思记录
python3 cli.py her-capabilities  # 查看能力评估
python3 cli.py her-test          # 运行系统测试
```

## 未来方向

- [ ] 情感状态追踪（挫败感、兴奋度）
- [ ] 长期记忆（跨项目学习）
- [ ] 社交模型（与其他 Agent 的协作）
- [ ] 预测性分析（预测任务难度）
- [ ] 自然语言反思（用对话形式进行反思）

## 技术栈

- Python 3.8+
- YAML (自我模型存储)
- JSON (反思记录)
- 标准库 only (无外部依赖)

## 许可证

MIT License - 实验性项目，欢迎探索和扩展。

---

*Her v1.0 | 元认知实验项目 | 2026*
