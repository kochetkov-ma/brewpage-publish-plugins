'use strict';

const { test, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const h = require('./helpers');

afterEach(h.reset);

const perform = h.App.creates.publish_page.operation.perform;

test('GIVEN page input WHEN publishing THEN exact request is sent and mapped output returned', async () => {
  const rows = [
    {
      name: 'private html with title, ttl and owner token',
      authData: { ownerToken: h.TOKEN },
      inputData: {
        content: '<h1>Report</h1>',
        format: 'html',
        title: 'Weekly / Report',
        visibility: 'private',
        ttl: 7,
      },
      path: '/api/html?ns=my&format=html&ttl=7',
      body: {
        content: '<h1>Report</h1>',
        format: 'html',
        filename: 'Weekly Report.html',
      },
      reply: {
        id: 'Xk3pQ9mT2a',
        namespace: 'my',
        link: 'https://xk3pq9mt2a.brewpage.app/',
        title: 'Report',
        format: 'html',
        access: 'unlisted',
        expiresAt: '2026-11-13T10:00:00Z',
        sizeBytes: 15,
        ownerToken: h.TOKEN,
        manageUrl: 'https://brewpage.app/manage/SECRET',
        result: { code: 'success', action: 'created' },
      },
      output: {
        id: 'Xk3pQ9mT2a',
        url: 'https://xk3pq9mt2a.brewpage.app/',
        title: 'Report',
        format: 'html',
        visibility: 'private',
        namespace: 'my',
        expires_at: '2026-11-13T10:00:00Z',
        size_bytes: 15,
        owner_token: h.TOKEN,
        reused_existing: false,
        notices: '',
      },
    },
    {
      name: 'public markdown without optional fields or token, merged',
      authData: {},
      inputData: {
        content: '# Notes',
        format: 'markdown',
        title: '',
        visibility: 'public',
        ttl: '',
      },
      path: '/api/html?ns=public&format=markdown',
      body: { content: '# Notes', format: 'markdown' },
      reply: {
        id: 'AbCdEf1234',
        namespace: 'public',
        link: 'https://brewpage.app/public/AbCdEf1234',
        format: 'markdown',
        access: 'public',
        expiresAt: '2026-11-21T10:00:00Z',
        sizeBytes: 7,
        ownerToken: 'ZyXwVu9876543210TsRqPo9876543210',
        result: { code: 'duplicate', action: 'merged' },
        notices: [
          { code: 'ttl-clamped', message: 'TTL clamped to 30 days.' },
          { code: 'owner-token-new', message: 'Save the new ownerToken.' },
        ],
      },
      output: {
        id: 'AbCdEf1234',
        url: 'https://brewpage.app/public/AbCdEf1234',
        title: null,
        format: 'markdown',
        visibility: 'public',
        namespace: 'public',
        expires_at: '2026-11-21T10:00:00Z',
        size_bytes: 7,
        owner_token: 'ZyXwVu9876543210TsRqPo9876543210',
        reused_existing: true,
        notices: 'TTL clamped to 30 days. Save the new ownerToken.',
      },
    },
  ];
  assert.equal(rows.length, 2, 'Both formats and visibilities are covered');
  for (const row of rows) {
    h.reset();
    const calls = h.intercept('POST', '/api/html', 201, row.reply);

    const output = await h.appTester(perform, {
      authData: row.authData,
      inputData: row.inputData,
    });

    assert.deepEqual(
      { calls, output },
      {
        calls: [
          {
            path: row.path,
            userAgent: h.USER_AGENT,
            ownerToken: row.authData.ownerToken ?? null,
            body: row.body,
          },
        ],
        output: row.output,
      },
      `${row.name}: one exact request and only mapped fields`,
    );
  }
});

test('GIVEN invalid input or an API failure WHEN publishing THEN a clear error is raised', async () => {
  const rows = [
    {
      inputData: { content: '  ', format: 'html' },
      error: [
        'Content is empty. Map the HTML or Markdown to publish.',
        'EMPTY_CONTENT',
        400,
      ],
      calls: 0,
    },
    {
      inputData: { content: '<p>x</p>', format: 'html', title: 'ab' },
      error: [
        'Title must be at least 4 characters long.',
        'INVALID_TITLE',
        400,
      ],
      calls: 0,
    },
    {
      inputData: { content: '<p>x</p>', format: 'html', ttl: 91 },
      error: [
        'Lifetime must be a whole number of days from 1 to 90.',
        'INVALID_TTL',
        400,
      ],
      calls: 0,
    },
    {
      inputData: { content: '<p>x</p>', format: 'html' },
      error: [
        'BrewPage rejected the request: Content is too large',
        'BREWPAGE_400',
        400,
      ],
      calls: 1,
    },
  ];
  for (const row of rows) {
    h.reset();
    const calls = h.intercept('POST', '/api/html', 400, {
      message: 'Content is too large',
    });

    await assert.rejects(
      h.appTester(perform, { authData: {}, inputData: row.inputData }),
      h.appError(...row.error),
      `${row.error[1]} is rejected`,
    );
    assert.equal(calls.length, row.calls, `${row.error[1]}: request count`);
  }
});
