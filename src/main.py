"""
基金研究助手 - 主程序
"""
import sys
import os
from typing import List, Dict, Any

from .config import config
from .data_fetcher import data_fetcher
from .analyzer import analyzer
from .notifier import create_notifier


def analyze_all_funds() -> List[Dict[str, Any]]:
    """
    分析所有基金

    Returns:
        list: 分析结果列表
    """
    funds = config.get_funds()
    analysis_days = config.get_analysis_days()

    if not funds:
        print("未配置基金列表")
        return []

    results = []

    for fund in funds:
        fund_code = fund["code"]
        fund_name = fund["name"]

        print(f"正在分析基金: {fund_name} ({fund_code})")

        # 获取净值数据
        nav_data = data_fetcher.get_fund_nav(fund_code, days=analysis_days)

        # 获取基金信息
        fund_info = data_fetcher.get_fund_info(fund_code)

        # 分析基金
        result = analyzer.analyze_fund(
            fund_code=fund_code,
            fund_name=fund_name,
            nav_data=nav_data,
            fund_info=fund_info
        )

        results.append(result)

        print(f"完成分析: {fund_name}")

    return results


def send_report(results: List[Dict[str, Any]]) -> bool:
    """
    发送分析报告

    Args:
        results: 分析结果

    Returns:
        bool: 是否发送成功
    """
    notifier = create_notifier()

    if not notifier.token:
        print("未配置 PushPlus Token，跳过推送")
        print("\n分析结果:")
        for result in results:
            print(f"\n{result['name']} ({result['code']})")
            if "error" in result:
                print(f"  错误: {result['error']}")
            else:
                print(f"  最新净值: {result.get('latest_nav', 0):.4f}")
                print(f"  日涨跌幅: {result.get('daily_return', 0):+.2f}%")
                print(f"  区间收益率: {result.get('total_return', 0):+.2f}%")
                print(f"  综合评级: {result.get('overall_score', 'N/A')}")
        return False

    return notifier.send_analysis_report(results)


def run_analysis():
    """运行分析"""
    print("=" * 50)
    print("基金研究助手 - 每日分析")
    print("=" * 50)

    try:
        # 分析所有基金
        results = analyze_all_funds()

        if not results:
            print("没有分析结果")
            return

        # 发送报告
        send_report(results)

        print("\n分析完成！")

    except Exception as e:
        print(f"分析过程中出现错误: {e}")

        # 尝试发送错误报告
        try:
            notifier = create_notifier()
            if notifier.token:
                notifier.send_error_report(str(e))
        except Exception as notify_error:
            print(f"发送错误报告失败: {notify_error}")


def main():
    """主函数"""
    # 检查是否是测试模式
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("测试模式")
        print(f"配置文件路径: {config.config_path}")
        print(f"基金数量: {len(config.get_funds())}")
        print(f"分析天数: {config.get_analysis_days()}")
        print(f"PushPlus Token: {'已配置' if config.get_pushplus_token() else '未配置'}")
        return

    run_analysis()


if __name__ == "__main__":
    main()
