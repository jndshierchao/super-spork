#!/bin/bash

# AI工具集 - 每日自动更新脚本
# 运行方式: ./update.sh

echo "========== AI工具集 自动更新 =========="
echo "更新时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 检查网络
echo "[1/4] 检查网络连接..."
if curl -s -o /dev/null -w "%{http_code}" https://github.com | grep -q "200"; then
    echo "✓ 网络连接正常"
else
    echo "✗ 网络连接失败"
    exit 1
fi

# 2. 提交更改
echo "[2/4] 提交网站更新..."
cd /Users/moxu/CodeBuddy/Claw
git add index.html
git commit -m "每日更新: $(date '+%Y-%m-%d')" 2>/dev/null || echo "无新内容需要提交"

# 3. 推送到GitHub
echo "[3/4] 推送到GitHub..."
git push origin gh-pages 2>&1

# 4. 检查部署状态
echo "[4/4] 检查网站状态..."
sleep 5
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://smallthings.cn)
if [ "$STATUS" = "200" ]; then
    echo "✓ 网站部署成功！"
else
    echo "⚠ 网站状态码: $STATUS"
fi

echo ""
echo "========== 更新完成 =========="
echo "网站地址: https://smallthings.cn"
echo "GitHub: https://github.com/jndshierchao/super-spork"
