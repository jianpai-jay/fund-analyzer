#!/usr/bin/env python3
"""
基金研究助手 - 本地运行脚本
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.main import main, run_analysis


def print_help():
    """打印帮助信息"""
    print("""
基金研究助手 - 本地运行脚本

用法:
    python run.py [选项]

选项:
    --help, -h      显示帮助信息
    --test          测试模式，显示配置信息
    --analyze       运行分析
    --add <代码> <名称> <类型>    添加基金
    --remove <代码>              删除基金
    --list                       显示基金列表

示例:
    python run.py --test
    python run.py --analyze
    python run.py --add 110011 "易方达中小盘混合" "混合型"
    python run.py --remove 110011
    python run.py --list
    """)


def list_funds():
    """显示基金列表"""
    from src.config import config

    funds = config.get_funds()
    if not funds:
        print("未配置基金")
        return

    print("\n当前基金列表:")
    print("-" * 50)
    print(f"{'代码':<10} {'名称':<25} {'类型':<10}")
    print("-" * 50)

    for fund in funds:
        print(f"{fund['code']:<10} {fund['name']:<25} {fund['type']:<10}")

    print("-" * 50)
    print(f"共 {len(funds)} 只基金\n")


def add_fund(code: str, name: str, fund_type: str):
    """添加基金"""
    from src.config import config

    if config.add_fund(code, name, fund_type):
        print(f"成功添加基金: {name} ({code})")
    else:
        print(f"添加基金失败: {name} ({code})")


def remove_fund(code: str):
    """删除基金"""
    from src.config import config

    if config.remove_fund(code):
        print(f"成功删除基金: {code}")
    else:
        print(f"删除基金失败: {code}")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]

    if command in ("--help", "-h"):
        print_help()
    elif command == "--test":
        main()
    elif command == "--analyze":
        run_analysis()
    elif command == "--add":
        if len(sys.argv) < 5:
            print("用法: python run.py --add <代码> <名称> <类型>")
            return
        add_fund(sys.argv[2], sys.argv[3], sys.argv[4])
    elif command == "--remove":
        if len(sys.argv) < 3:
            print("用法: python run.py --remove <代码>")
            return
        remove_fund(sys.argv[2])
    elif command == "--list":
        list_funds()
    else:
        print(f"未知命令: {command}")
        print_help()


if __name__ == "__main__":
    main()
