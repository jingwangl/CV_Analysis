# 阿里云 DashScope API Key 获取与配置指南

## 一、获取 API Key

### 步骤 1：注册/登录阿里云账号
1. 访问 [阿里云官网](https://www.aliyun.com/)
2. 如果没有账号，请先注册并完成实名认证
3. 如果已有账号，直接登录

### 步骤 2：开通百炼服务（DashScope）
1. 访问 [百炼控制台](https://dashscope.console.aliyun.com/)
2. 如果页面顶部显示需要开通服务的提示，请按照指引开通百炼的模型服务
3. 新用户通常有免费额度可以使用

### 步骤 3：创建 API Key
1. 在百炼控制台，点击右上角的 **"API-KEY"** 选项
2. 点击 **"创建新的 API-KEY"** 按钮
3. 系统将生成一个新的 API Key，**请立即复制并妥善保存**
   - ⚠️ **重要**：API Key 只显示一次，关闭后无法再次查看
   - 如果丢失，需要删除旧 Key 并重新创建

## 二、在函数计算中配置 API Key

### 方法 1：通过阿里云控制台配置（推荐）

1. 登录 [阿里云函数计算控制台](https://fcnext.console.aliyun.com/)
2. 找到你的函数：`cv-analysis-api`
3. 进入函数详情页
4. 点击左侧菜单 **"环境变量"**
5. 点击 **"新增环境变量"**
6. 填写：
   - **变量名**：`DASHSCOPE_API_KEY`
   - **变量值**：粘贴你刚才复制的 API Key
7. 点击 **"确定"** 保存
8. 等待几秒钟让配置生效

### 方法 2：通过 s.yaml 配置（需要重新部署）

如果你想在 `s.yaml` 中配置，可以这样修改：

```yaml
environmentVariables:
  DASHSCOPE_API_KEY: 'your-api-key-here'
```

⚠️ **注意**：这种方式会将 API Key 暴露在配置文件中，安全性较低，不推荐。

### 方法 3：通过 Serverless Devs CLI 配置

```bash
s env set DASHSCOPE_API_KEY=your-api-key-here
```

## 三、验证配置

配置完成后，可以通过以下方式验证：

1. **查看函数日志**：
   - 在函数计算控制台查看函数日志
   - 如果看到 "AI 分析功能已启用（DashScope）" 的日志，说明配置成功

2. **测试 API**：
   - 上传简历并输入岗位描述
   - 如果返回结果中包含 `ai_analysis` 字段且不为空，说明 AI 分析功能正常工作

## 四、费用说明

- 新用户通常有免费额度（具体额度以阿里云官方公告为准）
- 超出免费额度后，按实际使用量计费
- 建议在控制台查看使用情况和费用

## 五、安全建议

1. ✅ **不要**将 API Key 提交到 Git 仓库
2. ✅ **不要**在前端代码中暴露 API Key
3. ✅ 定期更换 API Key
4. ✅ 如果 API Key 泄露，立即删除并重新创建

## 六、常见问题

### Q: API Key 在哪里查看？
A: 在 [百炼控制台](https://dashscope.console.aliyun.com/) 右上角的 "API-KEY" 选项中。

### Q: 配置后还是提示未启用 AI？
A: 
1. 检查环境变量名称是否正确：`DASHSCOPE_API_KEY`（全大写）
2. 检查环境变量值是否正确（没有多余空格）
3. 等待几分钟让配置生效
4. 查看函数日志确认是否有错误

### Q: 没有 API Key 可以使用吗？
A: 可以！系统会自动回退到传统匹配算法，功能仍然可用，只是没有 AI 深度分析部分。

### Q: API Key 有使用限制吗？
A: 具体限制请查看阿里云 DashScope 的官方文档，通常有 QPS（每秒请求数）限制。

## 七、相关链接

- [百炼控制台](https://dashscope.console.aliyun.com/)
- [DashScope API 文档](https://help.aliyun.com/zh/dashscope/)
- [函数计算控制台](https://fcnext.console.aliyun.com/)

