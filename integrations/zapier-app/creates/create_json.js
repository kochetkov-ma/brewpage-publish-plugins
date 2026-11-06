'use strict';

const { API, checkedLink, noticeText, ttlParam } = require('../lib/brewpage');
const fields = require('../lib/fields');

const MAX_BYTES = 1024 * 1024;

const perform = async (z, bundle) => {
  const input = bundle.inputData;
  const text = typeof input.json === 'string' ? input.json.trim() : '';
  let document;
  try {
    document = JSON.parse(text);
  } catch {
    throw new z.errors.Error(
      'JSON is not valid. Map or type a JSON object, array or value.',
      'INVALID_JSON',
      400,
    );
  }
  if (Buffer.byteLength(text, 'utf8') > MAX_BYTES) {
    throw new z.errors.Error(
      'JSON is larger than the 1 MB document limit.',
      'JSON_TOO_LARGE',
      400,
    );
  }
  const response = await z.request({
    method: 'POST',
    url: `${API}/json`,
    params: { ns: 'my', ...ttlParam(z, input.ttl) },
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(document),
  });
  const result = response.data;
  return {
    id: result.id,
    url: checkedLink(z, result.link),
    namespace: result.namespace,
    expires_at: result.expiresAt,
    size_bytes: result.sizeBytes,
    owner_token: result.ownerToken ?? null,
    notices: noticeText(result.notices),
  };
};

module.exports = {
  key: 'create_json',
  noun: 'Document',
  display: {
    label: 'Create JSON Document',
    description: 'Stores a JSON document and returns its link.',
  },
  operation: {
    perform,
    inputFields: [
      {
        key: 'json',
        label: 'JSON',
        type: 'text',
        required: true,
        helpText:
          'Any valid JSON, up to 1 MB. The document is private: never listed or indexed, but anyone with the link can read it.',
      },
      fields.ttl,
    ],
    sample: {
      id: 'Jd4Nc8Wq1P',
      url: 'https://brewpage.app/my/Jd4Nc8Wq1P',
      namespace: 'my',
      expires_at: '2026-11-21T10:15:00Z',
      size_bytes: 128,
      owner_token: 'AbCdEf0123456789GhIjKl0123456789',
      notices: '',
    },
    outputFields: [
      { key: 'id', label: 'Document ID' },
      { key: 'url', label: 'Document URL' },
      { key: 'namespace', label: 'Namespace' },
      { key: 'expires_at', label: 'Expires At', type: 'datetime' },
      { key: 'size_bytes', label: 'Size (bytes)', type: 'integer' },
      { key: 'owner_token', label: 'Owner Token (keep private)' },
      { key: 'notices', label: 'Notices' },
    ],
  },
};
