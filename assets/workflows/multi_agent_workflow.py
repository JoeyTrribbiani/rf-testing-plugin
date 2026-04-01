# -*- coding: utf-8 -*-
"""
多 Agent 协作工作流示例

展示如何使用多 Agent 系统完成复杂的测试任务
"""

import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from app.core.agent.multi_agent import MultiAgentCoordinator, get_coordinator
from app.core.agent.protocol import (
    AgentMessage,
    MessageType,
    MessagePriority,
    TaskHandoff,
    CollaborationRequest
)
from utils.log import log


@dataclass
class WorkflowStep:
    """工作流步骤"""
    name: str
    description: str
    agent: str  # 负责此步骤的 Agent
    inputs: List[str] = field(default_factory=list)  # 输入（来自前序步骤）
    outputs: List[str] = field(default_factory=list)  # 输出（供后续步骤使用）


@dataclass
class WorkflowDefinition:
    """工作流定义"""
    name: str
    description: str
    steps: List[WorkflowStep]
    enable_parallel: bool = False  # 是否支持并行执行


# ========== 预定义工作流模板 ==========

REQUIREMENT_TO_TESTCASE_WORKFLOW = WorkflowDefinition(
    name="需求到用例",
    description="从需求分析到测试用例生成的完整流程",
    steps=[
        WorkflowStep(
            name="需求分析",
            description="解析需求文档，提取测试要点",
            agent="需求分析师",
            inputs=["requirement_document"],
            outputs=["test_points", "risks"]
        ),
        WorkflowStep(
            name="用例设计",
            description="根据测试点生成测试用例",
            agent="测试设计师",
            inputs=["test_points", "risks"],
            outputs=["test_cases", "scripts"]
        ),
        WorkflowStep(
            name="知识沉淀",
            description="将分析过程和用例沉淀为知识",
            agent="知识合成者",
            inputs=["test_points", "test_cases"],
            outputs=["knowledge_fragments"]
        )
    ],
    enable_parallel=False
)

BUG_LIFECYCLE_WORKFLOW = WorkflowDefinition(
    name="缺陷生命周期",
    description="从缺陷发现到复测通过的完整流程",
    steps=[
        WorkflowStep(
            name="缺陷分析",
            description="分析缺陷根因和影响范围",
            agent="缺陷管理者",
            inputs=["bug_report"],
            outputs=["bug_analysis"]
        ),
        WorkflowStep(
            name="创建缺陷单",
            description="在 TAPD/JIRA 创建缺陷单",
            agent="缺陷管理者",
            inputs=["bug_analysis"],
            outputs=["bug_id"]
        ),
        WorkflowStep(
            name="知识沉淀",
            description="记录缺陷处理经验",
            agent="知识合成者",
            inputs=["bug_analysis", "bug_id"],
            outputs=["knowledge_fragments"]
        )
    ],
    enable_parallel=False
)

TEST_EXECUTION_WORKFLOW = WorkflowDefinition(
    name="测试执行",
    description="执行测试用例并生成报告",
    steps=[
        WorkflowStep(
            name="用例执行",
            description="执行测试用例",
            agent="测试执行者",
            inputs=["test_cases"],
            outputs=["execution_results"]
        ),
        WorkflowStep(
            name="结果分析",
            description="分析执行结果，识别问题",
            agent="测试执行者",
            inputs=["execution_results"],
            outputs=["analysis_report"]
        )
    ],
    enable_parallel=False
)


