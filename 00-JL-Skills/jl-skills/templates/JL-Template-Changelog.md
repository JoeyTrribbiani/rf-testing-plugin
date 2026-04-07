# [{{version}}] {{summary}} 变更记录

## 📅 基本信息
- **发布日期**: {{date}}
- **关联需求**: {{requirements_link}}

## 🚀 核心变更 (What's New)
{{#each added}}
- **新增**: {{this}}
{{/each}}
{{#each changed}}
- **优化**: {{this}}
{{/each}}
{{#each fixed}}
- **修复**: {{this}}
{{/each}}

## ⚠️ 兼容性与影响 (Impact Analysis)
| 影响域 | 描述 | 应对措施 |
| :--- | :--- | :--- |
{{#each impact}}
| **{{this.area}}** | {{this.desc}} | {{this.action}} |
{{/each}}
## 🚨 应急与回滚策略 (Rollback Plan)
> 记录本次变更如果引发线上故障，应采取的快速降级或回滚方案。

1. **配置降级**: [描述可用于紧急降级的开关配置项参数]
2. **代码回滚**: [描述是否存在破坏性改动阻止直接逆向回滚代码]
3. **数据回滚**: [描述如果发生脏数据如何修数，或是否有前置脚本]

## 📝 详细需求清单
1. [P0] ...
