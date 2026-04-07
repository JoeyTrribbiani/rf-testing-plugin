# Agent Skills 通用约定 (Common Conventions)

> [!IMPORTANT]
> 所有 JL-Skills 系列的 Agent 技能**必须**严格遵守本文档定义的行为规范与输出目录结构。

## 1. 统一输出目录 (Standard Output Directory)

⚠️ **重大变更 (v2.0)**：全面废弃原有的 `jl-skills/generated/` 临时中转目录机制。
所有自动生成的文档、设计图表、测试报告和变更日志，必须遵循**"按业务域就地落盘 (Domain-Driven Documentation)"**的扁平化原则，直接生成到最终的归档位置。

标准目录架构生态如下：

```text
Project_Root/
├── README.md                   # 【核心门户】适用所有人：简介与一键启动指引
├── MAINTAIN.md (或 RUNBOOK.md)   # 【新增：维护手册】适用值班/新同学：系统大纲、操作后台指引、排错指南
│
├── docs/                       # 【核心沉淀库】
│   ├── CHANGELOG.md            # 最简变更记录流水账
│   ├── ARCHITECTURE.md         # (可选) 全局性复杂架构图与防腐层决策汇总
│   │
│   ├── modules/ (或 domains/)   # 【按业务域聚集】(取代旧的 FEATURES)
│   │   ├── order/              # 例如：订单模块
│   │   │   ├── DESIGN.md       # 该具体业务的产研要求、DDD模型建模 (设计类技能生成至此)
│   │   │   └── QA.md           # 该业务特定的验收标准与测试用例 (测试/质量类技能生成至此)
│   │   └── user/
│   │
│   └── adr/                    # 【架构决策记录库】仅在真正发生"架构技术选型变更"时生成
```

**指令输出要求**:
- 当执行涉及特定业务线（如 `/design` 或 `/test`）的动作时，Agent 必须**先向用户询问模块/域的名称**（例如 `order`、`payment`）。
- 获取模块名称后，所有该域的产物直接生成并维护在 `docs/modules/{ModuleName}/` 对应文件中（如 `DESIGN.md`, `QA.md`）。

## 2. 元数据管理 (Metadata Management)

Agent 在生成任何核心文档（如 `DESIGN.md`, `MAINTAIN.md`）时，应当在 Header 或文档顶部包含如下版本追踪信息（使用 Blockquote 格式即可，保持轻量）：

```markdown
> 版本: v1.0.0 | 最后更新: YYYY-MM-DD | 责任人: [User]
```

## 3. 进度可视化与交互 (Progress Visualization)

为了让用户清晰感知当前状态，Agent 的实质性长流程回复必须遵循单步流转，并包含进度指示器。

**文本进度条 (推荐用于中间步骤)**:
```text
---
📊 进度: [======>....] 60% | 当前阶段: 领域建模 | 下一步: 测试用例生成
---
```

## 4. 状态持久化 (State Management)

由于取消了统一的 `generated` 目录，断点续传状态文件将分散到各个执行上下文中存放：

- **全局级流程状态** (如全量 `/docs` 初始化)：存放在 `jl-skills/.agent-state.json`。
- **模块级流程状态** (如单模块的 `/design` 流程)：存放在其正在生成的目录 `docs/modules/{ModuleName}/.agent-state.json`。

**说明**:
- `status`: `in_progress`, `completed`, `failed`
- 每次启动技能时，Agent 优先检查当前上下文中是否存在未完成的 `.agent-state.json`，如果存在，必须询问用户是否恢复。

---

## JL-Skills 核心依赖目录说明

`jl-skills` 本身不再用作输出仓库，全盘转为纯粹的"规则引擎"与"模板库"：

```
Project_Root/
└── jl-skills/
    ├── instructions/          # 核心大脑：各技能的运行剧本设定
    │   ├── docs/
    │   ├── analyze/
    │   ├── design/
    │   ├── review/
    │   └── ...
    ├── specs/                 # 规章制度库
    │   ├── COMMON_CONVENTIONS.md
    │   ├── DDD与可视化规范.md
    │   ├── 编码规范.md
    │   └── 架构设计规范.md
    └── templates/             # 骨架蓝图库
        ├── JL-Template-*.md
        └── ...
```
