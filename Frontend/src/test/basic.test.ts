import { describe, it, expect } from 'vitest';

describe('Basic Test Suite', () => {
  it('should perform basic arithmetic', () => {
    expect(2 + 2).toBe(4);
  });

  it('should handle string operations', () => {
    expect('hello'.toUpperCase()).toBe('HELLO');
  });

  it('should work with arrays', () => {
    const arr = [1, 2, 3];
    expect(arr.length).toBe(3);
    expect(arr.includes(2)).toBe(true);
  });

  it('should handle async operations', async () => {
    const promise = Promise.resolve('test');
    const result = await promise;
    expect(result).toBe('test');
  });
});