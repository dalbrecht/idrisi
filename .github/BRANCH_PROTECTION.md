# Branch Protection Settings

These settings should be enabled manually in **GitHub → Settings → Branches → Branch protection rules** for the `main` branch.

## Recommended Rules for `main`

### Pull Request Requirements

- [x] **Require a pull request before merging**
  - Required approvals: 1
  - Dismiss stale pull request approvals when new commits are pushed
- [x] **Require conversation resolution before merging**

### Status Checks

- [x] **Require status checks to pass before merging**
  - Required checks: `ci` (the GitHub Actions workflow)
- [x] **Require branches to be up to date before merging**

### Push Restrictions

- [x] **Do not allow force pushes**
- [x] **Do not allow deletions**

### After Merge

- [x] **Automatically delete head branches**

## How to Enable

1. Go to **Settings → Branches** in the GitHub repository
2. Click **Add branch protection rule**
3. Set **Branch name pattern** to `main`
4. Enable the checkboxes listed above
5. Click **Create** (or **Save changes**)
