# 🚀 GitHub Actions 使用步骤

## 第一步：创建 GitHub 仓库

1. **打开浏览器，访问**：https://github.com/new
2. **填写仓库信息**：
   - Repository name: `swebench-evaluation` （或任何你喜欢的名字）
   - Description: `SWE-bench evaluation on x86_64 via GitHub Actions`
   - 选择 **Public**（推荐，免费额度更多）或 **Private**
   - **不要**勾选 "Add a README file"、"Add .gitignore"、"Choose a license"
3. **点击绿色按钮**：`Create repository`

## 第二步：推送代码到 GitHub

创建仓库后，GitHub 会显示一个页面。复制下面的命令到你的终端运行：

```bash
cd /home/yutong/Agents/swebench_evaluation

# 替换成你刚创建的仓库地址
git remote add origin https://github.com/Melodramma080727/swebench-evaluation.git

# 重命名分支为 main
git branch -M main

# 推送代码
git push -u origin main
```

**注意**：把上面的 `Melodramma080727/swebench-evaluation` 替换成你实际创建的仓库名！

## 第三步：添加 API Key（可选，如果要用 API 生成 patches）

1. 在 GitHub 仓库页面，点击顶部的 **Settings** 标签
2. 左侧菜单找到 **Secrets and variables** → 点击 **Actions**
3. 点击绿色按钮 **New repository secret**
4. 填写：
   - Name: `ANTHROPIC_API_KEY`
   - Secret: 粘贴你的 Anthropic API key
5. 点击 **Add secret**

## 第四步：运行评估

### 方式 1：手动触发（推荐）

1. **进入仓库页面**
2. **点击顶部的 Actions 标签**
3. **左侧选择 "SWE-bench Evaluation"**
4. **右侧点击 "Run workflow" 按钮**（灰色下拉菜单）
5. **选择分支**：main
6. **可选参数**：
   - Instance IDs: 留空（会自动评估 3 个测试实例）
   - Max workers: 1
7. **点击绿色的 "Run workflow" 按钮**

### 方式 2：自动触发

每次你推送新的 prediction 文件到 `predictions/` 目录时，会自动触发评估：

```bash
cd /home/yutong/Agents/swebench_evaluation
cp /path/to/new_predictions.jsonl predictions/
git add predictions/
git commit -m "Add new predictions"
git push
```

## 第五步：查看运行状态

1. **在 Actions 页面**，你会看到一个黄色的圆点 🟡 表示正在运行
2. **点击这个 workflow run** 进入详情页
3. **点击左侧的 "evaluate" 作业**
4. **展开每个步骤** 查看实时日志
5. **等待评估完成**（约 5-10 分钟）
   - ✅ 绿色勾：成功
   - ❌ 红色叉：失败

## 第六步：下载结果

评估完成后：

1. **滚动到页面底部** "Artifacts" 部分
2. **下载两个文件**：
   - **swebench-results**: 评估结果（JSON 格式）
   - **swebench-logs**: 详细日志
3. **解压 ZIP 文件** 查看内容

### 结果文件示例

`swebench-results` 中的 JSON 文件内容类似：

```json
{
    "total_instances": 300,
    "submitted_instances": 3,
    "completed_instances": 3,
    "resolved_instances": 1,
    "error_instances": 0,
    "resolved_ids": [
        "astropy__astropy-12907"
    ],
    "error_ids": []
}
```

## 🎯 关键指标说明

- **completed_instances**: 成功运行的实例数
- **resolved_instances**: 你的 patch 成功修复的 bug 数量 ⭐ **这是最重要的指标**
- **error_instances**: 运行出错的实例数
- **resolved_ids**: 具体是哪些 bug 被修复了

## 💡 提示

1. **免费额度**：公开仓库每月 2000 分钟，足够运行很多次
2. **运行时间**：每次约 5-10 分钟（取决于实例数量）
3. **并行运行**：可以同时运行多个 workflow，但会消耗更多额度
4. **日志保留**：结果保留 30 天，日志保留 7 天

## 🐛 如果出错了

1. **检查 Actions 日志**：点击失败的步骤查看错误信息
2. **常见问题**：
   - Docker 容器问题：GitHub Actions 是 x86_64，不会有 ARM64 问题
   - API key 错误：确认 Secret 名称是 `ANTHROPIC_API_KEY`
   - Prediction 文件格式：确保是有效的 JSONL 格式
3. **重新运行**：在 workflow run 页面右上角点击 "Re-run jobs"

## 📱 手机也能查看！

GitHub 有手机 App，你可以：
- 实时查看运行状态
- 收到完成通知
- 下载结果文件

---

**准备好了吗？现在去创建你的 GitHub 仓库吧！** 🚀
