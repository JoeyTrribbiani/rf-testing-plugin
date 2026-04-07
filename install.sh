#!/bin/bash
# RF Testing Plugin 一键安装脚本
# 用途: 自动安装和配置 rf-testing-plugin

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 插件配置
PLUGIN_NAME="rf-testing-plugin"
PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "$1 未安装，请先安装 $1"
        exit 1
    fi
}

# 检查 Python 环境（更新）
check_python_environment() {
    log_info "检测 Python 环境..."

    # 使用 Python 检测模块
    local detection_output
    detection_output=$(python3 "$PLUGIN_DIR/03-scripts/python_detector.py" --format json 2>/dev/null)

    if [ $? -ne 0 ]; then
        log_error "Python 环境检测失败"
        return 1
    fi

    # 显示检测结果
    echo ""
    python3 "$PLUGIN_DIR/03-scripts/python_detector.py"
    echo ""

    # 获取用户选择
    read -p "请选择目标 Python 环境 [默认=1]: " choice
    choice=${choice:-1}

    # 解析选择结果
    SELECTED_ENV=$(echo "$detection_output" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if len(data) >= $choice:
    print(json.dumps(data[$choice - 1]))
else:
    print('', end='')
")

    if [ -z "$SELECTED_ENV" ]; then
        log_error "无效的选择"
        return 1
    fi

    # 提取 Python 路径
    SELECTED_PYTHON_PATH=$(echo "$SELECTED_ENV" | python3 -c "import json,sys; print(json.load(sys.stdin)['python_path'])")
    SELECTED_PYTHON_VERSION=$(echo "$SELECTED_ENV" | python3 -c "import json,sys; print(json.load(sys.stdin)['version'])")

    log_info "已选择: Python $SELECTED_PYTHON_VERSION"
    log_info "路径: $SELECTED_PYTHON_PATH"
    echo ""

    # 设置 Python 和 pip 命令
    PYTHON_CMD="$SELECTED_PYTHON_PATH"
    # conda envs: bin/pip (Linux/macOS) or Scripts/pip.exe (Windows)
    local python_dir=$(dirname "$SELECTED_PYTHON_PATH")
    if [ -f "$python_dir/pip" ]; then
        PIP_CMD="$python_dir/pip"
    elif [ -f "$python_dir/Scripts/pip.exe" ]; then
        PIP_CMD="$python_dir/Scripts/pip.exe"
    else
        PIP_CMD="pip"
    fi
}

# 安装 Python 依赖（更新）
install_python_deps() {
    log_info "安装 Python 依赖..."

    local deps=("pandas" "openpyxl")

    for dep in "${deps[@]}"; do
        if "$PIP_CMD" show "$dep" &> /dev/null; then
            log_info "$dep 已安装"
        else
            log_info "安装 $dep..."
            "$PIP_CMD" install "$dep" || {
                log_error "安装 $dep 失败"
                exit 1
            }
        fi
    done

    # 安装 Robot Framework
    if "$PIP_CMD" show "robotframework" &> /dev/null; then
        log_info "robotframework 已安装"
    else
        log_info "安装 robotframework..."
        "$PIP_CMD" install "robotframework>=3.2.2,<4.0.0" || {
            log_error "安装 robotframework 失败"
            exit 1
        }
    fi

    log_info "Python 依赖安装完成"

    # 保存 Python 环境配置
    log_info "保存 Python 环境配置..."
    python3 "$PLUGIN_DIR/03-scripts/rf_config.py" --set-python "$PYTHON_CMD" 2>/dev/null || {
        log_warn "保存 Python 配置失败"
    }
}

# 安装 JLTestLibrary（更新）
install_jltestlibrary() {
    log_info "安装 JLTestLibrary..."

    local jl_library="$PLUGIN_DIR/03-scripts/JLTestLibrary.zip"

    if [ ! -f "$jl_library" ]; then
        log_warn "JLTestLibrary.zip 不存在，跳过安装"
        return
    fi

    # 检测 site-packages 目录
    log_info "检测 site-packages 目录..."

    # 获取 site-packages 列表
    local sp_output
    sp_output=$(python3 "$PLUGIN_DIR/03-scripts/python_detector.py" --site-packages --format json --python-path "$PYTHON_CMD" 2>/dev/null)

    if [ $? -ne 0 ]; then
        log_warn "无法自动检测 site-packages 目录，请手动安装"
        log_info "手动安装命令："
        log_info "  unzip $jl_library -d \$HOME/Library/Python/3.7/site-packages/"
        return
    fi

    # 检查 JLTestLibrary 是否已安装
    local jl_installed
    jl_installed=$(echo "$sp_output" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if data.get('jl_installed') and True in data['jl_installed']:
    print('true')
else:
    print('false')
")

    if [ "$jl_installed" = "true" ]; then
        log_info "JLTestLibrary 已安装，跳过安装"
        return
    fi

    # 显示 site-packages 选项
    echo ""
    python3 "$PLUGIN_DIR/03-scripts/python_detector.py" --site-packages --python-path "$PYTHON_CMD"
    echo ""

    # 获取用户选择
    read -p "请选择目标目录 [默认=1]: " sp_choice
    sp_choice=${sp_choice:-1}

    # 解析选择的路径
    local target_dir
    target_dir=$(echo "$sp_output" | python3 -c "
import json, sys
data = json.load(sys.stdin)
paths = data.get('site_packages', [])
if len(paths) >= $sp_choice:
    print(paths[$sp_choice - 1])
")

    if [ -z "$target_dir" ]; then
        log_warn "无效的选择，跳过安装"
        return
    fi

    # 安装
    log_info "解压 JLTestLibrary 到: $target_dir"
    unzip -q "$jl_library" -d "$target_dir" || {
        log_error "解压失败，请检查权限"
        return
    }

    # 验证
    "$PYTHON_CMD" -c "import JLTestLibrary" 2>/dev/null || {
        log_error "JLTestLibrary 安装验证失败"
        return
    }

    log_info "JLTestLibrary 安装成功"
}

# 检查插件目录
verify_plugin_directory() {
    log_info "检查插件目录..."

    if [ ! -f "$PLUGIN_DIR/05-plugins/rf-testing/.mcp.json" ]; then
        log_error "插件文件未找到，请确保从插件根目录运行此脚本"
        log_info "当前目录: $PLUGIN_DIR"
        exit 1
    fi

    log_info "插件目录验证通过: $PLUGIN_DIR"
}

# 配置插件（提示 marketplace 安装）
configure_plugin() {
    log_info "===================================="
    log_info "插件已准备就绪"
    log_info "===================================="
    log_info ""
    log_info "要让 Claude Code 识别此插件，请在 Claude Code 中执行："
    log_info ""
    log_info "  /plugin marketplace add $PLUGIN_DIR"
    log_info "  /plugin install rf-testing"
    log_info ""
}

# 一键配置环境变量和 MCP
configure_env_and_mcp() {
    echo ""
    echo "========================================"
    echo "  配置环境变量和 MCP 服务器"
    echo "========================================"
    echo ""

    # 检测 Shell
    if [[ "$SHELL" == */zsh ]]; then
        SHELL_RC="$HOME/.zshrc"
    else
        SHELL_RC="$HOME/.bashrc"
    fi

    log_info "检测到 Shell 配置文件: $SHELL_RC"

    # 收集 TAPD 配置
    echo ""
    echo "[1/4] 配置 TAPD 访问令牌"
    echo "----------------------------------------"
    read -p "请输入 TAPD_ACCESS_TOKEN: " TAPD_TOKEN

    if [[ -z "$TAPD_TOKEN" ]]; then
        log_error "TAPD_ACCESS_TOKEN 不能为空"
        log_warn "可以稍后手动配置，跳过此步骤"
        read -p "是否跳过配置？(y/n): " SKIP_CONFIG
        if [[ $SKIP_CONFIG =~ ^[Yy]$ ]]; then
            return
        fi
    fi

    # 收集 GitLab 配置（可选）
    echo ""
    echo "[2/4] 配置 GitLab（可选，按 Enter 跳过）"
    echo "----------------------------------------"
    read -p "请输入 GITLAB_API_URL（默认：https://gitlab.jlpay.com/api/v4）: " GITLAB_URL
    if [[ -z "$GITLAB_URL" ]]; then
        GITLAB_URL="https://gitlab.jlpay.com/api/v4"
    fi

    read -p "请输入 GITLAB_PERSONAL_ACCESS_TOKEN（可选）: " GITLAB_TOKEN

    # 收集 GitHub 配置（可选）
    echo ""
    echo "[3/5] 配置 GitHub（可选，按 Enter 跳过）"
    echo "----------------------------------------"
    read -p "请输入 GITHUB_TOKEN（可选）: " GITHUB_TOKEN

    # 收集 YAPI 配置（可选）
    echo ""
    echo "[4/5] 配置 YAPI（可选，按 Enter 跳过）"
    echo "----------------------------------------"
    read -p "请输入 YAPI_BASE_URL（YAPI 服务器地址）: " YAPI_URL
    if [[ -n "$YAPI_URL" ]]; then
        read -p "请输入 YAPI_TOKEN（格式：projectId:token）: " YAPI_TOKEN
    fi

    # 写入环境变量到 Shell RC
    echo ""
    echo "[4/5] 写入环境变量到 $SHELL_RC..."

    # 备份原文件
    if [[ -f "$SHELL_RC" ]]; then
        cp "$SHELL_RC" "$SHELL_RC.rf-plugin-backup"
    fi

    # 移除旧配置
    sed -i.bak '/^export TAPD_ACCESS_TOKEN=/d' "$SHELL_RC" 2>/dev/null || true
    sed -i.bak '/^export GITLAB_API_URL=/d' "$SHELL_RC" 2>/dev/null || true
    sed -i.bak '/^export GITLAB_PERSONAL_ACCESS_TOKEN=/d' "$SHELL_RC" 2>/dev/null || true
    sed -i.bak '/^export GITHUB_TOKEN=/d' "$SHELL_RC" 2>/dev/null || true
    sed -i.bak '/^export YAPI_BASE_URL=/d' "$SHELL_RC" 2>/dev/null || true
    sed -i.bak '/^export YAPI_TOKEN=/d' "$SHELL_RC" 2>/dev/null || true

    # 添加新配置
    echo "" >> "$SHELL_RC"
    echo "# RF Testing Plugin 配置" >> "$SHELL_RC"
    echo "export TAPD_ACCESS_TOKEN=\"$TAPD_TOKEN\"" >> "$SHELL_RC"
    echo "export GITLAB_API_URL=\"$GITLAB_URL\"" >> "$SHELL_RC"
    if [[ -n "$GITLAB_TOKEN" ]]; then
        echo "export GITLAB_PERSONAL_ACCESS_TOKEN=\"$GITLAB_TOKEN\"" >> "$SHELL_RC"
    fi
    if [[ -n "$GITHUB_TOKEN" ]]; then
        echo "export GITHUB_TOKEN=\"$GITHUB_TOKEN\"" >> "$SHELL_RC"
    fi
    if [[ -n "$YAPI_URL" ]]; then
        echo "export YAPI_BASE_URL=\"$YAPI_URL\"" >> "$SHELL_RC"
        echo "export YAPI_TOKEN=\"$YAPI_TOKEN\"" >> "$SHELL_RC"
    fi

    # 创建 MCP 配置
    echo ""
    echo "[5/5] 配置 Claude MCP 服务器..."

    CLAUDE_CONFIG_DIR="$HOME/.claude"
    MCP_FILE="$CLAUDE_CONFIG_DIR/mcp.json"

    # 创建目录
    mkdir -p "$CLAUDE_CONFIG_DIR"

    # 构建 JSON 配置
    cat > "$MCP_FILE" << EOF
{
  "mcpServers": {
    "tapd": {
      "command": "uvx",
      "args": ["mcp-server-tapd"],
      "env": {
        "TAPD_ACCESS_TOKEN": "${TAPD_TOKEN}",
        "TAPD_API_BASE_URL": "https://api.tapd.cn",
        "TAPD_BASE_URL": "https://www.tapd.cn"
      }
EOF

    # 添加 GitLab 服务器（如果配置了）
    if [[ -n "$GITLAB_TOKEN" ]]; then
        cat >> "$MCP_FILE" << EOF
,
    "gitlab": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gitlab"],
      "env": {
        "GITLAB_API_URL": "${GITLAB_URL}",
        "GITLAB_PERSONAL_ACCESS_TOKEN": "${GITLAB_TOKEN}"
      }
    }
EOF
    fi

    # 添加 GitHub 服务器（如果配置了）
    if [[ -n "$GITHUB_TOKEN" ]]; then
        cat >> "$MCP_FILE" << EOF
,
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
EOF
    fi

    # 添加 YAPI 服务器（如果配置了）
    if [[ -n "$YAPI_URL" ]]; then
        cat >> "$MCP_FILE" << EOF
,
    "yapi-auto-mcp": {
      "command": "npx",
      "args": ["-y", "yapi-auto-mcp", "--stdio"]
    }
EOF
    fi

    cat >> "$MCP_FILE" << EOF
  }
}
EOF

    # 验证配置
    echo ""
    echo "========================================"
    echo "[验证] 配置完成"
    echo "========================================"
    echo ""
    log_info "环境变量已写入: $SHELL_RC"
    log_info "MCP 配置已写入: $MCP_FILE"
    echo ""
    log_warn "配置的 MCP 服务器:"
    echo "  - tapd (TAPD 需求管理)"
    if [[ -n "$GITLAB_TOKEN" ]]; then
        echo "  - gitlab (GitLab 代码管理)"
    else
        echo "  - gitlab (未配置)"
    fi
    if [[ -n "$GITHUB_TOKEN" ]]; then
        echo "  - github (GitHub 代码管理)"
    else
        echo "  - github (未配置)"
    fi
    if [[ -n "$YAPI_URL" ]]; then
        echo "  - yapi-auto-mcp (YAPI 接口文档)"
    else
        echo "  - yapi-auto-mcp (未配置)"
    fi
    echo ""
    log_warn "[重要] 请执行以下命令使配置生效:"
    echo ""
    if [[ "$SHELL" == */zsh ]]; then
        echo "  source ~/.zshrc"
    else
        echo "  source ~/.bashrc"
    fi
    echo ""
    log_warn "或重启终端窗口。"
    echo ""
}

# 验证安装（更新）
verify_installation() {
    log_info "验证安装..."

    # 检查插件文件
    local plugin_files=(
        "$PLUGIN_DIR/05-plugins/rf-testing/.mcp.json"
        "$PLUGIN_DIR/05-plugins/rf-testing/.claude-plugin/plugin.json"
        "$PLUGIN_DIR/05-plugins/rf-testing/commands/start.md"
    )

    for plugin_file in "${plugin_files[@]}"; do
        if [ -f "$plugin_file" ]; then
            log_info "✓ $(basename $plugin_file)"
        else
            log_warn "✗ 插件文件不存在: $plugin_file"
        fi
    done

    # 检查 Python 依赖（使用检测到的 Python）
    "$PYTHON_CMD" -c "import pandas, openpyxl, robot" 2>/dev/null || {
        log_error "Python 依赖验证失败"
        return 1
    }

    log_info "✓ Python 依赖验证通过"

    return 0
}

# 打印使用说明
print_usage() {
    echo ""
    echo "=================================="
    echo "  安装完成！"
    echo "=================================="
    echo ""
    echo "插件路径: $PLUGIN_DIR"
    echo ""
    echo "推荐安装方式（marketplace）:"
    echo "  1. 进入插件目录:"
    echo "     cd $PLUGIN_DIR"
    echo "  2. 在 Claude Code 中执行:"
    echo "     /plugin marketplace add ."
    echo "     /plugin install rf-testing"
    echo ""
    echo "可用命令:"
    echo "  /rf-testing:start [tapd-link]  - 完整测试流程"
    echo ""
    echo "子工作流:"
    echo "  /rf-testing:requirement-to-rf  - 仅需求转用例"
    echo "  /rf-testing:rf-to-tapd       - 仅 RF 转 TAPD"
    echo ""
    echo "环境变量配置:"
    echo "  TAPD_ACCESS_TOKEN=your-tapd-token (必需)"
    echo "  GITLAB_API_URL=https://gitlab.example.com/api/v4 (可选)"
    echo "  GITLAB_PERSONAL_ACCESS_TOKEN=your-gitlab-token (可选)"
    echo "  GITHUB_TOKEN=your-github-token (可选)"
    echo "  YAPI_BASE_URL=https://yapi.example.com (可选)"
    echo "  YAPI_TOKEN=projectId:token (可选)"
    echo ""
    echo "使用方式:"
    echo "  1. 配置环境变量"
    echo "  2. 重启 Claude Code"
    echo "  3. 执行: /rf-testing:start"
    echo ""
    echo "注意事项:"
    echo "  - 确保 TAPD_ACCESS_TOKEN 已配置"
    echo "  - 首次使用需要提供 TAPD 需求链接"
    echo "  - RF 质量保证 Agent 会自动检查用例质量"
    echo ""
}

# 主流程（更新）
main() {
    log_info "开始安装 $PLUGIN_NAME..."

    # 检查环境
    check_command git
    check_python_environment  # 替换原有的 python3/pip3 检查

    # 安装步骤
    verify_plugin_directory
    install_python_deps
    configure_plugin
    install_jltestlibrary

    # 询问是否配置环境变量和 MCP
    echo ""
    read -p "是否现在配置环境变量和 MCP 服务器？(y/n): " DO_CONFIG
    if [[ $DO_CONFIG =~ ^[Yy]$ ]]; then
        configure_env_and_mcp
    fi

    # 验证
    if verify_installation; then
        print_usage
        log_info "安装成功！"
    else
        log_error "安装验证失败，请检查上述错误"
        exit 1
    fi
}

# 执行主流程
main