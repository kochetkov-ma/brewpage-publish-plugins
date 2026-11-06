'use strict';

const FormData = require('form-data');
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

const MAX_BYTES = 25 * 1024 * 1024;

const dispositionName = (header) => {
  if (!header) return '';
  const encoded = /filename\*=UTF-8''([^;]+)/i.exec(header);
  if (encoded) {
    try {
      return decodeURIComponent(encoded[1].trim());
    } catch {
      return '';
    }
  }
  const plain = /filename="?([^";]+)"?/i.exec(header);
  return plain ? plain[1].trim() : '';
};

const pathName = (url) => {
  try {
    const last = new URL(url).pathname.split('/').pop();
    return last ? decodeURIComponent(last) : '';
  } catch {
    return '';
  }
};

// Name order: user field, source Content-Disposition, URL path; the API fixes a wrong extension.
const fileName = (input, response, url) => {
  const name = [
    input.filename,
    dispositionName(response.headers.get('content-disposition')),
    pathName(url),
  ].find((candidate) => !blank(candidate));
  const clean = String(name || 'upload')
    .replace(/[\\/\u0000-\u001f]/g, '_')
    .trim();
  return clean || 'upload';
};

const perform = async (z, bundle) => {
  const input = bundle.inputData;
  if (blank(input.file)) {
    throw new z.errors.Error(
      'File is empty. Map a file from an earlier step.',
      'EMPTY_FILE',
      400,
    );
  }
  const url = String(input.file).trim();
  const visibility = visibilityParam(z, input.visibility);
  const ttl = ttlParam(z, input.ttl);
  const source = await z.request({ url, raw: true });
  const bytes = await source.buffer();
  if (bytes.length === 0 || bytes.length > MAX_BYTES) {
    throw new z.errors.Error(
      bytes.length === 0
        ? 'The file is empty.'
        : 'The file is larger than the 25 MB request limit.',
      'INVALID_FILE_SIZE',
      400,
    );
  }
  const form = new FormData();
  form.append('file', bytes, {
    filename: fileName(input, source, url),
    contentType:
      source.headers.get('content-type') || 'application/octet-stream',
    knownLength: bytes.length,
  });
  const response = await z.request({
    method: 'POST',
    url: `${API}/files`,
    params: { ns: namespaceFor(visibility), ...ttl },
    body: form,
  });
  const file = response.data;
  return {
    id: file.id,
    url: checkedLink(z, file.link),
    filename: file.filename,
    content_type: file.contentType,
    visibility: visibilityOf(file.access),
    namespace: file.namespace,
    expires_at: file.expiresAt,
    size_bytes: file.sizeBytes,
    owner_token: file.ownerToken ?? null,
    reused_existing: file.result?.action === 'merged',
    notices: noticeText(file.notices),
  };
};

module.exports = {
  key: 'upload_file',
  noun: 'File',
  display: {
    label: 'Upload File',
    description: 'Uploads a file and returns its link.',
  },
  operation: {
    perform,
    inputFields: [
      {
        key: 'file',
        label: 'File',
        type: 'file',
        required: true,
        helpText:
          'Up to 5 MB (video 20 MB). Images, PDF, Office documents, media, archives and text are supported. An `.html` or `.md` file becomes a web page.',
      },
      {
        key: 'filename',
        label: 'File name',
        type: 'string',
        required: false,
        helpText:
          'Name with extension, for example `report.pdf`. Defaults to the name of the source file.',
      },
      fields.visibility,
      fields.ttl,
    ],
    sample: {
      id: 'Rb7Lm2Qx9Z',
      url: 'https://brewpage.app/my/Rb7Lm2Qx9Z',
      filename: 'report.pdf',
      content_type: 'application/pdf',
      visibility: 'private',
      namespace: 'my',
      expires_at: '2026-11-21T10:15:00Z',
      size_bytes: 48213,
      owner_token: 'AbCdEf0123456789GhIjKl0123456789',
      reused_existing: false,
      notices: '',
    },
    outputFields: [
      { key: 'id', label: 'File ID' },
      { key: 'url', label: 'File URL' },
      { key: 'filename', label: 'File Name' },
      { key: 'content_type', label: 'Content Type' },
      { key: 'visibility', label: 'Visibility' },
      { key: 'namespace', label: 'Namespace' },
      { key: 'expires_at', label: 'Expires At', type: 'datetime' },
      { key: 'size_bytes', label: 'Size (bytes)', type: 'integer' },
      { key: 'owner_token', label: 'Owner Token (keep private)' },
      {
        key: 'reused_existing',
        label: 'Reused Existing File',
        type: 'boolean',
      },
      { key: 'notices', label: 'Notices' },
    ],
  },
};
