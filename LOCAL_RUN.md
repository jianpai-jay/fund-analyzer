# 🏠 本地运行指南

本指南帮助你在本地环境测试和运行基金研究助手。

## 📋 前置要求

- Python 3.9 或更高版本
- pip 包管理器
- 网络连接

## 🚀 快速开始

### 1. 安装依赖

```bash
# 进入项目目录
cd fund-analyzer

# 安装依赖
pip install -r requirements.txt
```

### 2. 测试配置

```bash
# 测试模式，显示配置信息
python run.py --test
```

### 3. 运行分析

```bash
# 运行完整分析
python run.py --analyze
```

## 🛠️ 常用命令

### 查看帮助

```bash
python run.py --help
```

### 显示基金列表

```bash
python run.py --list
```

### 添加基金

```bash
# 格式: python run.py --add <代码> <名称> <类型>
python run.py --add 110011 "易方达中小盘混合" "混合型"
```

### 删除基金

```bash
# 格式: python run.py --remove <代码>
python run.py --remove 110011
```

## 🔧 配置说明

### 基金列表配置

编辑 `config/funds.json` 文件：

```json
{
  "funds": [
    {
      "code": "基金代码",
      "name": "基金名称",
      "type": "基金类型"
    }
  ],
  "analysis_days": 30,
  "notify_webhook": ""
}
```

### 配置项说明

- `funds`: 基金列表
  - `code`: 基金代码（6位数字）
  - `name`: 基金名称
  - `type`: 基金类型（股票型、混合型、指数型等）
- `analysis_days`: 分析天数（默认30天）
- `notify_webhook`: 企业微信 Webhook URL（可选）

## 📊 输出示例

运行分析后，你会看到类似以下的输出：

```
==================================================
基金研究助手 - 每日分析
==================================================
正在分析基金: 易方达中小盘混合 (110011)
完成分析: 易方达中小盘混合
正在分析基金: 招商中证白酒指数 (161725)
完成分析: 招商中证白酒指数

分析结果:

易方达中小盘混合 (110011)
  最新净值: 4.5678
  日涨跌幅: +0.56%
  区间收益率: +3.45%
  综合评级: ⭐⭐⭐⭐ 良好

招商中证白酒指数 (161725)
  最新净值: 1.2345
  日涨跌幅: -0.12%
  区间收益率: -1.23%
  综合评级: ⭐⭐⭐ 中等

分析完成！
```

## 🐛 常见问题

### 问题1: 导入错误

**错误信息**: `ModuleNotFoundError: No module named 'akshare'`

**解决方案**:
```bash
pip install akshare
```

### 问题2: 数据获取失败

**错误信息**: `获取基金数据失败`

**可能原因**:
1. 基金代码错误
2. 网络连接问题
3. AKShare 数据源暂时不可用

**解决方案**:
1. 检查基金代码是否正确
2. 检查网络连接
3. 稍后重试

### 问题3: 配置文件不存在

**错误信息**: `配置文件不存在`

**解决方案**:
确保 `config/funds.json` 文件存在，可以参考 `config/test_funds.json` 创建。

## 📝 开发说明

### 项目结构

```
fund-analyzer/
├── run.py                  # 本地运行脚本
├── src/
│   ├── __init__.py
│   ├── main.py             # 主程序
│   ├── config.py           # 配置管理
│   ├── data_fetcher.py     # 数据获取模块
│   ├── analyzer.py         # 分析模块
│   └── notifier.py         # 推送模块
├── config/
│   ├── funds.json          # 基金列表配置
│   └── test_funds.json     # 测试配置
└── requirements.txt        # Python 依赖
```

### 调试模式

可以在代码中添加调试信息：

```python
from src.config import config

print(f"基金列表: {config.get_funds()}")
print(f"分析天数: {config.get_analysis_days()}")
print(f"Webhook URL: {config.get_webhook_url()}")
```

## 📞 获取帮助

如果遇到问题，请检查：

1. Python 版本是否为 3.9+
2. 依赖是否正确安装
3. 配置文件格式是否正确
4. 网络连接是否正常

---

**提示**: 本地运行主要用于测试和调试，生产环境建议使用 GitHub Actions 自动运行。
