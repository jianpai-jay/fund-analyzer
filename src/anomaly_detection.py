"""
异常检测模块
检测大额赎回、经理变更等异常事件
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class AnomalyDetector:
    """异常检测类"""

    def __init__(self):
        # 异常检测阈值
        self.thresholds = {
            "large_redemption": 0.1,      # 大额赎回阈值(净赎回比例)
            "nav_deviation": 0.03,        # 净值偏离阈值(3%)
            "volume_spike": 2.0,          # 成交量飙升阈值(2倍)
            "concentration_change": 0.2,  # 持仓集中度变化阈值(20%)
            "manager_change_days": 90     # 经理变更关注期(天)
        }

    def detect_large_redemption(self, fund_flow_data: Dict = None) -> Dict[str, Any]:
        """
        检测大额赎回

        Args:
            fund_flow_data: 基金 flow 数据

        Returns:
            dict: 大额赎回检测结果
        """
        # 模拟数据
        # 实际应接入基金 flow 数据
        has_anomaly = False
        anomaly_type = None
        description = ""
        risk_level = "low"

        if fund_flow_data:
            # 分析净赎回比例
            net_redemption = fund_flow_data.get("net_redemption", 0)
            if abs(net_redemption) > self.thresholds["large_redemption"]:
                has_anomaly = True
                anomaly_type = "large_redemption"
                risk_level = "high" if net_redemption < -0.15 else "medium"
                description = f"检测到大额赎回，净赎回比例{net_redemption*100:.1f}%"
        else:
            # 模拟无异常
            description = "暂未检测到大额赎回"

        return {
            "has_anomaly": has_anomaly,
            "anomaly_type": anomaly_type,
            "risk_level": risk_level,
            "description": description,
            "advice": "关注基金规模变化，大额赎回可能导致净值波动" if has_anomaly else "暂无风险"
        }

    def detect_nav_deviation(self, nav_data: pd.DataFrame, fund_code: str = None) -> Dict[str, Any]:
        """
        检测净值异常偏离

        Args:
            nav_data: 净值数据
            fund_code: 基金代码

        Returns:
            dict: 净值偏离检测结果
        """
        if nav_data is None or nav_data.empty or len(nav_data) < 5:
            return {
                "has_anomaly": False,
                "description": "数据不足，无法检测"
            }

        # 计算日收益率
        returns = nav_data['nav'].pct_change().dropna()

        # 检测异常收益
        mean_return = returns.mean()
        std_return = returns.std()
        latest_return = returns.iloc[-1]

        # Z-score 检测
        if std_return > 0:
            z_score = (latest_return - mean_return) / std_return
        else:
            z_score = 0

        has_anomaly = abs(z_score) > 2  # 超过2个标准差
        anomaly_type = None
        description = ""
        risk_level = "low"

        if has_anomaly:
            if z_score > 0:
                anomaly_type = "nav_surge"
                description = f"净值异常上涨，偏离度{z_score:.2f}个标准差"
                risk_level = "medium"
            else:
                anomaly_type = "nav_drop"
                description = f"净值异常下跌，偏离度{abs(z_score):.2f}个标准差"
                risk_level = "high"
        else:
            description = f"净值波动正常，偏离度{z_score:.2f}个标准差"

        return {
            "has_anomaly": has_anomaly,
            "anomaly_type": anomaly_type,
            "z_score": round(z_score, 2),
            "risk_level": risk_level,
            "description": description,
            "advice": "关注基金持仓变化，可能存在重大事件" if has_anomaly else "净值波动正常"
        }

    def detect_volume_spike(self, volume_data: pd.Series = None) -> Dict[str, Any]:
        """
        检测成交量异常

        Args:
            volume_data: 成交量数据

        Returns:
            dict: 成交量异常检测结果
        """
        if volume_data is None or len(volume_data) < 10:
            return {
                "has_anomaly": False,
                "description": "数据不足，无法检测"
            }

        # 计算均量
        mean_volume = volume_data.mean()
        latest_volume = volume_data.iloc[-1]

        # 计算量比
        volume_ratio = latest_volume / mean_volume if mean_volume > 0 else 1

        has_anomaly = volume_ratio > self.thresholds["volume_spike"]
        anomaly_type = None
        description = ""
        risk_level = "low"

        if has_anomaly:
            anomaly_type = "volume_spike"
            description = f"成交量异常放大，量比{volume_ratio:.1f}"
            risk_level = "medium"
        elif volume_ratio < 0.5:
            description = f"成交量明显萎缩，量比{volume_ratio:.1f}"
            risk_level = "low"
        else:
            description = f"成交量正常，量比{volume_ratio:.1f}"

        return {
            "has_anomaly": has_anomaly,
            "anomaly_type": anomaly_type,
            "volume_ratio": round(volume_ratio, 2),
            "risk_level": risk_level,
            "description": description,
            "advice": "关注是否有重大消息或资金异动" if has_anomaly else "成交正常"
        }

    def detect_manager_change(self, manager_info: Dict = None) -> Dict[str, Any]:
        """
        检测基金经理变更

        Args:
            manager_info: 基金经理信息

        Returns:
            dict: 经理变更检测结果
        """
        has_anomaly = False
        anomaly_type = None
        description = ""
        risk_level = "low"

        if manager_info:
            # 检查任职时间
            start_date = manager_info.get("start_date")
            if start_date:
                try:
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    days_in_position = (datetime.now() - start_dt).days

                    if days_in_position < self.thresholds["manager_change_days"]:
                        has_anomaly = True
                        anomaly_type = "new_manager"
                        risk_level = "medium"
                        description = f"新任经理，任职仅{days_in_position}天"
                    else:
                        description = f"经理任职{days_in_position}天，经验丰富"
                except:
                    description = "无法解析经理任职时间"
            else:
                description = "暂无经理任职时间信息"

            # 检查经理历史业绩
            historical_performance = manager_info.get("historical_performance", {})
            if historical_performance:
                avg_return = historical_performance.get("avg_return", 0)
                if avg_return < 0:
                    description += f"，历史平均收益{avg_return:.1f}%，表现一般"
        else:
            description = "暂无基金经理信息"

        return {
            "has_anomaly": has_anomaly,
            "anomaly_type": anomaly_type,
            "risk_level": risk_level,
            "description": description,
            "advice": "关注新任经理的投资策略和业绩" if has_anomaly else "经理情况正常"
        }

    def detect_concentration_change(self, holdings_data: Dict = None) -> Dict[str, Any]:
        """
        检测持仓集中度变化

        Args:
            holdings_data: 持仓数据

        Returns:
            dict: 持仓集中度变化检测结果
        """
        has_anomaly = False
        anomaly_type = None
        description = ""
        risk_level = "low"

        if holdings_data:
            # 检查前十大持仓占比
            top10_ratio = holdings_data.get("top10_ratio", 0)
            if top10_ratio > 70:
                has_anomaly = True
                anomaly_type = "high_concentration"
                risk_level = "medium"
                description = f"持仓高度集中，前十大占比{top10_ratio:.1f}%"
            elif top10_ratio > 50:
                description = f"持仓较集中，前十大占比{top10_ratio:.1f}%"
            else:
                description = f"持仓分散，前十大占比{top10_ratio:.1f}%"

            # 检查行业集中度
            industry_concentration = holdings_data.get("industry_concentration", {})
            if industry_concentration:
                max_industry = industry_concentration.get("max_ratio", 0)
                if max_industry > 40:
                    description += f"，单一行业占比{max_industry:.1f}%，行业风险较高"
        else:
            description = "暂无持仓数据"

        return {
            "has_anomaly": has_anomaly,
            "anomaly_type": anomaly_type,
            "risk_level": risk_level,
            "description": description,
            "advice": "持仓集中度较高，注意分散风险" if has_anomaly else "持仓分散度正常"
        }

    def detect_all_anomalies(self, fund_data: Dict) -> Dict[str, Any]:
        """
        综合异常检测

        Args:
            fund_data: 基金数据

        Returns:
            dict: 综合异常检测结果
        """
        anomalies = []

        # 大额赎回检测
        redemption_result = self.detect_large_redemption(fund_data.get("flow_data"))
        if redemption_result.get("has_anomaly"):
            anomalies.append(redemption_result)

        # 净值偏离检测
        nav_result = self.detect_nav_deviation(
            fund_data.get("nav_data"),
            fund_data.get("fund_code")
        )
        if nav_result.get("has_anomaly"):
            anomalies.append(nav_result)

        # 成交量异常检测
        volume_result = self.detect_volume_spike(fund_data.get("volume_data"))
        if volume_result.get("has_anomaly"):
            anomalies.append(volume_result)

        # 经理变更检测
        manager_result = self.detect_manager_change(fund_data.get("manager_info"))
        if manager_result.get("has_anomaly"):
            anomalies.append(manager_result)

        # 持仓集中度检测
        holdings_result = self.detect_concentration_change(fund_data.get("holdings_data"))
        if holdings_result.get("has_anomaly"):
            anomalies.append(holdings_result)

        # 综合评估
        if not anomalies:
            overall_risk = "low"
            description = "未检测到明显异常"
            advice = "基金运行正常，可继续持有"
        elif len(anomalies) == 1:
            overall_risk = anomalies[0].get("risk_level", "low")
            description = f"检测到1项异常: {anomalies[0].get('description', '')}"
            advice = anomalies[0].get("advice", "关注相关风险")
        else:
            high_risk_count = sum(1 for a in anomalies if a.get("risk_level") == "high")
            if high_risk_count > 0:
                overall_risk = "high"
            else:
                overall_risk = "medium"
            description = f"检测到{len(anomalies)}项异常"
            advice = "多项异常，建议密切关注并考虑调整仓位"

        return {
            "has_data": True,
            "overall_risk": overall_risk,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "description": description,
            "advice": advice
        }


# 全局异常检测实例
anomaly_detector = AnomalyDetector()
