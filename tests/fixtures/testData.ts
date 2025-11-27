/**
 * Test Data and Constants
 * Contains all test users, credentials, and test data for E2E tests
 */

export const TEST_USERS = {
  valid: {
    email: 'testuser@example.com',
    username: 'testuser',
    password: 'ValidPass123!',
  },
  validAlternate: {
    email: 'testuser2@example.com',
    username: 'testuser2',
    password: 'AnotherPass123!',
  },
  invalid: {
    weakPassword: {
      email: 'weakpass@example.com',
      username: 'weakpassuser',
      password: 'Weak123!', // Less than 12 chars
    },
    noSpecialChar: {
      email: 'nospecial@example.com',
      username: 'nospecialuser',
      password: 'NoSpecial123456', // No special character
    },
  },
};

export const VOCABULARY_DATA = {
  a1: {
    level: 'A1',
    totalWords: 715,
    wordsPerPage: 100,
    totalPages: 8,
    firstWords: ['Haus', 'ab', 'Abend', 'abendessen', 'aber', 'abfahren'],
    testWord: 'Haus',
  },
  a2: {
    level: 'A2',
    totalWords: 574,
  },
  b1: {
    level: 'B1',
    totalWords: 896,
  },
  b2: {
    level: 'B2',
    totalWords: 1409,
  },
  c1: {
    level: 'C1',
    totalWords: 0,
  },
  c2: {
    level: 'C2',
    totalWords: 0,
  },
};

export const API_ENDPOINTS = {
  auth: {
    register: '/api/auth/register',
    login: '/api/auth/login',
    logout: '/api/auth/logout',
    me: '/api/auth/me',
  },
  vocabulary: {
    stats: '/api/vocabulary/stats',
    library: '/api/vocabulary/library',
    markKnown: '/api/vocabulary/mark-known',
  },
  videos: {
    list: '/api/videos',
  },
};

export const ROUTES = {
  home: '/',
  login: '/login',
  register: '/register',
  videos: '/videos',
  vocabulary: '/vocabulary',
};

export const TIMEOUTS = {
  api: 10000,
  pageLoad: 10000,
  interaction: 5000,
};
