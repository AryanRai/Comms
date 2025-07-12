# Contributing Guide

## Working with the AriesUI Submodule

This project includes AriesUI as a git submodule in `ui/ariesUI`. Here's how to work with it:

### Initial Setup
When first cloning the repository, you'll need to initialize the submodule:
```bash
git clone <repository-url>
git submodule update --init --recursive
```

### Making Changes to AriesUI

#### If you have write access to AriesUI:
1. Navigate to the submodule directory:
   ```bash
   cd ui/ariesUI
   ```

2. Make your changes and commit them:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

3. Return to the parent repository and update the submodule reference:
   ```bash
   cd ../..
   git add ui/ariesUI
   git commit -m "Updated ariesUI submodule"
   git push
   ```

#### If you don't have write access to AriesUI:
1. Fork the [AriesUI repository](https://github.com/AryanRai/AriesUI) to your GitHub account
2. Update the submodule to point to your fork:
   ```bash
   git submodule set-url ui/ariesUI https://github.com/YOUR_USERNAME/AriesUI.git
   ```
3. Then follow the same steps as above to make changes

### Updating AriesUI
To update the submodule to its latest version:
```bash
git submodule update --remote ui/ariesUI
git add ui/ariesUI
git commit -m "Updated ariesUI submodule to latest version"
git push
```

### Important Notes
- Always commit and push changes in the submodule first, before committing in the parent repository
- Make sure you have the necessary permissions before pushing to the original AriesUI repository
- If you're working on a branch, make sure to create branches in both the main repository and the submodule 