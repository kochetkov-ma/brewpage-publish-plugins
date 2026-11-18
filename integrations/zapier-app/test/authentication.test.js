'use strict';

const { test, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const h = require('./helpers');

afterEach(h.reset);

const authTest = h.App.authentication.test;

test('GIVEN an optional owner token WHEN testing the connection THEN it is checked and labelled', async () => {
  const rows = [
    {
      name: 'blank token publishes anonymously',
      token: '',
      publications: 500,
      reach: 'token',
      result: {
        output: { reach: 'token', connection: 'Anonymous publishing' },
        error: null,
      },
      calls: ['/api/limits'],
    },
    {
      name: 'profile token',
      token: h.TOKEN,
      publications: 200,
      reach: 'profile',
      result: {
        output: { reach: 'profile', connection: 'Profile owner token' },
        error: null,
      },
      calls: ['/api/publications?limit=1', '/api/limits'],
    },
    {
      name: 'revoked token',
      token: h.TOKEN,
      publications: 403,
      reach: 'token',
      result: {
        output: null,
        error: {
          message:
            'Your owner token is revoked or expired. Mint a new one at https://account.brewpage.app.',
          code: 'OWNER_TOKEN_REJECTED',
          status: 401,
        },
      },
      calls: ['/api/publications?limit=1'],
    },
    {
      name: 'malformed token',
      token: 'not-a-token',
      publications: 500,
      reach: 'token',
      result: {
        output: null,
        error: {
          message:
            'Your owner token does not appear to be valid. It is 32 letters and digits.',
          code: 'INVALID_OWNER_TOKEN',
          status: 401,
        },
      },
      calls: [],
    },
  ];
  for (const row of rows) {
    h.reset();
    const publications = h.intercept(
      'GET',
      '/api/publications',
      row.publications,
      {
        items: [],
        total: 0,
      },
    );
    const limits = h.intercept('GET', '/api/limits', 200, { reach: row.reach });

    const result = await h
      .appTester(authTest, { authData: { ownerToken: row.token } })
      .then(
        (output) => ({ output, error: null }),
        (error) => ({ output: null, error: JSON.parse(error.message) }),
      );

    assert.deepEqual(
      { result, calls: [...publications, ...limits].map((call) => call.path) },
      { result: row.result, calls: row.calls },
      `${row.name}: exact checks and connection result`,
    );
  }
});

test('GIVEN an owner connection WHEN requesting a URL THEN only exact API routes receive BrewPage headers', async () => {
  // GIVEN the five intended operations and neighbouring method, host, port and path variants.
  const rows = [
    { method: 'GET', url: 'https://brewpage.app/api/limits', expected: true },
    {
      method: 'GET',
      url: 'https://brewpage.app/api/publications?limit=1',
      expected: true,
    },
    { method: 'POST', url: 'https://brewpage.app/api/html', expected: true },
    { method: 'POST', url: 'https://brewpage.app/api/files', expected: true },
    { method: 'POST', url: 'https://brewpage.app/api/json', expected: true },
    { method: 'GET', url: 'https://brewpage.app/api/html', expected: false },
    { method: 'GET', url: 'https://brewpage.app/api/files', expected: false },
    { method: 'POST', url: 'https://brewpage.app/api/other', expected: false },
    {
      method: 'GET',
      url: 'https://brewpage.app/api/limits/extra',
      expected: false,
    },
    { method: 'GET', url: 'https://brewpage.app/', expected: false },
    {
      method: 'GET',
      url: 'https://files.brewpage.app/api/limits',
      expected: false,
    },
    {
      method: 'GET',
      url: 'https://brewpage.app:8443/api/limits',
      expected: false,
    },
    { method: 'GET', url: 'http://brewpage.app/api/limits', expected: false },
    {
      method: 'GET',
      url: 'https://brewpage.app/api/limits',
      redirectTo: 'https://brewpage.app/my/report',
      expected: true,
    },
    {
      method: 'POST',
      url: 'https://brewpage.app/api/html',
      redirectTo: 'https://files.example.test/upload',
      expected: true,
    },
  ];
  for (const row of rows) {
    h.reset();
    const url = new URL(row.url);
    const calls = [];
    h.nock(url.origin)
      .intercept(url.pathname, row.method)
      .query(true)
      .reply(
        row.redirectTo ? 302 : 200,
        row.redirectTo ? '' : { outcome: 'observed' },
        row.redirectTo ? { Location: row.redirectTo } : {},
      )
      .on('request', (req) => {
        calls.push({
          userAgent: req.headers.get('user-agent'),
          ownerToken: req.headers.get('x-owner-token'),
        });
      });

    const redirectedCalls = [];
    for (const target of row.redirectTo ? [row.redirectTo] : []) {
      const redirected = new URL(target);
      h.nock(redirected.origin)
        .get(redirected.pathname)
        .reply(200, { outcome: 'redirected' })
        .on('request', () => redirectedCalls.push('followed'));
    }

    // WHEN the real SDK executes the application middleware and HTTP request.
    const result = await h.appTester(
      async (z) =>
        z.request({ method: row.method, url: row.url }).then(
          (response) => ({ output: response.data, error: null }),
          (error) => ({
            output: null,
            error: { name: error.name, type: error.type },
          }),
        ),
      { authData: { ownerToken: h.TOKEN } },
    );

    // THEN the full request observation and response preserve the exact authorization scope.
    assert.deepEqual(
      { calls, redirectedCalls, result },
      {
        calls: [
          {
            userAgent: row.expected ? h.USER_AGENT : 'Zapier',
            ownerToken: row.expected ? h.TOKEN : null,
          },
        ],
        redirectedCalls: [],
        result: row.redirectTo
          ? { output: null, error: { name: 'FetchError', type: 'no-redirect' } }
          : { output: { outcome: 'observed' }, error: null },
      },
      `${row.method} ${row.url}: exact API authorization boundary`,
    );
  }
});
