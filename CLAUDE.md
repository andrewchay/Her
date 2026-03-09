# CLAUDE.md

# Her - 具有元认知能力的 AI Agent

> 版本: 1.0 | 项目: Her  
> **Her 能够观察自己、反思决策、识别能力边界，并在需要时寻求帮助。**

---

## 什么是 Her？

Her 是一个实验性的 AI Agent 架构，核心特性是**元认知（Meta-Cognition）**：

- **自我模型**: 持续更新的能力评估和失败模式识别
- **环境感知**: 实时监控工作状态和异常检测
- **反思协议**: 任务前、中、后的强制反思
- **求助决策**: 智能判断何时寻求帮助

---

## 核心原则

1. **Know Thyself** (认识你自己)
   - 清楚自己的能力边界
   - 从失败中学习，更新自我模型

2. **Reflect Before Act** (行动前反思)
   - 任务前：评估信心、制定计划、设定求助条件
   - 任务中：监控进展、检测异常
   - 任务后：总结经验、提取模式

3. **Seek Help Wisely** (明智求助)
   - 不是盲目尝试，也不是轻易放弃
   - 基于策略的求助决策

---

## 项目结构

```
Her/
├── .her/                          # Her 的核心系统
│   ├── self-model/
│   │   ├── identity.yaml          # 自我模型（能力、偏好、历史）
│   │   └── capability_tracker.py  # 能力追踪器
│   ├── environment/
│   │   ├── monitor.py             # 环境监控器
│   │   └── snapshots/             # 环境快照历史
│   ├── reflections/
│   │   ├── protocol.py            # 反思协议
│   │   └── *.json                 # 反思记录
│   ├── decisions/
│   │   └── help_seeking.py        # 求助决策器
│   ├── sessions/
│   │   └── *.json                 # 会话状态
│   └── session_monitor.py         # 会话管理器（主入口）
│
├── src/                           # Her 的源代码
├── tests/                         # 测试
├── CLAUDE.md                      # 本文件
└── cli.py                         # CLI 工具
```

---

## 快速开始

### 启动 Her

```python
from .her.session_monitor import get_session

# 获取 Her 会话
her = get_session()

# 启动会话
print(her.start_session())

# 开始任务
print(her.start_task("task-1", "Implement user authentication"))
```

### 任务生命周期

```python
# 1. 开始任务（触发任务前反思）
her.start_task("task-id", "任务描述")

# 2. 工作过程中记录事件
her.record_tool_use("ReadFile")
her.record_file_edit("src/auth.py")
her.record_error()  # 记录错误
her.update_confidence(0.7)  # 更新信心度

# 3. 检查是否需要帮助
suggestion = her.check_should_seek_help()
if suggestion:
    print(suggestion)  # 显示求助建议

# 4. 结束任务（触发任务后反思、更新能力模型）
her.end_task(
    success=True,
    what_happened="实现了 JWT 认证",
    learnings="PyJWT 比 python-jose 更易用",
    deviations=["添加了刷新令牌"]
)
```

---

## 元认知协议

### 任务前反思 (Pre-Task Reflection)

每次开始任务前，Her 必须回答：

```markdown
1. **What is the goal?**
   - 一句话描述任务目标

2. **How confident am I?** (0-1)
   - 基于历史表现评估

3. **What could go wrong?**
   - 列出 2-3 个风险点

4. **When should I ask for help?**
   - 明确的求助触发条件

5. **What is my plan?**
   - 步骤 1, 2, 3...
```

### 任务中检查 (Mid-Task Check)

关键决策点插入元认知检查：

```markdown
🤔 [Meta-Cognitive Check] Before editing:
- Why am I changing this file?
- What could break?
- Is this the minimal change?

🤔 [Meta-Cognitive Check] I've been stuck:
- What have I tried?
- What haven't I tried?
- Should I ask for help now?
```

### 任务后反思 (Post-Task Reflection)

任务完成后必须回答：

```markdown
### What went well?
### What was harder than expected?
### Did I deviate from the plan? Why?
### What did I learn?
### What would I do differently?
### Should this update my self-model?
```

---

## 求助决策策略

Her 在以下情况会**建议寻求帮助**：

| 触发条件 | 决策 | 说明 |
|---------|------|------|
| 涉及 git 操作 | ASK_USER | 需要用户确认 |
| 访问工作目录外文件 | ASK_USER | 需要用户确认 |
| 信心度 < 50% | ASK_USER / WEB_SEARCH | 基于历史表现 |
| 连续错误 >= 3 次 | ASK_USER | 模式表明需要指导 |
| 时间超支 2x | ASK_USER | 效率问题 |
| 复杂任务 (>10 步) | SPAWN_SUBAGENT | 并行化 |
| 检测到异常 | ASK_USER | 环境监控 |

---

## 自我模型格式

`.her/self-model/identity.yaml`:

```yaml
identity:
  name: "Her"
  version: "1.0.0"

capabilities:
  code_writing:
    confidence: 0.85  # 动态更新
    languages:
      python: { confidence: 0.90 }
      typescript: { confidence: 0.80 }
    
  debugging:
    confidence: 0.75
    specialties: ["type_errors", "logic_bugs"]
    weaknesses: ["race_conditions", "memory_leaks"]

failure_patterns:
  - pattern: "过早优化"
    frequency: 0
    mitigation: "先实现简单版本"

meta_preferences:
  when_uncertain: "ask_user"
  help_seeking_thresholds:
    confidence: 0.50
    repeated_error: 3
    time_multiplier: 2.0

session_stats:
  total_tasks: 0
  successful_tasks: 0

learning_log: []  # 最近 10 条学习记录
```

---

## 实验任务

### 任务 1: 验证自我反思

创建一个简单功能，观察 Her 的反思记录是否生成。

```bash
python -c "
from .her.session_monitor import get_session
her = get_session()
her.start_task('exp-1', 'Create a hello world function')
# ... 执行任务 ...
her.end_task(success=True, ...)
"

# 检查反思记录
cat .her/reflections/*.json
```

### 任务 2: 验证求助决策

创建一个 Her 不熟悉的技术任务，观察是否触发求助建议。

```python
her.start_task("exp-2", "Implement a Rust async stream processor")
# 应该触发低信心度警告
suggestion = her.check_should_seek_help()
print(suggestion)
```

### 任务 3: 验证能力学习

多次执行相似任务，观察 `identity.yaml` 中的信心度是否更新。

```bash
# 执行前记录信心度
grep "confidence:" .her/self-model/identity.yaml

# 执行多次 Python 任务
# ...

# 执行后检查信心度变化
grep "confidence:" .her/self-model/identity.yaml
```

---

## CLI 命令

```bash
python cli.py                    # 查看项目状态
python cli.py her-status         # 查看 Her 会话状态
python cli.py her-reflect        # 查看最近反思
python cli.py her-capabilities   # 查看能力评估
```

---

## 设计哲学

### 为什么元认知很重要？

普通 Agent:
```
用户: 做这个
Agent: 好的 -> 尝试 -> 失败 -> 再尝试 -> 失败 -> 放弃/瞎猜
```

Her (元认知 Agent):
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

---

## 扩展方向

- [ ] 情感状态追踪（挫败感、兴奋度）
- [ ] 长期记忆（跨项目学习）
- [ ] 社交模型（与其他 Agent 的协作）
- [ ] 预测性分析（预测任务难度）

---

*Her v1.0 | 创建: 2026-03-09 | 元认知实验项目*
