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
PLUGIN_REPO="https://github.com/JoeyTrribbiani/rf-testing-plugin.git"
PLUGIN_DIR="$HOME/.claude/plugins/$PLUGIN_NAME"

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

# 检查 Python 版本
check_python_version() {
    local python_version=$(python3 --version 2>&1 | awk '{print $2}')
    local major=$(echo $python_version | cut -d. -f1)
    local minor=$(echo $python_version | cut -d. -f2)

    if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 7 ]); then
        log_error "Python 版本需要 3.7.16+，当前版本: $python_version"
        exit 1
    fi

    log_info "Python 版本检查通过: $python_version"
}

# 安装 Python 依赖
install_python_deps() {
    log_info "安装 Python 依赖..."

    local deps=("pandas" "openpyxl")

    for dep in "${deps[@]}"; do
        if pip3 show "$dep" &> /dev/null; then
            log_info "$dep 已安装"
        else
            log_info "安装 $dep..."
            pip3 install "$dep" || {
                log_error "安装 $dep 失败"
                exit 1
            }
        fi
    done

    log_info "基础依赖安装完成"
}

# 安装 Robot Framework
install_robotframework() {
    log_info "检查 Robot Framework..."

    local rf_version="3.2.2"
    if pip3 show "robotframework" &> /dev/null; then
        log_info "robotframework 已安装"
    else
        log_info "安装 robotframework>=3.2.2,<4.0.0..."
        pip3 install "robotframework>=3.2.2,<4.0.0" || {
            log_error "安装 robotframework 失败"
            exit 1
        }
    fi

    log_info "Robot Framework 安装完成: $rf_version"
}

# 安装自定义库
install_custom_library() {
    log_info "安装自定义库..."
    log_warn "自定义库需要从私有 PyPI 安装"
    log.info "请确认以下信息："
    log_warn "  - 镜像地址: https://nexus.jlpay.com/repository/local-pypi/simple"
    log_warn "  - 信任主机: nexus.jlpay.com"
    log_warn "  - 版本号: 需要确认（当前为 0.0.1.dev50+ge870d58）"
    log.warn ""
    log_warn "安装命令（请根据实际情况确认版本号）："
    log_warn "  pip install robotframework-jljltestlibrary==0.0.1.dev50+ge870d58 -U -i https://nexus.jlpay.com/repository/local-pypi/simple --trusted-host nexus.jlpay.com"

    # 询问用户是否安装
    read -p "是否继续安装自定义库？(y/n) " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "跳过自定义库安装"
        return
    fi

    # 安装自定义库
    pip3 install robotframework-jljltestlibrary==0.0.1.dev50+ge870d58 -U -i https://nexus.jlpay.com/repository/local-pypi/simple --trusted-host nexus.jlpay.com || {
        log_error "自定义库安装失败"
        log_warn "请检查："
        log_warn "  1. 网络连接和镜像地址"
        log_warn "  2. 版本号是否正确"
        log_warn "  3. Python 版本是否兼容"
        log_warn "  4. 是否有权限访问私有 PyPI"
        return 1
    }

    log_info "自定义库安装成功"
}

# 克隆插件仓库
clone_plugin() {
    log_info "克隆插件仓库..."

    if [ -d "$PLUGIN_DIR" ]; then
        log_warn "插件目录已存在: $PLUGIN_DIR"
        read -p "是否删除并重新克隆？(y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$PLUGIN_DIR"
        else
            log_info "跳过克隆步骤"
            return
        fi
    fi

    mkdir -p "$(dirname "$PLUGIN_DIR")"
    git clone "$PLUGIN_REPO" "$PLUGIN_DIR" || {
        log_error "克隆失败，请检查网络连接和仓库地址"
        exit 1
    }

    log_info "插件克隆完成: $PLUGIN_DIR"
}

