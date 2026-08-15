"""
资金流向分析模块
分析主力资金、北向资金、融资融券等
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class CapitalFlowAnalyzer:
    """资金流向分析类"""

    def __init__(self):
        pass

    def get_main_flow(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析主力资金流向

        Args:
            flow_data: 资金流向数据

        Returns:
            dict: 主力资金分析结果
        """
        if not flow_data:
            return {
                "signal": "unknown",
                "description": "无数据",
                "score": 0
            }

        main_net_inflow = flow_data.get("main_net_inflow", 0)
        main_net_inflow_pct = flow_data.get("main_net_inflow_pct", 0)

        # 判断信号
        signal = "neutral"
        description = ""
        score = 0

        if main_net_inflow > 0:
            if main_net_inflow_pct > 10:
                signal = "strong_inflow"
                description = f"主力大幅流入 {main_net_inflow/10000:.2f}亿，占比{main_net_inflow_pct:.1f}%"
                score = 2
            elif main_net_inflow_pct > 5:
                signal = "inflow"
                description = f"主力流入 {main_net_inflow/10000:.2f}亿，占比{main_net_inflow_pct:.1f}%"
                score = 1
            else:
                signal = "weak_inflow"
                description = f"主力小幅流入 {main_net_inflow/10000:.2f}亿"
                score = 0.5
        elif main_net_inflow < 0:
            if main_net_inflow_pct < -10:
                signal = "strong_outflow"
                description = f"主力大幅流出 {main_net_inflow/10000:.2f}亿，占比{abs(main_net_inflow_pct):.1f}%"
                score = -2
            elif main_net_inflow_pct < -5:
                signal = "outflow"
                description = f"主力流出 {main_net_inflow/10000:.2f}亿，占比{abs(main_net_inflow_pct):.1f}%"
                score = -1
            else:
                signal = "weak_outflow"
                description = f"主力小幅流出 {main_net_inflow/10000:.2f}亿"
                score = -0.5

        return {
            "signal": signal,
            "description": description,
            "score": score,
            "main_net_inflow": main_net_inflow,
            "main_net_inflow_pct": main_net_inflow_pct
        }

    def get_super_large_flow(self, flow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析超大单资金流向

        Args:
            flow_data: 资金流向数据

        Returns:
            dict: 超大单资金分析结果
        """
        if not flow_data:
            return {
                "signal": "unknown",
                "description": "无数据",
                "score": 0
            }

        super_large_inflow = flow_data.get("super_large_net_inflow", 0)
        super_large_inflow_pct = flow_data.get("super_large_net_inflow_pct", 0)

        signal = "neutral"
        description = ""
        score = 0

        if super_large_inflow > 0:
            if super_large_inflow_pct > 5:
                signal = "strong_inflow"
                description = f"超大单大幅流入 {super_large_inflow/10000:.2f}亿"
                score = 1.5
            else:
                signal = "inflow"
                description = f"超大单流入 {super_large_inflow/10000:.2f}亿"
                score = 0.5
        elif super_large_inflow < 0:
            if super_large_inflow_pct < -5:
                signal = "strong_outflow"
                description = f"超大单大幅流出 {super_large_inflow/10000:.2f}亿"
                score = -1.5
            else:
                signal = "outflow"
                description = f"超大单流出 {super_large_inflow/10000:.2f}亿"
                score = -0.5

        return {
            "signal": signal,
            "description": description,
            "score": score,
            "super_large_inflow": super_large_inflow,
            "super_large_inflow_pct": super_large_inflow_pct
        }

    def get_north_flow_analysis(self, north_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析北向资金流向

        Args:
            north_data: 北向资金数据

        Returns:
            dict: 北向资金分析结果
        """
        if not north_data:
            return {
                "signal": "unknown",
                "description": "无数据",
                "score": 0
            }

        north_net_flow = north_data.get("north_net_flow", 0)

        signal = "neutral"
        description = ""
        score = 0

        if north_net_flow > 0:
            if north_net_flow > 50:  # 50亿以上
                signal = "strong_inflow"
                description = f"北向资金大幅流入 {north_net_flow:.2f}亿"
                score = 2
            elif north_net_flow > 20:
                signal = "inflow"
                description = f"北向资金流入 {north_net_flow:.2f}亿"
                score = 1
            else:
                signal = "weak_inflow"
                description = f"北向资金小幅流入 {north_net_flow:.2f}亿"
                score = 0.5
        elif north_net_flow < 0:
            if north_net_flow < -50:
                signal = "strong_outflow"
                description = f"北向资金大幅流出 {north_net_flow:.2f}亿"
                score = -2
            elif north_net_flow < -20:
                signal = "outflow"
                description = f"北向资金流出 {north_net_flow:.2f}亿"
                score = -1
            else:
                signal = "weak_outflow"
                description = f"北向资金小幅流出 {north_net_flow:.2f}亿"
                score = -0.5

        return {
            "signal": signal,
            "description": description,
            "score": score,
            "north_net_flow": north_net_flow
        }

    def analyze_flow_trend(self, flow_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        分析资金流动趋势

        Args:
            flow_history: 历史资金流向数据

        Returns:
            dict: 趋势分析结果
        """
        if not flow_history or len(flow_history) < 3:
            return {
                "trend": "unknown",
                "description": "数据不足",
                "score": 0
            }

        # 提取主力资金流入数据
        inflows = [f.get("main_net_inflow", 0) for f in flow_history]

        # 计算趋势
        recent_avg = np.mean(inflows[-3:])
        earlier_avg = np.mean(inflows[:-3]) if len(inflows) > 3 else inflows[0]

        trend = "neutral"
        description = ""
        score = 0

        if recent_avg > earlier_avg * 1.2:
            trend = "increasing"
            description = "资金流入持续增加"
            score = 1
        elif recent_avg < earlier_avg * 0.8:
            trend = "decreasing"
            description = "资金流入持续减少"
            score = -1
        else:
            trend = "stable"
            description = "资金流入相对稳定"

        # 检查连续性
        if all(i > 0 for i in inflows[-3:]):
            trend = "continuous_inflow"
            description = "连续3日主力资金流入"
            score = 1.5
        elif all(i < 0 for i in inflows[-3:]):
            trend = "continuous_outflow"
            description = "连续3日主力资金流出"
            score = -1.5

        return {
            "trend": trend,
            "description": description,
            "score": score,
            "recent_avg": recent_avg,
            "earlier_avg": earlier_avg
        }

    def calculate_flow_score(self, main_flow: Dict, north_flow: Dict, flow_trend: Dict) -> float:
        """
        计算资金流向综合得分

        Args:
            main_flow: 主力资金分析
            north_flow: 北向资金分析
            flow_trend: 趋势分析

        Returns:
            float: 综合得分 (-2 到 2)
        """
        scores = []

        # 主力资金权重 50%
        if main_flow["score"] != 0:
            scores.append(main_flow["score"] * 0.5)

        # 北向资金权重 30%
        if north_flow["score"] != 0:
            scores.append(north_flow["score"] * 0.3)

        # 趋势权重 20%
        if flow_trend["score"] != 0:
            scores.append(flow_trend["score"] * 0.2)

        if scores:
            return sum(scores)
        return 0

    def generate_capital_signal(self, flow_data: Dict[str, Any], north_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成资金流向信号

        Args:
            flow_data: 资金流向数据
            north_data: 北向资金数据

        Returns:
            dict: 综合信号
        """
        # 分析主力资金
        main_flow = self.get_main_flow(flow_data)

        # 分析超大单
        super_large_flow = self.get_super_large_flow(flow_data)

        # 分析北向资金
        north_flow = self.get_north_flow_analysis(north_data)

        # 计算综合得分
        total_score = 0
        if main_flow["score"] != 0:
            total_score += main_flow["score"] * 0.6
        if super_large_flow["score"] != 0:
            total_score += super_large_flow["score"] * 0.4
        if north_flow["score"] != 0:
            total_score = (total_score + north_flow["score"] * 0.3) / 1.3 if total_score != 0 else north_flow["score"] * 0.3

        # 判断综合信号
        if total_score > 1:
            overall_signal = "strong_bullish"
            description = "资金面强烈看涨"
        elif total_score > 0.5:
            overall_signal = "bullish"
            description = "资金面看涨"
        elif total_score > 0:
            overall_signal = "weak_bullish"
            description = "资金面偏多"
        elif total_score < -1:
            overall_signal = "strong_bearish"
            description = "资金面强烈看跌"
        elif total_score < -0.5:
            overall_signal = "bearish"
            description = "资金面看跌"
        elif total_score < 0:
            overall_signal = "weak_bearish"
            description = "资金面偏空"
        else:
            overall_signal = "neutral"
            description = "资金面中性"

        return {
            "overall_signal": overall_signal,
            "total_score": total_score,
            "description": description,
            "main_flow": main_flow,
            "super_large_flow": super_large_flow,
            "north_flow": north_flow
        }


# 全局资金流向分析实例
capital_flow_analyzer = CapitalFlowAnalyzer()
