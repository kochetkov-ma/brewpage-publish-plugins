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
