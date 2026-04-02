#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAPD MCP Server - Model Context Protocol 服务器实现
用途：提供 TAPD API 工具接口，让 Claude 能够操作远程 TAPD
"""

import os
import sys
import json
import asyncio
from typing import Any
import requests

# MCP SDK imports
try:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.stdio import stdio_server
    from mcp.types import TextContent
except ImportError:
    print("Error: mcp package not installed. Run: pip install 'mcp[cli]'", file=sys.stderr)
    sys.exit(1)


# ==================== TAPD 配置 ====================

TAPD_API_BASE = os.getenv("TAPD_API_BASE_URL", "https://api.tapd.cn")
TAPD_BASE_URL = os.getenv("TAPD_BASE_URL", "https://www.tapd.cn")
TAPD_TOKEN = os.getenv("TAPD_ACCESS_TOKEN", "")

if not TAPD_TOKEN:
    print("Warning: TAPD_ACCESS_TOKEN not set in environment", file=sys.stderr)


# ==================== TAPD API 客户端 ====================

class TAPDClient:
    """TAPD API 客户端"""

    def __init__(self, api_token: str):
        self.api_token = api_token
        self.api_base = TAPD_API_BASE
        self.base_url = TAPD_BASE_URL

    def _request(self, method: str, endpoint: str, params: dict = None) -> dict:
        """发送 API 请求"""
        headers = {
            "Authorization": f"Basic {self.api_token}",
            "Content-Type": "application/json"
        }

        url = f"{self.api_base}{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, params=params, timeout=30)
            else:
                response = requests.request(method, url, headers=headers, json=params, timeout=30)

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"status": 1, "info": f"请求失败: {str(e)}", "data": {}}

    def get_story(self, story_id: str, workspace_id: str = None) -> dict:
        """获取需求详情"""
        endpoint = f"/stories/get"
        params = {"id": story_id}
        if workspace_id:
            params["workspace_id"] = workspace_id

        return self._request("GET", endpoint, params)

    def get_test_cases(self, story_id: str, workspace_id: str = None) -> dict:
        """获取需求的测试用例"""
        endpoint = f"/test_cases"
        params = {"story_id": story_id}
        if workspace_id:
            params["workspace_id"] = workspace_id

        return self._request("GET", endpoint, params)

    def create_test_case(self, workspace_id: str, case_data: dict) -> dict:
        """创建测试用例"""
        endpoint = f"/test_cases/add"
        params = {
            "workspace_id": workspace_id,
            **case_data
        }
        return self._request("POST", endpoint, params)

    def update_test_case(self, case_id: str, workspace_id: str, case_data: dict) -> dict:
        """更新测试用例"""
        endpoint = f"/test_cases/update"
        params = {
            "id": case_id,
            "workspace_id": workspace_id,
            **case_data
        }
        return self._request("POST", endpoint, params)

    def get_workspace_info(self, workspace_id: str) -> dict:
        """获取工作空间信息"""
        endpoint = f"/workspaces/get"
        params = {"id": workspace_id}
        return self._request("GET", endpoint, params)

    def search_stories(self, workspace_id: str, keyword: str, page: int = 1, limit: int = 20) -> dict:
        """搜索需求"""
        endpoint = f"/stories"
        params = {
            "workspace_id": workspace_id,
            "keyword": keyword,
            "page": page,
            "limit": limit
        }
        return self._request("GET", endpoint, params)


# ==================== MCP 服务器定义 ====================

mcp = FastMCP("tapd", json_response=True)

# 初始化 TAPD 客户端
tapd_client = None

if TAPD_TOKEN:
    tapd_client = TAPDClient(TAPD_TOKEN)


@mcp.tool()
def get_requirement(story_id: str, workspace_id: str = None) -> str:
    """
    获取 TAPD 需求详情

    Args:
        story_id: 需求 ID（例如：1020001234567）
        workspace_id: 工作空间 ID（可选，会从 story_id 自动推断）

    Returns:
        需求详情 JSON 字符串
    """
    if not tapd_client:
        return json.dumps({"error": "TAPD_ACCESS_TOKEN 未配置"})

    result = tapd_client.get_story(story_id, workspace_id)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_test_cases(story_id: str, workspace_id: str = None) -> str:
    """
    获取需求关联的测试用例列表

    Args:
        story_id: 需求 ID
        workspace_id: 工作空间 ID（可选）

    Returns:
        测试用例列表 JSON 字符串
    """
    if not tapd_client:
        return json.dumps({"error": "TAPD_ACCESS_TOKEN 未配置"})

    result = tapd_client.get_test_cases(story_id, workspace_id)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def create_test_case(workspace_id: str, title: str, description: str = "", priority: str = "2") -> str:
    """
    创建新的测试用例

    Args:
        workspace_id: 工作空间 ID
        title: 用例标题
        description: 用例描述
        priority: 优先级（1=高, 2=中, 3=低）

    Returns:
        创建结果 JSON 字符串
    """
    if not tapd_client:
        return json.dumps({"error": "TAPD_ACCESS_TOKEN 未配置"})

    case_data = {
        "title": title,
        "description": description,
        "priority": priority
    }

    result = tapd_client.create_test_case(workspace_id, case_data)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def update_test_case(case_id: str, workspace_id: str, title: str = None, description: str = None, priority: str = None) -> str:
    """
    更新测试用例

    Args:
        case_id: 用例 ID
        workspace_id: 工作空间 ID
        title: 新标题（可选）
        description: 新描述（可选）
        priority: 新优先级（可选）

    Returns:
        更新结果 JSON 字符串
    """
    if not tapd_client:
        return json.dumps({"error": "TAPD_ACCESS_TOKEN 未配置"})

    case_data = {}
    if title:
        case_data["title"] = title
    if description:
        case_data["description"] = description
    if priority:
        case_data["priority"] = priority

    if not case_data:
        return json.dumps({"error": "没有提供要更新的字段"})

    result = tapd_client.update_test_case(case_id, workspace_id, case_data)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def search_stories(workspace_id: str, keyword: str, page: int = 1) -> str:
    """
    搜索工作空间中的需求

    Args:
        workspace_id: 工作空间 ID
        keyword: 搜索关键词
        page: 页码（默认 1）

    Returns:
        需求列表 JSON 字符串
    """
    if not tapd_client:
        return json.dumps({"error": "TAPD_ACCESS_TOKEN 未配置"})

    result = tapd_client.search_stories(workspace_id, keyword, page)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def get_workspace_info(workspace_id: str) -> str:
    """
    获取工作空间信息

    Args:
        workspace_id: 工作空间 ID

    Returns:
        工作空间信息 JSON 字符串
    """
    if not tapd_client:
        return json.dumps({"error": "TAPD_ACCESS_TOKEN 未配置"})

    result = tapd_client.get_workspace_info(workspace_id)
    return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool()
def parse_tapd_url(tapd_url: str) -> str:
    """
    解析 TAPD URL，提取工作空间 ID 和需求 ID

    Args:
        tapd_url: TAPD 需求 URL（例如：https://www.tapd.cn/123456/prong/stories/view/1020001234567）

    Returns:
        包含 workspace_id 和 story_id 的 JSON 字符串
    """
    import re

    pattern = r"tapd\.cn/(\d+)/prong/stories/view/(\d+)"
    match = re.search(pattern, tapd_url)

    if match:
        result = {
            "workspace_id": match.group(1),
            "story_id": match.group(2),
            "url": tapd_url
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    else:
        return json.dumps({"error": "无法解析 TAPD URL", "url": tapd_url}, ensure_ascii=False)


# ==================== 主入口 ====================

async def main():
    """启动 MCP 服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await mcp.run(
            read_stream,
            write_stream,
            mcp._create_initialization_options()
        )


if __name__ == "__main__":
    # 直接运行
    import mcp.server.stdio
    mcp.server.stdio.run(mcp._mcp_server)