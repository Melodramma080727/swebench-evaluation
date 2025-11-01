# SWE-bench Evaluation on GitHub Actions

这个仓库用于在 GitHub Actions 的 x86_64 环境下运行 SWE-bench 评估，解决 ARM64 平台的兼容性问题。

## 🚀 快速开始

### 1. 创建 GitHub 仓库

在 GitHub 上创建一个新仓库（可以是私有的），然后：

```bash
cd /home/yutong/Agents/swebench_evaluation
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git add .
git commit -m "Initial commit: SWE-bench evaluation setup"
git push -u origin master
```

### 2. 设置 Anthropic API Key（可选）

如果你需要使用 Anthropic API 生成 patches：

1. 进入 GitHub 仓库设置页面
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. Name: `ANTHROPIC_API_KEY`
5. Value: 你的 API key
6. 点击 **Add secret**

### 3. 添加预测文件

将你的预测文件放入 `predictions/` 目录：

```bash
mkdir -p predictions
cp /home/yutong/swebench_results/api_predictions_v2_20251101_012012.jsonl predictions/
git add predictions/
git commit -m "Add prediction files"
git push
```

### 4. 手动触发评估

1. 进入 GitHub 仓库页面
2. 点击 **Actions** 标签
3. 选择 **SWE-bench Evaluation** workflow
4. 点击右侧的 **Run workflow** 按钮
5. （可选）输入参数：
   - **Instance IDs**: 留空使用默认的 3 个测试实例
   - **Max workers**: 并行工作数（建议保持 1）
6. 点击绿色的 **Run workflow** 按钮

### 5. 查看结果

评估完成后（约 5-10 分钟）：

1. 在 Actions 页面找到你的 workflow run
2. 滚动到底部的 **Artifacts** 部分
3. 下载：
   - `swebench-results`: 包含 JSON 格式的评估结果
   - `swebench-logs`: 包含详细的执行日志

## 📁 目录结构

```
.
├── .github/
│   └── workflows/
│       └── swebench_eval.yml   # GitHub Actions 工作流配置
├── predictions/                 # 放置你的预测文件（.jsonl）
│   └── *.jsonl
└── README.md                    # 本文件
```

## 🔧 工作流说明

GitHub Actions 会自动：

1. ✅ 在 Ubuntu x86_64 环境下运行
2. ✅ 安装 Python 3.10
3. ✅ 克隆并安装 SWE-bench
4. ✅ 升级 Docker 包到 7.1.0
5. ✅ 运行评估（使用你的 prediction 文件或 gold predictions）
6. ✅ 保存结果和日志为 artifacts

## 📊 评估指标

结果 JSON 文件包含：
- `total_instances`: 总实例数
- `completed_instances`: 完成的实例数
- `resolved_instances`: 成功解决的实例数
- `error_instances`: 出错的实例数
- `resolved_ids`: 成功解决的实例 ID 列表
- `error_ids`: 出错的实例 ID 列表

## 🆓 费用

- 公开仓库：**完全免费**（每月 2000 分钟）
- 私有仓库：每月 2000 分钟免费额度
- 每次运行约消耗 5-10 分钟

## 🐛 故障排除

### 评估失败
- 检查 Docker 是否正常运行
- 查看 `swebench-logs` artifact 中的详细日志
- 确认 prediction 文件格式正确

### API Key 错误
- 确认已在仓库 Secrets 中添加 `ANTHROPIC_API_KEY`
- 检查 API key 是否有效

### 容器问题
- GitHub Actions 使用 x86_64，不会有 ARM64 兼容问题
- 如果仍有问题，检查 SWE-bench 版本是否最新

## 📝 本地测试 vs GitHub Actions

| 特性 | ARM64 本地机器 | GitHub Actions x86_64 |
|------|---------------|----------------------|
| 架构 | ❌ ARM64 (不兼容) | ✅ x86_64 (兼容) |
| 容器稳定性 | ❌ 容器频繁退出 | ✅ 稳定运行 |
| 成本 | 免费 | 免费（有额度限制） |
| 速度 | 本地快 | 网络延迟 |
| 适用场景 | 开发测试 | 正式评估 |

## 🔗 相关链接

- [SWE-bench GitHub](https://github.com/SWE-bench/SWE-bench)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [SWE-bench 论文](https://arxiv.org/abs/2310.06770)
