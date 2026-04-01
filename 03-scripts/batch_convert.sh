#!/bin/bash
# 批量 RF 用例转换脚本
# 用法：./batch_convert.sh <robot_dir> <output_dir> <creator>

set -e

# 参数检查
if [ $# -lt 1 ]; then
    echo "用法: $0 <robot_dir> [output_dir] [creator]"
    echo "  robot_dir  - RF 用例文件所在目录"
    echo "  output_dir - 输出目录（默认：./output）"
    echo "  creator    - 创建人（默认：当前用户）"
    exit 1
fi

ROBOT_DIR="${1}"
OUTPUT_DIR="${2:-./output}"
CREATOR="${3:-$(whoami)}"

# 检查源目录
if [ ! -d "$ROBOT_DIR" ]; then
    echo "错误: 目录不存在: $ROBOT_DIR"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 统计变量
total=0
success=0
failed=0

echo "========================================="
echo "批量转换 RF 用例"
echo "========================================="
echo "源目录: $ROBOT_DIR"
echo "输出目录: $OUTPUT_DIR"
echo "创建人: $CREATOR"
echo "========================================="

# 查找所有 .robot 文件
while IFS= read -r -d '' robot_file; do
    total=$((total + 1))

    # 获取相对路径
    rel_path="${robot_file#$ROBOT_DIR/}"
    file_name=$(basename "$robot_file" .robot)
    output_excel="$OUTPUT_DIR/${file_name}.xlsx"
    base64_file="$OUTPUT_DIR/${file_name}.b64"

    echo ""
    echo "[$total] 处理: $rel_path"

    # 执行转换
    if python "03-scripts/robot2tapd.py" \
        "$robot_file" \
        --excel "$output_excel" \
        --creator "$CREATOR" \
        --out-b64 "$base64_file"; then
        success=$((success + 1))
        echo "  ✓ 转换成功"
    else
        failed=$((failed + 1))
        echo "  ✗ 转换失败"
    fi

done < <(find "$ROBOT_DIR" -name "*.robot" -print0)

echo ""
echo "========================================="
echo "转换完成"
echo "========================================="
echo "总计: $total"
echo "成功: $success"
echo "失败: $failed"
echo "========================================="

if [ $failed -gt 0 ]; then
    exit 1
fi