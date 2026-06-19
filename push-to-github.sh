#!/bin/bash
# Hi Mart GitHub推送脚本

echo "🚀 Hi Mart项目推送到GitHub..."

# 清除凭据缓存
git credential reject host=github.com protocol=https 2>/dev/null

# 配置远程（使用token在URL中）
git remote remove origin 2>/dev/null
git remote add origin "https://x-access-token:${GIT_TOKEN}@github.com/luckysong-sudo/HiMartShop.git"

# 推送
echo "📤 正在推送代码..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ 推送成功！"
    echo "仓库地址: https://github.com/luckysong-sudo/HiMartShop"
else
    echo "❌ 推送失败"
    exit 1
fi
