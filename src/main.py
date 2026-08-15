"""
基金研究助手 - 增强版主程序
支持全方位分析和实时信号推送
"""
import sys
import os
import json
from typing import List, Dict, Any
from datetime import datetime

from .config import config
from .data_fetcher import data_fetcher
from .analyzer import analyzer
from .technical import technical_analyzer
from .capital_flow import capital_flow_analyzer
from .news_analyzer import news_analyzer
from .sentiment import sentiment_analyzer
from .signals import signal_generator
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

        print(f"\n{'='*50}")
        print(f"正在分析基金: {fund_name} ({fund_code})")
        print('='*50)

        # 获取净值数据
        nav_data = data_fetcher.get_fund_nav(fund_code, days=analysis_days)

        # 获取实时净值
        realtime_nav = data_fetcher.get_realtime_nav(fund_code)

        # 获取基金信息
        fund_info = data_fetcher.get_fund_info(fund_code)

        # 获取资金流向
        flow_data = data_fetcher.get_capital_flow(fund_code)

        # 获取北向资金
        north_data = data_fetcher.get_north_flow()

        # 获取新闻
        news = data_fetcher.fetch_fund_news(fund_code)

        # 获取市场情绪
        market_sentiment = data_fetcher.get_market_sentiment()

        # 进行全方位分析
        result = comprehensive_analysis(
            fund_code=fund_code,
            fund_name=fund_name,
            nav_data=nav_data,
            realtime_nav=realtime_nav,
            fund_info=fund_info,
            flow_data=flow_data,
            north_data=north_data,
            news=news,
            market_sentiment=market_sentiment
        )

        results.append(result)
        print(f"完成分析: {fund_name}")

    return results


