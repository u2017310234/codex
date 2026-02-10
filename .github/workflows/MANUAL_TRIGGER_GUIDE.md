# How to Manually Trigger the SSH to VPS Workflow

This guide provides step-by-step instructions with visual guidance on how to manually trigger the workflow.

## Method 1: Using GitHub Web Interface

### Step 1: Go to Actions Tab

Navigate to your repository on GitHub and click the **Actions** tab:

```
https://github.com/[username]/[repository]/actions
```

**Note**: The Actions tab is typically located in the top navigation bar of your repository, between "Pull requests" and "Projects".

### Step 2: Find Your Workflow

In the left sidebar under "All workflows", click on **"SSH to VPS"**:

```
Actions
├── All workflows
│   └── SSH to VPS ← Click here
```

### Step 3: Click "Run workflow"

On the workflow page:
- You'll see a message: "This workflow has a workflow_dispatch event trigger"
- On the right side, click the **"Run workflow"** button (dropdown)

### Step 4: Select Branch and Confirm

- A dropdown menu appears
- Select the branch (usually `main` or your current working branch)
- Click the green **"Run workflow"** button to confirm

### Step 5: Watch It Run

- The workflow starts immediately
- A new entry appears in the workflow runs list
- Yellow circle (🟡) = running
- Green checkmark (✅) = success
- Red X (❌) = failed

Click on the workflow run to see detailed logs and results.

## Method 2: Using GitHub CLI (gh)

If you have [GitHub CLI](https://cli.github.com/) installed:

```bash
# Trigger the workflow on the default branch
gh workflow run "SSH to VPS"

# Trigger on a specific branch
gh workflow run "SSH to VPS" --ref your-branch-name

# List recent runs
gh run list --workflow="SSH to VPS"

# View details of the latest run
gh run view
```

## Method 3: Using GitHub API

You can also trigger the workflow via the GitHub REST API:

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/OWNER/REPO/actions/workflows/ssh-vps.yml/dispatches \
  -d '{"ref":"main"}'
```

Replace:
- `YOUR_GITHUB_TOKEN` with your personal access token
- `OWNER` with your GitHub username
- `REPO` with your repository name

## Verification

After triggering the workflow, you should see:
1. A new workflow run in the Actions tab
2. The run progresses through the steps:
   - Checkout code
   - Setup SSH
   - Test SSH Connection
3. If successful, the logs will show the VPS hostname and uptime

## Common Issues

### "Run workflow" button not visible?
- Ensure you have **write** access to the repository
- Refresh the page
- Check that you're on the correct branch
- Verify the workflow file exists at `.github/workflows/ssh-vps.yml`

### Workflow fails immediately?
- Check that secrets `VPS_IP` (VPS IP address) and `VPS_M` (SSH private key) are configured
- Verify the secrets have correct values
- Check workflow permissions

### SSH connection times out?
- Verify VPS_IP is correct and accessible
- Check VPS firewall rules
- Ensure SSH key (`VPS_M`) has access to the VPS

## Additional Resources

- [GitHub Actions Documentation - Manually running a workflow](https://docs.github.com/en/actions/managing-workflow-runs/manually-running-a-workflow)
- [GitHub Actions - workflow_dispatch event](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch)