# 配置 Claude Skills
configure_skills() {
    log_info "配置 Claude Skills..."

    local settings_file="$HOME/.claude/settings.json"
    local temp_file=$(mktemp)

    # 技能配置
    local skill_config='{
        "name": "rf-test",
        "path": "'"$PLUGIN_DIR"'/01-RF-Skills/skills/test/SKILL.md"
    },
    {
        "name": "rf-standards-check",
        "path": "'"$PLUGIN_DIR"'/01-RF-Skills/skills/rf-standards-check/SKILL.md"
    },
    {
        "name": "rf-tapd-conversion",
        "path": "'"$PLUGIN_DIR"'/01-RF-Skills/skills/tapd-conversion/SKILL.md"
    }'

    # 处理 settings.json
    if [ -f "$settings_file" ]; then
        # 检查是否已有 skills 配置
        if grep -q '"skills"' "$settings_file"; then
            log_warn "settings.json 中已有 skills 配置"
            log_warn "请手动添加以下技能配置到 settings.json 的 skills 数组中："
            echo ""
            echo "$skill_config"
            echo ""
            log_warn "配置后请重启 Claude Code"
        else
            # 创建包含 skills 的新配置
            python3 -c "
import json

with open('$settings_file', 'r', encoding='utf-8') as f:
    settings = json.load(f)

settings['skills'] = [
    {
        'name': 'rf-test',
        'path': '$PLUGIN_DIR/01-RF-Skills/skills/test/SKILL.md'
    },
    {
        'name': 'rf-standards-check',
        'path': '$PLUGIN_DIR/01-RF-Skills/skills/rf-standards-check/SKILL.md'
    },
    {
        'name': 'rf-tapd-conversion',
        'path': '$PLUGIN_DIR/01-RF-Skills/skills/tapd-conversion/SKILL.md'
    }
]

with open('$settings_file', 'w', encoding='utf-8') as f:
    json.dump(settings, f, ensure_ascii=False, indent=2)
"
            log_info "Skills 配置已添加到 settings.json"
        fi
    else
        # 创建新的 settings.json
        cat > "$settings_file" << EOF
{
  "skills": [
    {
      "name": "rf-test",
      "path": "$PLUGIN_DIR/01-RF-Skills/skills/test/SKILL.md"
    },
    {
      "name": "rf-standards-check",
      "path": "$PLUGIN_DIR/01-RF-Skills/skills/rf-standards-check/SKILL.md"
    },
    {
      "name": "rf-tapd-conversion",
      "path": "$PLUGIN_DIR/01-RF-Skills/skills/tapd-conversion/SKILL.md"
    }
  ]
}
EOF
        log_info "settings.json 已创建"
    fi
}

# 验证安装
verify_installation() {
    log_info "验证安装..."

    # 检查插件目录
    if [ ! -d "$PLUGIN_DIR" ]; then
        log_error "插件目录不存在: $PLUGIN_DIR"
        return 1
    fi

    # 检查技能文件
    local skill_files=(
        "$PLUGIN_DIR/01-RF-Skills/skills/test/SKILL.md"
        "$PLUGIN_DIR/01-RF-Skills/skills/rf-standards-check/SKILL.md"
        "$PLUGIN_DIR/01-RF-Skills/skills/tapd-conversion/SKILL.md"
    )

    for skill_file in "${skill_files[@]}"; do
        if [ -f "$skill_file" ]; then
            log_info "✓ $(basename $(dirname $skill_file))"
        else
            log_error "✗ 技能文件不存在: $skill_file"
            return 1
        fi
    done

    # 检查 Python 依赖
    python3 -c "import pandas, openpyxl, robotframework" 2>/dev/null || {
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
    echo "可用技能:"
    echo "  /rf-test              - 完整测试流程"
    echo "  /rf-standards-check   - RF 规范检查"
    echo "  /rf-tapd-conversion   - RF 转 TAPD"
    echo ""
    echo "使用方式:"
    echo "  1. 重启 Claude Code"
    echo "  2. 在对话框中输入技能命令"
    echo ""
    echo "注意事项:"
    echo "  - 确保 TAPD MCP Server 已配置"
    echo "  - 首次使用需要提供 TAPD 需求链接"
    echo ""
}

# 主流程
main() {
    log_info "开始安装 $PLUGIN_NAME..."

    # 检查环境
    check_command python3
    check_command pip3
    check_command git
    check_python_version

    # 安装步骤
    install_python_deps
    clone_plugin
    configure_skills

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