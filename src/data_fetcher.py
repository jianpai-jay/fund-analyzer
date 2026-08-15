"""
增强版数据获取模块
支持实时数据、资金流向、新闻数据获取
"""
import akshare as ak
import pandas as pd
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import re


class EnhancedDataFetcher:
    """增强版数据获取类"""

    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 缓存5分钟

    def _get_cache(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                return data
        return None

    def _set_cache(self, key: str, data: Any):
        """设置缓存"""
        self.cache[key] = (data, time.time())

    def get_fund_nav(self, fund_code: str, days: int = 30) -> Optional[pd.DataFrame]:
        """
        获取基金净值数据

        Args:
            fund_code: 基金代码
            days: 获取天数

        Returns:
            DataFrame: 净值数据
        """
        cache_key = f"nav_{fund_code}_{days}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

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

            self._set_cache(cache_key, df)
            return df

        except Exception as e:
            print(f"获取基金 {fund_code} 数据时出错: {e}")
            return None

    def get_realtime_nav(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """
        获取基金实时净值（估算）

        Args:
            fund_code: 基金代码

        Returns:
            dict: 实时净值数据
        """
        cache_key = f"realtime_{fund_code}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            # 使用东方财富API获取实时估值
            url = f"https://fundgz.1234567.com.cn/js/{fund_code}.js"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                # 解析JSONP响应
                content = response.text
                # 提取JSON部分
                json_match = re.search(r'jsonpgz\((.*?)\);', content)
                if json_match:
                    data = json.loads(json_match.group(1))
                    result = {
                        "code": data.get("fundcode"),
                        "name": data.get("name"),
                        "nav": float(data.get("dwjz", 0)),
                        "estimated_nav": float(data.get("gsz", 0)),
                        "estimated_return": float(data.get("gszzl", 0)),
                        "update_time": data.get("gztime"),
                        "is_trading": True
                    }
                    self._set_cache(cache_key, result)
                    return result

            return None

        except Exception as e:
            print(f"获取基金 {fund_code} 实时净值时出错: {e}")
            return None

    def get_fund_info(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """
        获取基金基本信息

        Args:
            fund_code: 基金代码

        Returns:
            dict: 基金信息
        """
        cache_key = f"info_{fund_code}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

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

            self._set_cache(cache_key, info)
            return info

        except Exception as e:
            print(f"获取基金 {fund_code} 信息时出错: {e}")
            return None

    def get_stock_quote(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票实时行情

        Args:
            stock_code: 股票代码

        Returns:
            dict: 股票行情数据
        """
        cache_key = f"stock_{stock_code}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            # 使用东方财富API
            url = f"https://push2.eastmoney.com/api/qt/stock/get"
            params = {
                "secid": f"1.{stock_code}" if stock_code.startswith("6") else f"0.{stock_code}",
                "fields": "f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f55,f57,f58,f60,f116,f117,f162,f167,f168,f169,f170,f171",
                "ut": "fa5fd1943c7b386f172d6893dbbd1"
            }

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                if data:
                    result = {
                        "code": data.get("f57"),
                        "name": data.get("f58"),
                        "price": data.get("f43", 0) / 100,
                        "change": data.get("f169", 0) / 100,
                        "change_pct": data.get("f170", 0) / 100,
                        "volume": data.get("f47"),
                        "amount": data.get("f48"),
                        "high": data.get("f44", 0) / 100,
                        "low": data.get("f45", 0) / 100,
                        "open": data.get("f46", 0) / 100,
                        "pe": data.get("f162", 0) / 100,
                        "pb": data.get("f167", 0) / 100,
                        "market_cap": data.get("f116"),
                        "turnover_rate": data.get("f168", 0) / 100
                    }
                    self._set_cache(cache_key, result)
                    return result

            return None

        except Exception as e:
            print(f"获取股票 {stock_code} 行情时出错: {e}")
            return None

    def get_capital_flow(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """
        获取基金资金流向

        Args:
            fund_code: 基金代码

        Returns:
            dict: 资金流向数据
        """
        cache_key = f"flow_{fund_code}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            # 使用东方财富API获取资金流向
            url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
            params = {
                "fltt": 2,
                "secids": fund_code,
                "fields": "f1,f2,f3,f12,f13,f14,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87",
                "ut": "b2884a393a59ad64002292a3e90d46a5"
            }

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                if data and data.get("diff"):
                    item = data["diff"][0]
                    result = {
                        "main_net_inflow": item.get("f62"),  # 主力净流入
                        "main_net_inflow_pct": item.get("f184"),  # 主力净流入占比
                        "super_large_net_inflow": item.get("f66"),  # 超大单净流入
                        "super_large_net_inflow_pct": item.get("f69"),
                        "large_net_inflow": item.get("f72"),  # 大单净流入
                        "large_net_inflow_pct": item.get("f75"),
                        "medium_net_inflow": item.get("f78"),  # 中单净流入
                        "medium_net_inflow_pct": item.get("f81"),
                        "small_net_inflow": item.get("f84"),  # 小单净流入
                        "small_net_inflow_pct": item.get("f87")
                    }
                    self._set_cache(cache_key, result)
                    return result

            return None

        except Exception as e:
            print(f"获取基金 {fund_code} 资金流向时出错: {e}")
            return None

    def get_north_flow(self) -> Optional[Dict[str, Any]]:
        """
        获取北向资金流向

        Returns:
            dict: 北向资金数据
        """
        cache_key = "north_flow"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            # 使用东方财富API
            url = "https://push2.eastmoney.com/api/qt/kamt.rtmin/get"
            params = {
                "fields1": "f1,f2,f3,f4",
                "fields2": "f51,f52,f53,f54,f55,f56",
                "ut": "b2884a393a59ad64002292a3e90d46a5"
            }

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                if data:
                    # 获取沪股通和深股通数据
                    s2n = data.get("s2n", [])
                    if s2n:
                        latest = s2n[-1].split(",") if s2n[-1] else []
                        if len(latest) >= 4:
                            result = {
                                "time": latest[0],
                                "north_net_flow": float(latest[1]) if latest[1] != "-" else 0,
                                "hgt_net_flow": float(latest[2]) if latest[2] != "-" else 0,
                                "sgt_net_flow": float(latest[3]) if latest[3] != "-" else 0,
                                "is_trading": True
                            }
                            self._set_cache(cache_key, result)
                            return result

            return None

        except Exception as e:
            print(f"获取北向资金数据时出错: {e}")
            return None

    def get_market_sentiment(self) -> Optional[Dict[str, Any]]:
        """
        获取市场情绪指标

        Returns:
            dict: 市场情绪数据
        """
        cache_key = "market_sentiment"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            # 获取涨跌家数
            url = "https://push2.eastmoney.com/api/qt/clist/get"
            params = {
                "pn": 1,
                "pz": 1,
                "po": 1,
                "np": 1,
                "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                "fltt": 2,
                "invt": 2,
                "fid": "f3",
                "fs": "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
                "fields": "f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152,f124,f107,f104,f105,f140,f141,f207,f208,f209,f222"
            }

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                if data:
                    total = data.get("total", 0)
                    # 这里简化处理，实际需要获取涨跌家数
                    result = {
                        "total_stocks": total,
                        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self._set_cache(cache_key, result)
                    return result

            return None

        except Exception as e:
            print(f"获取市场情绪数据时出错: {e}")
            return None

    def fetch_fund_news(self, fund_code: str) -> List[Dict[str, Any]]:
        """
        获取基金相关新闻

        Args:
            fund_code: 基金代码

        Returns:
            list: 新闻列表
        """
        cache_key = f"news_{fund_code}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            # 使用东方财富新闻API
            url = "https://search-api-web.eastmoney.com/search/jsonp"
            params = {
                "cb": "jQuery",
                "param": json.dumps({
                    "uid": "",
                    "keyword": fund_code,
                    "type": ["cmsArticleWebOld"],
                    "client": "web",
                    "clientType": "web",
                    "clientVersion": "curr",
                    "param": {
                        "cmsArticleWebOld": {
                            "searchScope": "default",
                            "sort": "default",
                            "pageIndex": 1,
                            "pageSize": 10,
                            "preTag": "",
                            "postTag": ""
                        }
                    }
                })
            }

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                content = response.text
                # 解析JSONP
                json_match = re.search(r'jQuery\((.*?)\)', content)
                if json_match:
                    data = json.loads(json_match.group(1))
                    articles = data.get("result", {}).get("cmsArticleWebOld", [])
                    news = []
                    for article in articles[:5]:  # 只取前5条
                        news.append({
                            "title": article.get("title", ""),
                            "content": article.get("content", ""),
                            "time": article.get("date", ""),
                            "source": article.get("mediaName", ""),
                            "url": article.get("url", "")
                        })
                    self._set_cache(cache_key, news)
                    return news

            return []

        except Exception as e:
            print(f"获取基金 {fund_code} 新闻时出错: {e}")
            return []

    def fetch_market_news(self) -> List[Dict[str, Any]]:
        """
        获取市场新闻

        Returns:
            list: 新闻列表
        """
        cache_key = "market_news"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            # 使用东方财富7x24小时快讯
            url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns"
            params = {
                "client": "web",
                "biz": "web_news_col",
                "column": "102",
                "order": 1,
                "needInteractData": 0,
                "page_index": 1,
                "page_size": 20
            }

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json().get("data", {})
                if data:
                    news_list = data.get("list", [])
                    news = []
                    for item in news_list[:10]:  # 只取前10条
                        news.append({
                            "title": item.get("title", ""),
                            "content": item.get("digest", ""),
                            "time": item.get("showTime", ""),
                            "source": item.get("source", "")
                        })
                    self._set_cache(cache_key, news)
                    return news

            return []

        except Exception as e:
            print(f"获取市场新闻时出错: {e}")
            return []


# 全局数据获取实例
data_fetcher = EnhancedDataFetcher()
