# LangPlug QA Workflow Guide

## Overview
This document outlines the comprehensive Quality Assurance workflow for testing the LangPlug German language learning platform. All tests should be performed using browser automation (browsermcp) to simulate real user interactions.

## Prerequisites
- Backend server running on `http://172.30.96.1:8000`
- Frontend server running on `http://localhost:3000`
- Browser with MCP extension connected
- Test data cleared or fresh database

## Test Workflows

### 1. User Registration & Authentication Flow

#### 1.1 Landing Page Verification
- [ ] Navigate to `http://localhost:3000`
- [ ] Verify landing page loads without errors
- [ ] Check for proper styling and layout
- [ ] Verify no console errors in browser

#### 1.2 User Registration
- [ ] Click "Register" or "Sign Up" button
- [ ] Fill registration form:
  - Username: `qa_user_[timestamp]`
  - Email: `qa_[timestamp]@test.com`
  - Password: `QaTest123!@#`
- [ ] Submit registration form
- [ ] Verify successful registration message
- [ ] Check redirect to login or dashboard

#### 1.3 User Login
- [ ] Navigate to login page (if not auto-redirected)
- [ ] Enter registered credentials
- [ ] Submit login form
- [ ] Verify successful login
- [ ] Check JWT token stored in localStorage/sessionStorage
- [ ] Verify redirect to dashboard/home

#### 1.4 Session Persistence
- [ ] Refresh the page
- [ ] Verify user remains logged in
- [ ] Check user profile/name displayed
- [ ] Test logout functionality
- [ ] Verify redirect to login page after logout

### 2. Vocabulary Library Management

#### 2.1 Access Vocabulary Library
- [ ] Navigate to Vocabulary/Library section
- [ ] Verify vocabulary stats load:
  - Total words count
  - Known words count
  - Progress indicators

#### 2.2 Browse Vocabulary Levels
- [ ] Click on A1 level
- [ ] Verify word list loads
- [ ] Check word display format:
  - German word
  - Part of speech
  - Definition/translation
  - Known/unknown status

#### 2.3 Mark Words as Known
- [ ] Select individual words
- [ ] Mark as known using checkbox/button
- [ ] Verify UI updates immediately
- [ ] Check stats update accordingly
- [ ] Test bulk marking (mark all A1 as known)
- [ ] Verify persistence after page refresh

#### 2.4 Filter and Search
- [ ] Test filtering by known/unknown
- [ ] Search for specific words
- [ ] Test navigation between levels (A1, A2, B1, B2)
- [ ] Verify counts are accurate for each level

### 3. Episode Selection & Content

#### 3.1 Browse Episodes
- [ ] Navigate to Episodes/Videos section
- [ ] Verify video list loads
- [ ] Check video thumbnails display
- [ ] Verify episode information:
  - Series name
  - Episode number
  - Duration
  - Difficulty level

#### 3.2 Select Episode
- [ ] Click on first episode (Superstore Episode 1)
- [ ] Verify episode details page loads
- [ ] Check for episode metadata
- [ ] Verify "Start Learning" or "Play" button

### 4. Timer Game / Pre-Learning Phase

#### 4.1 Start Timer Game
- [ ] Click "Start Learning" for first chunk
- [ ] Verify timer game interface loads
- [ ] Check blocking words display:
  - List of difficult vocabulary
  - Definitions visible
  - Difficulty indicators (A1/A2/B1/B2)

#### 4.2 Review Blocking Words
- [ ] Scroll through blocking words list
- [ ] Click on words for more details
- [ ] Mark words as "learned" if option available
- [ ] Verify countdown timer (if implemented)

#### 4.3 Complete Pre-Learning
- [ ] Click "Continue to Video" or "Start Watching"
- [ ] Verify transition to video player
- [ ] Check that reviewed words are tracked

### 5. Video Player & Subtitles

#### 5.1 Video Player Interface
- [ ] Verify video player loads
- [ ] Check video controls:
  - Play/Pause button
  - Volume control
  - Fullscreen toggle
  - Progress bar
  - Time display

#### 5.2 Video Playback
- [ ] Click play button
- [ ] Verify video starts playing
- [ ] Test pause functionality
- [ ] Test seek/scrub through timeline
- [ ] Verify smooth playback without buffering

#### 5.3 Subtitle Display
- [ ] Verify German subtitles appear
- [ ] Check subtitle synchronization with audio
- [ ] Test subtitle styling and readability
- [ ] Verify subtitle position on screen

#### 5.4 Interactive Subtitles
- [ ] Click on subtitle words (if clickable)
- [ ] Check word definition popup/tooltip
- [ ] Test marking words from subtitles
- [ ] Verify vocabulary integration

#### 5.5 Playback Controls
- [ ] Test playback speed adjustment
- [ ] Test 10-second skip forward/backward
- [ ] Test keyboard shortcuts:
  - Space: Play/Pause
  - Arrow keys: Seek
  - F: Fullscreen
- [ ] Test loop segment feature (if available)

### 6. Learning Progress & Analytics

