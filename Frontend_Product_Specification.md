# LangPlug Frontend Product Specification

## Overview

LangPlug is a Netflix-style German language learning platform that combines video content with intelligent vocabulary training. The frontend provides an engaging, responsive user interface for browsing content, playing videos, and learning German through interactive experiences.

## System Architecture

### Technology Stack
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **State Management**: Zustand
- **Styling**: Styled Components
- **Routing**: React Router v6
- **API Communication**: Axios with React Query
- **UI Components**: Custom components with Heroicons
- **Animations**: Framer Motion
- **Video Player**: React Player
- **Form Handling**: React Hook Form
- **Error Handling**: React Error Boundary
- **Notifications**: React Hot Toast

### Core Components

#### 1. Authentication System
- User registration and login forms
- Protected route management
- Session persistence
- JWT token handling

#### 2. Content Browsing
- Netflix-style video selection interface
- Series and episode browsing
- Responsive grid layouts
- Search and filtering capabilities

#### 3. Video Player
- Custom video player with playback controls
- Subtitle display and management
- 5-minute learning segment navigation
- Responsive design for all screen sizes

#### 4. Vocabulary Training
- Interactive vocabulary games (Tinder-style swiping)
- Vocabulary library with CEFR level filtering
- Word progress tracking
- Known/unknown word management

#### 5. Processing Pipeline
- Background task progress tracking
- Pipeline status visualization
- Error handling and user feedback

#### 6. Learning Experience
- Chunked learning flow
- Interactive exercises
- Progress tracking dashboard
- Performance analytics

## User Interface Components

### Authentication Pages
- **Login Screen**: Secure user authentication with form validation
- **Registration Screen**: New user onboarding with email verification

### Main Dashboard
- **Series Selection**: Grid view of available TV series
- **Episode Browser**: List view of episodes within a series
- **Search Functionality**: Find content by title or keywords

### Video Player Interface
- **Custom Video Controls**: Play, pause, volume, fullscreen
- **Subtitle Display**: Synchronized subtitle rendering
- **Learning Segments**: 5-minute segment navigation
- **Vocabulary Highlighting**: Unknown words highlighted in subtitles

### Vocabulary Training
- **Word Swiping Game**: Tinder-style interface for vocabulary learning
- **Vocabulary Library**: Browse and manage known words
- **Level Filtering**: Filter by CEFR levels (A1, A2, B1, B2)

### Processing Screens
- **Pipeline Progress**: Visual progress indicator for video processing
- **Status Updates**: Real-time processing status feedback
- **Error Messages**: Clear error communication with recovery options

## State Management

### Authentication Store (useAuthStore)
- User session data
- Authentication status
- Token management
- Login/logout functions

### Game Store (useGameStore)
- Vocabulary game state
- Current word tracking
- Swipe history
- Game progress

## API Integration

### Core Services
- **Authentication API**: User login, registration, session management
- **Video API**: Series/episode listing, video streaming
- **Processing API**: Transcription, filtering, translation pipeline
- **Vocabulary API**: Word management, library access, progress tracking

### Error Handling
- Network error recovery
- API error messaging
- Retry mechanisms
- Graceful degradation

## Responsive Design

### Breakpoints
- **Mobile**: 320px - 767px
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px and above

### Adaptive Features
- Flexible grid layouts
- Scalable typography
- Touch-friendly controls
- Orientation-aware UI adjustments

## User Experience Flows

### 1. User Onboarding
1. Landing on login/registration page
2. Account creation or authentication
3. Welcome to dashboard

### 2. Content Discovery
1. Browse series in Netflix-style grid
2. Select a series to view episodes
3. Choose an episode to begin learning

### 3. Vocabulary Preparation
1. Play vocabulary swiping game
2. Mark words as known/unknown
3. Review vocabulary library

### 4. Video Learning
1. Watch 5-minute segments with subtitles
2. See highlighted unknown words
3. Complete post-segment vocabulary review

### 5. Progress Tracking
1. View vocabulary mastery statistics
2. Track learning progress across episodes
3. Monitor CEFR level advancement

## Performance Requirements

### Loading Times
- **Initial Page Load**: < 3 seconds
- **Route Transitions**: < 1 second
- **API Responses**: < 500ms for simple operations
- **Video Streaming**: Adaptive bitrate streaming

### Browser Support
- **Chrome**: Latest 2 versions
- **Firefox**: Latest 2 versions
- **Safari**: Latest 2 versions
- **Edge**: Latest 2 versions

### Accessibility
- Keyboard navigation support
- Screen reader compatibility
- Color contrast compliance
- Focus management

## Security

### Client-Side Security
- JWT token storage in secure cookies
- Input validation and sanitization
- CORS protection
- XSS prevention

### Data Protection
- Secure password handling
- Encrypted user data transmission
- Privacy-focused data collection
- GDPR compliance

## Error Handling

### UI Error States
- Network connectivity issues
- API error responses
- Video loading failures
- Playback errors

### Recovery Mechanisms
- Automatic retry for transient errors
- User-friendly error messages
- Alternative navigation paths
- Offline capability where possible

## Testing

### Test Coverage
- **Unit Tests**: Component and utility function testing
- **Integration Tests**: API integration and state management
- **E2E Tests**: Critical user flows
- **Accessibility Tests**: WCAG compliance verification

### Testing Frameworks
- **Vitest**: Unit and integration testing
- **Testing Library**: React component testing
- **JSDOM**: DOM simulation

## Deployment

### Build Process
```bash
# Development
npm run dev

# Production Build
npm run build

# Preview Production Build
npm run preview
```

### Environment Configuration
```bash
# Required environment variables
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=LangPlug
```

### Hosting
- **Development**: Local development server
- **Production**: Static file hosting (Vercel, Netlify, etc.)
- **CDN**: Content delivery optimization

## Future Enhancements

### Planned Features
- **Mobile App**: Native mobile application
- **Social Features**: Leaderboards and friend comparisons
- **Offline Mode**: Download content for offline learning
- **Advanced Analytics**: Detailed learning insights
- **Multi-language Support**: Additional language options

### Technical Improvements
- **Performance Optimization**: Code splitting and lazy loading
- **PWA Support**: Progressive web app capabilities
- **Micro-frontend Architecture**: Modular component development
- **Real-time Collaboration**: Shared learning experiences
- **AI-Powered Recommendations**: Personalized content suggestions
