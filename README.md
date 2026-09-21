# EcomDevAgent Coding-Agent

> 面向电商研发场景的**终端 AI 研发自动化 Agent**。以 ReAct 推理-行动循环为内核，用交互层 / 引擎层 / 工具层 / 记忆层 / 安全层五层架构组织代码，并叠加 **Loop Engineering（循环工程）** 与 **Harness Engineering（运行基座）** 双工程体系；兼容 Anthropic 与 OpenAI 双协议，支持 MCP 工具动态扩展、Skill 技能包、跨会话长期记忆、多 Agent 团队协作，以及**双路闭环的 Agent 自进化**——从执行轨迹中同时识别「失败模式」与「成功经验」，自动生成 Skill、评估晋升并注入复用。

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)

![Textual](https://img.shields.io/badge/Textual-2.1%2B-FF6F61?logo=textual&logoColor=white)

![Anthropic](https://img.shields.io/badge/Anthropic-0.42%2B-D97757)

![OpenAI](https://img.shields.io/badge/OpenAI-1.60%2B-412991?logo=openai&logoColor=white)

![MCP](https://img.shields.io/badge/MCP-1.12%2B-1C3C3C)

![Pydantic](https://img.shields.io/badge/Pydantic-2.x-E92063?logo=pydantic&logoColor=white)

![uv](https://img.shields.io/badge/uv-managed-6C7AFF?logo=uv&logoColor=white)

![pytest](https://img.shields.io/badge/pytest-9.0%2B-0A9EDC?logo=pytest&logoColor=white)

---

## 目录

- [一、项目简介](#一项目简介)
  - [1.1 背景](#11-背景)
  - [1.2 核心功能](#12-核心功能)
  - [1.3 关键特性](#13-关键特性)
  - [1.4 技术栈](#14-技术栈)
- [二、系统架构](#二系统架构)
  - [2.1 五层分层架构](#21-五层分层架构)
  - [2.2 ReAct 主循环](#22-react-主循环)
  - [2.3 Plan Mode 规划模式](#23-plan-mode-规划模式)
  - [2.4 七层权限拦截](#24-七层权限拦截)
- [三、目录结构](#三目录结构)
- [四、快速开始](#四快速开始)
  - [4.1 环境要求](#41-环境要求)
  - [4.2 安装依赖](#42-安装依赖)
  - [4.3 配置 API Key](#43-配置-api-key)
  - [4.4 创建配置文件](#44-创建配置文件)
  - [4.5 启动](#45-启动)
- [五、基础使用](#五基础使用)
  - [5.1 TUI 快捷键](#51-tui-快捷键)
  - [5.2 斜杠命令](#52-斜杠命令)
  - [5.3 权限模式](#53-权限模式)
- [六、模块说明](#六模块说明)
  - [6.1 内置工具（Tool Registry）](#61-内置工具tool-registry)
  - [6.2 Harness 工具与进化工具](#62-harness-工具与进化工具)
  - [6.3 上下文压缩与恢复](#63-上下文压缩与恢复)
  - [6.4 Skill 技能包](#64-skill-技能包)
  - [6.5 子 Agent 与团队协作](#65-子-agent-与团队协作)
  - [6.6 Loop Engineering](#66-loop-engineering)
  - [6.7 Harness Engineering](#67-harness-engineering)
  - [6.8 Agent 自进化（双路闭环）](#68-agent-自进化双路闭环)
  - [6.9 长期记忆与 Hook](#69-长期记忆与-hook)
- [七、开发指南](#七开发指南)
  - [7.1 配置项](#71-配置项)
  - [7.2 Hook 配置](#72-hook-配置)
  - [7.3 MCP 配置](#73-mcp-配置)
  - [7.4 扩展一个新工具](#74-扩展一个新工具)
- [八、测试](#八测试)
- [九、常见问题 FAQ](#九常见问题-faq)
- [十、路线图](#十路线图)

---

## 一、项目简介

### 1.1 背景

把「写代码」这件事交给 Agent，难点从来不是调用一次 LLM，而是**长任务下 Agent 会失控**。EcomDevAgent 要解决的就是四类失控：

| 失控类型           | 具体表现                                             | 本项目对应机制                                        |
| -------------- | ------------------------------------------------ | ---------------------------------------------- |
| **上下文失控**      | 长会话里工具结果越堆越多，最终撑爆 context window，且压缩时把 `tool_use` / `tool_result` 拆散导致请求报错 | 双层渐进式压缩：超限工具结果落盘 + 全对话摘要，并用 `_align_keep_start_to_tool_pair()` 保证配对完整 |
| **行为失控**       | Agent 全自动跑起来后误删文件、执行危险命令、越界读写                | 七层权限拦截模型（Plan 例外 → 只读放行 → 危险命令黑名单 → 路径沙箱 → 规则引擎 → 模式兜底 → 人工确认） |
| **能力失控（不会成长）** | 同类任务反复失败，Agent 每次从零摸索，经验无法沉淀               | 双路自进化闭环：失败驱动补短板 + 成功经验沉淀为指南型 Skill，评估晋升后才注入复用 |
| **流程失控**       | 任务需要多阶段推进、定时调度、断点续跑，靠一次性对话撑不住            | Loop Engineering：phase-based 工作流引擎 + Journal 断点恢复 + 预算控制 + Cron 调度 |

### 1.2 核心功能

1. **ReAct 双模式推理**：默认 ReAct（Think → Act → Observe → Loop）推理-行动循环；开启 Plan Mode 后先产出 Markdown 计划、经用户确认再逐步执行。两模式共用同一套工具与权限链路（`ecomdevagent/agent.py`）。
2. **五层分层架构**：交互层（Textual TUI）、引擎层（Agent 主循环）、工具层（Tool Registry + 延迟加载）、记忆层（Session / Auto Memory / Instructions）、安全层（Permissions / Sandbox / Audit），职责边界清晰。
3. **双协议 LLM 客户端**：`client.py` 用统一 `create_client(provider)` 抽象 Anthropic 与 OpenAI 两种协议，消息序列化差异由 `serialization.py` 收敛，换模型厂商不改业务代码。
4. **MCP 工具动态扩展**：`mcp/` 模块负责 MCP Server 生命周期管理与工具包装，配置即接入外部工具能力。
5. **Skill 技能包**：内置 `commit` / `review` / `test` 技能，支持从项目目录或用户目录加载自定义 Skill，支持 `tool.json` 为 Skill 挂载自定义工具实现。
6. **跨会话记忆**：自动提取并分类四类长期记忆（用户偏好 / 纠正反馈 / 项目知识 / 参考资料），JSONL 持久化，支持会话摘要与恢复（compact）。
7. **多 Agent 协作**：子 Agent 分发（Fork / SubAgent）、Team 团队协作（Coordinator + 共享任务 + 邮箱通信），跨终端面板（tmux / iTerm2）或进程内并发执行，并以 Git Worktree 做任务隔离。
8. **Agent 自进化**：失败驱动与成功经验两条独立闭环，含轨迹采集、模式分类、Skill 生成、重放评估、晋升/降级、自动备份回滚。
9. **Harness 运行基座**：完整性审查（CompletenessCritic）、审计日志（AuditLogger）、单工具粒度限流（RateLimiter）、全链路指标（MetricsCollector）四大增强组件，并暴露运行时自调控工具。

### 1.3 关键特性

- **上下文压缩是「不报错优先」的**：Layer 1 单条工具结果超 `50_000` 字符、或聚合超 `200_000` 字符即落盘到 `.ecomdevagent/session/tool-results/` 并替换为预览 + 路径；Layer 2 在 `context_window - 13_000` 安全边界触发全对话摘要，尾部保留 `10_000` tokens 原文，且保留边界会向工具对对齐，**不会把 `tool_use` 与 `tool_result` 拆到两侧**。
- **压缩不是单向丢弃**：`RecoveryState` 在压缩时抢救最近读取的文件内容（最多 5 个，每文件 5K tokens）与激活的 Skill SOP（预算 25K tokens），压缩后仍能继续干活。
- **prompt cache 一致性**：`ContentReplacementState` 做决策冻结，避免同一内容在后续轮次被反复换写法导致缓存失效；fork 出子 Agent 时继承父 Agent 的替换状态。
- **权限是七层串联短路判定**：任一环节返回 DENY 立即终止，不做「侥幸放行」；只读命令与 Plan 模式在白名单层直接放行，减少不必要的交互打断。
- **自进化「不凭空虚造」**：`SkillGenerator` 必须基于真实失败证据生成 SKILL.md，禁止凭空编造；生成前自动备份、评估不通过自动回滚。
- **成功经验两阶段晋升防污染**：单次复杂成功只生成「候选」Skill 且不注入；同类成功复发达到阈值（默认 2 次）才晋升「正式」并可被匹配注入，避免一次偶发经验污染 Skill 库。
- **匹配不阻塞主流程**：成功经验匹配走轻量 LLM 侧路调用并带超时（默认 8s），超时或失败静默跳过；命中后也不强制执行，交由 Agent 自主判断是否采纳。
- **工具延迟加载**：`ToolRegistry` 中标记 `should_defer` 的工具不出现在初始 schema 中，由 `ToolSearch` 按需检索拉取，减少 prompt 体积。
- **配置多源分层合并**：配置按「用户级 → 项目级 → 项目 local」顺序加载并逐层覆盖，密钥走 `.env` / `.env.local`，结构与密钥分离。

### 1.4 技术栈

| 层次       | 技术选型                                                                                |
| -------- | ----------------------------------------------------------------------------------- |
| 语言 / 运行时 | Python **>= 3.11**（`requires-python = ">=3.11"`）                                     |
| 依赖管理     | [uv](https://docs.astral.sh/uv/)（`pyproject.toml` + `uv.lock`）                       |
| 终端 UI    | [Textual](https://textual.textualize.io/) >= 2.1.0（含自定义 `NoAltScreenDriver` 保留 scrollback） |
| LLM 协议   | `anthropic` >= 0.42.0（Anthropic）/ `openai` >= 1.60.0（OpenAI 及 OpenAI 兼容）             |
| 工具协议     | `mcp` >= 1.12.0（Model Context Protocol）                                             |
| 数据校验     | `pydantic` >= 2.0（工具参数模型、配置模型）                                                       |
| 配置解析     | `pyyaml` >= 6.0                                                                     |
| HTTP 客户端 | `httpx` >= 0.27.0                                                                   |
| 测试框架     | `pytest` >= 9.0.3 + `pytest-asyncio` >= 1.3.0（dev 依赖组）                              |
| 构建后端     | Hatchling                                                                           |

---

## 二、系统架构

### 2.1 五层分层架构

```
┌───────────────────────────────────────────────────────────┐
│                     交互层 (TUI / CLI)                     │
│   app.py (EcomDevAgentApp) · ChatInput · 流式输出           │
│   permission_dialog / plan_dialog / askuser_dialog         │
├───────────────────────────────────────────────────────────┤
│                      引擎层 (Agent)                        │
│   agent.py：ReAct Loop / Plan Mode / run_to_completion      │
│   context/manager.py：双层渐进式压缩 + RecoveryState         │
├───────────────────────────────────────────────────────────┤
│                      工具层 (Tools)                        │
│   ToolRegistry（延迟加载 / should_defer / ToolSearch）       │
│   ReadFile WriteFile EditFile Bash Glob Grep Agent …       │
│   MCP 工具 · Skill 自定义工具 (tool.json + references/)      │
├───────────────────────────────────────────────────────────┤
│                     记忆层 (Memory)                        │
│   session.py (JSONL 持久化) · auto_memory.py (四类记忆)      │
│   instructions.py (项目/用户指令) · recall.py (召回)          │
├───────────────────────────────────────────────────────────┤
│                   安全层 (Permissions)                     │
│   checker.py 七层串联校验 · sandbox.py 路径沙箱              │
│   dangerous.py 危险命令 · rules.py 三级规则 · audit.py 审计  │
│   rate_limit.py 限流    ┃  Harness: critic/audit/metrics    │
└───────────────────────────────────────────────────────────┘
          │                                    │
          ▼                                    ▼
   workflow/ + scheduler/              harness/evolution/
   (Loop Engineering)                  (Agent 自进化双路闭环)
```

> `workflow/`、`scheduler/`、`harness/` 三个目录横跨引擎层与安全层：前者提供「任务怎么循环推进」，后者提供「运行时基座与自我改进」。

### 2.2 ReAct 主循环

Agent 采用标准 ReAct（Reasoning + Acting）循环，由 `agent.py` 的 `run_to_completion()` 驱动：

1. **Think** — LLM 推理当前上下文，决定下一步行动（或直接给出答案）
2. **Act** — 调用工具执行操作（读文件、写代码、跑命令、派发子 Agent 等）
3. **Observe** — 收集工具执行结果，必要时落盘并替换为预览
4. **Loop** — 观察结果回灌 LLM，继续推理，直至任务完成或达到最大轮次

每次工具调用期间自动穿插：**七层权限检查 → Hook 回调 → 上下文压缩判定 → 记忆提取**。异步子任务（`Agent` 工具的异步模式）完成时，会以 `<task-notification>` 形式注入对话继续处理。

### 2.3 Plan Mode 规划模式

开启 Plan Mode 后，Agent 只能做只读探索，把方案写成 Markdown 计划文件，经用户确认（`ExitPlanMode` 退出）后才切换到可写模式逐步执行。适合复杂、高风险、需要人工把关的任务。Plan 模式下 `Agent` / `ToolSearch` / `AskUser` / `ExitPlanMode` 等工具在权限层 Layer 0 例外放行。

### 2.4 七层权限拦截

```
工具调用请求
   │
   ├─ Layer 0  Plan 模式例外放行（Agent / ToolSearch / AskUser / ExitPlanMode）
   ├─ Layer 1  安全的只读命令自动放行
   ├─ Layer 1b 危险命令黑名单检测（DangerousCommandDetector，仅 Bash）
   ├─ Layer 2  路径沙箱检查（PathSandbox：限定工作目录 + 临时目录）
   ├─ Layer 3  规则引擎匹配（RuleEngine：user / project / local 三级 YAML）
   ├─ Layer 4  权限模式兜底判定（default / acceptEdits / plan / bypass…）
   └─ Layer 5  触发人工确认（HITL 弹窗）
   │
   ▼
 任一环节 DENY → 立即终止；全部放行 → 执行工具
```

---

## 三、目录结构

```
EcomDevAgent/
├── main.py                     # 占位脚本（不参与运行，真实入口为 ecomdevagent 命令）
├── pyproject.toml              # 项目元数据与依赖声明（uv 管理，Python >= 3.11）
├── uv.lock                     # 依赖锁定文件
├── .env.example                # 密钥样例（脱敏，可提交；cp .env.example .env 后填写）
│
├── ecomdevagent/               # ── 核心源码包 ──
│   ├── __main__.py             #   CLI 入口（ecomdevagent 命令 / -p 非交互模式）
│   ├── app.py                  #   Textual TUI 应用主体
│   ├── agent.py                #   Agent 主循环：ReAct / Plan Mode
│   ├── client.py               #   LLM 统一客户端（Anthropic / OpenAI 双协议）
│   ├── serialization.py        #   消息序列化适配层（两种协议格式互转）
│   ├── config.py               #   配置多源分层加载与合并
│   ├── validator.py            #   配置校验（协议 / 权限模式 / context window 映射表）
│   ├── conversation.py         #   对话消息生命周期管理
│   ├── prompts.py              #   系统提示词动态构建
│   ├── cache.py                #   文件/内容缓存
│   ├── driver.py               #   终端驱动（NoAltScreenDriver，保留 scrollback）
│   ├── styles.tcss             #   Textual 样式表
│   ├── permission_dialog.py    #   TUI 权限确认弹窗
│   ├── plan_dialog.py          #   TUI 规划弹窗
│   ├── session_dialog.py       #   TUI 会话选择弹窗
│   ├── askuser_dialog.py       #   TUI AskUser 交互弹窗
│   ├── teammate_tree.py        #   团队 Agent 树展示组件
│   │
│   ├── agents/                 #   多智能体核心
│   │   ├── builtins/           #     内置 Agent 定义（general-purpose / explore / plan / verification）
│   │   ├── loader.py           #     Agent 加载器（项目 > 用户 > 内置 三级优先级）
│   │   ├── parser.py           #     Agent 定义文件（frontmatter）解析
│   │   ├── fork.py             #     Fork 子 Agent 分发
│   │   ├── task_manager.py     #     异步子任务调度与完成通知
│   │   ├── tool_filter.py      #     Agent 工具权限过滤
│   │   ├── trace.py            #     全链路调用 Trace 记录与回放
│   │   ├── metrics.py          #     MetricsCollector 指标收集
│   │   └── notification.py     #     子 Agent 完成通知
│   │
│   ├── tools/                  #   工具层
│   │   ├── base.py             #     Tool 基类与流式事件定义
│   │   ├── __init__.py         #     ToolRegistry + create_default_registry()
│   │   ├── file_state_cache.py #     read-before-edit 约束的文件状态缓存
│   │   ├── read_file.py / write_file.py / edit_file.py / bash.py / glob.py / grep.py
│   │   ├── agent_tool.py       #     Agent 工具（同步 / 异步 / Worktree 隔离三模式）
│   │   ├── ask_user.py / load_skill.py / send_message.py / synthetic_output.py
│   │   ├── task_create.py / task_get.py / task_list.py / task_update.py
│   │   ├── team_create.py / team_delete.py
│   │   ├── enter_worktree.py / exit_worktree.py / exit_plan_mode.py
│   │   └── impl/tool_search.py #     ToolSearch 延迟加载检索
│   │
│   ├── commands/               #   斜杠命令系统
│   │   ├── registry.py / parser.py / completion.py
│   │   └── handlers/           #     16 个命令处理器（clear/compact/help/mcp/memory/permission/plan/review/rewind/session/skill/skill_register/status/tasks/trace/worktree）
│   │
│   ├── context/                #   上下文窗口治理
│   │   ├── manager.py          #     双层渐进式压缩 + ContentReplacementState + RecoveryState
│   │   └── critic.py           #     CompletenessCritic 会话完整性审查
│   │
│   ├── memory/                 #   跨会话记忆
│   │   ├── session.py          #     JSONL 会话持久化与压缩边界
│   │   ├── auto_memory.py      #     异步记忆提取（四类记忆分类）
│   │   ├── recall.py           #     历史记忆检索召回
│   │   └── instructions.py     #     项目 / 用户指令加载合并
│   │
│   ├── permissions/            #   安全层
│   │   ├── checker.py          #     七层串联式权限校验器
│   │   ├── modes.py            #     权限模式矩阵
│   │   ├── sandbox.py          #     路径沙箱
│   │   ├── dangerous.py        #     危险命令检测
│   │   ├── rules.py            #     三级 YAML 规则引擎
│   │   ├── audit.py            #     AuditLogger 会话审计日志
│   │   └── rate_limit.py       #     RateLimiter 单工具粒度限流
│   │
│   ├── hooks/                  #   Hook 生命周期钩子
│   │   ├── engine.py / models.py / events.py
│   │   ├── conditions.py       #     触发条件表达式解析
│   │   ├── executors.py        #     动作执行器（命令 / HTTP / 提示词 / 子 Agent）
│   │   └── loader.py           #     Hook 配置加载
│   │
│   ├── skills/                 #   Skill 技能包
│   │   ├── builtins/           #     内置技能（commit / review / test 各自的 SKILL.md）
│   │   ├── loader.py           #     技能加载器（项目 > 用户 > 内置，支持热重载）
│   │   ├── parser.py           #     SKILL.md（frontmatter）解析
│   │   ├── executor.py         #     技能执行调度
│   │   └── directory.py        #     目录技能扫描 + tool.json 自定义工具注册
│   │
│   ├── teams/                  #   多 Agent 团队协作
│   │   ├── coordinator.py      #     Coordinator 调度（任务拆分 / 结果汇总）
│   │   ├── manager.py / registry.py / models.py / shared_task.py
│   │   ├── mailbox.py          #     Agent 间消息通信
│   │   ├── progress.py / transcript.py
│   │   ├── backend_detect.py   #     终端后端自动检测
│   │   └── spawn_tmux.py / spawn_iterm2.py / spawn_inprocess.py   # Worker 启动方式
│   │
│   ├── mcp/                    #   MCP 协议扩展
│   │   ├── client.py / manager.py / tool_wrapper.py
│   │
│   ├── workflow/               #   Loop Engineering 工作流引擎
│   │   ├── engine.py           #     WorkflowEngine 分阶段闭环引擎
│   │   ├── context.py          #     agent()/pipeline()/parallel()/phase() API
│   │   ├── patterns.py         #     循环模板（次数 / 预算 / 干跑保护）
│   │   ├── journal.py / resume.py   # 断点持久化与恢复
│   │   ├── models.py           #     工作流 / 预算 / 调用记录模型
│   │   └── tool.py             #     Workflow Agent Tool
│   │
│   ├── scheduler/              #   Cron 定时调度
│   │   ├── runtime.py / store.py / cron.py / wakeup.py / tools.py
│   │
│   ├── harness/                #   Harness Engineering 运行基座
│   │   ├── hook_manager.py / config_manager.py / permission_manager.py
│   │   ├── tools.py            #     运行时自调控工具集（AddHook / UpdateConfig / …）
│   │   └── evolution/          #     Agent 自进化子系统
│   │       ├── manager.py            # EvolutionManager 门面
│   │       ├── decision_loop.py      # EvolutionDecisionLoop 主控（失败 + 成功双路）
│   │       ├── trace_store.py        # 轨迹采集与按日分片存储
│   │       ├── problem_classifier.py # 失败模式 LLM 分类
│   │       ├── skill_generator.py    # 基于失败证据的 Skill 生成
│   │       ├── success_detector.py   # 复杂成功任务识别
│   │       ├── success_generator.py  # 成功经验指南型 Skill 生成
│   │       ├── skill_matcher.py      # 语义匹配器（晋升 + 注入两用）
│   │       ├── evaluator.py          # 历史用例重放评估
│   │       ├── backup.py             # 进化前备份与回滚
│   │       ├── skill_meta.py         # Skill 元信息与状态机
│   │       ├── models.py / tools.py
│   │
│   ├── worktree/               #   Git Worktree 隔离
│   │   ├── manager.py / integration.py / session.py / setup.py
│   │   ├── cleanup.py          #     过期临时分支清理
│   │   ├── changes.py / models.py / slug.py
│   │
│   └── filehistory/            #   文件编辑历史
│       └── history.py
│
├── tests/                      # 测试套件（20 个 test_ 模块 + verify_subagent.py 人工验证脚本）
└── .ecomdevagent/              # 运行时数据目录（启动时自动创建，已在 .gitignore 中）
    ├── config.yaml             #   项目级配置
    ├── debug.log               #   调试日志
    ├── sessions/               #   JSONL 会话日志
    ├── skills/                 #   项目级自定义 Skill
    └── session/tool-results/   #   落盘的超长工具结果
```

> ⚠️ `.ecomdevagent/` 是运行时数据目录（配置 + 会话 + 记忆 + 技能），**不是缓存**，请勿随意删除。

---

## 四、快速开始

### 4.1 环境要求

| 项目            | 要求                            | 说明                                                         |
| ------------- | ----------------------------- | ---------------------------------------------------------- |
| 操作系统          | Windows / Linux / macOS       | 终端需支持 TUI；团队 Worker 跨面板模式额外需要 tmux（Linux/macOS）或 iTerm2（macOS） |
| Python        | **>= 3.11**                   | `pyproject.toml` 已声明 `requires-python = ">=3.11"`            |
| 包管理器          | [uv](https://docs.astral.sh/uv/)（推荐） | 也可用原生 `venv` + `pip`                                        |
| LLM API Key   | Anthropic 或 OpenAI（或任意 OpenAI 兼容服务） | 至少配置一个，见 4.3                                              |
| Git（可选）       | 任意较新版本                        | 仅 `/review`、Worktree 隔离、`commit` 技能需要                       |

### 4.2 安装依赖

```bash
# 1) 克隆仓库
git clone <your-repo-url> EcomDevAgent
cd EcomDevAgent

# 2) 创建虚拟环境
uv venv

# 3) 激活虚拟环境
# Windows (PowerShell)
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 4) 以可编辑模式安装
uv pip install -e .
```

也可以直接用 `uv run` 免激活运行（见 4.5）。

### 4.3 配置 API Key

推荐把密钥写进项目根目录的 `.env`（已被 `.gitignore` 忽略），仓库已提供 `.env.example`：

```bash
cp .env.example .env
```

```dotenv
# 按 protocol 自动匹配的通用 key
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx

# 按 provider 名精确覆盖（优先于上面的通用 key）
# 规则：ECOMDEVAGENT_<PROVIDER_NAME 大写>_API_KEY
ECOMDEVAGENT_DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

> 加载顺序：`.env` → `.env.local`（后者覆盖前者）；**真实 shell 环境变量永远优先**。`.env` 只放密钥，provider 结构（`protocol` / `base_url` / `model` / `thinking`）写在 `config.yaml` 里。

也可以直接用系统环境变量：

```bash
# Windows
set ANTHROPIC_API_KEY=your-key-here
# Linux / macOS
export ANTHROPIC_API_KEY=your-key-here
```

### 4.4 创建配置文件

在项目目录下创建 `.ecomdevagent/config.yaml`（或全局 `~/.ecomdevagent/config.yaml`）。配置按 **用户级 → 项目级 → 项目 local** 三层合并，后者覆盖前者：

```yaml
providers:
  - name: claude
    protocol: anthropic          # anthropic | openai | openai-compat
    base_url: https://api.anthropic.com
    model: claude-sonnet-4-5-20250929
    api_key: ${ANTHROPIC_API_KEY}  # 也可留空，由 .env 的通用 key 回落
    thinking: true
    # context_window: 200000       # 可选：显式覆盖自动探测值（最高优先级）

permission_mode: default

mcp_servers: []

enable_fork: false
enable_verification_agent: false
teammate_mode: ""                # "" | "in-process"
enable_coordinator_mode: false

hooks: []

worktree:
  symlink_directories:
    - node_modules
    - .venv
  stale_cleanup_interval: 3600
  stale_cutoff_hours: 24
```

**context window 四层回退链**：配置显式值（`context_window`）→ 启动时自动从 provider 拉取 → 内置「模型名子串 → window」映射表（`validator.py` 的 `MODEL_CONTEXT_WINDOWS`）→ 默认值 `200_000`。映射表仅为合理起始点，模型更新后可能过时，不准确时请显式配置覆盖。

### 4.5 启动

```bash
# 交互式 TUI（裸 Python 环境用 python -m ecomdevagent）
ecomdevagent

# uv 环境免激活运行
uv run ecomdevagent

# 非交互模式：执行一条 prompt 并把结果打到 stdout
ecomdevagent -p "帮我写一个 Python 的快速排序函数"

# 临时覆盖权限模式（等价于 config.yaml 的 permission_mode）
ecomdevagent --mode acceptEdits
```

> 程序启动时会自动创建 `.ecomdevagent/` 目录并把日志写入 `.ecomdevagent/debug.log`（每次启动覆盖）。首次运行若报 `No config file found`，说明 4.4 的配置文件还没建。

---

## 五、基础使用

### 5.1 TUI 快捷键

| 快捷键                        | 功能                    |
| -------------------------- | --------------------- |
| `Enter`                    | 发送消息                  |
| `Shift+Enter` / `Ctrl+J`   | 换行（不发送）               |
| `Tab`                      | 命令 / 文件路径补全           |
| `Shift+Tab`                | 循环切换权限模式              |
| `Ctrl+O`                   | 展开 / 折叠工具调用详情         |
| `Escape`                   | 取消当前操作                |
| `Ctrl+C`                   | 退出                    |
| `@`                        | 引用文件（触发路径自动补全）        |
| `/`                        | 输入斜杠命令                |

### 5.2 斜杠命令

| 命令                | 功能                |
| ----------------- | ----------------- |
| `/clear`          | 清空当前对话            |
| `/compact`        | 手动触发上下文压缩         |
| `/help`           | 显示帮助信息            |
| `/mcp`            | 管理 MCP 服务连接       |
| `/memory`         | 查看 / 管理长期记忆       |
| `/permission`     | 切换权限模式            |
| `/plan`           | 进入规划模式            |
| `/review`         | 代码审查当前变更          |
| `/rewind`         | 回退到之前的对话节点        |
| `/session`        | 会话管理（保存 / 恢复 / 切换） |
| `/skill`          | 查看 / 管理 Skill 技能包 |
| `/skill-register` | 注册自定义 Skill       |
| `/status`         | 查看系统运行状态          |
| `/tasks`          | 查看后台任务列表          |
| `/trace`          | 查看 Agent 调用 Trace |
| `/worktree`       | 管理 Git Worktree 隔离环境 |

### 5.3 权限模式

| 模式                  | 读取  | 写入  | 命令  | 说明                        |
| ------------------- | --- | --- | --- | ------------------------- |
| `default`           | ✓ 允许 | 🔔 询问 | 🔔 询问 | 默认安全模式，写操作需确认            |
| `acceptEdits`       | ✓ 允许 | ✓ 允许 | 🔔 询问 | 自动接受文件编辑，命令仍需确认          |
| `plan`              | ✓ 允许 | 🔔 询问 | 🔔 询问 | 规划模式，仅允许只读探索             |
| `bypassPermissions` | ✓ 允许 | ✓ 允许 | ✓ 允许 | 跳过所有权限检查（**慎用**）          |

> 配置层面还接受 `custom` 与 `dontAsk` 两个取值（`validator.py` 中 `VALID_PERMISSION_MODES`），用于规则引擎驱动的自定义策略与免打扰场景。TUI 中按 `Shift+Tab` 快速切换。

---

## 六、模块说明

### 6.1 内置工具（Tool Registry）

`create_default_registry()`（`tools/__init__.py`）默认注册 6 个文件与命令类工具，其余工具在启动流程中按需追加：

| 工具                                                | 功能                                              |
| ------------------------------------------------- | ----------------------------------------------- |
| `ReadFile` / `WriteFile` / `EditFile`             | 读文件 / 覆写文件 / 精确编辑（search-replace）              |
| `Bash`                                            | 执行 Shell 命令                                    |
| `Glob` / `Grep`                                   | 文件模式匹配 / 正则内容搜索                                 |
| `Agent`                                           | 派发子 Agent（同步 / 异步 / Git Worktree 隔离三模式）         |
| `TeamCreate` / `TeamDelete`                       | 创建 / 删除 Agent 团队                               |
| `TaskCreate` / `TaskGet` / `TaskList` / `TaskUpdate` | 任务管理（后台任务与通知注入）                              |
| `LoadSkill`                                       | 激活 Skill 技能包                                   |
| `ToolSearch`                                      | 延迟加载工具检索（按需拉取 schema）                          |
| `AskUser`                                         | 向用户提问                                           |
| `EnterWorktree` / `ExitWorktree`                  | 进入 / 退出 Git Worktree 隔离环境                      |
| `ExitPlanMode`                                    | 退出规划模式                                          |
| `SyntheticOutput`                                 | Coordinator 模式结构化输出                            |
| `SendMessage`                                     | 团队内消息通信                                         |

> `WriteFile` / `EditFile` 与 `FileStateCache` 联动，强制 **read-before-edit**：未先读取的文件不会被盲目改写。

### 6.2 Harness 工具与进化工具

**运行时自调控工具**（需配置 `allow_self_modification: true`）：

| 工具                                | 功能           |
| --------------------------------- | ------------ |
| `AddHook` / `RemoveHook` / `ListHooks` | 生命周期 Hook 增删查 |
| `UpdateConfig`                    | 更新运行时配置      |
| `AddPermissionRule` / `RemovePermissionRule` | 权限规则增删 |
| `ManageMemory`                    | 管理长期记忆       |

**自进化工具**（需配置 `allow_self_evolution: true`）：

| 工具                     | 功能                                |
| ---------------------- | --------------------------------- |
| `TriggerEvolution`     | 手动触发一轮进化检查（失败 + 成功双路）             |
| `ListEvolutions`       | 列出进化历史记录（含 `path` 字段区分 failure / success） |
| `GetEvolutionDetail`   | 查看某次进化详情                          |
| `ListAutoSkills`       | 列出自动生成的 Skill 及状态（candidate / active / deprecated） |
| `DeprecateSkill`       | 手动废弃某个自动生成的 Skill                 |

### 6.3 上下文压缩与恢复

**Layer 1 — 工具结果落盘**（`context/manager.py`）

- 单条工具结果超 `SINGLE_RESULT_CHAR_LIMIT = 50_000` 字符 → 落盘到 `.ecomdevagent/session/tool-results/`，原位替换为预览 + 文件路径
- 聚合超 `AGGREGATE_CHAR_LIMIT = 200_000` 字符 → 从最旧的结果开始批量落盘，直至降到限额内
- `ContentReplacementState` 做**决策冻结**：同一内容在后续轮次保持同一替换写法，保证 prompt cache 命中；fork 子 Agent 时继承父 Agent 的替换状态

**Layer 2 — 全对话摘要**

- 触发阈值：`context_window - AUTO_COMPACT_SAFETY_MARGIN`（安全边界 `13_000` tokens）
- 尾部保留 `KEEP_RECENT_TOKENS = 10_000` tokens 原文
- 保留边界经 `_align_keep_start_to_tool_pair()` 对齐，**保证 `tool_use` 与配对的 `tool_result` 不被拆散**（这是压缩后请求报错最常见的成因）

**RecoveryState（压缩时抢救关键上下文）**

- 最近读取的文件内容：最多 `RECOVERY_FILE_LIMIT = 5` 个，每文件 `RECOVERY_TOKENS_PER_FILE = 5_000` tokens
- 激活的 Skill SOP：总预算 `RECOVERY_SKILLS_BUDGET = 25_000` tokens

### 6.4 Skill 技能包

内置技能（`skills/builtins/`，各自目录下为 `SKILL.md`）：

| 技能        | 说明                       | 允许的工具                    |
| --------- | ------------------------ | ------------------------ |
| `commit`  | 分析 git diff 并生成规范 commit | `Bash` / `ReadFile` / `Grep` |
| `review`  | 多维度代码审查                  | 见 `SKILL.md`              |
| `test`    | 自动生成测试用例                 | 见 `SKILL.md`              |

**加载优先级**：项目级 `.ecomdevagent/skills/` > 用户级 `~/.ecomdevagent/skills/` > 内置。同名技能以高优先级为准。

Skill 支持两种组织方式：

- **单文件**：`.md` 文件直接放在技能目录下
- **目录式（可挂载自定义工具）**：目录内放 `SKILL.md`，可选 `tool.json`（工具 schema 数组）+ `references/<tool_name>.py`（实现，需导出 `execute` 函数）——加载时由 `register_skill_tools()` 自动注册成可用工具

技能支持**热重载**：每次 `get()` 会重新解析磁盘文件，改完 SKILL.md 无需重启。

### 6.5 子 Agent 与团队协作

**内置子 Agent**（`agents/builtins/*.md`，通过 frontmatter 定义）：

| Agent 类型          | 说明                              |
| ----------------- | ------------------------------- |
| `general-purpose` | 通用子 Agent，可使用较完整的工具集            |
| `explore`         | 代码探索 Agent，专注搜索与理解代码           |
| `plan`            | 规划 Agent，专注制定执行计划               |
| `verification`    | 验证 Agent，专注审查与验证代码（需 `enable_verification_agent: true`） |

Agent 定义可从 `<project>/.ecomdevagent/agents/` 与 `~/.ecomdevagent/agents/` 加载，优先级为 **项目 > 用户 > 内置**，支持热重载。

**团队协作**：开启 `enable_coordinator_mode: true` 后，主 Agent 担任 Coordinator，通过 `TeamCreate` 组建团队、`SendMessage` 通信、`SyntheticOutput` 汇总结构化结果。Worker 的启动方式有三种，由 `backend_detect.py` 自动探测：

- `spawn_inprocess.py`：进程内轻量 Worker（`teammate_mode: "in-process"`）
- `spawn_tmux.py`：独立 tmux 面板（Linux / macOS）
- `spawn_iTerm2.py`：独立 iTerm2 面板（macOS）

**Worktree 隔离**：`EnterWorktree` 基于 `git worktree` 为任务开独立工作树，避免污染主工作区；`symlink_directories` 指定的目录（如 `node_modules` / `.venv`）以软链接共享，`cleanup.py` 定期清理过期分支。

### 6.6 Loop Engineering

- **WorkflowEngine**：phase-based 分阶段工作流编排；`workflow/context.py` 暴露 `agent()` / `pipeline()` / `parallel()` / `phase()` 组合 API
- **循环控制**：`patterns.py` 提供 `loop_until_count()` / `loop_until_budget()`，内置**干跑保护**（`dry_protection=3`），防止循环空转烧 token
- **断点恢复**：`journal.py` 持久化每个 phase 的执行状态，`resume.py` 支持中断后续跑
- **预算追踪**：`models.py` 的 `BudgetInfo` 记录预算与消耗，超预算即停止
- **调度系统**：`scheduler/` 提供 `CronStore` + `SchedulerRuntime` + `WakeupScheduler`，支持 Cron 表达式定时任务与休眠唤醒
- **执行追踪**：`AgentCallRecord` 记录每次调用的 `prompt_hash` / `opts_hash` / 状态 / 耗时 / token 用量

### 6.7 Harness Engineering

**四大增强组件**：

| 组件                   | 职责                                        | 关键位置                     |
| -------------------- | ----------------------------------------- | ------------------------ |
| `CompletenessCritic` | 会话完整性审查，检查任务是否真正完成                        | `context/critic.py`      |
| `AuditLogger`        | 会话级审计日志（JSONL），记录每次工具调用与权限决策              | `permissions/audit.py`   |
| `RateLimiter`        | **单工具粒度**限流，默认 `30` 次/分钟，可 per-tool 覆盖    | `permissions/rate_limit.py` |
| `MetricsCollector`   | 全链路指标采集（token 用量、执行时长等）                    | `agents/metrics.py`      |

**三大运行时管理器**（`harness/`）：`HookManager`（生命周期 Hook）、`ConfigManager`（动态配置）、`PermissionManager`（运行时权限规则）。

### 6.8 Agent 自进化（双路闭环）

**失败补救路径**（Read → Classify → Write → Evaluate → Decide → Archive）：

| 阶段    | 组件                     | 职责                                                                                   |
| ----- | ---------------------- | ------------------------------------------------------------------------------------ |
| 采集    | `TraceCollector` + `ExecutionTraceStore` | 任务结束后被动收集执行轨迹（成功失败、错误信息、工具使用、token），按日分片 JSONL 持久化，自动清理 90 天前旧数据 |
| 分类    | `ProblemClassifier`    | LLM 分析失败轨迹，识别四类系统性失败模式：能力缺失 / 重复错误 / 工具误用 / 知识缺口；**同一模式至少出现 3 次**才判定有效 |
| 生成    | `SkillGenerator`       | 基于失败证据生成 SKILL.md（YAML frontmatter + 触发条件 + 操作步骤），**禁止凭空编造**                    |
| 评估    | `EvolutionEvaluator`   | 重放历史失败用例，对比新旧成功率与 token —— 成功率提升 **且** token 增幅 ≤ `15%` 才保留新 Skill                |
| 决策    | `SkillMetaManager`     | 维护 Skill 状态机（candidate / active / deprecated / superseded）与来源、使用统计                |
| 归档    | `BackupManager`        | 生成前自动备份现有 Skills，评估不通过自动回滚                                                          |

**成功经验路径**（在失败路径之上叠加）：

- **复杂成功识别**：`SuccessDetector` 依据迭代数 ≥ `success_iteration_threshold`（默认 8）与工具调用数 ≥ `success_tool_call_threshold`（默认 10）判定「复杂成功任务」，只有复杂**且成功**才进入沉淀
- **指南型沉淀**：`SuccessSkillGenerator` 把关键步骤、工具选择、决策点总结为**指南型 SKILL.md**（而非死板的调用序列），Agent 读取后按指引弹性执行
- **两阶段晋升**：首次复杂成功生成「候选」（**不注入**）；同类成功复发 ≥ `success_promotion_recurrence`（默认 2）才晋升「正式」，方可被匹配注入 —— 避免单次偶发经验污染 Skill 库
- **语义匹配注入**：任务开始时 `SkillMatcher` 用轻量 LLM 侧路调用在正式 Skill 中找同类经验，命中则注入上下文；超时（`success_match_timeout`，默认 8s）或失败**静默跳过**，不阻塞主循环
- **Agent 二次校验**：命中的 Skill 不强制执行，Agent 可判断差异较大而拒绝采纳
- **命中后降本评估**：正式 Skill 被采纳后，对比本次迭代数 / tokens 与同类历史基线（`success_baseline_samples`，默认 5 个样本）—— 迭代降幅 ≥ `success_iteration_reduction_threshold`（默认 20%）**且** token 增幅 ≤ 15% 才维持正式，否则降级；命中失败累计 ≥ `success_hit_failure_threshold`（默认 3）自动废弃
- **双路独立去重**：成功路径与失败路径独立生成、不互相查重合并 —— 重叠 Skill 由各自的废弃机制自然淘汰
- **可观测**：生成、晋升、命中、采纳、评估结果均写入进化记录，可用 `ListEvolutions` / `GetEvolutionDetail` 查询

### 6.9 长期记忆与 Hook

**记忆层**（`memory/`）：

- `session.py`：JSONL 会话持久化，维护压缩边界；`/session` 与 `/rewind` 基于它做会话切换与回退
- `auto_memory.py`：异步提取长期记忆，自动归类四类 —— **用户偏好 / 纠正反馈 / 项目知识 / 参考资料**
- `recall.py`：历史记忆检索召回
- `instructions.py`：加载并合并项目 / 用户指令文件

**Hook 系统**（`hooks/`）：支持 `session` / `turn` / `tool` 生命周期事件，`conditions.py` 解析触发条件表达式，`executors.py` 支持四类动作（执行命令 / 发 HTTP / 注入提示词 / 派发子 Agent）。配置见 7.2。

---

## 七、开发指南

### 7.1 配置项

**Harness / Evolution 配置段**（追加到 `.ecomdevagent/config.yaml`）：

```yaml
compact:
  utilization_threshold: 0.85   # 上下文利用率触发阈值
  min_keep_messages: 3          # 至少保留的消息条数

critic:
  enabled: false                # 完整性审查（默认关闭，会增加额外 LLM 调用）

rate_limit:
  enabled: true
  default_max_per_minute: 30    # 单工具默认限流
  per_tool:
    Bash: 10
    WriteFile: 20

allow_self_modification: false  # Harness 运行时自调控工具总开关
allow_self_evolution: false     # 自进化（双路）总开关

evolution:
  enabled: true
  min_traces_trigger: 30
  max_traces_per_evolution: 50
  min_traces_per_evolution: 30
  min_failure_recurrence: 3
  token_increase_threshold: 0.15
  deprecation_task_threshold: 60
  # —— 成功经验路径 ——
  success_enabled: true
  success_iteration_threshold: 8              # 迭代数 ≥ 此值视为复杂任务
  success_tool_call_threshold: 10             # 工具调用数 ≥ 此值视为复杂任务
  success_promotion_recurrence: 2             # 同类成功复发达此值晋升正式
  success_match_enabled: true                 # 任务开始时做 Skill 注入匹配
  success_match_timeout: 8.0                  # 匹配侧路调用超时（秒）
  success_baseline_samples: 5                 # 降本评估的历史基线样本数
  success_iteration_reduction_threshold: 0.20 # 迭代降幅阈值
  success_hit_failure_threshold: 3            # 命中失败达此值自动废弃
```

> `evolution` 也支持嵌套写法 `evolution.success.<key>`，配置加载时会自动平铺为 `success_<key>`。

### 7.2 Hook 配置

```yaml
hooks:
  - id: lint-on-write
    event: post_tool_use
    tool_name: WriteFile
    condition: "file_path.endswith('.py')"
    command: ruff check $FILE_PATH

  - id: format-on-write
    event: post_tool_use
    tool_name: WriteFile
    condition: "file_path.endswith('.py')"
    command: ruff format $FILE_PATH

  - id: notify-on-error
    event: error
    action_type: http
    url: https://hooks.example.com/alert
    method: POST
    body: '{"error": "$ERROR", "tool": "$TOOL_NAME"}'
```

支持的变量占位符：`$EVENT`、`$TOOL_NAME`、`$FILE_PATH`、`$MESSAGE`、`$ERROR`、`$TOOL_ARGS.<key>`。

### 7.3 MCP 配置

```yaml
mcp_servers:
  - name: filesystem
    command: npx
    args:
      - -y
      - @modelcontextprotocol/server-filesystem
      - /path/to/allowed/dir

  - name: github
    command: npx
    args:
      - -y
      - @modelcontextprotocol/server-github
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: ${GITHUB_TOKEN}
```

每个 MCP Server 必须且只能提供 `command`（stdio 方式）或 `url`（HTTP 方式）之一，配置校验会强制检查。

### 7.4 扩展一个新工具

1. 在 `ecomdevagent/tools/` 下定义类，继承 `tools/base.py` 的 `Tool`，实现 `name` / `description` / `params_model`（Pydantic 模型）与 `async def execute(params) -> ToolResult`
2. 在 `tools/__init__.py` 的 `create_default_registry()`（或启动流程中的注册点）调用 `registry.register(YourTool(...))`
3. 若工具希望被延迟加载（不进初始 schema、由 `ToolSearch` 按需检索），设置类属性 `should_defer = True`；`ToolRegistry` 只对 `should_defer=True` 且未被发现/禁用的工具做检索
4. 若工具涉及写操作或外部副作用，请在权限层确认它走 `PermissionChecker.check()`（写文件类工具还需接入 `FileStateCache` 的 read-before-edit 约束）

```python
# ecomdevagent/tools/your_tool.py
from pydantic import BaseModel
from ecomdevagent.tools.base import Tool, ToolResult


class YourParams(BaseModel):
    target: str


class YourTool(Tool):
    name = "YourTool"
    description = "一句话说明这个工具干什么"
    params_model = YourParams
    should_defer = False      # True 则改为延迟加载

    async def execute(self, params: YourParams) -> ToolResult:
        return ToolResult(output=f"done: {params.target}")
```

---

## 八、测试

测试套件位于 `tests/`，当前包含 **20 个 `test_` 模块**（另有 `verify_subagent.py` 为人工验证脚本，非 pytest 用例）：

| 覆盖领域   | 测试模块                                                                                                    |
| ------ | ------------------------------------------------------------------------------------------------------- |
| 核心引擎   | `test_agent` / `test_commands` / `test_serialization` / `test_dotenv`                                     |
| 上下文治理  | `test_context` / `test_context_window` / `test_recovery` / `test_replacement_state`                       |
| 安全与权限  | `test_permissions` / `test_hooks`                                                                         |
| 记忆与技能  | `test_memory` / `test_skills`                                                                             |
| 多 Agent | `test_subagent` / `test_teams` / `test_tool_search` / `test_worktree`                                      |
| 自进化    | `test_evolution_e2e` / `test_evolution_matcher` / `test_evolution_success`                                 |
| 协议扩展   | `test_mcp`                                                                                                |

```bash
# 跑全部测试
uv run pytest

# 跑单个模块
uv run pytest tests/test_evolution_success.py -v

# 仅跑自进化相关
uv run pytest tests/ -k evolution -v
```

> 自进化相关测试（`test_evolution_*`）涉及 LLM 调用与轨迹重放，建议在配置好 API Key 后运行；离线场景下请确认是否有可用的 mock 前置。

---

## 九、常见问题 FAQ

**Q1：启动报 `No config file found. Expected .ecomdevagent/config.yaml in project or ~/.ecomdevagent/config.yaml`？**
配置文件缺失。按 [4.4](#44-创建配置文件) 在项目根建 `.ecomdevagent/config.yaml`，或放到 `~/.ecomdevagent/config.yaml` 作为全局配置。

**Q2：配了 Key 但报鉴权失败 / provider 拿不到 key？**
密钥解析优先级是：真实 shell 环境变量 > `.env.local` > `.env`。若用 `ECOMDEVAGENT_<NAME>_API_KEY` 形式命名，请确认 `<NAME>` 与 `config.yaml` 里该 provider 的 `name` 完全一致（同一大写规则）。

**Q3：长会话突然报 `tool_use` / `tool_result` 配对的 API 错误？**
理论上不会 —— `_align_keep_start_to_tool_pair()` 会把保留边界对齐到完整工具对。若确实遇到，请把 `.ecomdevagent/debug.log` 与触发时的会话 JSONL 一并留下，并确认没有手工编辑过 `.ecomdevagent/sessions/` 下的文件（落盘的工具结果文件被手动删除或改名也会破坏一致性）。

**Q4：`.ecomdevagent/session/tool-results/` 越来越大？**
这是 Layer 1 压缩刻意落盘的超长工具结果目录（单条 > 50K 字符才落盘）。它属于运行时数据，可以安全清理不再需要的旧文件；清理后若某轮对话仍引用该文件，Agent 会看到「文件不存在」并在需要时重新执行工具。

**Q5：按下 `Shift+Tab` 切成 `bypassPermissions` 后 Agent 乱改文件？**
`bypassPermissions` **跳过全部七层检查**，仅建议在一次性容器 / 可丢弃的工作副本里使用。日常请用 `acceptEdits`（自动接受编辑、命令仍需确认）或 `default`。

**Q6：自进化开了但从未生成 Skill？**
逐项排查：① `allow_self_evolution` 与 `evolution.enabled` 是否都为 `true`；② 轨迹数是否达到 `min_traces_trigger`（默认 30）；③ 失败路径要求**同一失败模式至少出现 3 次**才会判定为有效模式；④ 成功路径要求任务同时满足迭代数 ≥ 8 **且** 工具调用数 ≥ 10，且**成功结束**；⑤ 生成后还需通过重放评估（成功率提升且 token 增幅 ≤ 15%）才会保留。

**Q7：成功型 Skill 生成了却没被用上？**
成功路径是**两阶段晋升**：首次复杂成功只产生「候选」，候选不会被匹配注入；需同类复杂成功复发达到 `success_promotion_recurrence`（默认 2）晋升为「正式」后才可注入。用 `ListAutoSkills` 可查看当前状态。

**Q8：限流导致工具调用被拒？**
`RateLimiter` 默认单工具 `30` 次/分钟，`Bash` / `WriteFile` 在默认 per-tool 配置下更严（`10` / `20`）。批量操作场景可在 `rate_limit.per_tool` 里按工具放宽，或整体 `enabled: false`（不推荐长期关闭）。

**Q9：团队 Worker 起不来？**
Worker 启动方式由后端自动探测：`tmux` 面板需要 Linux/macOS 且已装 tmux；iTerm2 面板需要 macOS + iTerm2。两者都不可用时请设 `teammate_mode: "in-process"` 走进程内 Worker。另外 `Agent` 工具的 Worktree 隔离模式需要当前目录是一个 git 仓库。

**Q10：`-p` 非交互模式的输出里混了 `[poll N] ...` 之类的日志？**
那是团队任务轮询的进度输出，走 `stderr`，不影响 `stdout` 的最终结果。若要干净输出，重定向即可：`ecomdevagent -p "..." 2>/dev/null`。

---

## 十、路线图

> 原则：**非侵入式增量** —— 新能力以独立模块挂载，不重写既有主循环与权限链路；重大变更前建立可逆快照，改后跑通「单测 + 一次真实任务」双验证。

### 10.1 已完成

- [x] **ReAct + Plan Mode 双模式主循环**，共用工具层与权限链路
- [x] **五层分层架构**与双协议 LLM 客户端抽象
- [x] **七层权限拦截模型**（含路径沙箱、危险命令检测、三级规则引擎）
- [x] **双层渐进式上下文压缩** + `ContentReplacementState` 决策冻结 + `RecoveryState` 恢复
- [x] **Loop Engineering**：WorkflowEngine / Journal 断点恢复 / 循环模板 / Cron 调度
- [x] **Harness Engineering**：审计、限流、指标、完整性审查 + 三大运行时管理器 + 自调控工具集
- [x] **Agent 自进化失败驱动路径**：轨迹采集 → 模式分类 → Skill 生成 → 重放评估 → 备份回滚
- [x] **Agent 自进化成功经验路径**：复杂成功识别 → 指南型沉淀 → 两阶段晋升 → 语义注入 → 降本评估与废弃
- [x] **多 Agent 协作**：Fork / SubAgent / Team（Coordinator + 邮箱 + 共享任务 + 三种 Worker 后端）
- [x] **MCP 工具动态扩展**与 **Skill 技能包体系**（含 `tool.json` 自定义工具、热重载）
- [x] **跨会话长期记忆**（四类记忆分类 + JSONL 持久化 + 会话恢复）
- [x] **Hook 生命周期钩子系统**（session / turn / tool，四类动作执行器）

### 10.2 规划中 / 待评估

- [ ] 自进化的**跨项目经验共享**：当前 Skill 与轨迹按项目 / 用户目录隔离，考虑可选的共享层与来源标注
- [ ] Skill 依赖与版本管理：Skill 之间引用、版本锁与升级迁移
- [ ] 检索增强的记忆召回（当前为 `recall.py` 的轻量召回，可评估引入向量检索）
- [ ] 更细粒度的**成本治理**：按 provider / 任务维度的 token 预算与告警
- [ ] 团队协作的持久化：跨进程 Worker 的崩溃恢复与任务重派
- [ ] 打包分发：PyPI 发布与 `pipx` 一键安装
