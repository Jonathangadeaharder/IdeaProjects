# E2E Test Opportunities - LangPlug Application

**Date**: 2025-10-11
**Method**: Manual exploration with Chrome DevTools MCP
**Status**: Partial exploration completed (blocked by backend argon2-cffi issue)

## Summary

This document outlines E2E test opportunities identified through manual exploration of the LangPlug application. The exploration was conducted using Chrome DevTools to interact with the live application and identify critical user workflows.

## Critical Blocker

**Backend Issue**: The backend server crashes during user registration due to missing argon2-cffi backend, despite the package being installed in the venv. This prevents testing of authenticated user flows.

**Error**: `passlib.exc.MissingBackendError: argon2: no backends available`

**Resolution Needed**: Manual installation of argon2-cffi in the Windows environment running the backend server.

## Test Opportunities Identified

### 1. Landing Page and Navigation ✓

**Status**: Verified Working

**User Flow**:
1. Navigate to `http://localhost:3000`
2. Landing page displays with:
   - Hero section: "Learn German Through Your Favorite Shows"
   - 6 feature cards: Watch & Learn, Smart Vocabulary, Interactive Games, Track Progress, Context-Based, Chunked Learning
   - Two CTA buttons: "Get Started Free" and "Sign In"

**E2E Test Scenarios**:
- Verify landing page loads within 3 seconds
- Verify all 6 feature cards are present with correct content
- Verify "Get Started Free" button navigates to registration page
- Verify "Sign In" button navigates to login page
- Verify responsive design at different viewport sizes

**Assertion Points**:
- Page title: "LangPlug - German Learning Platform"
- Hero heading exists and contains "Learn German"
- All navigation buttons are clickable
- No console errors on page load

---

### 2. User Registration Flow ⚠️

**Status**: Partially Verified (Blocked by backend issue)

**User Flow**:
1. Click "Get Started Free" from landing page
2. Registration form displays with fields:
   - Email (email input)
   - Username (text input)
   - Password (password input with show/hide toggle)
   - Confirm Password (password input)
3. Password requirements displayed:
   - At least 12 characters
   - Passwords must match
4. Fill form and click "Sign Up"
5. **Expected**: Redirect to dashboard with authenticated session
6. **Actual**: Error message "Failed to create account. Please try again."

**E2E Test Scenarios**:
- **Happy Path**: Valid registration creates account and logs in user
- **Validation**: Empty fields show validation errors
- **Validation**: Password < 12 characters shows error
- **Validation**: Non-matching passwords show error
- **Validation**: Invalid email format shows error
- **Error Handling**: Duplicate email/username shows appropriate error
- **UI State**: Form disables during submission (shows "Creating Account...")

**Assertion Points**:
- Form validation triggers before API call
- API returns 201 on successful registration
- User is automatically logged in after registration
- Auth token is stored in localStorage/sessionStorage
- Redirect to dashboard occurs
- Success toast/notification appears

**Backend Requirement**: argon2-cffi must be properly installed

---

### 3. User Login Flow

**Status**: Not Yet Tested

**User Flow**:
1. Click "Sign In" from landing page OR "Sign in now" from registration page
2. Login form displays with fields:
   - Email or Username
   - Password
   - "Remember me" checkbox
3. Submit credentials
4. Redirect to dashboard on success

**E2E Test Scenarios**:
- **Happy Path**: Valid credentials log in user
- **Validation**: Empty fields show errors
- **Error Handling**: Invalid credentials show "Invalid email or password"
- **Error Handling**: Non-existent user shows appropriate error
- **Remember Me**: Checkbox persists session across browser restarts
- **Navigation**: "Need help?" link navigates to password reset
- **Navigation**: "Sign up now" link navigates to registration

**Assertion Points**:
- Login API returns 200 with access_token
- Token is stored correctly
- User object is retrieved and stored
- Dashboard loads after successful login
- Failed login shows clear error message
- Login form remains accessible after error

---

### 4. Dashboard and Authenticated Navigation

**Status**: Not Yet Tested (Requires working registration/login)

**User Flow**:
1. After successful login, user lands on dashboard
2. Dashboard should display:
   - User vocabulary stats
   - Recent learning activity
   - Quick actions (Upload Video, Browse Vocabulary, Play Game)
   - Navigation menu

**E2E Test Scenarios**:
- Verify dashboard loads with user-specific data
- Verify navigation menu is accessible
- Verify logout functionality
- Verify protected routes redirect unauthenticated users to login

**Assertion Points**:
- Dashboard displays correct user information
- API calls include authentication token
- Unauthorized requests (401) redirect to login
- Logout clears session and redirects to landing page

---

### 5. Vocabulary Browsing and Management

**Status**: Not Yet Tested

**User Flow**:
1. Navigate to Vocabulary section from dashboard
2. Browse vocabulary by level (A1, A2, B1, B2, C1)
3. View word details (translation, example sentences, context)
4. Mark words as known/unknown
5. Filter vocabulary by known/unknown status

**E2E Test Scenarios**:
- **Browse**: Load vocabulary for each level
- **Detail View**: Click word to see full details
- **Mark Known**: Toggle word known status
- **Filter**: Apply filters and verify results
- **Search**: Search for specific words
- **Progress**: Verify progress updates after marking words

**Assertion Points**:
- Vocabulary list loads without errors
- Pagination works correctly
- Word count matches API response
- Known/unknown toggle updates immediately
- Progress stats update in real-time
- Filters persist across page reloads

---

### 6. Video Upload and Processing

**Status**: Not Yet Tested

