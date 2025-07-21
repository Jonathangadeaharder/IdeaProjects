# CI/CD Pipeline Documentation

This document describes the comprehensive CI/CD pipeline implemented for the EpisodeGameApp using GitHub Actions.

## Overview

The CI/CD pipeline consists of multiple workflows that automate various aspects of development, testing, and deployment:

- **Main CI Pipeline** (`ci.yml`) - Core build, test, and deployment workflow
- **Pull Request Checks** (`pr-checks.yml`) - Comprehensive PR validation
- **Release Automation** (`release.yml`) - Automated release process
- **Dependency Management** (`dependency-update.yml`) - Automated dependency updates
- **Performance Monitoring** (`performance.yml`) - Performance testing and monitoring

## Workflows

### 1. Main CI Pipeline (`ci.yml`)

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

**Jobs:**
- **Linting**: ESLint and Prettier checks
- **Testing**: Jest tests with coverage reporting
- **Web Build**: Build web application
- **Android Build**: Build Android APK
- **iOS Build**: Build iOS application (main branch only)
- **Security**: npm audit and CodeQL analysis
- **Type Check**: TypeScript type checking
- **Notification**: Success/failure notifications

### 2. Pull Request Checks (`pr-checks.yml`)

**Triggers:**
- Pull requests to any branch

**Jobs:**
- **PR Validation**: Title format, merge conflicts, changed files analysis
- **Accessibility**: WAVE and axe-core accessibility testing
- **Security**: Vulnerability scanning and license compliance
- **Performance**: Bundle size impact analysis
- **Code Quality**: Complexity and duplication analysis

### 3. Release Automation (`release.yml`)

**Triggers:**
- Version tags (v*.*.*)
- Manual workflow dispatch

**Jobs:**
- **Version Validation**: Semantic version validation
- **Build Artifacts**: Web, Android, and iOS builds
- **GitHub Release**: Automated release creation with changelog
- **Deployment**: Optional web application deployment

### 4. Dependency Management (`dependency-update.yml`)

**Triggers:**
- Weekly schedule (Mondays at 9 AM UTC)
- Manual workflow dispatch

**Jobs:**
- **Dependency Updates**: Automated dependency updates with PR creation
- **Security Audit**: Vulnerability scanning with issue creation
- **License Compliance**: License compatibility checking
- **Dependency Graph**: GitHub dependency graph submission

### 5. Performance Monitoring (`performance.yml`)

**Triggers:**
- Push to `main` branch
- Pull requests to `main` branch
- Daily schedule (2 AM UTC)
- Manual workflow dispatch

**Jobs:**
- **Bundle Size Analysis**: Bundle size tracking and comparison
- **Lighthouse Audit**: Performance, accessibility, and SEO scoring
- **Load Testing**: Stress testing with Artillery (scheduled only)
- **Memory Profiling**: Memory usage analysis
- **Regression Detection**: Performance regression detection for PRs

## Setup Requirements

### Repository Secrets

The following secrets need to be configured in your GitHub repository:

```
# Required for all workflows
GITHUB_TOKEN (automatically provided)

# Optional for enhanced features
CODECOV_TOKEN          # For code coverage reporting
SLACK_WEBHOOK_URL      # For Slack notifications
TELEGRAM_BOT_TOKEN     # For Telegram notifications
TELEGRAM_CHAT_ID       # For Telegram notifications

# For release deployment (if using)
DEPLOY_TOKEN           # For deployment authentication
DEPLOY_URL             # For deployment target
```

### Branch Protection Rules

Recommended branch protection rules for `main` and `develop` branches:

- Require pull request reviews
- Require status checks to pass:
  - `lint`
  - `test`
  - `build-web`
  - `security-scan`
  - `type-check`
- Require branches to be up to date
- Restrict pushes to matching branches

## Workflow Configuration

### Customizing Triggers

You can modify workflow triggers by editing the `on` section in each workflow file:

```yaml
on:
  push:
    branches: [ main, develop, feature/* ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 9 * * 1'  # Weekly on Mondays
```

