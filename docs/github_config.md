# GitHub Repository Configuration

This document outlines the recommended GitHub configuration for the Content Calendar Template repository.

## Branch Protection Rules

### Main Branch Protection

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["test (3.11)", "test (3.12)"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
```

#### Branch Protection

Branch protection is configured to require:
- At least 1 approving review before merging
- Status checks to pass before merging
- Linear commit history
- No force pushes
- No branch deletion
- Conversation resolution before merging

#### Admin Bypass
- Repository admins (like `stratofax`) can bypass these requirements
- Look for the "Merge without waiting for requirements to be met (bypass rules)" option
- This is only visible to users with bypass privileges
- Regular contributors will need to get their PRs approved before merging

#### Configuration Notes
- `enforce_admins` is disabled to allow admin bypass
- Bypass is configured per-user in the branch protection settings
- The `develop` branch has similar protection rules

#### Key Protection Settings:

1. **Required Status Checks**
   - All status checks must pass before merging
   - Branches must be up to date before merging
   - Required checks: `test (3.11)`, `test (3.12)`

2. **Pull Request Reviews**
   - Require at least 1 approval before merging
   - Dismiss stale pull request approvals when new commits are pushed
   - Code owner approval not required (can be enabled later)

3. **Additional Rules**
   - Require linear history (no merge commits)
   - Do not allow force pushes
   - Do not allow branch deletion
   - Require conversation resolution before merging

## Recommended Repository Settings

### Branch Rules
- Default branch: `main`
- Branch protection: Enabled for `main`
- Allow merge commits: Disabled
- Allow squash merging: Enabled
- Allow rebase merging: Enabled
- Automatically delete head branches: Enabled

### Security & Analysis
- Enable vulnerability alerts
- Enable Dependabot security updates
- Enable automated security fixes

## Workflow

### Branching Strategy
- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches
- `release/*`: Release preparation branches

### Pull Request Process
1. Create a feature/bugfix branch from `develop`
2. Open a pull request to `develop`
3. Ensure all tests pass
4. Get at least one approval
5. Merge using squash or rebase
6. Delete the feature branch after merge

## Code Review Guidelines
- Review the code, not the author
- Be constructive and specific in feedback
- Check for security implications
- Verify tests cover new functionality
- Ensure documentation is updated

## Security Best Practices
- Never commit secrets or credentials
- Use GitHub secrets for sensitive data
- Keep dependencies updated
- Review dependency licenses
- Run security scans regularly