class MultiAgentWorkflow:
    """
    多 Agent 工作流执行器
    
    执行预定义的工作流，协调多个 Agent 完成复杂任务
    """
    
    # 工作流模板注册表
    WORKFLOW_TEMPLATES = {
        "requirement_to_testcase": REQUIREMENT_TO_TESTCASE_WORKFLOW,
        "bug_lifecycle": BUG_LIFECYCLE_WORKFLOW,
        "test_execution": TEST_EXECUTION_WORKFLOW
    }
    
    def __init__(
        self,
        coordinator: Optional[MultiAgentCoordinator] = None
    ):
        """
        初始化工作流执行器
        
        Args:
            coordinator: 多 Agent 协调器
        """
        self.coordinator = coordinator or get_coordinator()
        self.execution_history: List[Dict[str, Any]] = []
        
        log.logging(
            {
                "message": "MultiAgentWorkflow 初始化完成",
                "available_workflows": list(self.WORKFLOW_TEMPLATES.keys())
            },
            level="info"
        )
    
    def list_workflows(self) -> List[Dict[str, Any]]:
        """列出所有可用的工作流"""
        return [
            {
                "id": wid,
                "name": wf.name,
                "description": wf.description,
                "steps": len(wf.steps),
                "agents": [s.agent for s in wf.steps]
            }
            for wid, wf in self.WORKFLOW_TEMPLATES.items()
        ]
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        """获取工作流定义"""
        return self.WORKFLOW_TEMPLATES.get(workflow_id)
    
    async def execute(
        self,
        workflow_id: str,
        initial_input: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行工作流
        
        Args:
            workflow_id: 工作流 ID
            initial_input: 初始输入数据
            context: 额外上下文
            
        Returns:
            执行结果
        """
        workflow = self.get_workflow(workflow_id)
        
        if not workflow:
            return {
                "success": False,
                "error": f"未找到工作流: {workflow_id}"
            }
        
        log.logging(
            {
                "message": f"开始执行工作流: {workflow.name}",
                "steps": len(workflow.steps)
            },
            level="info"
        )
        
        # 工作流状态
        step_outputs: Dict[str, Any] = dict(initial_input)
        step_results: List[Dict[str, Any]] = []
        
        for step_idx, step in enumerate(workflow.steps):
            log.logging(
                {
                    "message": f"执行步骤 {step_idx + 1}/{len(workflow.steps)}: {step.name}",
                    "agent": step.agent
                },
                level="info"
            )
            
            # 准备步骤输入
            step_input = {
                key: step_outputs.get(key)
                for key in step.inputs
                if step_outputs.get(key) is not None
            }
            
            # 构建任务描述
            task = f"{step.description}"
            if step_input:
                task += f"\n输入数据: {step_input}"
            
            # 获取并执行 Agent
            agent = self.coordinator.get_agent(step.agent)
            
            if not agent:
                step_results.append({
                    "step": step.name,
                    "success": False,
                    "error": f"Agent 未找到: {step.agent}"
                })
                continue
            
            # 执行步骤
            step_context = {**(context or {}), "step_input": step_input}
            result = await agent.process(task, step_context)
            
            # 收集输出
            for output_key in step.outputs:
                if output_key in result:
                    step_outputs[output_key] = result[output_key]
            
            step_results.append({
                "step": step.name,
                "agent": step.agent,
                "success": result.get("success", False),
                "outputs": {k: step_outputs.get(k) for k in step.outputs}
            })
            
            log.logging(
                {
                    "message": f"步骤 {step.name} 完成",
                    "success": result.get("success", False),
                    "outputs": list(step.outputs)
                },
                level="info"
            )
        
        # 整合最终结果
        final_result = {
            "success": all(r.get("success", False) for r in step_results),
            "workflow": workflow.name,
            "step_results": step_results,
            "final_outputs": {
                k: v for k, v in step_outputs.items()
                if k not in initial_input
            }
        }
        
        # 记录执行历史
        self.execution_history.append(final_result)
        
        log.logging(
            {
                "message": f"工作流 {workflow.name} 执行完成",
                "success": final_result["success"]
            },
            level="info"
        )
        
        return final_result
    
    async def execute_custom(
        self,
        steps: List[Dict[str, Any]],
        initial_input: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行自定义工作流
        
        Args:
            steps: 自定义步骤列表
            initial_input: 初始输入
            context: 额外上下文
            
        Returns:
            执行结果
        """
        workflow = WorkflowDefinition(
            name="自定义工作流",
            description="用户自定义的工作流",
            steps=[
                WorkflowStep(
                    name=s.get("name", f"步骤{i+1}"),
                    description=s.get("description", ""),
                    agent=s.get("agent", ""),
                    inputs=s.get("inputs", []),
                    outputs=s.get("outputs", [])
                )
                for i, s in enumerate(steps)
            ]
        )
        
        # 临时注册
        self.WORKFLOW_TEMPLATES["custom"] = workflow
        
        try:
            return await self.execute("custom", initial_input, context)
        finally:
            del self.WORKFLOW_TEMPLATES["custom"]


# ========== 工作流使用示例 ==========

async def example_requirement_to_testcase():
    """需求到用例工作流示例"""
    workflow = MultiAgentWorkflow()
    
    # 初始输入：需求文档
    initial_input = {
        "requirement_document": """
        用户登录功能需求：
        1. 支持用户名密码登录
        2. 支持手机验证码登录
        3. 支持第三方登录（微信、支付宝）
        4. 密码错误超过5次锁定账户
        5. 登录成功后跳转首页
        """
    }
    
    # 执行工作流
    result = await workflow.execute(
        workflow_id="requirement_to_testcase",
        initial_input=initial_input
    )
    
    print("工作流执行结果:")
    print(f"成功: {result['success']}")
    print(f"步骤结果: {result['step_results']}")
    print(f"最终输出: {result['final_outputs']}")
    
    return result


async def example_bug_lifecycle():
    """缺陷生命周期工作流示例"""
    workflow = MultiAgentWorkflow()
    
    # 初始输入：缺陷报告
    initial_input = {
        "bug_report": """
        缺陷标题：用户登录页面无法正常显示
        现象：打开登录页面时出现白屏
        环境：Chrome 120, Windows 11
        复现步骤：
        1. 打开浏览器
        2. 访问登录页面
        3. 页面显示白屏
        """
    }
    
    # 执行工作流
    result = await workflow.execute(
        workflow_id="bug_lifecycle",
        initial_input=initial_input
    )
    
    return result


async def example_custom_workflow():
    """自定义工作流示例"""
    workflow = MultiAgentWorkflow()
    
    # 自定义步骤
    custom_steps = [
        {
            "name": "需求理解",
            "description": "理解用户需求，提取关键信息",
            "agent": "需求分析师",
            "inputs": ["user_input"],
            "outputs": ["understood_requirements"]
        },
        {
            "name": "用例生成",
            "description": "根据理解的需求生成测试用例",
            "agent": "测试设计师",
            "inputs": ["understood_requirements"],
            "outputs": ["test_cases"]
        }
    ]
    
    # 执行自定义工作流
    result = await workflow.execute_custom(
        steps=custom_steps,
        initial_input={"user_input": "测试支付功能"}
    )
    
    return result


if __name__ == "__main__":
    # 运行示例
    asyncio.run(example_requirement_to_testcase())