### Environment Variables

Common environment variables used across workflows:

- `NODE_VERSION`: Node.js version (default: 18)
- `JAVA_VERSION`: Java version for Android builds (default: 11)
- `XCODE_VERSION`: Xcode version for iOS builds (default: latest)

### Caching Strategy

The pipeline uses aggressive caching to improve performance:

- **Node modules**: `npm ci` with cache
- **Gradle**: Android build cache
- **CocoaPods**: iOS dependency cache
- **Build artifacts**: Cross-job artifact sharing

## Monitoring and Notifications

### Status Badges

Add these badges to your README.md:

```markdown
[![CI](https://github.com/yourusername/EpisodeGameApp/workflows/CI/badge.svg)](https://github.com/yourusername/EpisodeGameApp/actions)
[![Security](https://github.com/yourusername/EpisodeGameApp/workflows/Security/badge.svg)](https://github.com/yourusername/EpisodeGameApp/actions)
[![Performance](https://github.com/yourusername/EpisodeGameApp/workflows/Performance/badge.svg)](https://github.com/yourusername/EpisodeGameApp/actions)
```

### Notification Channels

The pipeline supports multiple notification channels:

- **GitHub**: Native GitHub notifications and status checks
- **Slack**: Workflow status updates (requires webhook configuration)
- **Telegram**: Build notifications (requires bot token)
- **Email**: GitHub's built-in email notifications

## Performance Thresholds

### Bundle Size Limits

- **Total bundle**: 500KB increase threshold
- **JavaScript**: Monitored separately
- **CSS**: Monitored separately

### Lighthouse Thresholds

- **Performance**: Minimum 80%
- **Accessibility**: Minimum 90%
- **First Contentful Paint**: Maximum 2000ms
- **Largest Contentful Paint**: Maximum 4000ms
- **Cumulative Layout Shift**: Maximum 0.1

### Load Testing Limits

- **Response Time**: 95th percentile under 2000ms
- **Error Rate**: Maximum 10 errors per test run
- **Memory Usage**: Maximum 100MB heap usage

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Node.js version compatibility
   - Verify all dependencies are properly installed
   - Review error logs in GitHub Actions

2. **Test Failures**
   - Ensure test environment is properly configured
   - Check for missing test dependencies
   - Verify mock configurations

3. **Performance Issues**
   - Review bundle size changes
   - Check Lighthouse audit results
   - Analyze memory usage patterns

4. **Security Alerts**
   - Review npm audit results
   - Check CodeQL findings
   - Update vulnerable dependencies

### Debugging Workflows

Enable debug logging by setting repository secrets:

```
ACTIONS_STEP_DEBUG=true
ACTIONS_RUNNER_DEBUG=true
```

## Best Practices

### Code Quality

- Write comprehensive tests with good coverage
- Follow ESLint and Prettier configurations
- Use TypeScript for type safety
- Document complex functionality

### Performance

- Monitor bundle size regularly
- Optimize images and assets
- Use code splitting and lazy loading
- Profile memory usage

### Security

- Keep dependencies updated
- Review security audit results
- Use secure coding practices
- Validate all inputs

### Deployment

- Use semantic versioning
- Test releases thoroughly
- Maintain changelog
- Monitor production metrics

## Maintenance

### Regular Tasks

- **Weekly**: Review dependency updates
- **Monthly**: Update workflow actions to latest versions
- **Quarterly**: Review and update performance thresholds
- **As needed**: Update Node.js and other runtime versions

### Workflow Updates

When updating workflows:

1. Test changes in a feature branch
2. Review workflow syntax
3. Validate secret requirements
4. Update documentation
5. Monitor first runs after deployment

## Support

For issues with the CI/CD pipeline:

1. Check GitHub Actions logs
2. Review this documentation
3. Search existing GitHub issues
4. Create a new issue with detailed information

---

*This pipeline is designed to ensure code quality, security, and performance while automating repetitive tasks. Regular maintenance and monitoring will help maintain its effectiveness.*