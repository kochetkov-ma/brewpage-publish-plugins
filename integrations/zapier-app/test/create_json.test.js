'use strict';

const { test, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const h = require('./helpers');

afterEach(h.reset);

const perform = h.App.creates.create_json.operation.perform;

test('GIVEN JSON input WHEN creating a document THEN it is posted privately or rejected before any request', async () => {
  const rows = [
    {
      name: 'object with ttl and token',
      authData: { ownerToken: h.TOKEN },
      inputData: { json: ' {"status":"ok","count":3} ', ttl: 5 },
      calls: [
        {
          path: '/api/json?ns=my&ttl=5',
          userAgent: h.USER_AGENT,
          ownerToken: h.TOKEN,
          body: { status: 'ok', count: 3 },
        },
      ],
      output: {
        id: 'Jd4Nc8Wq1P',
        url: 'https://brewpage.app/json/my/Jd4Nc8Wq1P',
        namespace: 'my',
        expires_at: '2026-11-11T10:00:00Z',
        size_bytes: 26,
        owner_token: h.TOKEN,
        notices: '',
      },
      error: null,
    },
    {
      name: 'invalid JSON',
      authData: {},
      inputData: { json: '{status: ok}' },
      calls: [],
      output: null,
      error: {
        message:
          'JSON is not valid. Map or type a JSON object, array or value.',
        code: 'INVALID_JSON',
        status: 400,
      },
    },
  ];
  for (const row of rows) {
    h.reset();
    const calls = h.intercept('POST', '/api/json', 201, {
      id: 'Jd4Nc8Wq1P',
      namespace: 'my',
      link: 'https://brewpage.app/json/my/Jd4Nc8Wq1P',
      expiresAt: '2026-11-11T10:00:00Z',
      sizeBytes: 26,
      ownerToken: h.TOKEN,
      access: 'unlisted',
    });

    const outcome = await h
      .appTester(perform, { authData: row.authData, inputData: row.inputData })
      .then(
        (output) => ({ output, error: null }),
        (error) => ({ output: null, error: JSON.parse(error.message) }),
      );

    assert.deepEqual(
      { calls, ...outcome },
      {
        calls: row.calls,
        output: row.output,
        error: row.error,
      },
      `${row.name}: exact request, output and error`,
    );
  }
});
