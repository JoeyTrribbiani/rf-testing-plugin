# -*- coding: utf-8 -*-
"""
Robot Framework 事件监听器
捕获测试执行事件并实时输出进度
"""
import sys
from typing import Any, Dict
from datetime import datetime


class RFListener:
    """Robot Framework 事件监听器"""

    def __init__(self, verbose: bool = True):
        """
        初始化监听器

        Args:
            verbose: 是否输出详细日志
        """
        self.verbose = verbose
        self.test_count = 0
        self.pass_count = 0
        self.fail_count = 0
        self.skip_count = 0
        self.start_time = None

    def start_suite(self, name: str, attrs: Dict[str, Any]) -> None:
        """测试套件开始"""
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Suite: {name}")
            print(f"{'='*60}")

    def end_suite(self, name: str, attrs: Dict[str, Any]) -> None:
        """测试套件结束"""
        if self.verbose:
            duration = attrs.get('elapsedtime', 0) / 1000
            print(f"\nSuite {name} completed in {duration:.2f}s")

    def start_test(self, name: str, attrs: Dict[str, Any]) -> None:
        """测试用例开始"""
        if self.verbose:
            print(f"\n[Test] {name} ...", end="", flush=True)

    def end_test(self, name: str, attrs: Dict[str, Any]) -> None:
        """测试用例结束"""
        self.test_count += 1
        status = attrs.get('status', 'UNKNOWN')

        if status == 'PASS':
            self.pass_count += 1
            if self.verbose:
                print(f" \033[92mPASS\033[0m ({attrs.get('elapsedtime', 0)/1000:.2f}s)")
        elif status == 'FAIL':
            self.fail_count += 1
            if self.verbose:
                print(f" \033[91mFAIL\033[0m ({attrs.get('elapsedtime', 0)/1000:.2f}s)")
                message = attrs.get('message', '')
                if message:
                    print(f"  Error: {message}")
        elif status == 'SKIP':
            self.skip_count += 1
            if self.verbose:
                print(f" \033[93mSKIP\033[0m")

    def start_keyword(self, name: str, attrs: Dict[str, Any]) -> None:
        """关键字开始"""
        pass

    def end_keyword(self, name: str, attrs: Dict[str, Any]) -> None:
        """关键字结束"""
        pass

    def log_message(self, message: Dict[str, Any]) -> None:
        """日志消息"""
        if self.verbose and message.get('level') == 'FAIL':
            print(f"  [LOG] {message.get('message', '')}")

    def close(self) -> None:
        """关闭监听器"""
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Summary: {self.pass_count} passed, {self.fail_count} failed, {self.skip_count} skipped")
            print(f"{'='*60}\n")