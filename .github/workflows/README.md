# GitHub Actions Workflows

## SSH to VPS Workflow

This workflow enables SSH access to a VPS (Virtual Private Server) using GitHub Actions.

### Quick Start - Trigger Workflow Manually

**TL;DR**: `Repository → Actions → SSH to VPS → Run workflow → Select branch → Run workflow`

If you want to trigger the workflow right now:
1. Go to the **Actions** tab in your GitHub repository
2. Click **"SSH to VPS"** in the left sidebar
3. Click the **"Run workflow"** button
4. Select your branch and click **"Run workflow"** again

📖 **For detailed instructions with visual guidance, see [MANUAL_TRIGGER_GUIDE.md](./MANUAL_TRIGGER_GUIDE.md)**

⚠️ **Important**: Make sure you've configured the required secrets first (see Prerequisites below)!

### Prerequisites

Before using this workflow, you need to configure the following GitHub secrets in your repository:

1. **VPS_IP**: The IP address of your VPS server
2. **VPS_M**: The SSH private key for authentication

### Setting Up Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add the following secrets:
   - Name: `VPS_IP`, Value: Your VPS IP address (e.g., `203.0.113.10`)
   - Name: `VPS_M`, Value: Your SSH private key (the entire content of your `id_rsa` file)

### How to Use

The workflow can be triggered in two ways:

#### 1. Automatically
The workflow runs automatically when you push code to the `main` branch.

#### 2. Manually (workflow_dispatch)

To trigger the workflow manually:

**Step 1**: Navigate to the Actions tab
- Go to your repository on GitHub
- Click on the **"Actions"** tab at the top of the repository page

**Step 2**: Select the workflow
- In the left sidebar, you'll see a list of workflows
- Click on **"SSH to VPS"** workflow

**Step 3**: Run the workflow
- You'll see a gray banner with the text "This workflow has a workflow_dispatch event trigger"
- Click the **"Run workflow"** button (on the right side)
- A dropdown will appear showing the branch selector
- Select the branch you want to run the workflow on (default: `main`)
- Click the green **"Run workflow"** button to confirm

**Step 4**: Monitor the workflow run
- The workflow will start running immediately
- You'll see a new workflow run appear in the list with a yellow/orange indicator (⚪ or 🟡) showing it's in progress
- Click on the workflow run to see detailed logs
- Once complete, it will show either:
  - ✅ Green checkmark if successful
  - ❌ Red X if failed

**Visual Guide:**
```
GitHub Repository
    └── Actions tab
        └── Workflows (left sidebar)
            └── "SSH to VPS"
                └── "Run workflow" button (top right)
                    └── Select branch → "Run workflow"
```

**Note**: The "Run workflow" button only appears if:
- You have `write` access to the repository
- The workflow file contains `workflow_dispatch:` trigger (which it does)

### What the Workflow Does

1. Checks out the repository code
2. Sets up SSH with the provided private key
3. Attempts to connect to the VPS and run basic commands (echo, hostname, uptime)

### Troubleshooting

#### Cannot trigger workflow manually?

If you don't see the "Run workflow" button:
1. **Check permissions**: You need write access to the repository
2. **Verify workflow file**: Ensure `.github/workflows/ssh-vps.yml` contains `workflow_dispatch:` in the `on:` section
3. **Refresh the page**: Sometimes the GitHub UI needs a refresh after pushing a new workflow
4. **Check branch**: Make sure you're viewing the correct branch that has the workflow file

#### SSH connection fails?

If the SSH connection fails:

1. Verify that `VPS_IP` contains the correct IP address
2. Ensure `VPS_M` contains a valid SSH private key
3. Check that the SSH private key has access to the VPS
4. Verify that the VPS allows SSH connections from GitHub Actions IPs
5. Make sure the SSH user (default: `root`) exists on the VPS

### Security Notes

- Never commit SSH private keys directly to the repository
- Always use GitHub Secrets to store sensitive information
- The workflow uses `ssh-keyscan` to automatically accept the host key, which may be vulnerable to man-in-the-middle attacks on first connection. For enhanced security, consider manually adding the VPS host key to the workflow or using a known_hosts file.
- Consider using SSH keys with limited permissions for automation tasks
- Ensure your VPS firewall allows connections from GitHub Actions IP ranges
