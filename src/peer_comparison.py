"""
同类基金对比模块
与同类基金进行对比分析
"""
from typing import Dict, Any, List, Optional


class PeerComparisonAnalyzer:
    """同类基金对比分析类"""

    def __init__(self):
        pass

    def analyze_peer_comparison(self, fund_data: Dict[str, Any], peer_funds: List[Dict[str, Any]], fund_code: str) -> Dict[str, Any]:
        """
        分析同类基金对比

        Args:
            fund_data: 当前基金数据
            peer_funds: 同类基金列表
            fund_code: 基金代码

        Returns:
            dict: 对比分析结果
        """
        if not peer_funds:
            return {
                "fund_code": fund_code,
                "has_data": False,
                "analysis": "无同类基金数据"
            }

        # 计算当前基金排名
        ranking = self._calculate_ranking(fund_data, peer_funds)

        # 对比各项指标
        comparison = self._compare_metrics(fund_data, peer_funds)

        # 生成对比信号
        signal = self._generate_comparison_signal(ranking, comparison)

        return {
            "fund_code": fund_code,
            "has_data": True,
            "peer_count": len(peer_funds),
            "ranking": ranking,
            "comparison": comparison,
            "signal": signal,
            "top_peers": peer_funds[:5]
        }

    def _calculate_ranking(self, fund_data: Dict[str, Any], peer_funds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算基金排名

        Args:
            fund_data: 当前基金数据
            peer_funds: 同类基金列表

        Returns:
            dict: 排名分析
        """
        fund_return = fund_data.get("total_return", 0)

        # 按收益率排序
        sorted_peers = sorted(peer_funds, key=lambda x: x.get("total_return", 0), reverse=True)

        # 计算排名
        rank = 1
        for peer in sorted_peers:
            if peer.get("total_return", 0) > fund_return:
                rank += 1
            else:
                break

        total = len(sorted_peers)
        percentile = (total - rank) / total * 100 if total > 0 else 0

        # 计算平均收益
        avg_return = sum(p.get("total_return", 0) for p in sorted_peers) / total if total > 0 else 0

        # 判断排名水平
        if percentile >= 80:
            level = "top"
            description = f"排名前{100-percentile:.0f}%，表现优秀"
            score = 0.9
        elif percentile >= 60:
            level = "above_average"
            description = f"排名中上，优于{percentile:.0f}%的同类基金"
            score = 0.7
        elif percentile >= 40:
            level = "average"
            description = "排名中等"
            score = 0.5
        elif percentile >= 20:
            level = "below_average"
            description = f"排名中下，落后于{100-percentile:.0f}%的同类基金"
            score = 0.3
        else:
            level = "bottom"
            description = f"排名垫底，落后于大部分同类基金"
            score = 0.1

        return {
            "rank": rank,
            "total": total,
            "percentile": percentile,
            "avg_return": avg_return,
            "level": level,
            "score": score,
            "description": description
        }

    def _compare_metrics(self, fund_data: Dict[str, Any], peer_funds: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        对比各项指标

        Args:
            fund_data: 当前基金数据
            peer_funds: 同类基金列表

        Returns:
            dict: 指标对比
        """
        comparisons = []

        # 对比收益率
        fund_return = fund_data.get("total_return", 0)
        peer_returns = [p.get("total_return", 0) for p in peer_funds]
        avg_return = sum(peer_returns) / len(peer_returns) if peer_returns else 0

        comparisons.append({
            "metric": "区间收益率",
            "fund_value": fund_return,
            "peer_avg": avg_return,
            "difference": fund_return - avg_return,
            "is_better": fund_return > avg_return
        })

        # 对比夏普比率
        fund_sharpe = fund_data.get("sharpe_ratio", 0)
        peer_sharpes = [p.get("sharpe_ratio", 0) for p in peer_funds]
        avg_sharpe = sum(peer_sharpes) / len(peer_sharpes) if peer_sharpes else 0

        comparisons.append({
            "metric": "夏普比率",
            "fund_value": fund_sharpe,
            "peer_avg": avg_sharpe,
            "difference": fund_sharpe - avg_sharpe,
            "is_better": fund_sharpe > avg_sharpe
        })

        # 对比最大回撤
        fund_drawdown = fund_data.get("max_drawdown", 0)
        peer_drawdowns = [p.get("max_drawdown", 0) for p in peer_funds]
        avg_drawdown = sum(peer_drawdowns) / len(peer_drawdowns) if peer_drawdowns else 0

        comparisons.append({
            "metric": "最大回撤",
            "fund_value": fund_drawdown,
            "peer_avg": avg_drawdown,
            "difference": fund_drawdown - avg_drawdown,
            "is_better": fund_drawdown < avg_drawdown  # 回撤越小越好
        })

        # 对比波动率
        fund_volatility = fund_data.get("volatility", 0)
        peer_volatilities = [p.get("volatility", 0) for p in peer_funds]
        avg_volatility = sum(peer_volatilities) / len(peer_volatilities) if peer_volatilities else 0

        comparisons.append({
            "metric": "年化波动率",
            "fund_value": fund_volatility,
            "peer_avg": avg_volatility,
            "difference": fund_volatility - avg_volatility,
            "is_better": fund_volatility < avg_volatility  # 波动率越小越好
        })

        # 计算总体优势
        better_count = sum(1 for c in comparisons if c["is_better"])
        total_count = len(comparisons)

        return {
            "details": comparisons,
            "better_count": better_count,
            "total_count": total_count,
            "advantage_ratio": better_count / total_count if total_count > 0 else 0
        }

    def _generate_comparison_signal(self, ranking: Dict, comparison: Dict) -> Dict[str, Any]:
        """
        生成对比信号

        Args:
            ranking: 排名分析
            comparison: 指标对比

        Returns:
            dict: 对比信号
        """
        # 综合得分
        total_score = (
            ranking.get("score", 0.5) * 0.6 +
            comparison.get("advantage_ratio", 0.5) * 0.4
        )

        # 判断信号
        if total_score >= 0.7:
            signal = "outperform"
            description = "明显跑赢同类基金"
        elif total_score >= 0.5:
            signal = "average"
            description = "与同类基金表现相当"
        else:
            signal = "underperform"
            description = "跑输同类基金"

        return {
            "signal": signal,
            "score": total_score,
            "description": description
        }


# 全局同类基金对比分析实例
peer_comparison_analyzer = PeerComparisonAnalyzer()
