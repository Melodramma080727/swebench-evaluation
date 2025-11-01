# GitHub Personal Access Token 设置指南

## 为什么需要这个？

Real Agents evaluation workflow 需要克隆私有的 Agents 仓库。GitHub Actions 默认的 `GITHUB_TOKEN` 只能访问当前仓库，所以我们需要创建一个 Personal Access Token (PAT)。

## 步骤 1: 创建 Personal Access Token

1. 访问 GitHub Token 创建页面：
   ```
   https://github.com/settings/tokens/new
   ```

2. 填写以下信息：
   - **Note**: `SWE-bench Agents Access`（或任何你喜欢的名字）
   - **Expiration**: 建议选择 `90 days` 或 `No expiration`（如果需要长期使用）
   
3. **Select scopes** - 勾选权限：
   - ✅ **repo** (Full control of private repositories)
     - 这会自动勾选所有子选项：
       - repo:status
       - repo_deployment
       - public_repo
       - repo:invite
       - security_events

4. 滚动到页面底部，点击绿色的 **Generate token** 按钮

5. **重要！** 复制生成的 token（格式类似：`ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`）
   - ⚠️ Token 只会显示一次，离开页面后无法再次查看
   - 建议先保存到安全的地方（密码管理器）

## 步骤 2: 添加 Secret 到评估仓库

1. 访问你的评估仓库的 Secrets 设置页面：
   ```
   https://github.com/Melodramma080727/swebench-evaluation/settings/secrets/actions
   ```

2. 点击右上角的 **New repository secret** 按钮

3. 填写以下信息：
   - **Name**: `GH_PAT` （必须是这个名字！）
   - **Secret**: 粘贴刚才复制的 token（以 `ghp_` 开头的那串字符）

4. 点击 **Add secret** 按钮

## 步骤 3: 验证配置

运行以下命令触发 workflow：

```bash
cd /home/yutong/Agents/swebench_evaluation
git commit --allow-empty -m "Test Agents repo cloning with GH_PAT"
git push
```

然后访问 Actions 页面查看结果：
```
https://github.com/Melodramma080727/swebench-evaluation/actions
```

## 预期结果

如果配置正确，你会在 "Clone Agents repository" 步骤看到：

```
✓ Successfully cloned Agents repository using GITHUB_TOKEN or GH_PAT
Agents repo commit: <commit_hash>
```

## 故障排除

### 问题 1: 仍然提示 "fatal: could not read Username"

**原因**: Secret 可能没有正确设置

**解决方案**:
1. 确认 Secret 名称是 `GH_PAT`（大小写敏感）
2. 确认 token 是完整的（包含 `ghp_` 前缀）
3. 尝试重新创建 token 和 secret

### 问题 2: "Authentication failed"

**原因**: Token 权限不足或已过期

**解决方案**:
1. 确认 token 勾选了 `repo` scope
2. 检查 token 是否过期
3. 创建新的 token 并更新 secret

### 问题 3: "Repository not found"

**原因**: Token 无法访问 Agents 仓库

**解决方案**:
1. 确认你的 GitHub 账户有访问 Agents 仓库的权限
2. 如果 Agents 是组织仓库，可能需要授权 token 访问组织
3. 尝试用 token 手动克隆验证：
   ```bash
   git clone https://YOUR_TOKEN@github.com/YOUR_ORG/Agents.git /tmp/test-clone
   ```

## 安全提示

- ⚠️ **永远不要**在代码中硬编码 token
- ⚠️ **永远不要**在 commit 消息或 issue 中泄露 token
- ✅ Token 应该只存储在 GitHub Secrets 中
- ✅ 定期轮换 token（建议 90 天）
- ✅ 如果 token 泄露，立即在 https://github.com/settings/tokens 删除它

## 更多信息

- GitHub PAT 文档: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token
- GitHub Actions Secrets: https://docs.github.com/en/actions/security-guides/encrypted-secrets
