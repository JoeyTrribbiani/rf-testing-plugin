<!--
 * @Author: Joey Xu
 * @Date: 2026-02-04 08:39:13
 * @FilePath: \\merch-services\\README_robot2excel_tapd_base64.md
-->
# robot2excel_tapd_base64 用法说明

将 Robot Framework 用例的 `[Documentation]` 按【预置条件】【操作步骤】【预期结果】解析，生成 TAPD 通用模板可识别的 Excel，并输出 base64 字符串。

## 依赖

- Python 3
- `pandas`、`openpyxl`

安装：`pip install pandas openpyxl`

## [Documentation] 格式要求

用例的 `[Documentation]` 需为**一行**、**三段式**，与项目规则一致：

```
[Documentation]    【预置条件】<描述> 【操作步骤】<描述> 【预期结果】<描述>
```

- **预置条件**：执行前需满足的条件  
- **操作步骤**：用业务语言描述做了什么（不要写接口/关键字流水账）  
- **预期结果**：执行后应达到的结果  

缺段时对应 Excel 列为空；若整条仅为占位「【预置条件】【操作步骤】【预期结果】」则跳过不导出。

## 命令格式

```bash
python robot2excel_tapd_base64.py <robot路径> [选项]
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `robot_path` | .robot 文件路径（必填） | - |
| `--excel` / `-e` | 输出 Excel 文件路径 | 自动化用例导出.xlsx |
| `--dir` / `-d` | 用例目录（Excel 列「用例目录」）；不传则**按路径自动生成** | 见下 |
| `--sheet` / `-s` | Excel 工作表名称 | 项目池测试用例导入模板 |
| `--creator` / `-c` | 创建人 | CURSOR |
| `--out-b64` / `-b` | 将 base64 字符串写入该 .txt 文件 | 不写文件 |

**默认用例目录**（不传 `--dir` 时）：根据 robot 路径生成，规则为  
- 路径中的 **V4.0** 用方括号包起来：`[V4.0]`  
- 各段（目录 + 文件名去掉 .robot）用 **" - "**（空格-空格）连接  

例如：`V4.0商户系统/业务接入层/商户变更/身份信息变更.robot` → `[V4.0]商户系统 - 业务接入层 - 商户变更 - 身份信息变更`。

## 示例

```bash
# 仅指定 robot 文件；用例目录自动为 [V4.0]商户系统 - 业务接入层 - 商户变更 - 身份信息变更
python robot2excel_tapd_base64.py "V4.0商户系统-业务接入层-商户变更-身份信息变更.robot"

# 自定义用例目录、Excel、sheet，并保存 base64 到文件
python robot2excel_tapd_base64.py "存量业务-商户系统-查询-存量业务-商户系统-查询-商户查询服务.robot" --excel 商户查询用例导出.xlsx --dir "存量业务 - 商户系统 - 查询" --sheet "商户查询测试用例" --out-b64 商户查询_base64.txt
```

## 输出

- 生成 Excel，列顺序：用例目录、用例名称、需求ID、前置条件、用例步骤、预期结果、用例类型、用例状态、用例等级、创建人、是否自动化、实现自动化、计划自动化  
- 控制台打印 Excel 的 base64 字符串；若指定 `--out-b64`，则同时写入该 .txt 文件  

## 注意事项

- 仅解析**单行** `[Documentation]`，多行续写不会合并  
- Excel 工作表名称最多 31 个字符，脚本会自动截断  
- 若 .robot 路径或输出路径含空格，请用引号包裹
