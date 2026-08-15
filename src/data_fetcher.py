"""
数据获取模块
使用 AKShare 获取基金数据
"""
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional


class FundDataFetcher:
    """基金数据获取类"""

    def __init__(self):
        self.cache = {}

    def get_fund_nav(self, fund_code: str, days: int = 30) -> Optional[pd.DataFrame]:
        """
        获取基金净值数据

        Args:
            fund_code: 基金代码
            days: 获取天数

        Returns:
            DataFrame: 净值数据
        """
        try:
            # 获取开放式基金净值走势
            df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")

            if df is None or df.empty:
                print(f"获取基金 {fund_code} 数据失败")
                return None

            # 重命名列
            df = df.rename(columns={
                "净值日期": "date",
                "单位净值": "nav",
                "累计净值": "acc_nav",
                "日增长率": "daily_return"
            })

            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'])

            # 转换数值类型
            df['nav'] = pd.to_numeric(df['nav'], errors='coerce')
            df['daily_return'] = pd.to_numeric(df['daily_return'], errors='coerce')

            # 获取最近N天的数据
            df = df.tail(days)

            return df

        except Exception as e:
            print(f"获取基金 {fund_code} 数据时出错: {e}")
            return None

    def get_fund_info(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """
        获取基金基本信息

        Args:
            fund_code: 基金代码

        Returns:
            dict: 基金信息
        """
        try:
            # 获取基金详情
            df = ak.fund_individual_basic_info_xq(symbol=fund_code)

            if df is None or df.empty:
                print(f"获取基金 {fund_code} 信息失败")
                return None

            # 转换为字典
            info = {}
            for _, row in df.iterrows():
                info[row['item']] = row['value']

            return info

        except Exception as e:
            print(f"获取基金 {fund_code} 信息时出错: {e}")
            return None

    def get_fund_performance(self, fund_code: str) -> Optional[Dict[str, float]]:
        """
        获取基金业绩表现

        Args:
            fund_code: 基金代码

        Returns:
            dict: 业绩数据
        """
        try:
            # 获取基金业绩
            df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="累计收益率走势")

            if df is None or df.empty:
                return None

            # 计算不同时间段的收益率
            df['净值日期'] = pd.to_datetime(df['净值日期'])
            df = df.sort_values('净值日期')

            latest = df['累计净值'].iloc[-1]
            performance = {}

            # 近1周
            week_ago = datetime.now() - timedelta(days=7)
            week_data = df[df['净值日期'] >= week_ago]
            if not week_data.empty:
                performance['1w'] = (latest / week_data['累计净值'].iloc[0] - 1) * 100

            # 近1月
            month_ago = datetime.now() - timedelta(days=30)
            month_data = df[df['净值日期'] >= month_ago]
            if not month_data.empty:
                performance['1m'] = (latest / month_data['累计净值'].iloc[0] - 1) * 100

            # 近3月
            quarter_ago = datetime.now() - timedelta(days=90)
            quarter_data = df[df['净值日期'] >= quarter_ago]
            if not quarter_data.empty:
                performance['3m'] = (latest / quarter_data['累计净值'].iloc[0] - 1) * 100

            # 近1年
            year_ago = datetime.now() - timedelta(days=365)
            year_data = df[df['净值日期'] >= year_ago]
            if not year_data.empty:
                performance['1y'] = (latest / year_data['累计净值'].iloc[0] - 1) * 100

            return performance

        except Exception as e:
            print(f"获取基金 {fund_code} 业绩时出错: {e}")
            return None


# 全局数据获取实例
data_fetcher = FundDataFetcher()
