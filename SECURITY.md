# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.0.0   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please send an email to: `[security-email-placeholder]`

Include the following information in your report:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact of the vulnerability
- Any suggested fixes or workarounds (if known)

### What to Expect

- We will acknowledge receipt of your report within 48 hours
- We will provide a detailed response within 7 days
- We will work with you to understand and resolve the issue
- We will coordinate a release to address the vulnerability
- We will credit you in the security advisory (unless you prefer to remain anonymous)

### Security Best Practices

When working with Video Processor, follow these best practices:

1. **Input Validation**: Always validate input folders and file paths
2. **Permissions**: Ensure proper read/write permissions for source and output folders
3. **Disk Space**: Verify adequate disk space before processing large batches
4. **FFmpeg Security**: Keep FFmpeg updated to the latest stable version
5. **Dependencies**: Keep Python and all dependencies updated
6. **Logs**: Review logs regularly for any unusual activity or errors

### Known Security Considerations

- **File Processing**: The application processes video files from user-specified directories. Always ensure you trust the source of input files.
- **FFmpeg**: FFmpeg is used to process videos. Keep FFmpeg updated to benefit from security fixes.
- **Local Processing**: All processing happens locally on your machine. No files are uploaded to external servers.
- **No Network Access**: By default, Video Processor does not require network access and does not make external connections.

### Privacy

- Video Processor does not collect or transmit any data
- All processing happens locally on your machine
- No telemetry or analytics are included
- Logs are stored locally and are not shared automatically

### Dependency Security

We regularly update dependencies to include security fixes. You can check for security vulnerabilities in dependencies using:

```bash
# Check for security vulnerabilities in installed packages
uv pip install --upgrade
```

### Receiving Security Updates

To receive notifications about security advisories:

1. Watch this repository on GitHub
2. Enable "Custom" notifications and select "Security advisories"
3. Check the [Releases](https://github.com/yourusername/video-processor/releases) page regularly

### Security Advisories

Security advisories will be published on GitHub Security Advisories and will include:

- Description of the vulnerability
- Affected versions
- Impact assessment
- Recommended actions
- Available patches or updates

---

Thank you for helping keep Video Processor secure!
