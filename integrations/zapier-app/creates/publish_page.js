'use strict';

const {
  API,
  blank,
  checkedLink,
  namespaceFor,
  noticeText,
  ttlParam,
  visibilityOf,
  visibilityParam,
} = require('../lib/brewpage');
const fields = require('../lib/fields');

const EXTENSIONS = { html: '.html', markdown: '.md' };
const MAX_BYTES = 5 * 1024 * 1024;

// The API keeps a name of 4-200 chars without path or control characters.
const titleFilename = (z, title, format) => {
  if (blank(title)) return undefined;
  const clean = String(title)
    .replace(/[\\/\u0000-\u001f]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, 190)
    .trim();
  if (clean.length < 4) {
    throw new z.errors.Error(
      'Title must be at least 4 characters long.',
      'INVALID_TITLE',
      400,
    );
  }
  const extension = EXTENSIONS[format];
  return clean.toLowerCase().endsWith(extension) ? clean : clean + extension;
};

const perform = async (z, bundle) => {
  const input = bundle.inputData;
  const format = blank(input.format) ? 'html' : String(input.format).trim();
  if (!EXTENSIONS[format]) {
    throw new z.errors.Error(
      'Format must be HTML or Markdown.',
      'INVALID_FORMAT',
      400,
    );
  }
  const content = typeof input.content === 'string' ? input.content : '';
  if (content.trim() === '') {
    throw new z.errors.Error(
      'Content is empty. Map the HTML or Markdown to publish.',
      'EMPTY_CONTENT',
      400,
    );
  }
  if (Buffer.byteLength(content, 'utf8') > MAX_BYTES) {
    throw new z.errors.Error(
      'Content is larger than the 5 MB page limit.',
      'CONTENT_TOO_LARGE',
      400,
    );
  }
  const visibility = visibilityParam(z, input.visibility);
  const filename = titleFilename(z, input.title, format);
  const response = await z.request({
    method: 'POST',
    url: `${API}/html`,
    params: {
      ns: namespaceFor(visibility),
      format,
      ...ttlParam(z, input.ttl),
    },
    headers: { 'Content-Type': 'application/json' },
    body: { content, format, ...(filename ? { filename } : {}) },
  });
  const page = response.data;
  return {
    id: page.id,
    url: checkedLink(z, page.link),
    title: page.title ?? null,
    format: page.format ?? format,
    visibility: visibilityOf(page.access),
    namespace: page.namespace,
    expires_at: page.expiresAt,
    size_bytes: page.sizeBytes,
    owner_token: page.ownerToken ?? null,
    reused_existing: page.result?.action === 'merged',
    notices: noticeText(page.notices),
  };
};

module.exports = {
  key: 'publish_page',
  noun: 'Page',
  display: {
    label: 'Publish HTML or Markdown Page',
    description:
      'Publishes HTML or Markdown as a web page and returns its link.',
  },
  operation: {
    perform,
    inputFields: [
      {
        key: 'content',
        label: 'Content',
        type: 'text',
        required: true,
        helpText: 'HTML or Markdown to publish, up to 5 MB.',
      },
      {
        key: 'format',
        label: 'Format',
        type: 'string',
        required: true,
        default: 'html',
        choices: [
          { value: 'html', label: 'HTML', sample: 'html' },
          { value: 'markdown', label: 'Markdown', sample: 'markdown' },
        ],
      },
      {
        key: 'title',
        label: 'Title',
        type: 'string',
        required: false,
        helpText:
          'Shown in the browser tab when the content has no `<title>` or heading. Also used as the download file name. At least 4 characters.',
      },
      fields.visibility,
      fields.ttl,
    ],
    sample: {
      id: 'Xk3pQ9mT2a',
      url: 'https://brewpage.app/my/Xk3pQ9mT2a',
      title: 'Weekly Report',
      format: 'html',
      visibility: 'private',
      namespace: 'my',
      expires_at: '2026-11-21T10:15:00Z',
      size_bytes: 2048,
      owner_token: 'AbCdEf0123456789GhIjKl0123456789',
      reused_existing: false,
      notices: '',
    },
    outputFields: [
      { key: 'id', label: 'Page ID' },
      { key: 'url', label: 'Page URL' },
      { key: 'title', label: 'Title' },
      { key: 'format', label: 'Format' },
      { key: 'visibility', label: 'Visibility' },
      { key: 'namespace', label: 'Namespace' },
      { key: 'expires_at', label: 'Expires At', type: 'datetime' },
      { key: 'size_bytes', label: 'Size (bytes)', type: 'integer' },
      { key: 'owner_token', label: 'Owner Token (keep private)' },
      {
        key: 'reused_existing',
        label: 'Reused Existing Page',
        type: 'boolean',
      },
      { key: 'notices', label: 'Notices' },
    ],
  },
};
