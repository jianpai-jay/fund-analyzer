"""
技术分析模块
实现 MACD、RSI、布林带、K线形态识别等技术指标
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional


class TechnicalAnalyzer:
    """技术分析类"""

    def __init__(self):
        pass

    def calculate_ma(self, prices: pd.Series, periods: List[int] = None) -> Dict[str, pd.Series]:
        """
        计算移动平均线

        Args:
            prices: 价格序列
            periods: 周期列表

        Returns:
            dict: 各周期的移动平均线
        """
        if periods is None:
            periods = [5, 10, 20, 60]

        result = {}
        for period in periods:
            if len(prices) >= period:
                result[f"ma{period}"] = prices.rolling(window=period).mean()
            else:
                result[f"ma{period}"] = pd.Series([np.nan] * len(prices), index=prices.index)

        return result

    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """
        计算指数移动平均线

        Args:
            prices: 价格序列
            period: 周期

        Returns:
            Series: EMA序列
        """
        return prices.ewm(span=period, adjust=False).mean()

    def calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Any]:
        """
        计算MACD指标

        Args:
            prices: 价格序列
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            dict: MACD指标
        """
        if len(prices) < slow + signal:
            return {
                "dif": pd.Series([np.nan] * len(prices), index=prices.index),
                "dea": pd.Series([np.nan] * len(prices), index=prices.index),
                "macd": pd.Series([np.nan] * len(prices), index=prices.index),
                "signal": "unknown",
                "description": "数据不足"
            }

        # 计算EMA
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)

        # 计算DIF
        dif = ema_fast - ema_slow

        # 计算DEA
        dea = self.calculate_ema(dif, signal)

        # 计算MACD柱
        macd = 2 * (dif - dea)

        # 判断信号
        signal_type = "neutral"
        description = ""

        # 检查金叉/死叉
        if len(dif) >= 2 and len(dea) >= 2:
            if dif.iloc[-1] > dea.iloc[-1] and dif.iloc[-2] <= dea.iloc[-2]:
                signal_type = "golden_cross"
                description = "MACD金叉，看涨信号"
            elif dif.iloc[-1] < dea.iloc[-1] and dif.iloc[-2] >= dea.iloc[-2]:
                signal_type = "death_cross"
                description = "MACD死叉，看跌信号"
            elif dif.iloc[-1] > 0 and dea.iloc[-1] > 0:
                signal_type = "bullish"
                description = "MACD在零轴上方，多头趋势"
            elif dif.iloc[-1] < 0 and dea.iloc[-1] < 0:
                signal_type = "bearish"
                description = "MACD在零轴下方，空头趋势"

        # 检查背离
        if len(prices) >= 20:
            price_higher = prices.iloc[-1] > prices.iloc[-10]
            dif_higher = dif.iloc[-1] > dif.iloc[-10]

            if price_higher and not dif_higher:
                signal_type = "bearish_divergence"
                description = "顶背离，可能反转下跌"
            elif not price_higher and dif_higher:
                signal_type = "bullish_divergence"
                description = "底背离，可能反转上涨"

        return {
            "dif": dif,
            "dea": dea,
            "macd": macd,
            "signal": signal_type,
            "description": description,
            "dif_value": dif.iloc[-1] if not dif.empty else None,
            "dea_value": dea.iloc[-1] if not dea.empty else None,
            "macd_value": macd.iloc[-1] if not macd.empty else None
        }

    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> Dict[str, Any]:
        """
        计算RSI指标

        Args:
            prices: 价格序列
            period: 周期

        Returns:
            dict: RSI指标
        """
        if len(prices) < period + 1:
            return {
                "rsi": pd.Series([np.nan] * len(prices), index=prices.index),
                "signal": "unknown",
                "description": "数据不足"
            }

        # 计算涨跌幅
        delta = prices.diff()

        # 计算涨跌幅的绝对值
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # 计算RS
        rs = gain / loss

        # 计算RSI
        rsi = 100 - (100 / (1 + rs))

        # 判断信号
        signal_type = "neutral"
        description = ""

        current_rsi = rsi.iloc[-1] if not rsi.empty else None

        if current_rsi is not None:
            if current_rsi < 30:
                signal_type = "oversold"
                description = f"RSI={current_rsi:.1f}，超卖区域，可能反弹"
            elif current_rsi > 70:
                signal_type = "overbought"
                description = f"RSI={current_rsi:.1f}，超买区域，可能回调"
            elif 30 <= current_rsi <= 50:
                signal_type = "weak"
                description = f"RSI={current_rsi:.1f}，偏弱"
            elif 50 < current_rsi <= 70:
                signal_type = "strong"
                description = f"RSI={current_rsi:.1f}，偏强"

        return {
            "rsi": rsi,
            "signal": signal_type,
            "description": description,
            "rsi_value": current_rsi
        }

    def calculate_bollinger(self, prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> Dict[str, Any]:
        """
        计算布林带

        Args:
            prices: 价格序列
            period: 周期
            std_dev: 标准差倍数

        Returns:
            dict: 布林带指标
        """
        if len(prices) < period:
            return {
                "upper": pd.Series([np.nan] * len(prices), index=prices.index),
                "middle": pd.Series([np.nan] * len(prices), index=prices.index),
                "lower": pd.Series([np.nan] * len(prices), index=prices.index),
                "signal": "unknown",
                "description": "数据不足"
            }

        # 计算中轨（移动平均线）
        middle = prices.rolling(window=period).mean()

        # 计算标准差
        std = prices.rolling(window=period).std()

        # 计算上下轨
        upper = middle + std_dev * std
        lower = middle - std_dev * std

        # 计算价格位置
        current_price = prices.iloc[-1]
        current_upper = upper.iloc[-1]
        current_lower = lower.iloc[-1]
        current_middle = middle.iloc[-1]

        # 判断信号
        signal_type = "neutral"
        description = ""

        if current_price > current_upper:
            signal_type = "above_upper"
            description = "价格突破上轨，可能超买"
        elif current_price < current_lower:
            signal_type = "below_lower"
            description = "价格跌破下轨，可能超卖"
        elif current_price > current_middle:
            signal_type = "above_middle"
            description = "价格在中轨上方，偏强"
        elif current_price < current_middle:
            signal_type = "below_middle"
            description = "价格在中轨下方，偏弱"

        # 计算带宽
        bandwidth = (current_upper - current_lower) / current_middle * 100

        return {
            "upper": upper,
            "middle": middle,
            "lower": lower,
            "signal": signal_type,
            "description": description,
            "upper_value": current_upper,
            "middle_value": current_middle,
            "lower_value": current_lower,
            "bandwidth": bandwidth
        }

    def identify_patterns(self, prices: pd.Series) -> List[Dict[str, Any]]:
        """
        识别K线形态

        Args:
            prices: 价格序列

        Returns:
            list: 识别到的形态
        """
        patterns = []

        if len(prices) < 5:
            return patterns

        # 获取最近5个价格
        recent = prices.tail(5).values

        # 检测锤子线
        if self._is_hammer(recent):
            patterns.append({
                "name": "锤子线",
                "signal": "bullish",
                "description": "可能反转上涨"
            })

        # 检测十字星
        if self._is_doji(recent):
            patterns.append({
                "name": "十字星",
                "signal": "neutral",
                "description": "趋势可能反转"
            })

        # 检测吞没形态
        if self._is_engulfing(recent):
            patterns.append({
                "name": "吞没形态",
                "signal": "reversal",
                "description": "趋势可能反转"
            })

        # 检测三只乌鸦
        if self._is_three_crows(recent):
            patterns.append({
                "name": "三只乌鸦",
                "signal": "bearish",
                "description": "看跌信号"
            })

        # 检测红三兵
        if self._is_three_soldiers(recent):
            patterns.append({
                "name": "红三兵",
                "signal": "bullish",
                "description": "看涨信号"
            })

        return patterns

    def _is_hammer(self, prices: np.ndarray) -> bool:
        """检测锤子线"""
        if len(prices) < 3:
            return False

        # 简化判断：连续下跌后出现反弹
        if prices[-3] > prices[-2] and prices[-2] < prices[-1]:
            return True
        return False

    def _is_doji(self, prices: np.ndarray) -> bool:
        """检测十字星"""
        if len(prices) < 3:
            return False

        # 简化判断：价格波动很小
        if abs(prices[-1] - prices[-2]) / prices[-2] < 0.001:
            return True
        return False

    def _is_engulfing(self, prices: np.ndarray) -> bool:
        """检测吞没形态"""
        if len(prices) < 4:
            return False

        # 简化判断
        if prices[-4] > prices[-3] and prices[-2] < prices[-1]:
            return True
        if prices[-4] < prices[-3] and prices[-2] > prices[-1]:
            return True
        return False

    def _is_three_crows(self, prices: np.ndarray) -> bool:
        """检测三只乌鸦"""
        if len(prices) < 4:
            return False

        # 连续三天下跌
        if prices[-4] > prices[-3] > prices[-2] > prices[-1]:
            return True
        return False

    def _is_three_soldiers(self, prices: np.ndarray) -> bool:
        """检测红三兵"""
        if len(prices) < 4:
            return False

        # 连续三天上涨
        if prices[-4] < prices[-3] < prices[-2] < prices[-1]:
            return True
        return False

    def calculate_kdj(self, prices: pd.Series, n: int = 9, m1: int = 3, m2: int = 3) -> Dict[str, Any]:
        """
        计算KDJ指标

        Args:
            prices: 价格序列
            n: 周期
            m1: K值平滑因子
            m2: D值平滑因子

        Returns:
            dict: KDJ指标
        """
        if len(prices) < n:
            return {
                "k": pd.Series([np.nan] * len(prices), index=prices.index),
                "d": pd.Series([np.nan] * len(prices), index=prices.index),
                "j": pd.Series([np.nan] * len(prices), index=prices.index),
                "signal": "unknown",
                "description": "数据不足"
            }

        # 计算RSV
        low_list = prices.rolling(window=n).min()
        high_list = prices.rolling(window=n).max()
        rsv = (prices - low_list) / (high_list - low_list) * 100

        # 计算K值
        k = rsv.ewm(com=m1-1, adjust=False).mean()

        # 计算D值
        d = k.ewm(com=m2-1, adjust=False).mean()

        # 计算J值
        j = 3 * k - 2 * d

        # 判断信号
        signal_type = "neutral"
        description = ""

        current_k = k.iloc[-1] if not k.empty else None
        current_d = d.iloc[-1] if not d.empty else None
        current_j = j.iloc[-1] if not j.empty else None

        if current_k is not None and current_d is not None:
            if current_k < 20 and current_d < 20:
                signal_type = "oversold"
                description = f"KDJ超卖区域，K={current_k:.1f}, D={current_d:.1f}"
            elif current_k > 80 and current_d > 80:
                signal_type = "overbought"
                description = f"KDJ超买区域，K={current_k:.1f}, D={current_d:.1f}"
            elif current_k > current_d:
                signal_type = "bullish"
                description = f"K线上穿D线，看涨"
            elif current_k < current_d:
                signal_type = "bearish"
                description = f"K线下穿D线，看跌"

        return {
            "k": k,
            "d": d,
            "j": j,
            "signal": signal_type,
            "description": description,
            "k_value": current_k,
            "d_value": current_d,
            "j_value": current_j
        }

    def calculate_volume_ma(self, volumes: pd.Series, period: int = 20) -> Dict[str, Any]:
        """
        计算成交量均线和量价关系

        Args:
            volumes: 成交量序列
            period: 周期

        Returns:
            dict: 成交量分析
        """
        if len(volumes) < period or volumes is None:
            return {
                "volume_ma": None,
                "signal": "unknown",
                "description": "数据不足"
            }

        # 计算成交量均线
        volume_ma = volumes.rolling(window=period).mean()
        current_volume = volumes.iloc[-1]
        current_ma = volume_ma.iloc[-1]

        # 计算量比
        volume_ratio = current_volume / current_ma if current_ma > 0 else 1

        # 判断信号
        signal_type = "neutral"
        description = ""

        if volume_ratio > 2:
            signal_type = "heavy_volume"
            description = f"放量明显(量比{volume_ratio:.1f})，关注趋势变化"
        elif volume_ratio > 1.5:
            signal_type = "increasing"
            description = f"温和放量(量比{volume_ratio:.1f})"
        elif volume_ratio < 0.5:
            signal_type = "shrinking"
            description = f"缩量明显(量比{volume_ratio:.1f})，观望为主"
        elif volume_ratio < 0.7:
            signal_type = "light_volume"
            description = f"轻微缩量(量比{volume_ratio:.1f})"
        else:
            description = f"成交量正常(量比{volume_ratio:.1f})"

        return {
            "volume_ma": volume_ma,
            "volume_ratio": volume_ratio,
            "signal": signal_type,
            "description": description
        }

    def calculate_vwap(self, prices: pd.Series, volumes: pd.Series) -> Dict[str, Any]:
        """
        计算VWAP (成交量加权平均价)

        Args:
            prices: 价格序列
            volumes: 成交量序列

        Returns:
            dict: VWAP指标
        """
        if prices is None or volumes is None or len(prices) < 20:
            return {
                "vwap": None,
                "signal": "unknown",
                "description": "数据不足"
            }

        # 计算VWAP
        vwap = (prices * volumes).cumsum() / volumes.cumsum()
        current_price = prices.iloc[-1]
        current_vwap = vwap.iloc[-1]

        # 判断价格与VWAP的关系
        signal_type = "neutral"
        description = ""

        if current_price > current_vwap * 1.02:
            signal_type = "above_vwap"
            description = f"价格高于VWAP 2%以上，短期偏强"
        elif current_price > current_vwap:
            signal_type = "near_vwap_above"
            description = f"价格略高于VWAP，中性偏强"
        elif current_price < current_vwap * 0.98:
            signal_type = "below_vwap"
            description = f"价格低于VWAP 2%以上，短期偏弱"
        elif current_price < current_vwap:
            signal_type = "near_vwap_below"
            description = f"价格略低于VWAP，中性偏弱"
        else:
            description = "价格围绕VWAP波动"

        return {
            "vwap": vwap,
            "current_vwap": current_vwap,
            "signal": signal_type,
            "description": description
        }

    def generate_signals(self, prices: pd.Series, volumes: pd.Series = None) -> Dict[str, Any]:
        """
        生成技术指标综合信号

        Args:
            prices: 价格序列
            volumes: 成交量序列(可选)

        Returns:
            dict: 综合信号
        """
        signals = []

        # MACD信号
        macd = self.calculate_macd(prices)
        if macd["signal"] in ["golden_cross", "bullish_divergence"]:
            signals.append({"indicator": "MACD", "signal": "bullish", "weight": 0.25})
        elif macd["signal"] in ["death_cross", "bearish_divergence"]:
            signals.append({"indicator": "MACD", "signal": "bearish", "weight": 0.25})

        # RSI信号
        rsi = self.calculate_rsi(prices)
        if rsi["signal"] == "oversold":
            signals.append({"indicator": "RSI", "signal": "bullish", "weight": 0.2})
        elif rsi["signal"] == "overbought":
            signals.append({"indicator": "RSI", "signal": "bearish", "weight": 0.2})

        # 布林带信号
        bollinger = self.calculate_bollinger(prices)
        if bollinger["signal"] == "below_lower":
            signals.append({"indicator": "Bollinger", "signal": "bullish", "weight": 0.2})
        elif bollinger["signal"] == "above_upper":
            signals.append({"indicator": "Bollinger", "signal": "bearish", "weight": 0.2})

        # KDJ信号
        kdj = self.calculate_kdj(prices)
        if kdj["signal"] == "oversold":
            signals.append({"indicator": "KDJ", "signal": "bullish", "weight": 0.15})
        elif kdj["signal"] == "overbought":
            signals.append({"indicator": "KDJ", "signal": "bearish", "weight": 0.15})

        # K线形态
        patterns = self.identify_patterns(prices)
        for pattern in patterns:
            if pattern["signal"] == "bullish":
                signals.append({"indicator": "Pattern", "signal": "bullish", "weight": 0.1})
            elif pattern["signal"] == "bearish":
                signals.append({"indicator": "Pattern", "signal": "bearish", "weight": 0.1})

        # 成交量信号(如果有)
        volume_analysis = None
        vwap_analysis = None
        if volumes is not None:
            volume_analysis = self.calculate_volume_ma(volumes)
            if volume_analysis["signal"] in ["heavy_volume", "increasing"]:
                signals.append({"indicator": "Volume", "signal": "bullish", "weight": 0.1})
            elif volume_analysis["signal"] in ["shrinking", "light_volume"]:
                signals.append({"indicator": "Volume", "signal": "bearish", "weight": 0.1})

            vwap_analysis = self.calculate_vwap(prices, volumes)
            if vwap_analysis["signal"] == "above_vwap":
                signals.append({"indicator": "VWAP", "signal": "bullish", "weight": 0.1})
            elif vwap_analysis["signal"] == "below_vwap":
                signals.append({"indicator": "VWAP", "signal": "bearish", "weight": 0.1})

        # 计算综合信号
        bullish_weight = sum(s["weight"] for s in signals if s["signal"] == "bullish")
        bearish_weight = sum(s["weight"] for s in signals if s["signal"] == "bearish")

        if bullish_weight > bearish_weight and bullish_weight > 0.3:
            overall_signal = "bullish"
            signal_strength = bullish_weight
            description = f"技术面看涨，信号强度: {bullish_weight:.0%}"
        elif bearish_weight > bullish_weight and bearish_weight > 0.3:
            overall_signal = "bearish"
            signal_strength = bearish_weight
            description = f"技术面看跌，信号强度: {bearish_weight:.0%}"
        else:
            overall_signal = "neutral"
            signal_strength = 0
            description = "技术面中性，无明显信号"

        return {
            "overall_signal": overall_signal,
            "signal_strength": signal_strength,
            "description": description,
            "signals": signals,
            "macd": macd,
            "rsi": rsi,
            "bollinger": bollinger,
            "kdj": kdj,
            "patterns": patterns,
            "volume": volume_analysis,
            "vwap": vwap_analysis
        }


# 全局技术分析实例
technical_analyzer = TechnicalAnalyzer()
