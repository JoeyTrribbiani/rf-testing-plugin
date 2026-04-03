# -*- coding: utf-8 -*-
"""
Robot Framework 结果解析模块
解析 output.xml 文件，提取测试结果和统计信息
"""
import xml.etree.ElementTree as ET
from typing import Dict, List, Any
from datetime import datetime


def parse_robot_output(output_file: str) -> Dict[str, Any]:
    """
    解析 Robot Framework 输出文件

    Args:
        output_file: output.xml 文件路径

    Returns:
        包含统计信息和测试结果的结构化数据
    """
    try:
        tree = ET.parse(output_file)
        root = tree.getroot()
    except Exception as e:
        return {
            "error": f"Failed to parse XML: {str(e)}",
            "statistics": {"total": 0, "passed": 0, "failed": 0, "skipped": 0},
            "tests": []
        }

    # 解析统计信息
    statistics = _parse_statistics(root)

    # 解析测试用例
    tests = _parse_tests(root)

    return {
        "statistics": statistics,
        "tests": tests,
        "suites": _parse_suites(root)
    }


def _parse_statistics(root: ET.Element) -> Dict[str, Any]:
    """解析统计信息"""
    total = 0
    passed = 0
    failed = 0
    skipped = 0
    duration = 0.0

    for stat in root.findall('.//stat'):
        status = stat.get('pass', '')
        if status == 'PASS':
            try:
                passed += int(stat.get('value', '0'))
            except (ValueError, TypeError):
                passed += 0
        elif status == 'FAIL':
            try:
                failed += int(stat.get('value', '0'))
            except (ValueError, TypeError):
                failed += 0
        elif status == 'SKIP':
            try:
                skipped += int(stat.get('value', '0'))
            except (ValueError, TypeError):
                skipped += 0

    total = passed + failed + skipped

    # 获取总耗时
    elapsed_elem = root.find('.//statistics/total/elapsedtime')
    if elapsed_elem is not None:
        try:
            duration = int(elapsed_elem.get('value', '0')) / 1000.0
        except (ValueError, TypeError):
            duration = 0.0

    return {
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "duration": duration
    }


def _parse_tests(root: ET.Element) -> List[Dict[str, Any]]:
    """解析所有测试用例"""
    tests = []

    for test in root.findall('.//test'):
        try:
            duration = int(test.get('elapsedtime', '0')) / 1000.0
        except (ValueError, TypeError):
            duration = 0.0

        test_data = {
            "name": test.get('name', ''),
            "status": test.get('status', 'UNKNOWN'),
            "duration": duration,
            "tags": [tag.get('name', '') for tag in test.findall('tag')],
            "doc": test.get('doc', ''),
            "message": ''
        }

        # 获取失败消息
        if test_data["status"] == 'FAIL':
            msg_elem = test.find('status/message')
            if msg_elem is not None:
                test_data["message"] = msg_elem.text or ''

        tests.append(test_data)

    return tests


def _parse_suites(root: ET.Element) -> List[Dict[str, Any]]:
    """解析测试套件"""
    suites = []

    for suite in root.findall('.//suite'):
        try:
            duration = int(suite.get('elapsedtime', '0')) / 1000.0
        except (ValueError, TypeError):
            duration = 0.0

        suite_data = {
            "name": suite.get('name', ''),
            "source": suite.get('source', ''),
            "status": suite.get('status', 'UNKNOWN'),
            "duration": duration
        }
        suites.append(suite_data)

    return suites