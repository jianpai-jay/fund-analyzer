"""
Web应用模块
提供手动触发分析和推送的Web界面
"""
import os
import sys
import json
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config
from src.main import analyze_all_funds
from src.notifier import create_notifier

app = Flask(__name__)

# 全局状态
analysis_status = {
    "running": False,
    "last_run": None,
    "last_result": None,
    "error": None
}

# HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>基金研究助手 - 控制面板</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        }
        .card-title {
            font-size: 1.3em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .status-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .status-item .label {
            font-size: 0.9em;
            color: #666;
            margin-bottom: 5px;
        }
        .status-item .value {
            font-size: 1.4em;
            font-weight: bold;
            color: #333;
        }
        .status-item.running .value { color: #f39c12; }
        .status-item.success .value { color: #27ae60; }
        .status-item.error .value { color: #e74c3c; }
        .btn-group {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }
        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        .btn-success {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            color: white;
        }
        .btn-success:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(17, 153, 142, 0.4);
        }
        .btn-warning {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        .btn-warning:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(245, 87, 108, 0.4);
        }
        .config-table {
            width: 100%;
            border-collapse: collapse;
        }
        .config-table th,
        .config-table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .config-table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
        }
        .config-table td {
            color: #555;
        }
        .fund-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .fund-tag {
            background: #e8f4fd;
            color: #2980b9;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        .log-box {
            background: #1e1e1e;
            color: #d4d4d4;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            max-height: 300px;
            overflow-y: auto;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .log-box .info { color: #4ec9b0; }
        .log-box .success { color: #6a9955; }
        .log-box .error { color: #f44747; }
        .spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid #ffffff;
            border-radius: 50%;
            border-top-color: transparent;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 基金研究助手</h1>
            <p>手动控制面板 - 分析 & 推送</p>
        </div>

        <!-- 状态卡片 -->
        <div class="card">
            <div class="card-title">📈 运行状态</div>
            <div class="status-grid">
                <div class="status-item {{ 'running' if status.running else ('success' if status.last_run else '') }}">
                    <div class="label">当前状态</div>
                    <div class="value" id="statusText">{{ '运行中...' if status.running else ('就绪' if status.last_run else '等待中') }}</div>
                </div>
                <div class="status-item">
                    <div class="label">上次运行</div>
                    <div class="value" id="lastRun">{{ status.last_run or '从未运行' }}</div>
                </div>
                <div class="status-item {{ 'error' if status.error else '' }}">
                    <div class="label">状态信息</div>
                    <div class="value" id="statusMsg">{{ status.error or '正常' }}</div>
                </div>
            </div>
        </div>

        <!-- 操作按钮 -->
        <div class="card">
            <div class="card-title">🎮 操作面板</div>
            <div class="btn-group">
                <button class="btn btn-primary" onclick="runAnalysis()" id="btnAnalyze" {{ 'disabled' if status.running }}>
                    {{ '<span class="spinner"></span> 分析中...' if status.running else '🔍 开始分析' }}
                </button>
                <button class="btn btn-success" onclick="runAndPush()" id="btnPush" {{ 'disabled' if status.running }}>
                    📤 分析并推送
                </button>
                <button class="btn btn-warning" onclick="refreshStatus()">
                    🔄 刷新状态
                </button>
            </div>
        </div>

        <!-- 配置信息 -->
        <div class="card">
            <div class="card-title">⚙️ 当前配置</div>
            <table class="config-table">
                <tr>
                    <th>配置项</th>
                    <th>值</th>
                </tr>
                <tr>
                    <td>分析天数</td>
                    <td>{{ config.analysis_days }}天</td>
                </tr>
                <tr>
                    <td>推送主题</td>
                    <td>{{ config.pushplus_topic or '未配置' }}</td>
                </tr>
                <tr>
                    <td>推送Token</td>
                    <td>{{ '已配置' if config.pushplus_token else '未配置' }}</td>
                </tr>
                <tr>
                    <td>监控基金</td>
                    <td>
                        <div class="fund-list">
                            {% for fund in config.funds %}
                            <span class="fund-tag">{{ fund.name }} ({{ fund.code }})</span>
                            {% endfor %}
                        </div>
                    </td>
                </tr>
            </table>
        </div>

        <!-- 运行日志 -->
        <div class="card">
            <div class="card-title">📝 运行日志</div>
            <div class="log-box" id="logBox">
{% if logs %}
{% for log in logs %}
{{ log }}
{% endfor %}
{% else %}
等待操作...
{% endif %}
            </div>
        </div>

        <div class="footer">
            <p>基金研究助手 v2.0 | 数据仅供参考，不构成投资建议</p>
        </div>
    </div>

    <script>
        let refreshInterval;

        function addLog(message, type = 'info') {
            const logBox = document.getElementById('logBox');
            const time = new Date().toLocaleTimeString();
            logBox.innerHTML += `<span class="${type}">[${time}] ${message}</span>\\n`;
            logBox.scrollTop = logBox.scrollHeight;
        }

        function updateStatus(data) {
            document.getElementById('statusText').textContent = data.running ? '运行中...' : '就绪';
            document.getElementById('lastRun').textContent = data.last_run || '从未运行';
            document.getElementById('statusMsg').textContent = data.error || '正常';

            document.getElementById('btnAnalyze').disabled = data.running;
            document.getElementById('btnPush').disabled = data.running;

            if (data.running) {
                document.getElementById('btnAnalyze').innerHTML = '<span class="spinner"></span> 分析中...';
            } else {
                document.getElementById('btnAnalyze').innerHTML = '🔍 开始分析';
            }
        }

        async function refreshStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                updateStatus(data);
                addLog('状态已刷新', 'info');
            } catch (error) {
                addLog('刷新状态失败: ' + error.message, 'error');
            }
        }

        async function runAnalysis() {
            if (!confirm('确定要开始分析吗？')) return;

            addLog('开始分析...', 'info');
            document.getElementById('btnAnalyze').disabled = true;
            document.getElementById('btnAnalyze').innerHTML = '<span class="spinner"></span> 分析中...';

            try {
                const response = await fetch('/api/analyze', { method: 'POST' });
                const data = await response.json();

                if (data.success) {
                    addLog('分析完成！', 'success');
                    refreshStatus();
                } else {
                    addLog('分析失败: ' + data.error, 'error');
                }
            } catch (error) {
                addLog('请求失败: ' + error.message, 'error');
            }

            document.getElementById('btnAnalyze').disabled = false;
            document.getElementById('btnAnalyze').innerHTML = '🔍 开始分析';
        }

        async function runAndPush() {
            if (!confirm('确定要分析并推送到微信吗？')) return;

            addLog('开始分析并推送...', 'info');
            document.getElementById('btnPush').disabled = true;

            try {
                const response = await fetch('/api/analyze-and-push', { method: 'POST' });
                const data = await response.json();

                if (data.success) {
                    addLog('分析并推送完成！', 'success');
                    if (data.push_result) {
                        addLog('推送结果: ' + (data.push_result.success ? '成功' : '失败'), data.push_result.success ? 'success' : 'error');
                    }
                    refreshStatus();
                } else {
                    addLog('失败: ' + data.error, 'error');
                }
            } catch (error) {
                addLog('请求失败: ' + error.message, 'error');
            }

            document.getElementById('btnPush').disabled = false;
        }

        // 自动刷新状态
        refreshInterval = setInterval(refreshStatus, 30000);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """主页"""
    return render_template_string(
        HTML_TEMPLATE,
        status=analysis_status,
        config=config,
        logs=analysis_status.get('logs', [])
    )


@app.route('/api/status')
def api_status():
    """获取状态API"""
    return jsonify({
        "running": analysis_status["running"],
        "last_run": analysis_status["last_run"],
        "error": analysis_status["error"]
    })


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """分析API"""
    if analysis_status["running"]:
        return jsonify({"success": False, "error": "分析正在进行中"})

    def run_analysis():
        analysis_status["running"] = True
        analysis_status["error"] = None
        analysis_status["logs"] = []

        try:
            analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 开始分析...")
            results = analyze_all_funds()
            analysis_status["last_result"] = results
            analysis_status["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 分析完成，共分析{len(results)}只基金")
        except Exception as e:
            analysis_status["error"] = str(e)
            analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 错误: {str(e)}")
        finally:
            analysis_status["running"] = False

    thread = threading.Thread(target=run_analysis)
    thread.start()

    return jsonify({"success": True, "message": "分析已开始"})


@app.route('/api/analyze-and-push', methods=['POST'])
def api_analyze_and_push():
    """分析并推送API"""
    if analysis_status["running"]:
        return jsonify({"success": False, "error": "分析正在进行中"})

    def run_analysis_and_push():
        analysis_status["running"] = True
        analysis_status["error"] = None
        analysis_status["logs"] = []

        try:
            analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 开始分析...")
            results = analyze_all_funds()
            analysis_status["last_result"] = results
            analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 分析完成，共分析{len(results)}只基金")

            # 推送
            if config.pushplus_token:
                analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 开始推送...")
                notifier = create_notifier()
                push_result = notifier.send_daily_report(results)
                analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 推送{'成功' if push_result else '失败'}")
            else:
                analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 未配置PushPlus Token，跳过推送")

            analysis_status["last_run"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            analysis_status["error"] = str(e)
            analysis_status["logs"].append(f"[{datetime.now().strftime('%H:%M:%S')}] 错误: {str(e)}")
        finally:
            analysis_status["running"] = False

    thread = threading.Thread(target=run_analysis_and_push)
    thread.start()

    return jsonify({"success": True, "message": "分析并推送已开始"})


def run_web_app(host='0.0.0.0', port=5000, debug=False):
    """运行Web应用"""
    print(f"🚀 启动Web服务: http://localhost:{port}")
    print(f"📊 控制面板: http://localhost:{port}")
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_web_app(debug=True)