**User Flow**:
1. Navigate to Video Upload from dashboard
2. Select video file from local filesystem
3. Video uploads and begins processing
4. Progress indicator shows transcription/translation status
5. Vocabulary is extracted and displayed
6. Video is ready for chunked learning

**E2E Test Scenarios**:
- **Upload**: Select and upload valid video file
- **Validation**: Reject invalid file types
- **Validation**: Reject files exceeding size limit
- **Progress**: Show upload progress
- **Processing**: Show transcription/translation progress
- **Error Handling**: Handle processing failures gracefully
- **Completion**: Redirect to video view after processing

**Assertion Points**:
- File picker opens on button click
- Upload progress displays accurately
- Processing status updates in real-time
- Vocabulary extraction completes successfully
- Video becomes available in library

---

### 7. Chunked Learning Player

**Status**: Not Yet Tested

**User Flow**:
1. Select processed video from library
2. Video player loads with chunked interface
3. Play video chunk-by-chunk (5-minute segments)
4. View extracted vocabulary for current chunk
5. Mark vocabulary as known during playback
6. Navigate between chunks

**E2E Test Scenarios**:
- **Playback**: Video plays correctly
- **Chunks**: Navigate forward/backward between chunks
- **Vocabulary**: Display vocabulary for current chunk
- **Interaction**: Mark words as known during playback
- **Progress**: Save progress and resume from last position
- **Subtitles**: Display bilingual subtitles

**Assertion Points**:
- Video loads and plays without buffering issues
- Chunk boundaries are respected
- Vocabulary updates when chunk changes
- Progress is saved to backend
- Subtitles sync with video

---

### 8. Vocabulary Quiz/Game

**Status**: Not Yet Tested

**User Flow**:
1. Navigate to Games section
2. Select vocabulary level for quiz
3. Start quiz with words from selected level
4. Answer multiple-choice questions
5. Review results and see correct answers
6. View updated progress stats

**E2E Test Scenarios**:
- **Setup**: Select level and start quiz
- **Questions**: Display random questions from vocabulary pool
- **Answer**: Submit answers and get immediate feedback
- **Results**: Show score and correct/incorrect answers
- **Progress**: Update known/unknown status based on performance
- **Retry**: Option to retry with different words

**Assertion Points**:
- Quiz loads with correct number of questions
- Questions are randomized
- Answer feedback is immediate and correct
- Score calculation is accurate
- Progress updates persist

---

### 9. User Profile and Settings

**Status**: Not Yet Tested

**User Flow**:
1. Navigate to Profile/Settings
2. View user information
3. Update profile (name, language preferences)
4. Change password
5. View learning statistics

**E2E Test Scenarios**:
- **Profile View**: Display current user information
- **Update**: Change user details
- **Password**: Change password with validation
- **Stats**: Display accurate learning statistics
- **Preferences**: Update language pair settings

**Assertion Points**:
- Profile data loads correctly
- Updates are saved to backend
- Password change requires current password
- Statistics reflect actual user progress

---

## Backend API Endpoints to Test

Based on exploration, these endpoints need E2E coverage:

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user
- `GET /api/vocabulary/stats` - Get vocabulary statistics
- `GET /api/vocabulary/level/{level}` - Get vocabulary by level
- `POST /api/vocabulary/mark-known` - Mark word as known
- `POST /api/videos/upload` - Upload video file
- `GET /api/videos/{id}` - Get video details
- `POST /api/game/start` - Start vocabulary game
- `POST /api/game/answer` - Submit quiz answer

---

## Recommended E2E Test Priority

### High Priority (Critical User Flows)
1. **User Registration and Login** - Foundation for all authenticated features
2. **Vocabulary Browsing** - Core feature for learning
3. **Mark Word Known/Unknown** - Essential interaction
4. **Dashboard Navigation** - Entry point for authenticated users

### Medium Priority (Important Features)
5. **Video Upload and Processing** - Key differentiator
6. **Chunked Learning Player** - Main learning interface
7. **Vocabulary Quiz** - Engagement and reinforcement

### Low Priority (Nice to Have)
8. **Profile Management** - Settings and preferences
9. **Password Reset Flow** - Account recovery
10. **Multi-language Support** - Internationalization

---

## Technical Considerations

### Test Framework Recommendations
- **Playwright** - Already configured, good for cross-browser testing
- **Test Isolation** - Each test should create its own user to avoid conflicts
- **Cleanup** - Tests should clean up created users/data after completion
- **Fixtures** - Reusable fixtures for user creation, authentication, video upload

### Key Testing Patterns
- **Page Object Model** - Encapsulate page interactions
- **API Mocking** - Mock heavy operations (video processing) when needed
- **Visual Regression** - Screenshot comparison for UI consistency
- **Accessibility** - Include aria-label and keyboard navigation tests

### Performance Benchmarks
- Landing page should load < 2 seconds
- Registration/login should complete < 1 second
- Vocabulary list should load < 500ms
- Video upload should show progress immediately

---

## Next Steps

1. **Fix Backend Issue**: Resolve argon2-cffi installation problem
2. **Complete Manual Exploration**: Test authenticated flows
3. **Write E2E Tests**: Implement tests for identified scenarios
4. **CI/CD Integration**: Add E2E tests to automated pipeline
5. **Monitoring**: Add performance monitoring to E2E tests

---

## Notes

- All manual exploration was conducted via Chrome DevTools MCP
- Backend and frontend servers were running on Windows CMD (not visible from WSL)
- Log files were used to verify server status: `/mnt/c/Users/Jonandrop/IdeaProjects/LangPlug/src/backend/logs/backend.log`
- The application uses React with TypeScript for frontend and FastAPI for backend
