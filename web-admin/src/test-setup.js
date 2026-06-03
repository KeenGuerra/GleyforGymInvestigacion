import '@testing-library/jest-dom';
import { beforeAll, afterAll } from 'vitest';

// ─── Global localStorage mock ──────────────────────────────────────────────
const store = {};

Object.defineProperty(globalThis, 'localStorage', {
  value: {
    getItem: (key) => store[key] ?? null,
    setItem: (key, value) => { store[key] = String(value); },
    removeItem: (key) => { delete store[key]; },
    clear: () => { Object.keys(store).forEach((k) => delete store[k]); },
  },
  writable: true,
});

delete globalThis.location;
globalThis.location = {
  href: 'http://localhost/',
  origin: 'http://localhost',
  protocol: 'http:',
  host: 'localhost',
  hostname: 'localhost',
  port: '',
  pathname: '/',
  search: '',
  hash: '',
  assign: () => {},
  replace: () => {},
  reload: () => {},
};

// ─── Silence noisy console.error in tests ─────────────────────────────────
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (typeof args[0] === 'string' && args[0].includes('Warning')) return;
    originalError(...args);
  };
});
afterAll(() => {
  console.error = originalError;
});