#### 6.1 Progress Tracking
- [ ] Complete watching a segment
- [ ] Verify progress is saved
- [ ] Check progress indicators update
- [ ] Navigate away and return
- [ ] Verify progress persists

#### 6.2 Vocabulary Progress
- [ ] Return to vocabulary library
- [ ] Check if watched words are marked
- [ ] Verify statistics updated
- [ ] Check learning history

#### 6.3 Episode Progress
- [ ] Return to episode list
- [ ] Verify watched episodes marked
- [ ] Check progress percentage
- [ ] Test resume functionality

### 7. Additional Features

#### 7.1 Video Processing
- [ ] Upload new video (if admin)
- [ ] Trigger transcription
- [ ] Monitor processing progress
- [ ] Verify subtitle generation

#### 7.2 Settings & Preferences
- [ ] Access user settings
- [ ] Modify display preferences
- [ ] Change playback defaults
- [ ] Test language settings

#### 7.3 Responsive Design
- [ ] Test on different screen sizes
- [ ] Verify mobile responsiveness
- [ ] Check tablet layout
- [ ] Test orientation changes

### 8. Error Handling & Edge Cases

#### 8.1 Network Issues
- [ ] Test with slow connection
- [ ] Simulate connection loss
- [ ] Verify error messages
- [ ] Test retry mechanisms

#### 8.2 Invalid Data
- [ ] Test with invalid login credentials
- [ ] Try accessing protected routes without auth
- [ ] Test with malformed requests
- [ ] Verify validation messages

#### 8.3 Browser Compatibility
- [ ] Test on Chrome
- [ ] Test on Firefox
- [ ] Test on Safari
- [ ] Test on Edge

## Performance Checklist

### Page Load Times
- [ ] Landing page: < 2 seconds
- [ ] Dashboard: < 3 seconds
- [ ] Video player: < 5 seconds
- [ ] Vocabulary library: < 2 seconds

### Interaction Response
- [ ] Button clicks: < 200ms feedback
- [ ] Form submissions: < 1 second
- [ ] Page transitions: < 500ms
- [ ] Search/filter: < 300ms

## Security Checklist

- [ ] JWT tokens properly stored
- [ ] Sensitive data not in localStorage
- [ ] API requests use authentication
- [ ] CORS properly configured
- [ ] Input validation on all forms
- [ ] XSS protection verified

## Accessibility Checklist

- [ ] Keyboard navigation works
- [ ] Tab order is logical
- [ ] ARIA labels present
- [ ] Color contrast sufficient
- [ ] Screen reader compatible
- [ ] Focus indicators visible

## Bug Reporting Template

When issues are found during QA testing, document them using this format:

```markdown
### Issue: [Brief description]
**Severity**: Critical | High | Medium | Low
**Component**: Frontend | Backend | Database | Integration
**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result**: [What should happen]
**Actual Result**: [What actually happens]
**Screenshots**: [If applicable]
**Browser/Environment**: [Chrome 120, Windows 11, etc.]
**Additional Notes**: [Any other relevant information]
```

## Test Execution Log

### Test Run Information
- **Date**: [Test date]
- **Tester**: [Name]
- **Environment**: [Dev/Staging/Prod]
- **Build Version**: [Version number]

### Results Summary
- Total Tests: [Number]
- Passed: [Number]
- Failed: [Number]
- Blocked: [Number]
- Skipped: [Number]

### Critical Issues Found
1. [Issue 1]
2. [Issue 2]
3. [Issue 3]

## Automation Script Commands

### Browser MCP Setup
```javascript
// Connect to application
await browser.navigate('http://localhost:3000')

// Take snapshot for element references
await browser.snapshot()

// Interact with elements
await browser.click('element', 'ref_from_snapshot')
await browser.type('element', 'ref', 'text_to_type', false)

// Wait for loading
await browser.wait(2)

// Take screenshot for documentation
await browser.screenshot()
```

### Common Test Patterns
```javascript
// Login flow
await browser.navigate('http://localhost:3000/login')
await browser.type('username_field', 'ref', 'qa_user_123', false)
await browser.type('password_field', 'ref', 'QaTest123!@#', false)
await browser.click('login_button', 'ref')
await browser.wait(2)

// Check for success
await browser.snapshot()
// Verify dashboard loaded

// Navigate to video
await browser.navigate('http://localhost:3000/episodes')
await browser.click('first_episode', 'ref')
await browser.wait(3)

// Start video playback
await browser.click('play_button', 'ref')
await browser.wait(5)
await browser.screenshot()
```

## Continuous Testing

### Daily Smoke Tests
- User login/logout
- Video playback
- Vocabulary marking
- Basic navigation

### Weekly Regression Tests
- Full workflow testing
- All CRUD operations
- Edge case scenarios
- Performance benchmarks

### Release Testing
- Complete QA workflow
- Cross-browser testing
- Load testing
- Security audit

## Notes & Observations

### Known Issues
- [List any known issues that shouldn't be reported]

### Areas Needing Improvement
- [List areas identified for enhancement]

### Positive Findings
- [List features working exceptionally well]

---

**Last Updated**: December 2024
**Version**: 1.0
**Next Review**: January 2025