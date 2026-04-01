# -*- coding: utf-8 -*-
"""
工作流模块

提供预定义的工作流模板和执行引擎
"""

from assets.workflows.multi_agent_workflow import (
    MultiAgentWorkflow,
    WorkflowDefinition,
    WorkflowStep,
    REQUIREMENT_TO_TESTCASE_WORKFLOW,
    BUG_LIFECYCLE_WORKFLOW,
    TEST_EXECUTION_WORKFLOW
)

__all__ = [
    "MultiAgentWorkflow",
    "WorkflowDefinition",
    "WorkflowStep",
    "REQUIREMENT_TO_TESTCASE_WORKFLOW",
    "BUG_LIFECYCLE_WORKFLOW",
    "TEST_EXECUTION_WORKFLOW"
]