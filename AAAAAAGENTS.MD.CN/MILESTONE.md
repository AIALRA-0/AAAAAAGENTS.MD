---
last_updated: 2026-03-08-23-17
---

# MILESTONE

## TEMPLATE
```yaml
{
  "milestones": [
    {
      "id": "MS-TYPE-NUM",
      "title": "里程碑标题",
      "prerequisites": [],
      "postnodes": [],
      "why": [
        "为什么要做1",
        "为什么要做2",
        ……
      ],
      "what": [
        "要做什么1",
        "要做什么2",
        ……
      ],
      "how": [
        "怎么做1",
        "怎么做2",
        ……
      ],
      "verify": [
        "如何验证1",
        "如何验证2",
        ……
      ],
      "ddl": "YYYY-MM-DD",
      "status": "unfinished",
      "notes": [
        "补充说明1",
        "补充说明2",
        ……
      ],
      "updated_at": "YYYY-MM-DD-HH-MM"
    }
  ],
  "layout": {
    "positions": {}
  }
}
```

## DATA
```yaml
{
  "milestones": [
    {
      "id": "MS-INIT-001",
      "title": "初始化通用项目骨架",
      "prerequisites": [],
      "postnodes": [],
      "why": [
        "建立统一的 AGENTS 协作规则与基础工程结构，让所有参与者在同一规范下工作",
        "减少未来新增任务或模块时因流程理解不同而产生的执行偏差，降低协作摩擦",
        "让项目关键规则可以被追溯、自动校验，并具备清晰的审计能力",
        "通过脚本化工具自动检查项目状态，减少依赖口头约定带来的隐性风险",
        "为后续扩展新的标准文件或模块提供稳定且兼容的初始化基础"
      ],
      "what": [
        "建立 AGENTS、BACKGROUND、MILESTONE、CHANGE、TREE 五类核心文档的最小可用模板",
        "打通 tree、baseline_refresh、verify_rules 三个核心脚本，使其形成完整执行流程",
        "实现本地可视化工作台的基础能力，支持文档读取、编辑、保存与预览",
        "建立项目目录结构与文件树的自动索引机制，保证 TREE 文件与真实目录保持同步",
        "初始化项目第一份基线文件以及终检状态文件，为后续校验提供参考基准"
      ],
      "how": [
        "先按照约束模板定义各类文档字段结构，再填充最小可执行示例数据",
        "执行 tree sync 生成项目 TREE 文件，记录当前目录结构",
        "执行 baseline_refresh 生成项目基线，用于未来变更对比",
        "在可视化页面测试文档读取、编辑、保存与预览流程是否完整可用",
        "运行 finalize 执行规则校验，并自动修复所有可修复问题",
        "回放完整初始化流程，并将初始化阶段结果记录到 CHANGE 文件中"
      ],
      "verify": [
        "运行 python agents_tools/tree.py sync 后脚本执行成功，无报错",
        "运行 python agents_tools/baseline_refresh.py 后返回 status=ok",
        "运行 python agents_tools/verify_rules.py finalize --json 后返回 status=ok",
        "可视化页面能够正确加载并展示 MILESTONE、CHANGE、TREE 三类核心文档",
        "TREE 文件中新增节点均包含非空 note 字段，且结构与真实目录保持一致"
      ],
      "ddl": "2026-03-10",
      "status": "done",
      "notes": [
        "当前里程碑仅用于完成通用项目初始化阶段",
        "在新增新的里程碑之前，需要确认模板字段与规则校验逻辑保持一致",
        "如果修改只读约束文件，需要先执行 baseline_refresh 更新基线",
        "初始化完成后，可以基于该节点继续扩展新的业务里程碑",
        "本节点将作为后续流程图生成与规则校验的参考起点"
      ],
      "updated_at": "2026-03-08-23-17"
    }
  ],
  "layout": {
    "positions": {}
  }
}
```