def comprehensive_analysis(
    fund_code: str,
    fund_name: str,
    nav_data,
    realtime_nav,
    fund_info,
    flow_data,
    north_data,
    news,
    market_sentiment
) -> Dict[str, Any]:
    """
    综合分析基金

    Args:
        fund_code: 基金代码
        fund_name: 基金名称
        nav_data: 净值数据
        realtime_nav: 实时净值
        fund_info: 基金信息
        flow_data: 资金流向
        north_data: 北向资金
        news: 新闻数据
        market_sentiment: 市场情绪

    Returns:
        dict: 综合分析结果
    """
    result = {
        "code": fund_code,
        "name": fund_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # 1. 基础指标分析
    if nav_data is not None and not nav_data.empty:
        basic_metrics = analyzer.calculate_basic_metrics(nav_data)
        risk_metrics = analyzer.calculate_risk_metrics(nav_data)
        result.update(basic_metrics)
        result.update(risk_metrics)

        # 2. 技术分析
        prices = nav_data['nav']
        technical_result = technical_analyzer.generate_signals(prices)
        result["technical"] = {
            "overall_signal": technical_result["overall_signal"],
            "signal_strength": technical_result["signal_strength"],
            "description": technical_result["description"],
            "macd_signal": technical_result["macd"].get("signal"),
            "rsi_signal": technical_result["rsi"].get("signal"),
            "bollinger_signal": technical_result["bollinger"].get("signal")
        }

        # 3. 资金流向分析
        capital_result = capital_flow_analyzer.generate_capital_signal(flow_data, north_data)
        result["capital"] = {
            "overall_signal": capital_result["overall_signal"],
            "total_score": capital_result["total_score"],
            "description": capital_result["description"],
            "main_flow": capital_result["main_flow"]["description"],
            "north_flow": capital_result["north_flow"]["description"]
        }

        # 4. 新闻分析
        news_sentiment = news_analyzer.analyze_sentiment(news)
        policy_impact = news_analyzer.analyze_policy_impact(news)
        news_result = news_analyzer.generate_news_signal(news_sentiment, policy_impact)
        result["news"] = {
            "overall_signal": news_result["overall_signal"],
            "total_score": news_result["total_score"],
            "description": news_result["description"],
            "sentiment": news_sentiment["sentiment_label"],
            "policy_impact": policy_impact["overall_impact"]
        }

        # 5. 情绪分析
        if market_sentiment:
            fear_greed = sentiment_analyzer.calculate_fear_greed_index(market_sentiment)
            investor_sentiment = sentiment_analyzer.analyze_investor_sentiment({
                "subscription": 0,
                "redemption": 0,
                "retail_sentiment": 0,
                "institutional_sentiment": 0
            })
            sentiment_score = sentiment_analyzer.calculate_sentiment_score(fear_greed, investor_sentiment)
            sentiment_result = sentiment_analyzer.generate_sentiment_signal(sentiment_score)
            result["sentiment"] = {
                "overall_signal": sentiment_result["signal"],
                "score": sentiment_score,
                "description": sentiment_result["description"],
                "advice": sentiment_result["advice"],
                "fear_greed_index": fear_greed["index"],
                "fear_greed_sentiment": fear_greed["sentiment"]
            }

        # 6. 估值分析
        result["valuation"] = analyze_valuation(fund_info, basic_metrics)

        # 7. 生成综合信号
        all_analysis = {
            "technical": result.get("technical", {}),
            "capital": result.get("capital", {}),
            "sentiment": result.get("sentiment", {}),
            "news": result.get("news", {}),
            "valuation": result.get("valuation", {})
        }
        comprehensive_signal = signal_generator.generate_comprehensive_signal(all_analysis)
        result["signal"] = {
            "category": comprehensive_signal.get("signal_category"),
            "type": comprehensive_signal.get("signal_type"),
            "description": comprehensive_signal.get("description"),
            "confidence": comprehensive_signal.get("confidence"),
            "conditions": comprehensive_signal.get("conditions")
        }

        # 8. 综合评分
        result["overall_score"] = calculate_overall_score(result)

    else:
        result["error"] = "无法获取数据"

    # 添加实时净值
    if realtime_nav:
        result["realtime_nav"] = realtime_nav.get("estimated_nav")
        result["estimated_return"] = realtime_nav.get("estimated_return")

    return result


def analyze_valuation(fund_info, basic_metrics) -> Dict[str, Any]:
    """
    分析估值

    Args:
        fund_info: 基金信息
        basic_metrics: 基础指标

    Returns:
        dict: 估值分析
    """
    if not fund_info:
        return {
            "score": 0,
            "description": "无估值数据"
        }

    # 简化估值分析
    # 实际应该根据基金持仓的股票估值来计算
    return {
        "score": 0,
        "description": "估值中性"
    }


def calculate_overall_score(result: Dict) -> Dict[str, Any]:
    """
    计算综合评分

    Args:
        result: 分析结果

    Returns:
        dict: 综合评分
    """
    scores = []

    # 技术面评分
    technical = result.get("technical", {})
    if technical.get("overall_signal") == "bullish":
        scores.append(80)
    elif technical.get("overall_signal") == "bearish":
        scores.append(40)
    else:
        scores.append(60)

    # 资金面评分
    capital = result.get("capital", {})
    capital_score = capital.get("total_score", 0)
    scores.append(50 + capital_score * 25)

    # 情绪面评分
    sentiment = result.get("sentiment", {})
    sentiment_score = sentiment.get("score", 0)
    scores.append(50 - sentiment_score * 25)  # 情绪高时评分低

    # 新闻面评分
    news = result.get("news", {})
    news_score = news.get("total_score", 0)
    scores.append(50 + news_score * 25)

    # 计算平均分
    avg_score = sum(scores) / len(scores) if scores else 50

    # 判断评级
    if avg_score >= 80:
        rating = "⭐⭐⭐⭐⭐ 优秀"
    elif avg_score >= 65:
        rating = "⭐⭐⭐⭐ 良好"
    elif avg_score >= 50:
        rating = "⭐⭐⭐ 中等"
    elif avg_score >= 35:
        rating = "⭐⭐ 较差"
    else:
        rating = "⭐ 差"

    return {
        "score": avg_score,
        "rating": rating,
        "components": {
            "technical": scores[0] if len(scores) > 0 else 50,
            "capital": scores[1] if len(scores) > 1 else 50,
            "sentiment": scores[2] if len(scores) > 2 else 50,
            "news": scores[3] if len(scores) > 3 else 50
        }
    }


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
            print_result(result)
        return False

    return notifier.send_analysis_report(results)


def print_result(result: Dict):
    """打印单个基金分析结果"""
    print(f"\n{'='*50}")
    print(f"📊 {result['name']} ({result['code']})")
    print('='*50)

    if "error" in result:
        print(f"❌ 错误: {result['error']}")
        return

    # 基础指标
    print(f"\n📈 基础指标:")
    print(f"  最新净值: {result.get('latest_nav', 0):.4f}")
    print(f"  日涨跌幅: {result.get('daily_return', 0):+.2f}%")
    print(f"  区间收益率: {result.get('total_return', 0):+.2f}%")

    # 实时净值
    if result.get("realtime_nav"):
        print(f"  实时估值: {result.get('realtime_nav', 0):.4f}")
        print(f"  估算涨跌: {result.get('estimated_return', 0):+.2f}%")

    # 技术分析
    technical = result.get("technical", {})
    print(f"\n📊 技术分析: {technical.get('description', 'N/A')}")
    print(f"  MACD: {technical.get('macd_signal', 'N/A')}")
    print(f"  RSI: {technical.get('rsi_signal', 'N/A')}")
    print(f"  布林带: {technical.get('bollinger_signal', 'N/A')}")

    # 资金流向
    capital = result.get("capital", {})
    print(f"\n💰 资金流向: {capital.get('description', 'N/A')}")
    print(f"  主力资金: {capital.get('main_flow', 'N/A')}")
    print(f"  北向资金: {capital.get('north_flow', 'N/A')}")

    # 新闻分析
    news = result.get("news", {})
    print(f"\n📰 新闻分析: {news.get('description', 'N/A')}")
    print(f"  情绪: {news.get('sentiment', 'N/A')}")
    print(f"  政策影响: {news.get('policy_impact', 'N/A')}")

    # 情绪分析
    sentiment = result.get("sentiment", {})
    print(f"\n😊 情绪分析: {sentiment.get('description', 'N/A')}")
    print(f"  恐慌贪婪指数: {sentiment.get('fear_greed_index', 'N/A')}")
    print(f"  建议: {sentiment.get('advice', 'N/A')}")

    # 交易信号
    signal = result.get("signal", {})
    print(f"\n🔔 交易信号: {signal.get('description', 'N/A')}")
    print(f"  信号类型: {signal.get('type', 'N/A')}")
    print(f"  信号强度: {signal.get('confidence', 0):.0%}")
    if signal.get("conditions"):
        print(f"  触发条件: {', '.join(signal.get('conditions', []))}")

    # 综合评分
    overall = result.get("overall_score", {})
    print(f"\n⭐ 综合评分: {overall.get('rating', 'N/A')} ({overall.get('score', 0):.1f}分)")


def send_signal_alert(result: Dict) -> bool:
    """
    发送信号提醒

    Args:
        result: 分析结果

    Returns:
        bool: 是否发送成功
    """
    signal = result.get("signal", {})
    if signal.get("category") in ["buy", "sell"]:
        notifier = create_notifier()
        if notifier.token:
            return notifier.send_signal_alert(result)
    return False


def run_analysis():
    """运行分析"""
    print("=" * 60)
    print("📊 基金研究助手 - 增强版")
    print(f"⏰ 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        # 分析所有基金
        results = analyze_all_funds()

        if not results:
            print("没有分析结果")
            return

        # 发送报告
        send_report(results)

        # 检查并发送信号提醒
        for result in results:
            send_signal_alert(result)

        print("\n" + "=" * 60)
        print("✅ 分析完成！")
        print("=" * 60)

    except Exception as e:
        print(f"分析过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

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
