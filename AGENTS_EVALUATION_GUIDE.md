# SWE-bench Agents Framework Evaluation

本项目用于在 GitHub Actions 上评估 Agents 框架在 SWE-bench 上的性能。

## 📊 两种评估方案

### 1. 简化 API 评估（已完成 ✅）

**Workflow**: `swebench_eval.yml`

**结果**: 
- ✅ 3/3 instances resolved (100% 成功率)
- 使用直接 API 调用 + 改进的 prompt
- 验证了评估环境完全正常

**文件**: 
- Predictions: `predictions/api_predictions_v2_20251101_061646.jsonl`
- 测试实例: astropy__astropy-12907, astropy__astropy-14182, astropy__astropy-14365

### 2. Agents 框架完整评估（新增 🆕）

**Workflow**: `swebench_agents_eval.yml`

**特点**:
- 使用 Agents 框架风格的 prompts
- 两阶段 workflow：生成 patches → 评估
- 支持配置实例数量（3个测试 / 300个完整）
- 完全在 x86_64 GitHub Actions 环境运行

## 🚀 使用方法

### 方式 1: GitHub UI 手动触发

1. 访问: https://github.com/Melodramma080727/swebench-evaluation/actions
2. 选择 "SWE-bench Agents Framework Evaluation"
3. 点击 "Run workflow"
4. 配置参数：
   - `num_instances`: 3（测试）或 300（完整评估）
   - `max_workers`: 1（推荐）或更多
5. 点击 "Run workflow" 开始

### 方式 2: GitHub CLI

```bash
gh workflow run swebench_agents_eval.yml \
    -f num_instances=3 \
    -f max_workers=1
```

### 方式 3: 自动触发

修改 `predictions/` 目录下的文件并 push 会自动触发简化版评估。

## 📋 Workflow 详情

### Job 1: Generate Patches (生成补丁)

- **环境**: Ubuntu latest (x86_64)
- **时间限制**: 2 小时
- **步骤**:
  1. 安装 Python 3.12 和依赖
  2. 配置 Anthropic API
  3. 加载 SWE-bench_Lite 数据集
  4. 使用 Agents 风格的 prompts 生成 patches
  5. 上传 predictions 作为 artifact

### Job 2: Evaluate Patches (评估补丁)

- **环境**: Ubuntu latest (x86_64)
- **时间限制**: 1 小时
- **步骤**:
  1. 安装 SWE-bench harness
  2. 下载 Job 1 生成的 predictions
  3. 在 Docker 容器中运行评估
  4. 上传结果（JSON + logs）

## 📊 预期结果

### 测试模式（3 instances）

- **运行时间**: ~10-15 分钟
- **成本**: GitHub Actions 免费额度内
- **目的**: 快速验证 pipeline 正常工作

### 完整评估（300 instances）

- **运行时间**: ~2-4 小时
- **成本**: 使用约 120-240 分钟的 GitHub Actions 时间
- **目的**: 完整性能评估，可与 leaderboard 对比

## 🔍 查看结果

### 在 GitHub Actions UI

1. 进入 Actions 页面
2. 点击对应的 workflow run
3. 查看 "Summary" 中的 artifacts
4. 下载 `evaluation-results` 查看详细结果

### 结果文件

- `*.json`: 总体评估指标
  - `total_instances`: 总实例数
  - `instances_resolved`: 成功解决的数量
  - `resolution_rate`: 成功率
- `logs/`: 每个实例的详细日志

## 📈 性能对比

| 方案 | 成功率 | 平均时间/实例 | 说明 |
|------|--------|---------------|------|
| API 直接调用 | 100% (3/3) | ~100s | 简单 prompt，已验证 |
| Agents 框架 | 待测试 | 待测试 | 使用框架级 prompts |
| Gold patches | 100% (3/3) | ~105s | 官方标准答案 |

## 🎯 下一步

1. ✅ 运行 Agents 框架评估（3个实例）
2. 📊 对比 API vs Agents 性能差异
3. 🚀 如果效果好，运行完整 300 实例评估
4. 📝 分析结果，提交到 SWE-bench leaderboard

## ⚙️ 配置要求

### GitHub Secrets

需要设置以下 secret：

- `ANTHROPIC_API_KEY`: Anthropic Claude API Key

设置方法：
1. Repository Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. Name: `ANTHROPIC_API_KEY`
4. Value: 你的 API key (sk-ant-...)

### 本地运行（可选）

如果想在本地运行（需要 x86_64 架构）：

```bash
# 1. 安装依赖
pip install datasets tqdm anthropic

# 2. 生成 predictions
python3 /home/yutong/swebench_agents_docker_runner.py

# 3. 评估
cd /home/yutong/SWE-bench
python3 -m swebench.harness.run_evaluation \
    --dataset_name princeton-nlp/SWE-bench_Lite \
    --predictions_path /path/to/predictions.jsonl \
    --max_workers 1 \
    --instance_ids astropy__astropy-12907 astropy__astropy-14182 astropy__astropy-14365
```

## 📚 相关资源

- [SWE-bench 官方文档](https://www.swebench.com/SWE-bench/)
- [SWE-bench GitHub](https://github.com/SWE-bench/SWE-bench)
- [SWE-bench Leaderboard](https://swebench.com/)
- [Agents 框架](https://github.com/Melodramma080727/Agents)

## 🐛 故障排除

### Workflow 失败

1. 检查 ANTHROPIC_API_KEY 是否正确设置
2. 查看 Job logs 找到具体错误
3. 确认 API quota 是否充足

### 评估超时

- 减少 `num_instances` 数量
- 增加 workflow 的 `timeout-minutes`

### Docker 错误

- GitHub Actions runners 已预装 Docker
- 如果有问题，检查 Docker daemon 状态

## 📞 联系

- GitHub Issues: [Create an issue](https://github.com/Melodramma080727/swebench-evaluation/issues)
- Email: yguo113@jh.edu
