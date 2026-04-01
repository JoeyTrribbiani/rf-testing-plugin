# Reach 多平台搜索

**Reach** 是 AI 测试平台的多平台搜索能力模块，提供统一接口访问多个搜索平台。

## 支持的平台

| 平台 | 类型 | 需求 | 状态 |
|------|------|------|------|
| **Tavily** | 搜索 | API Key | 需要配置 |
| **Exa** | 语义搜索 | mcporter | 可选 |
| **Web** | 内容获取 | 无 | 装好即用 |

## 配置方法

### Tavily 搜索

```bash
# .env 文件
TAVILY_API_KEY=your_api_key_here

# 或
WEBSEARCH_TAVILY_API_KEY=your_api_key_here
```

### Exa 语义搜索

```bash
# 1. 安装 mcporter
npm install -g mcporter

# 2. 配置 Exa MCP
mcporter config add exa https://mcp.exa.ai/mcp

# 3. 启用（.env）
WEBSEARCH_EXA_ENABLED=true
```

### Web 内容获取（Jina Reader）

```bash
# 无需配置，默认启用
WEBSEARCH_WEB_ENABLED=true
```

## 使用方法

### 在 Agent 模式中使用

```
帮我搜索 Tavily 上关于 "Robot Framework" 的最新信息
```

### 检查渠道状态

```python
from app.core.rag.reach import ReachDoctor

doctor = ReachDoctor()
report = doctor.format_report()
print(report)
```

## 扩展新渠道

创建新的 Channel 类继承 `Channel` 基类：

```python
from app.core.rag.reach.base import Channel, ChannelCheckResult, ChannelStatus

class MyChannel(Channel):
    name = "my_channel"
    description = "我的搜索渠道"
    backends = ["My API"]
    tier = 1
    supports_search = True

    def can_handle(self, url: str) -> bool:
        return False

    def check(self, config: dict = None) -> ChannelCheckResult:
        # 检查 API Key 是否配置
        return ChannelCheckResult(
            status=ChannelStatus.OK,
            message="My API 可用"
        )

    async def search(self, query: str, top_k: int = 5, **kwargs):
        # 实现搜索逻辑
        return results
```