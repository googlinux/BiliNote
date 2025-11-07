# BiliNote SaaS Testing Guide

完整的测试指南，包含前后端测试流程。

---

## 📋 目录

1. [环境准备](#环境准备)
2. [后端API测试](#后端api测试)
3. [前端功能测试](#前端功能测试)
4. [端到端测试场景](#端到端测试场景)
5. [常见问题](#常见问题)

---

## 环境准备

### 1. 启动后端服务器

```bash
cd backend

# 安装依赖（首次运行）
pip install -r requirements.txt

# 初始化数据库（首次运行）
python -m app.db.init_db

# 启动服务器
uvicorn app.main:app --reload --port 8483
```

服务器应该运行在: `http://localhost:8483`

### 2. 启动前端开发服务器

```bash
cd saas-web

# 安装依赖（首次运行）
pnpm install

# 启动开发服务器
pnpm dev
```

前端应该运行在: `http://localhost:3000`

---

## 后端API测试

### 自动化测试脚本

运行完整的API集成测试：

```bash
cd backend
python tests/test_api.py
```

测试内容包括：
- ✅ 服务器健康检查
- ✅ 用户注册
- ✅ 用户登录
- ✅ 获取当前用户信息
- ✅ 获取订阅信息
- ✅ 获取使用统计
- ✅ 获取可用计划
- ✅ Token刷新
- ✅ 未授权访问保护

### 手动API测试（使用curl）

#### 1. 注册新用户

```bash
curl -X POST http://localhost:8483/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234!",
    "full_name": "Test User"
  }'
```

预期响应：
```json
{
  "code": 200,
  "msg": "Registration successful. Welcome to BiliNote!",
  "data": {
    "id": 1,
    "email": "test@example.com",
    "full_name": "Test User",
    "is_active": true
  }
}
```

#### 2. 用户登录

```bash
curl -X POST http://localhost:8483/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test1234!"
  }'
```

预期响应：
```json
{
  "code": 200,
  "msg": "Success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
  }
}
```

**保存access_token用于后续请求！**

#### 3. 获取当前用户信息

```bash
curl -X GET http://localhost:8483/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### 4. 获取订阅信息

```bash
curl -X GET http://localhost:8483/api/subscription/current \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

预期响应：
```json
{
  "code": 200,
  "msg": "Success",
  "data": {
    "id": 1,
    "user_id": 1,
    "plan_type": "free",
    "status": "active",
    "max_videos_per_month": 5,
    "max_video_duration_minutes": 10,
    "videos_used": 0,
    "duration_used_minutes": 0
  }
}
```

#### 5. 获取所有计划

```bash
curl -X GET http://localhost:8483/api/subscription/plans
```

#### 6. 管理员统计（需要管理员账号）

```bash
# 首先注册一个管理员邮箱账号（admin@localhost）
curl -X POST http://localhost:8483/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@localhost",
    "password": "Admin1234!",
    "full_name": "Admin User"
  }'

# 登录获取管理员token
curl -X POST http://localhost:8483/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@localhost",
    "password": "Admin1234!"
  }'

# 获取系统统计
curl -X GET http://localhost:8483/api/admin/stats \
  -H "Authorization: Bearer ADMIN_ACCESS_TOKEN"
```

---

## 前端功能测试

### 测试场景列表

访问: `http://localhost:3000`

#### 1. 首页加载测试
- [ ] 页面正常加载，无控制台错误
- [ ] Hero部分显示正确
- [ ] Features部分显示4-6个特性
- [ ] Pricing部分显示4个计划（Free/Basic/Pro/Enterprise）
- [ ] FAQ部分可展开/收起
- [ ] CTA按钮可点击

#### 2. 用户注册流程
1. 点击"Get Started"或"Sign Up"
2. 访问: `http://localhost:3000/auth/register`
3. 填写表单：
   - Email: test@example.com
   - Password: Test1234!
   - Full Name: Test User
4. 勾选同意条款
5. 点击"Create Account"
6. **预期结果**:
   - [ ] 显示成功Toast通知
   - [ ] 自动跳转到Dashboard
   - [ ] 欢迎邮件发送（如果配置了SMTP）

#### 3. 用户登录流程
1. 访问: `http://localhost:3000/auth/login`
2. 输入凭据：
   - Email: test@example.com
   - Password: Test1234!
3. 点击"Sign In"
4. **预期结果**:
   - [ ] 显示"Welcome back!"Toast
   - [ ] 跳转到Dashboard
   - [ ] 显示用户邮箱

#### 4. Dashboard功能测试
访问: `http://localhost:3000/dashboard`

检查项：
- [ ] 显示用户名/邮箱
- [ ] 显示当前计划（Free）
- [ ] 显示使用统计（0/5 videos）
- [ ] 显示快速操作卡片
- [ ] "Generate Note"按钮可见
- [ ] "Billing"按钮可见
- [ ] "Settings"按钮可见
- [ ] 对Free用户显示升级横幅

#### 5. 计费页面测试
访问: `http://localhost:3000/dashboard/settings/billing`

检查项：
- [ ] 显示当前订阅状态
- [ ] 显示使用配额
- [ ] 显示所有可用计划
- [ ] 每个计划有月付/年付选项
- [ ] 点击"Subscribe Monthly"显示加载状态

#### 6. Stripe结账流程测试（需要配置Stripe）

**前提**: 在`.env`中配置Stripe测试密钥

1. 在Billing页面点击"Subscribe Monthly"（Basic计划）
2. **预期结果**:
   - [ ] 重定向到Stripe结账页面
   - [ ] 页面显示正确的金额和计划
3. 使用Stripe测试卡号：`4242 4242 4242 4242`
   - Expiry: 12/34
   - CVC: 123
   - ZIP: 12345
4. 完成支付
5. **预期结果**:
   - [ ] 重定向回Billing页面
   - [ ] 显示"Payment Successful!"Toast
   - [ ] 订阅状态更新为"Active"
   - [ ] 计划显示为"Basic"
   - [ ] 配额更新为100 videos/month
   - [ ] 支付成功邮件发送

#### 7. 客户门户测试
1. 在Billing页面点击"Manage Billing"
2. **预期结果**:
   - [ ] 重定向到Stripe客户门户
   - [ ] 可以查看发票
   - [ ] 可以更新支付方式
   - [ ] 可以取消订阅

#### 8. 登出测试
1. 在Dashboard点击"Logout"
2. **预期结果**:
   - [ ] 清除本地存储
   - [ ] 跳转到首页
   - [ ] 再次访问`/dashboard`应跳转到登录页

---

## 端到端测试场景

### 场景1: 新用户完整流程

**目标**: 测试从注册到生成笔记的完整流程

1. **注册** → 访问首页 → 点击"Get Started"
2. **填写注册表单** → 提交
3. **验证Dashboard** → 检查Free计划配额
4. **升级到付费计划** → 访问Billing → 选择Basic计划
5. **完成Stripe支付** → 使用测试卡
6. **验证升级成功** → 检查配额更新
7. **生成笔记** → （需要实现笔记生成UI）
8. **检查配额消耗** → 验证使用统计更新

### 场景2: 订阅管理流程

**目标**: 测试订阅生命周期

1. **登录已有账号**
2. **订阅Basic计划** → 月付$9
3. **验证订阅激活**
4. **访问客户门户** → 更新支付方式
5. **取消订阅**
6. **验证降级** → 检查是否回到Free计划
7. **接收取消邮件** → 确认邮件内容

### 场景3: Token刷新测试

**目标**: 测试自动token刷新

1. **登录用户**
2. **打开浏览器开发工具** → Network标签
3. **等待token过期** （设置短过期时间测试）
4. **执行任何API请求** （如刷新Dashboard）
5. **验证**:
   - [ ] 看到401响应
   - [ ] 看到自动refresh请求
   - [ ] 看到重试原始请求
   - [ ] 请求成功完成

### 场景4: 错误处理测试

**目标**: 测试各种错误情况

1. **测试网络错误**:
   - 停止后端服务器
   - 尝试登录
   - 验证显示友好错误消息

2. **测试验证错误**:
   - 使用弱密码注册（少于8字符）
   - 验证显示密码要求错误

3. **测试重复注册**:
   - 使用已存在邮箱注册
   - 验证显示"Email already registered"

4. **测试配额超限**:
   - 使用Free账号
   - 尝试生成第6个笔记（超过5个限制）
   - 验证显示配额超限错误

---

## 性能测试

### 前端加载性能

```bash
# 使用Lighthouse测试（Chrome DevTools）
1. 打开Chrome DevTools
2. 切换到Lighthouse标签
3. 选择"Performance"
4. 点击"Analyze page load"

目标指标：
- Performance: >90
- Accessibility: >90
- Best Practices: >90
- SEO: >90
```

### API响应时间测试

```bash
# 使用Apache Bench测试
ab -n 100 -c 10 http://localhost:8483/api/subscription/plans

# 目标:
# - 平均响应时间 < 100ms
# - 99th percentile < 500ms
# - 0% 失败率
```

---

## 邮件测试

### 配置测试邮件服务器

使用MailHog进行本地邮件测试：

```bash
# 使用Docker运行MailHog
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# 在backend/.env中配置:
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=test
SMTP_PASSWORD=test
EMAILS_FROM_EMAIL=noreply@bilinote.app
```

访问MailHog UI: `http://localhost:8025`

### 测试邮件类型

1. **欢迎邮件** - 注册新用户时发送
2. **支付成功邮件** - 完成Stripe支付后发送
3. **支付失败邮件** - 支付失败时发送
4. **订阅取消邮件** - 取消订阅时发送

---

## 移动端测试

### 响应式设计检查

使用Chrome DevTools测试不同设备：

1. 打开DevTools (F12)
2. 点击设备工具栏图标
3. 测试以下设备：
   - iPhone 12 Pro (390x844)
   - iPad Air (820x1180)
   - Galaxy S20 (360x800)

检查项：
- [ ] 导航菜单在移动端正常工作
- [ ] 表单在小屏幕上可用
- [ ] 图片正确缩放
- [ ] 文字可读
- [ ] 按钮可点击（足够大）
- [ ] Toast通知正确显示

---

## 常见问题

### Q: 测试脚本报错"Connection refused"

A: 确保后端服务器正在运行：
```bash
cd backend
uvicorn app.main:app --reload --port 8483
```

### Q: 前端页面白屏

A: 检查控制台错误，可能的原因：
1. API URL配置错误 - 检查`.env.local`
2. 后端未启动
3. CORS配置问题

### Q: Stripe测试付款失败

A: 确认：
1. `.env`中配置了正确的Stripe测试密钥
2. 使用Stripe测试卡号：`4242 4242 4242 4242`
3. Webhook已配置（使用Stripe CLI或ngrok）

### Q: Toast通知不显示

A: 检查：
1. `<Toaster />`组件已添加到layout.tsx
2. 没有CSS冲突隐藏toast
3. 检查浏览器控制台错误

### Q: 管理员API返回403

A: 确认：
1. 使用的是管理员邮箱（admin@localhost或admin@bilinote.app）
2. Token未过期
3. 请求头包含正确的Authorization

---

## 测试检查清单

### 发布前必须测试

- [ ] 所有API测试通过
- [ ] 用户注册和登录工作正常
- [ ] Dashboard正确显示用户信息
- [ ] Billing页面显示所有计划
- [ ] Toast通知在所有操作中显示
- [ ] 移动端响应式布局正常
- [ ] 错误情况有友好提示
- [ ] 邮件正确发送（如配置SMTP）
- [ ] 性能指标达标

### 生产环境测试

- [ ] 使用PostgreSQL数据库
- [ ] Stripe实时模式支付
- [ ] 实际域名CORS配置
- [ ] HTTPS连接
- [ ] 真实邮件发送
- [ ] 错误监控（Sentry等）
- [ ] 性能监控
- [ ] 备份恢复测试

---

## 测试报告模板

```markdown
## 测试报告

**日期**: YYYY-MM-DD
**测试人员**: Your Name
**环境**: Development/Staging/Production

### 测试结果摘要

- 总测试用例: X
- 通过: Y
- 失败: Z
- 跳过: W

### 详细结果

#### 后端API测试
- ✅ 用户注册
- ✅ 用户登录
- ❌ Token刷新（错误详情）
- ...

#### 前端功能测试
- ✅ 首页加载
- ✅ Dashboard
- ✅ Billing页面
- ...

### 发现的问题

1. **问题描述**
   - 重现步骤
   - 预期行为
   - 实际行为
   - 截图（如有）

### 建议

- 建议1
- 建议2

### 结论

测试是否通过，是否可以发布。
```

---

**最后更新**: 2025-11-07

完成测试后，请确保所有功能正常运行再进行部署！
