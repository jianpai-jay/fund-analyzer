# 📊 基金研究助手 (Fund Analyzer)

一个自动化的基金分析系统，每天在 GitHub Actions 上运行，分析基金指标并推送到企业微信。

## ✨ 功能特点

- 🔄 **自动化分析**: 每天定时运行，无需手动操作
- 📈 **综合指标**: 基础指标 + 风险指标全面分析
- 📱 **微信推送**: 分析结果自动推送到企业微信
- 🎯 **自选基金**: 支持自定义要追踪的基金列表
- ⭐ **综合评分**: 智能评级系统，一目了然

## 📊 分析指标

### 基础指标
- 最新净值
- 日涨跌幅
- 区间收益率
- 平均日收益率

### 风险指标
- 年化波动率
- 最大回撤
- 夏普比率
- 卡玛比率
- 索提诺比率

### 综合评分
- ⭐⭐⭐⭐⭐ 优秀 (85分以上)
- ⭐⭐⭐⭐ 良好 (70-84分)
- ⭐⭐⭐ 中等 (55-69分)
- ⭐⭐ 较差 (40-54分)
- ⭐ 差 (40分以下)

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/fund-analyzer.git
cd fund-analyzer
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置基金列表

编辑 `config/funds.json` 文件，添加你要追踪的基金：

```json
{
  "funds": [
    {
      "code": "110011",
      "name": "易方达中小盘混合",
      "type": "混合型"
    },
    {
      "code": "161725",
      "name": "招商中证白酒指数",
      "type": "指数型"
    }
  ],
  "analysis_days": 30,
  "notify_webhook": ""
}
```

### 4. 配置企业微信机器人

1. 在企业微信群中添加机器人
2. 获取 Webhook URL
3. 在 GitHub 仓库的 Settings → Secrets and variables → Actions 中添加：
   - Name: `WECHAT_WEBHOOK_URL`
   - Value: 你的 Webhook URL

### 5. 推送到 GitHub

```bash
git add .
git commit -m "初始化基金分析系统"
git push origin main
```

## 📅 定时任务

系统默认在以下时间运行：
- **时间**: 每天北京时间 18:00（A股收盘后）
- **日期**: 周一到周五（交易日）
- **支持**: 手动触发运行

## 🔧 配置说明

### 基金列表配置

`config/funds.json` 文件说明：

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

- `code`: 基金代码（6位数字）
- `name`: 基金名称
- `type`: 基金类型（股票型、混合型、指数型等）
- `analysis_days`: 分析天数（默认30天）
- `notify_webhook`: 企业微信 Webhook URL（可选，优先使用环境变量）

### 环境变量

- `WECHAT_WEBHOOK_URL`: 企业微信机器人 Webhook URL

## 🛠️ 本地运行

### 测试配置

```bash
python -m src.main --test
```

### 运行分析

```bash
python -m src.main
```

## 📁 项目结构

```
fund-analyzer/
├── .github/
│   └── workflows/
│       └── daily_analysis.yml    # GitHub Actions 工作流
├── src/
│   ├── __init__.py
│   ├── main.py                   # 主程序
│   ├── config.py                 # 配置管理
│   ├── data_fetcher.py           # 数据获取模块
│   ├── analyzer.py               # 分析模块
│   └── notifier.py               # 推送模块
├── config/
│   └── funds.json                # 基金列表配置
├── requirements.txt              # Python 依赖
└── README.md                     # 项目文档
```

## 🔍 数据源

本项目使用 [AKShare](https://github.com/akfamily/akshare) 作为数据源，这是一个开源的财经数据接口库。

## ⚠️ 注意事项

1. **数据更新**: 基金净值数据通常在每天晚上更新
2. **网络请求**: 数据获取依赖网络，请确保网络通畅
3. **请求频率**: AKShare 可能有请求频率限制，系统已内置缓存机制
4. **隐私保护**: Webhook URL 等敏感信息只存储在 GitHub Secrets 中

## 🐛 常见问题

### Q: 推送没有收到？
A: 请检查：
1. Webhook URL 是否正确配置
2. 企业微信群机器人是否正常
3. GitHub Actions 是否运行成功

### Q: 数据获取失败？
A: 可能原因：
1. 基金代码错误
2. 网络连接问题
3. AKShare 数据源暂时不可用

### Q: 如何添加新基金？
A: 编辑 `config/funds.json` 文件，添加新的基金信息即可。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题，请提交 Issue 或联系项目维护者。

---

**免责声明**: 本工具仅供学习和研究使用，不构成任何投资建议。基金有风险，投资需谨慎。
