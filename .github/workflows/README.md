# GitHub Actions Workflows

## SSH to VPS Workflow

This workflow enables SSH access to a VPS (Virtual Private Server) using GitHub Actions.

### Prerequisites

Before using this workflow, you need to configure the following GitHub secrets in your repository:

1. **VPS_IP**: The IP address of your VPS server
2. **VPS_M**: The SSH private key for authentication

### Setting Up Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Add the following secrets:
   - Name: `VPS_IP`, Value: Your VPS IP address (e.g., `192.168.1.100`)
   - Name: `VPS_M`, Value: Your SSH private key (the entire content of your `id_rsa` file)

### How to Use

The workflow can be triggered in two ways:

1. **Automatically**: Push code to the `main` branch
2. **Manually**: Go to Actions → SSH to VPS → Run workflow

### What the Workflow Does

1. Checks out the repository code
2. Sets up SSH with the provided private key
3. Attempts to connect to the VPS and run basic commands (echo, hostname, uptime)

### Troubleshooting

If the SSH connection fails:

1. Verify that `VPS_IP` contains the correct IP address
2. Ensure `VPS_M` contains a valid SSH private key
3. Check that the SSH private key has access to the VPS
4. Verify that the VPS allows SSH connections from GitHub Actions IPs
5. Make sure the SSH user (default: `root`) exists on the VPS

### Security Notes

- Never commit SSH private keys directly to the repository
- Always use GitHub Secrets to store sensitive information
- The workflow uses `StrictHostKeyChecking=no` for convenience, but be aware of security implications
- Consider using SSH keys with limited permissions for automation tasks
