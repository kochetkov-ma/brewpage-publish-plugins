'use strict';

const { test, afterEach } = require('node:test');
const assert = require('node:assert/strict');
const h = require('./helpers');

afterEach(h.reset);

const perform = h.App.creates.upload_file.operation.perform;
const SOURCE = 'https://files.example.test';
const PDF = '%PDF-1.7 fixture';

// Reads the single multipart part back as name, type and bytes.
const part = (body) => {
  const match =
    /Content-Disposition: form-data; name="file"; filename="([^"]+)"\r\nContent-Type: ([^\r]+)\r\n\r\n([\s\S]*?)\r\n--/.exec(
      body,
    );
  return match && { filename: match[1], contentType: match[2], data: match[3] };
};

const source = (path, headers) => {
  const seen = [];
  h.nock(SOURCE)
    .get(path)
    .reply(function () {
      return [200, PDF, headers];
    })
    .on('request', (req) => {
      seen.push({
        userAgent: req.headers.get('user-agent'),
        ownerToken: req.headers.get('x-owner-token'),
      });
    });
  return seen;
};

test('GIVEN a file WHEN uploading THEN the source is fetched without credentials and posted as multipart', async () => {
  const rows = [
    {
      name: 'named public upload with owner token and ttl',
      authData: { ownerToken: h.TOKEN },
      inputData: {
        file: `${SOURCE}/hydrated/abc123`,
        filename: 'Quarterly report.pdf',
        visibility: 'public',
        ttl: '30',
      },
      sourcePath: '/hydrated/abc123',
      sourceHeaders: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'attachment; filename="ignored.pdf"',
      },
      path: '/api/files?ns=public&ttl=30',
      part: {
        filename: 'Quarterly report.pdf',
        contentType: 'application/pdf',
        data: PDF,
      },
      reply: {
        id: 'Rb7Lm2Qx9Z',
        namespace: 'public',
        filename: 'Quarterly report.pdf',
        contentType: 'application/pdf',
        sizeBytes: 16,
        link: 'https://brewpage.app/public/Rb7Lm2Qx9Z',
        access: 'public',
        expiresAt: '2026-12-06T10:00:00Z',
        ownerToken: h.TOKEN,
      },
      output: {
        id: 'Rb7Lm2Qx9Z',
        url: 'https://brewpage.app/public/Rb7Lm2Qx9Z',
        filename: 'Quarterly report.pdf',
        content_type: 'application/pdf',
        visibility: 'public',
        namespace: 'public',
        expires_at: '2026-12-06T10:00:00Z',
        size_bytes: 16,
        owner_token: h.TOKEN,
        reused_existing: false,
        notices: '',
      },
    },
    {
      name: 'private upload named by Content-Disposition, merged, no token',
      authData: {},
      inputData: {
        file: `${SOURCE}/x/y`,
        filename: '',
        visibility: '',
        ttl: '',
      },
      sourcePath: '/x/y',
      sourceHeaders: {
        'Content-Type': 'application/pdf',
        'Content-Disposition':
          "attachment; filename*=UTF-8''r%C3%A9sum%C3%A9.pdf",
      },
      path: '/api/files?ns=my',
      part: {
        filename: 'résumé.pdf',
        contentType: 'application/pdf',
        data: PDF,
      },
      reply: {
        id: 'Qw8Er4Ty6U',
        namespace: 'my',
        filename: 'résumé.pdf',
        contentType: 'application/pdf',
        sizeBytes: 16,
        link: 'https://qw8er4ty6u.brewpage.app/',
        access: 'unlisted',
        expiresAt: '2026-11-21T10:00:00Z',
        result: {
          code: 'duplicate',
          action: 'merged',
          extras: { isOwner: false },
        },
        notices: [
          { code: 'namespace-defaulted', message: 'Private namespace.' },
        ],
      },
      output: {
        id: 'Qw8Er4Ty6U',
        url: 'https://qw8er4ty6u.brewpage.app/',
        filename: 'résumé.pdf',
        content_type: 'application/pdf',
        visibility: 'private',
        namespace: 'my',
        expires_at: '2026-11-21T10:00:00Z',
        size_bytes: 16,
        owner_token: null,
        reused_existing: true,
        notices: 'Private namespace.',
      },
    },
  ];
  for (const row of rows) {
    h.reset();
    const seen = source(row.sourcePath, row.sourceHeaders);
    const calls = h.intercept('POST', '/api/files', 201, row.reply);

    const output = await h.appTester(perform, {
      authData: row.authData,
      inputData: row.inputData,
    });

    assert.deepEqual(
      {
        seen,
        calls: calls.map((call) => ({ ...call, body: part(call.body) })),
        output,
      },
      {
        seen: [{ userAgent: 'Zapier', ownerToken: null }],
        calls: [
          {
            path: row.path,
            userAgent: h.USER_AGENT,
            ownerToken: row.authData.ownerToken ?? null,
            body: row.part,
          },
        ],
        output: row.output,
      },
      `${row.name}: source gets no BrewPage headers, upload is exact`,
    );
  }
});

test('GIVEN an oversized upload WHEN BrewPage answers 413 THEN a clear error is raised', async () => {
  const seen = source('/big.bin', { 'Content-Type': 'application/zip' });
  const calls = h.intercept('POST', '/api/files', 413, {
    message: 'Request body exceeds 25 MiB',
  });

  await assert.rejects(
    h.appTester(perform, {
      authData: {},
      inputData: { file: `${SOURCE}/big.bin` },
    }),
    h.appError(
      'The upload is larger than the 25 MB request limit: Request body exceeds 25 MiB',
      'BREWPAGE_413',
      413,
    ),
    '413 maps to the size message',
  );
  assert.deepEqual(
    { seen: seen.length, calls: calls.length },
    { seen: 1, calls: 1 },
    'One download and one upload attempt, no retry',
  );
});
