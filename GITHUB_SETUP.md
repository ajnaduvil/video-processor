# GitHub Repository Setup Guide

This guide will help you prepare and publish your Video Processor project to GitHub.

## Pre-Publishing Checklist

### 1. Update Repository Information

Before pushing to GitHub, update the following files with your information:

#### `README.md`
- Replace `https://github.com/yourusername/video-processor` with your actual repository URL
- Replace `yourusername` with your GitHub username in all instances
- Add screenshots once the GUI is ready
- Update the "Star History" section after publishing

#### `CHANGELOG.md`
- Update the repository URL in the links section
- Replace `yourusername` with your GitHub username

#### `CONTRIBUTORS.md`
- Update the "Maintainer" section with your name and GitHub profile
- Update the security email in `SECURITY.md`

#### `SECURITY.md`
- Replace `[security-email-placeholder]` with your actual email address for security reports

#### Issue & PR Templates
- Update any placeholder links with your repository URLs

### 2. Verify All Files Are Ready

```bash
# Check what files are ready to be committed
git status
```

You should see:
- `LICENSE` (new)
- `README.md` (modified)
- `CONTRIBUTING.md` (new)
- `CHANGELOG.md` (new)
- `SECURITY.md` (new)
- `CONTRIBUTORS.md` (new)
- `.github/` directory with templates (new)
- `.gitignore` (modified)

### 3. Create GitHub Repository

