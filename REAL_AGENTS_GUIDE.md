# 🤖 真正的 Agents 框架 SWE-bench 评估

## 🎯 这个 Workflow 做什么？

**与之前的 workflow 的关键区别**：

| 特性 | 之前的方案 | 这个方案（真正的 Agents） |
|------|-----------|------------------------|
| **LLM 调用** | 直接 API 调用 | 通过 Agents 框架 |
| **工具使用** | ❌ 无 | ✅ 文件操作、命令执行 |
| **迭代能力** | ❌ 单次生成 | ✅ 多轮迭代修复 |
| **推理规划** | ❌ 简单 prompt | ✅ Agent 自主规划 |
| **Docker** | ❌ 不需要 | ✅ 完整 Docker Compose |
| **运行方式** | Python 脚本 | 真实 Agent 容器 |

## 🚀 如何运行

### 方法 1: GitHub UI

1. 访问: https://github.com/Melodramma080727/swebench-evaluation/actions

2. 选择 **"SWE-bench Real Agents Framework Evaluation"**

3. 点击 "Run workflow"

4. 配置参数：
   ```
   num_instances: 1  (强烈建议从 1 开始测试！)
   agent_repo: https://github.com/Melodramma080727/Agents.git
   ```

5. 点击 "Run workflow" 开始

### 方法 2: GitHub CLI

```bash
gh workflow run swebench_real_agents.yml \
    -f num_instances=1 \
    -f agent_repo=https://github.com/Melodramma080727/Agents.git
```

## ⚠️  重要提示

### 时间和资源

- **每个实例预计时间**: 10-20 分钟（Agent 需要推理、规划、迭代）
- **1 个实例**: ~20 分钟
- **3 个实例**: ~1 小时
- **10 个实例**: ~3+ 小时

**建议**: 先用 1 个实例测试，确认成功后再增加！

### 前置要求

1. **ANTHROPIC_API_KEY Secret 必须设置**
   - 访问: https://github.com/Melodramma080727/swebench-evaluation/settings/secrets/actions
   - 添加: `ANTHROPIC_API_KEY`
   - 值: 你的完整 API key

2. **Agents 仓库必须可访问**
   - 如果是 private repo，需要配置 GitHub token
   - 或者使用 public repo

## 📊 预期结果

### 成功的运行会生成

1. **Predictions 文件** (`real-agents-predictions`)
   - 每个实例的 patch
   - 格式: `.jsonl`
   - 包含: instance_id, model_patch, elapsed_time

2. **Patch 文件** (`real-agents-patches`)
   - 单独的 `.patch` 文件
   - 方便检查每个 patch

3. **评估结果** (`real-agents-evaluation-results`)
   - SWE-bench 评估报告
   - 成功率、详细日志

4. **Debug 日志** (`real-agents-logs`)
   - Agent 运行日志
   - 错误信息（如果有）

## 🔍 如何查看结果

1. 进入 Actions 页面
2. 点击对应的 workflow run
3. 等待两个 jobs 完成：
   - ✅ Job 1: `generate_with_agents` (生成 patches)
   - ✅ Job 2: `evaluate_patches` (评估结果)
4. 在 Summary 中下载 artifacts
5. 查看评估结果 JSON 文件

## 📈 与其他方案对比

运行完成后，你可以对比：

| 方案 | 类型 | 成功率 | 特点 |
|------|------|--------|------|
| **Gold Patches** | 标准答案 | 100% (3/3) | 官方正确答案 |
| **API 直接调用** | 简单 | 100% (3/3) | 单次 prompt |
| **真实 Agents** | 完整框架 | 待测试 | 多轮迭代、工具使用 |

## 🐛 故障排除

### 问题: "No predictions found"

**原因**: Agent 没有生成 patch 或保存位置错误

**解决**:
1. 下载 `real-agents-logs` artifact
2. 查看 Agent 输出
3. 检查是否有错误信息

### 问题: "Timeout"

**原因**: Agent 运行超过 20 分钟

**解决**:
1. 检查任务是否太复杂
2. 可以在 workflow 中增加 timeout
3. 检查 Agent 是否卡在某个步骤

### 问题: "Docker image build failed"

**原因**: Agents 仓库问题或依赖问题

**解决**:
1. 检查 Agents 仓库是否正常
2. 查看 build logs
3. 确认 Dockerfile 正确

### 问题: "API key error"

**原因**: ANTHROPIC_API_KEY 未设置或错误

**解决**:
1. 检查 GitHub Secrets 配置
2. 确认 API key 有效
3. 检查 API quota

## 🎯 下一步

1. **首次运行**: 用 1 个实例测试
   - 验证整个 pipeline 工作
   - 检查 Agent 能否生成有效 patch
   - 查看运行时间

2. **分析结果**: 
   - 对比 Agent vs API 性能
   - 看 Agent 是否能处理更复杂的任务
   - 分析 Agent 的推理过程

3. **扩大规模**:
   - 如果效果好，增加到 3-5 个实例
   - 继续增加到 10 个实例
   - 最终可以跑全部 300 个（需要很长时间）

4. **优化**:
   - 根据结果调整 Agent 配置
   - 优化 prompt 或 task description
   - 调整 max_iterations 参数

## 📚 技术细节

### Workflow 做了什么

1. **准备阶段**:
   - 克隆 Agents 仓库
   - 配置环境变量（API key等）
   - 构建 Docker 镜像

2. **生成阶段**:
   - 对每个 SWE-bench 实例：
     - 创建 Agent 任务
     - 启动 Docker 容器
     - Agent 自主工作（推理、工具使用、迭代）
     - 从 workspace 提取 patch
   - 保存所有 predictions

3. **评估阶段**:
   - 下载 predictions
   - 运行 SWE-bench harness
   - 在 Docker 容器中应用 patches 并测试
   - 生成评估报告

### Agent 如何工作

1. 接收任务描述
2. 分析问题
3. 可以：
   - 读取文件
   - 执行命令
   - 修改代码
   - 运行测试
   - 迭代修复
4. 最终生成 patch 并保存到 workspace

这是真正的 AI Agent，不只是 LLM API 调用！

## 🔗 相关链接

- **Workflow 文件**: `.github/workflows/swebench_real_agents.yml`
- **Agents 仓库**: https://github.com/Melodramma080727/Agents
- **SWE-bench**: https://www.swebench.com/
- **Actions 页面**: https://github.com/Melodramma080727/swebench-evaluation/actions

---

**准备好了吗？去 GitHub Actions 运行你的第一个真实 Agents 评估！** 🚀
