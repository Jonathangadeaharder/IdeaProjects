import { test, expect } from 'vitest';
import { parseSRT } from './utils';

describe('SRT Parsing', () => {
  const sampleSRT = `1
00:00:01,000 --> 00:00:04,000
This is a test subtitle

2
00:00:05,000 --> 00:00:08,000
This is another test subtitle | This is the translation

3
00:00:10,000 --> 00:00:13,000
Single language subtitle
`;

  test('parses SRT content correctly', () => {
    const parsed = parseSRT(sampleSRT);
    
    expect(parsed).toHaveLength(3);
    expect(parsed[0]).toEqual({
      start: 1,
      end: 4,
      text: 'This is a test subtitle',
      translation: ''
    });
    
    expect(parsed[1]).toEqual({
      start: 5,
      end: 8,
      text: 'This is another test subtitle',
      translation: 'This is the translation'
    });
    
    expect(parsed[2]).toEqual({
      start: 10,
      end: 13,
      text: 'Single language subtitle',
      translation: ''
    });
  });

  test('handles empty SRT content', () => {
    const parsed = parseSRT('');
    expect(parsed).toHaveLength(0);
  });

  test('handles malformed SRT blocks', () => {
    const malformedSRT = `1
Invalid timestamp
This is invalid

2
00:00:01,000 --> 00:00:04,000
This is valid
`;
    
    const parsed = parseSRT(malformedSRT);
    expect(parsed).toHaveLength(1);
    expect(parsed[0].text).toBe('This is valid');
  });
});