#### Option A: Create via GitHub Website
1. Go to [github.com/new](https://github.com/new)
2. Repository name: `video-processor`
3. Description: `A modern, cross-platform batch video optimization tool powered by FFmpeg with a PySide6 GUI`
4. Visibility: Public (for open source)
5. Initialize with:
   - [ ] Add a README file (we already have one)
   - [ ] Add .gitignore (we already have one)
   - [ ] Choose a license (we already have MIT)
6. Click "Create repository"
7. Follow the instructions to push your existing repository

#### Option B: Create via GitHub CLI (gh)

```bash
# Install GitHub CLI if needed
# Windows: winget install --id=GitHub.cli
# macOS: brew install gh
# Linux: See https://github.com/cli/cli/blob/trunk/docs/install_linux.md

# Create repository
gh repo create video-processor \
  --public \
  --description "A modern, cross-platform batch video optimization tool powered by FFmpeg with a PySide6 GUI" \
  --source=. \
  --remote=origin \
  --push

# Or create without pushing (you'll push manually)
gh repo create video-processor \
  --public \
  --description "A modern, cross-platform batch video optimization tool powered by FFmpeg with a PySide6 GUI"
```

### 4. Add Remote Repository (if using Option A)

```bash
# Add the remote repository (replace with your URL)
git remote add origin https://github.com/YOUR_USERNAME/video-processor.git

# Verify the remote
git remote -v
```

### 5. Commit and Push Changes

```bash
# Stage all changes
git add .

# Review what will be committed
git status

# Create a commit
git commit -m "$(cat <<'EOF'
feat: prepare for open source release with MIT license

- Add MIT License
- Create comprehensive README with installation and usage docs
- Add CONTRIBUTING.md with contribution guidelines
- Add CHANGELOG.md for version tracking
- Add SECURITY.md with security policy
- Add CONTRIBUTORS.md template
- Add GitHub issue and pull request templates
- Update .gitignore with additional patterns
EOF
)"

# Push to GitHub
git push -u origin main
```

### 6. Configure Repository Settings

After pushing to GitHub, configure these settings:

#### Repository Settings

1. **General** (Settings → General)
   - ✅ Make repository public
   - Add topics: `video-processing`, `ffmpeg`, `pyside6`, `qt6`, `video-optimizer`, `batch-processing`, `python`
   - Set default branch: `main`
   - Enable features: Issues, Projects, Discussions, Wikis

2. **Branches** (Settings → Branches)
   - Add branch protection rule for `main`:
     - ✅ Require pull request reviews before merging
     - ✅ Require status checks to pass before merging
     - ✅ Require branches to be up to date before merging

3. **Webhooks** (Settings → Webhooks)
   - Optional: Add webhook for CI/CD (if setting up GitHub Actions)

4. **Danger Zone** (Settings → Scroll to bottom)
   - Do NOT change the default branch without testing

### 7. Create Initial Release

1. Go to "Releases" → "Create a new release"
2. Tag: `v0.0.0`
3. Release title: `Video Processor v0.0.0 - Initial Release`
4. Description:
   ```markdown
   ## 🎉 Initial Release

   This is the first release of Video Processor, a modern batch video optimization tool powered by FFmpeg with a PySide6 GUI.

   ### Features
   - Batch video compression with CRF-based encoding
   - Support for H.264 and H.265 codecs
   - AAC and Opus audio encoding
   - Modern GUI with dark/light theme support
   - Real-time batch progress tracking
   - Comprehensive CSV logging
   - CLI mode for automation
   - Parallel processing support

   ### Installation
   See the [README.md](https://github.com/YOUR_USERNAME/video-processor#installation) for detailed installation instructions.

   ### Requirements
   - Python 3.10+
   - FFmpeg 7.0+
   - PySide6

   ### Documentation
   - [README](https://github.com/YOUR_USERNAME/video-processor#readme)
   - [Contributing](https://github.com/YOUR_USERNAME/video-processor/blob/main/CONTRIBUTING.md)
   - [Requirements](https://github.com/YOUR_USERNAME/video-processor/blob/main/REQUIREMENTS.md)

   ### License
   This project is licensed under the MIT License - see the [LICENSE](https://github.com/YOUR_USERNAME/video-processor/blob/main/LICENSE) file for details.

   ### Support
   - 🐛 Report bugs: [Issues](https://github.com/YOUR_USERNAME/video-processor/issues)
   - 💬 Ask questions: [Discussions](https://github.com/YOUR_USERNAME/video-processor/discussions)
   - 📚 Read documentation: [README](https://github.com/YOUR_USERNAME/video-processor#readme)
   ```
5. ✅ Set as a pre-release (optional, for early versions)
6. Click "Publish release"

### 8. Add Badges to README

After creating the repository, add these badges at the top of your README.md:

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![PySide6](https://img.shields.io/badge/PySide6-Qt6-blue.svg)](https://doc.qt.io/qtforpython/)
[![GitHub Stars](https://img.shields.io/github/stars/YOUR_USERNAME/video-processor?style=social)](https://github.com/YOUR_USERNAME/video-processor)
[![GitHub Forks](https://img.shields.io/github/forks/YOUR_USERNAME/video-processor?style=social)](https://github.com/YOUR_USERNAME/video-processor/network/members)
[![GitHub Issues](https://img.shields.io/github/issues/YOUR_USERNAME/video-processor)](https://github.com/YOUR_USERNAME/video-processor/issues)
```

### 9. Set Up GitHub Issues

1. **Configure Labels** (Issues → Labels)
   - Keep default labels (bug, enhancement, documentation, help wanted, etc.)
   - Add custom labels if needed:
     - `good first issue` - For newcomers
     - `priority: high` - High priority issues
     - `priority: low` - Low priority issues
     - `gui` - GUI-related issues
     - `cli` - CLI-related issues
     - `ffmpeg` - FFmpeg-related issues

2. **Configure Milestones** (Issues → Milestones)
   - Create milestones for versions:
     - v0.1.0
     - v0.2.0
     - v1.0.0
   - Assign issues to milestones

### 10. Set Up GitHub Actions (Optional but Recommended)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install uv
      run: pip install uv
    
    - name: Install FFmpeg
      run: |
        sudo apt-get update
        sudo apt-get install -y ffmpeg
      if: runner.os == 'Linux'
    
    - name: Install dependencies
      run: |
        uv venv
        source .venv/bin/activate
        uv pip install -e .
    
    - name: Run tests
      run: |
        source .venv/bin/activate
        python -m unittest
```

### 11. Set Up GitHub Discussions

1. Enable Discussions in repository settings
2. Create pinned discussions:
   - "Welcome & Introductions"
   - "Questions & Support"
   - "Feature Ideas"
   - "Show & Tell"

### 12. Add to README

Add this section to your README.md after the installation section:

```markdown
## Community

- 🐛 [Report Bugs](https://github.com/YOUR_USERNAME/video-processor/issues)
- 💡 [Request Features](https://github.com/YOUR_USERNAME/video-processor/issues)
- 💬 [Discussions](https://github.com/YOUR_USERNAME/video-processor/discussions)
- 📝 [Contributing](https://github.com/YOUR_USERNAME/video-processor/blob/main/CONTRIBUTING.md)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=YOUR_USERNAME/video-processor&type=Date)](https://star-history.com/#YOUR_USERNAME/video-processor&Date)
```

### 13. Optional: Add a Website or Wiki

- **GitHub Pages**: Add a static site for documentation
- **GitHub Wiki**: Add additional documentation and tutorials
- **Documentation Site**: Use tools like MkDocs, Sphinx, or Docusaurus

### 14. Social Media & Promotion

Once published, promote your project:

- Share on relevant forums (Reddit, Hacker News, etc.)
- Post in Python/Qt/FFmpeg communities
- Add to awesome lists
- Share on social media (Twitter, LinkedIn, etc.)

## Post-Publishing Checklist

- [ ] Repository is public
- [ ] All placeholders replaced with actual information
- [ ] Badges are working
- [ ] Initial release created
- [ ] Issue templates are working
- [ ] PR template is working
- [ ] Branch protection enabled (optional)
- [ ] GitHub Actions configured (optional)
- [ ] Discussions enabled (optional)
- [ ] Topics added
- [ ] README is complete and accurate
- [ ] LICENSE is present
- [ ] CONTRIBUTING.md is present
- [ ] SECURITY.md is present
- [ ] CHANGELOG.md is present
- [ ] Links in README point to correct URLs

## Maintenance Tips

### Regular Tasks
- Update dependencies regularly
- Review and merge pull requests
- Respond to issues and discussions
- Create releases for new versions
- Update CHANGELOG with each release

### Release Process
1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Tag the release
4. Create GitHub release
5. Update badges if needed

### Monitoring
- Watch for security advisories in dependencies
- Monitor issues and discussions
- Track usage analytics (GitHub Insights)

## Resources

- [GitHub Documentation](https://docs.github.com/)
- [Open Source Guides](https://opensource.guide/)
- [Choosing an Open Source License](https://choosealicense.com/)
- [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/)

---

Good luck with your open source project, Boss! 🚀
