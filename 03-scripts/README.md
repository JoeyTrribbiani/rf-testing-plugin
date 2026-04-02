# 实用脚本

本目录包含 Robot Framework 测试相关的实用脚本和资源。

## 脚本列表

### robot2tapd.py

RF 用例转 TAPD Excel 格式脚本。

**用法**：
```bash
python robot2tapd.py <robot_path> \
    --excel <output_excel> \
    --dir <用例目录> \
    --sheet <工作表名称> \
    --creator <创建人> \
    --out-b64 <base64_file>
```

**参数说明**：
- `robot_path`: RF 用例文件或目录路径
- `--excel`: 输出 Excel 文件路径
- `--dir`: 用例目录（批量转换时使用）
- `--sheet`: Excel 工作表名称
- `--creator`: 创建人名称
- `--out-b64`: Base64 编码输出文件路径

### batch_convert.sh

批量转换脚本，用于转换整个目录下的 RF 用例。

**用法**：
```bash
./batch_convert.sh <robot_dir> <output_dir> <creator>
```

**参数说明**：
- `robot_dir`: RF 用例目录
- `output_dir`: 输出目录
- `creator`: 创建人名称

## 资源文件

### JLTestLibrary.zip

Robot Framework 自定义测试库，提供特定业务关键字。

**安装方式**：
```bash
# 解压到 Python site-packages 目录
unzip JLTestLibrary.zip -d "$HOME/Library/Python/3.7/site-packages/"

# 或解压到当前项目依赖目录
unzip JLTestLibrary.zip -d ./Lib/site-packages/
```

**安装验证**：
```bash
python -c "import JLTestLibrary; print('JLTestLibrary 安装成功')"
```

**说明**：
- 该库包含 JL 企业特定的测试关键字
- 提供业务相关的封装函数
- 遵循 JL Robot Framework 编写规范

## 使用示例

### 单个文件转换

```bash
python robot2tapd.py cases/商户状态变更.robot \
    --excel output/商户状态变更.xlsx \
    --sheet "测试用例" \
    --creator "测试工程师" \
    --out-b64 output/商户状态变更.b64
```

### 批量转换

```bash
./batch_convert.sh ./cases ./output "测试工程师"
```

### 安装自定义库

```bash
# 解压到 Python site-packages
unzip JLTestLibrary.zip -d "$HOME/Library/Python/3.7/site-packages/"

# 验证安装
python -c "import JLTestLibrary; print('JLTestLibrary 安装成功')"
```

## 注意事项

1. **Python 版本**：确保使用 Python 3.7.16+
2. **依赖安装**：运行脚本前确保已安装所需依赖（pandas, openpyxl）
3. **文件编码**：确保 RF 用例文件使用 UTF-8 编码
4. **目录权限**：确保对输出目录有写入权限
5. **路径格式**：Windows 系统路径请使用正斜杠或双反斜杠

## 故障排除

### 问题1：ModuleNotFoundError

**解决方案**：
```bash
pip install pandas openpyxl
```

### 问题2：UnicodeDecodeError

**解决方案**：
确保 RF 用例文件使用 UTF-8 编码：
```bash
file -i cases/用例文件.robot
```

### 问题3：权限错误

**解决方案**：
```bash
chmod +x batch_convert.sh
```

### 问题4：JLTestLibrary 导入失败

**解决方案**：
确认库已正确解压到 site-packages 目录：
```bash
ls $HOME/Library/Python/3.7/site-packages/JLTestLibrary/
```