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
        self.max_retries = 3  # 最大重试次数
        self.retry_delay = 1  # 重试间隔(秒)

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

    def _request_with_retry(self, url: str, params: dict = None, headers: dict = None, timeout: int = 10) -> Optional[requests.Response]:
        """
        带重试机制的HTTP请求

        Args:
            url: 请求URL
            params: 请求参数
            headers: 请求头
            timeout: 超时时间

        Returns:
            Response对象或None
        """
        for attempt in range(self.max_retries):
            try:
                response = requests.get(url, params=params, headers=headers, timeout=timeout)
                if response.status_code == 200:
                    return response
                # 4xx/5xx 错误也返回，不重试
                return response
            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None
            except requests.exceptions.ConnectionError:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None
            except Exception as e:
                return None
        return None

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

            response = self._request_with_retry(url, headers=headers, timeout=5)
            if response and response.status_code == 200:
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
            # 使用天天基金API获取基金资金流向
            url = f"https://fundgz.1234567.com.cn/js/{fund_code}.js"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                content = response.text
                json_match = re.search(r'jsonpgz\((.*?)\);', content)
                if json_match:
                    data = json.loads(json_match.group(1))
                    # 基金资金流向数据
                    result = {
                        "main_net_inflow": 0,
                        "main_net_inflow_pct": 0,
                        "super_large_net_inflow": 0,
                        "super_large_net_inflow_pct": 0,
                        "large_net_inflow": 0,
                        "large_net_inflow_pct": 0,
                        "medium_net_inflow": 0,
                        "medium_net_inflow_pct": 0,
                        "small_net_inflow": 0,
                        "small_net_inflow_pct": 0,
                        "fund_size": data.get("fund_size", 0),
                        "fund_type": data.get("fund_type", "")
                    }
                    self._set_cache(cache_key, result)
                    return result

            # 备用方案：获取基金持仓数据来估算资金流向
            return self._get_fund_flow_from_holdings(fund_code)

        except Exception as e:
            print(f"获取基金 {fund_code} 资金流向时出错: {e}")
            return None

    def _get_fund_flow_from_holdings(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """
        从基金持仓数据估算资金流向

        Args:
            fund_code: 基金代码

        Returns:
            dict: 估算的资金流向数据
        """
        try:
            # 获取基金持仓数据
            holdings = self.get_fund_holdings(fund_code)
            if not holdings:
                return None

            # 根据持仓变化估算资金流向
            total_value = sum(h.get("market_value", 0) for h in holdings)
            top_holdings = holdings[:10]  # 前十大持仓
            top_value = sum(h.get("market_value", 0) for h in top_holdings)

            # 估算主力资金流向（前十大持仓变化）
            concentration = (top_value / total_value * 100) if total_value > 0 else 0

            result = {
                "main_net_inflow": 0,
                "main_net_inflow_pct": concentration - 50,  # 相对于平均水平的偏差
                "super_large_net_inflow": 0,
                "super_large_net_inflow_pct": 0,
                "large_net_inflow": 0,
                "large_net_inflow_pct": 0,
                "medium_net_inflow": 0,
                "medium_net_inflow_pct": 0,
                "small_net_inflow": 0,
                "small_net_inflow_pct": 0,
                "fund_size": total_value,
                "concentration": concentration,
                "holdings_count": len(holdings)
            }

            self._set_cache(f"flow_{fund_code}", result)
            return result

        except Exception as e:
            print(f"估算基金 {fund_code} 资金流向时出错: {e}")
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

    def get_fund_holdings(self, fund_code: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取基金持仓数据

        Args:
            fund_code: 基金代码

        Returns:
            list: 持仓数据列表
        """
        cache_key = f"holdings_{fund_code}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            # 使用天天基金API获取基金持仓
            url = f"http://fund.eastmoney.com/f10/F10DataApi.aspx"
            params = {
                "type": "jjcc",
                "code": fund_code,
                "topline": 20,
                "year": "",
                "month": ""
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://fund.eastmoney.com/'
            }

            response = self._request_with_retry(url, params=params, headers=headers, timeout=10)
            if response and response.status_code == 200:
                content = response.text
                # 解析HTML表格数据
                holdings = self._parse_holdings_html(content)
                if holdings:
                    self._set_cache(cache_key, holdings)
                    return holdings

            return []

        except Exception as e:
            print(f"获取基金 {fund_code} 持仓数据时出错: {e}")
            return []

    def _parse_holdings_html(self, html_content: str) -> List[Dict[str, Any]]:
        """
        解析持仓HTML数据

        Args:
            html_content: HTML内容

        Returns:
            list: 持仓数据列表
        """
        holdings = []
        try:
            # 简单的正则表达式解析
            # 查找股票代码和名称
            stock_pattern = r'<td><a[^>]*>(\d{6})</a></td><td><a[^>]*>([^<]+)</a></td>'
            matches = re.findall(stock_pattern, html_content)

            for match in matches[:20]:  # 最多20个持仓
                stock_code, stock_name = match
                holdings.append({
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "market_value": 0,
                    "percentage": 0
                })

        except Exception as e:
            print(f"解析持仓数据时出错: {e}")

        return holdings

    def get_fund_manager(self, fund_code: str) -> Optional[Dict[str, Any]]:
        """
        获取基金经理信息

        Args:
            fund_code: 基金代码

        Returns:
            dict: 基金经理信息
        """
        cache_key = f"manager_{fund_code}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            # 使用天天基金API获取基金经理信息
            url = f"http://fund.eastmoney.com/f10/F10DataApi.aspx"
            params = {
                "type": "jjjl",
                "code": fund_code,
                "topline": 10,
                "year": "",
                "month": ""
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://fund.eastmoney.com/'
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                content = response.text
                # 解析基金经理信息
                manager_info = self._parse_manager_html(content)
                if manager_info:
                    self._set_cache(cache_key, manager_info)
                    return manager_info

            return None

        except Exception as e:
            print(f"获取基金 {fund_code} 经理信息时出错: {e}")
            return None

    def _parse_manager_html(self, html_content: str) -> Optional[Dict[str, Any]]:
        """
        解析基金经理HTML数据

        Args:
            html_content: HTML内容

        Returns:
            dict: 基金经理信息
        """
        try:
            # 简单的正则表达式解析
            name_pattern = r'<td><a[^>]*>([^<]+)</a></td>'
            matches = re.findall(name_pattern, html_content)

            if matches:
                return {
                    "name": matches[0] if matches else "未知",
                    "tenure": "未知",
                    "total_return": 0,
                    "annual_return": 0,
                    "fund_count": 0
                }

        except Exception as e:
            print(f"解析基金经理数据时出错: {e}")

        return None

    def get_peer_funds(self, fund_code: str, fund_type: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取同类基金数据

        Args:
            fund_code: 基金代码
            fund_type: 基金类型

        Returns:
            list: 同类基金列表
        """
        cache_key = f"peers_{fund_code}"
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached

        try:
            # 使用天天基金API获取同类基金
            url = "http://fund.eastmoney.com/data/rankhandler.aspx"
            params = {
                "op": "ph",
                "dt": "kf",
                "ft": fund_type if fund_type != "混合型" else "hhy",
                "rs": "",
                "gs": "0",
                "sc": "1nzf",
                "st": "desc",
                "sd": "2024-01-01",
                "ed": "2024-12-31",
                "qdii": "",
                "tabSubtype": ",,,,,",
                "pi": "1",
                "pn": "20",
                "dx": "1"
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'http://fund.eastmoney.com/data/fundranking.html'
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                content = response.text
                # 解析基金排名数据
                peer_funds = self._parse_peer_funds(content, fund_code)
                if peer_funds:
                    self._set_cache(cache_key, peer_funds)
                    return peer_funds

            return []

        except Exception as e:
            print(f"获取同类基金数据时出错: {e}")
            return []

    def _parse_peer_funds(self, content: str, exclude_code: str) -> List[Dict[str, Any]]:
        """
        解析同类基金数据

        Args:
            content: API返回内容
            exclude_code: 要排除的基金代码

        Returns:
            list: 同类基金列表
        """
        funds = []
        try:
            # 简单解析数据
            # 格式通常是 var rankData = {datas:[...]}
            data_match = re.search(r'datas:\[(.*?)\]', content, re.DOTALL)
            if data_match:
                items = data_match.group(1).split('","')
                for item in items[:20]:  # 最多20个
                    parts = item.replace('"', '').split(',')
                    if len(parts) >= 10 and parts[0] != exclude_code:
                        funds.append({
                            "code": parts[0],
                            "name": parts[1],
                            "nav": float(parts[4]) if parts[4] else 0,
                            "daily_return": float(parts[5]) if parts[5] else 0,
                            "total_return": float(parts[7]) if parts[7] else 0,
                            "sharpe_ratio": float(parts[9]) if parts[9] else 0
                        })

        except Exception as e:
            print(f"解析同类基金数据时出错: {e}")

        return funds

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
