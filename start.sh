#!/bin/bash
set -e

echo ""
echo "🚀 104 高年級 友善企業品牌頁開發工具"
echo "============================================"

# 檢查 ANTHROPIC_API_KEY
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "⚠️  請先設定 ANTHROPIC_API_KEY："
  echo "   export ANTHROPIC_API_KEY=sk-ant-..."
  echo ""
  read -p "或直接輸入你的 API Key: " key
  if [ -z "$key" ]; then
    echo "❌ 未提供 API Key，終止"
    exit 1
  fi
  export ANTHROPIC_API_KEY="$key"
fi

echo "✅ API Key 已就緒"
echo ""

# 安裝依賴
echo "📦 安裝 Python 套件..."
pip3 install -q flask flask-cors anthropic

echo "✅ 套件安裝完成"
echo ""

# 啟動伺服器並開啟瀏覽器
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "🌐 開啟瀏覽器中..."
sleep 1
open "$DIR/index.html" &

echo "🔄 啟動後端伺服器（Ctrl+C 停止）..."
python3 "$DIR/server.py"
