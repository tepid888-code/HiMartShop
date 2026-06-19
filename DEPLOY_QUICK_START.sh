#!/bin/bash
# 🚀 Hi Mart 云部署 - 快速参考卡片

cat << 'EOF'

╔══════════════════════════════════════════════════════════════════╗
║                  🚀 Hi Mart 云部署快速参考                       ║
╚══════════════════════════════════════════════════════════════════╝

📍 目标服务器信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  服务器 IP: 64.181.193.238
  域名: mail.aitepid.crabdance.com
  操作系统: Ubuntu 24.04 LTS
  用户: ubuntu
  项目目录: /home/ubuntu/himart

【第 1 步】连接到云服务器
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ssh ubuntu@64.181.193.238
  [输入密码或使用密钥]

【第 2 步】准备项目文件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # 在本地执行（上传项目文件）
  scp -r ./webshop ubuntu@64.181.193.238:/home/ubuntu/himart

  # 或者在云服务器上 clone
  cd /home/ubuntu
  git clone <your-repo-url> himart
  cd himart

【第 3 步】运行部署脚本
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  cd /home/ubuntu/himart
  chmod +x deploy-to-cloud.sh
  ./deploy-to-cloud.sh

  ⏱️  预计耗时: 20-30 分钟

【第 4 步】验证部署
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # 检查服务状态
  sudo supervisorctl status

  # 查看后端日志
  sudo tail -50 /var/log/supervisor/himart-backend.log

  # 测试 API
  curl http://localhost:8000/api/products/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 部署完成后访问地址
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔗 前端应用: https://mail.aitepid.crabdance.com
  🔗 API 文档: https://mail.aitepid.crabdance.com/api/schema/
  🔗 管理后台: https://mail.aitepid.crabdance.com/admin

  👤 登录用户名: admin
  🔑 登录密码: admin123456

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️  常见问题快速排查
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  【502 Bad Gateway】
  ▶ sudo supervisorctl restart himart:*

  【数据库连接错误】
  ▶ sudo systemctl restart postgresql

  【前端页面 404】
  ▶ cd /home/ubuntu/himart/frontend
    npm run build

  【Redis 错误】
  ▶ sudo systemctl restart redis-server

  【查看完整日志】
  ▶ tail -f /var/log/supervisor/himart-backend.log

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 部署脚本自动执行清单
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ 系统更新和依赖安装
  ✅ PostgreSQL 数据库配置
  ✅ Redis 缓存配置
  ✅ 后端环境配置
  ✅ 前端构建
  ✅ Nginx 反向代理配置
  ✅ SSL/TLS 证书配置
  ✅ Supervisor 进程管理
  ✅ 自动启动配置
  ✅ 完整性验证

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔒 部署后安全操作
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. 登录管理后台: https://mail.aitepid.crabdance.com/admin
  2. 更改管理员密码:
     python manage.py changepassword admin
  3. 创建其他用户账户（可选）
  4. 验证 HTTPS 证书有效性

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 监控和维护命令
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  # 实时查看后端日志
  tail -f /var/log/supervisor/himart-backend.log

  # 查看 Nginx 错误日志
  tail -f /var/log/nginx/error.log

  # 查看服务状态
  sudo supervisorctl status

  # 重启单个服务
  sudo supervisorctl restart himart-backend

  # 查看系统资源
  free -h && df -h && top -bn1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💾 定期维护清单
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  【每日】
  ▶ 检查服务状态: sudo supervisorctl status

  【每周】
  ▶ 数据库备份: pg_dump himart_db | gzip > backup.sql.gz
  ▶ 检查磁盘: df -h
  ▶ 检查日志: journalctl -u nginx -n 100

  【每月】
  ▶ 系统更新: sudo apt-get update && apt-get upgrade
  ▶ 清理日志: sudo journalctl --vacuum=time=30d
  ▶ 性能检查: python performance_benchmark.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ 部署成功指标
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ 能访问 HTTPS 主页
  ✓ API 返回 200 状态码
  ✓ 管理后台可登录
  ✓ 数据库有数据
  ✓ 缓存正常工作
  ✓ SSL 证书有效
  ✓ 所有进程正在运行

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 详细文档位置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • CLOUD_DEPLOYMENT_GUIDE.md - 完整部署指南
  • DEPLOYMENT_CHECKLIST.md - 部署检查清单
  • INTEGRATION_TEST_GUIDE.md - 测试指南
  • PERFORMANCE_OPTIMIZATION.md - 性能优化
  • deploy-to-cloud.sh - 自动化部署脚本

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🆘 需要帮助？
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. 查看相关日志文件
  2. 检查常见问题部分
  3. 运行诊断脚本
  4. 查看详细部署指南

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

部署状态: 🎊 准备就绪 🎊

版本: v1.0 Production Ready
最后更新: 2026-06-19
维护者: DevOps Team

╔══════════════════════════════════════════════════════════════════╗
║              祝部署成功！🚀 系统正式上线！                        ║
╚══════════════════════════════════════════════════════════════════╝

EOF
