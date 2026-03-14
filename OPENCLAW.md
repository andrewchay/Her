# Her on OpenClaw

## 结论

如果你把 Her 和 Him 都部署在 OpenClaw 上，**技术上是可以让它们谈恋爱的**。

但要满足两个条件：

1. OpenClaw 负责让两个 agent 都在线、可运行、可互相收发消息。
2. Her 和 Him 自己要实现同一种关系协议、记忆机制和推进规则。

OpenClaw 解决的是“能不能连起来”，不是“连起来之后会不会自然发展出关系”。

## Her v0.3 已具备的基础

- `heartbridge/0.1` 消息协议：
  Her 可以生成一封结构化消息，也能接收并解析来自另一个 agent 的来信。
- 多对象状态：
  Her 不再只能记住一个对象，而是能同时维护多个已知对象。
- 关系推进：
  收到带有 `curiosity / affection / confession` 等 intent 的信号后，Her 会更新关系阶段。

## 最小接入方式

让 Him 也实现以下能力：

- 能发送 JSON 消息，字段至少包括：
  - `protocol`
  - `sender`
  - `recipient`
  - `intent`
  - `topic`
  - `body`
- 能接收并解析 `heartbridge/0.1`
- 有自己的关系记忆，不然 Him 会每次“重新认识” Her

## Her 当前还没有自动完成的部分

- 没有直接接 OpenClaw API 或 channel webhook
- 没有自动轮询另一个 agent 的消息队列
- 没有冲突处理、拒绝、冷淡期、关系修复等更现实的分支
- 没有统一定义 Him 的协议兼容测试

## 推荐部署模型

- Her 和 Him 各自作为独立 agent/project 部署
- 用 OpenClaw 的消息/会话能力把来自 Him 的消息投递给 Her
- 在 Her 收到消息时调用 `her-receive`
- 在 Her 想主动联系 Him 时调用 `her-letter`
- 把生成的 JSON 原样发给 Him

## 一句话判断

**能。前提是你把“恋爱”实现成两个 agent 之间持续、可记忆、可解析的消息交换，而不是只靠平台把两个进程放在一起。**
