'use strict';

const { version } = require('../package.json');

const API = 'https://brewpage.app/api';
const USER_AGENT = `brewpage-zapier/${version} (+https://brewpage.app)`;
const PRIVATE_NAMESPACE = 'my';
const PUBLIC_NAMESPACE = 'public';
const TOKEN_PATTERN = /^[A-Za-z0-9]{32}$/;

const isBrewPageUrl = (url) => {
  const { protocol, hostname } = new URL(url);
  return (
    protocol === 'https:' &&
    (hostname === 'brewpage.app' || hostname.endsWith('.brewpage.app'))
  );
};

const ownerToken = (bundle) => {
  const token = bundle.authData?.ownerToken;
  return typeof token === 'string' ? token.trim() : '';
};

// Token and User-Agent go only to brewpage.app, never to a file source URL.
const addBrewPageHeaders = (request, z, bundle) => {
  if (!isBrewPageUrl(request.url)) return request;
  request.headers = {
    ...request.headers,
    'user-agent': USER_AGENT,
    accept: 'application/json',
  };
  const token = ownerToken(bundle);
  if (token) request.headers['x-owner-token'] = token;
  return request;
};

const STATUS_MESSAGES = {
  400: 'BrewPage rejected the request',
  403: 'BrewPage refused the request',
  404: 'BrewPage could not find the resource',
  413: 'The upload is larger than the 25 MB request limit',
  422: 'BrewPage does not support this content type',
  503: 'BrewPage is busy right now. Try again in a minute',
};

const readError = (response) => {
  try {
    const body = JSON.parse(response.content);
    return typeof body.message === 'string' ? body.message : '';
  } catch {
    return '';
  }
};

const handleBrewPageErrors = (response, z) => {
  if (
    response.status < 400 ||
    response.skipThrowForStatus ||
    !isBrewPageUrl(response.request.url)
  ) {
    return response;
  }
  const base = STATUS_MESSAGES[response.status] || 'BrewPage request failed';
  const detail = readError(response);
  throw new z.errors.Error(
    detail ? `${base}: ${detail}` : `${base}.`,
    `BREWPAGE_${response.status}`,
    response.status,
  );
};

const namespaceFor = (visibility) =>
  visibility === 'public' ? PUBLIC_NAMESPACE : PRIVATE_NAMESPACE;

const blank = (value) =>
  value === undefined || value === null || String(value).trim() === '';

// Profile tokens allow up to 90 days; the API clamps others to 30 and says so.
const ttlParam = (z, value) => {
  if (blank(value)) return {};
  const days = Number(value);
  if (!Number.isInteger(days) || days < 1 || days > 90) {
    throw new z.errors.Error(
      'Lifetime must be a whole number of days from 1 to 90.',
      'INVALID_TTL',
      400,
    );
  }
  return { ttl: String(days) };
};

const visibilityParam = (z, value) => {
  const visibility = blank(value) ? 'private' : String(value).trim();
  if (!['private', 'public'].includes(visibility)) {
    throw new z.errors.Error(
      'Visibility must be private or public.',
      'INVALID_VISIBILITY',
      400,
    );
  }
  return visibility;
};

const checkedLink = (z, link) => {
  if (typeof link !== 'string' || !isBrewPageUrl(link)) {
    throw new z.errors.Error(
      'BrewPage returned an unexpected response without a link.',
      'UNEXPECTED_RESPONSE',
      502,
    );
  }
  return link;
};

const noticeText = (notices) =>
  Array.isArray(notices)
    ? notices
        .map((notice) => notice?.message)
        .filter((message) => typeof message === 'string')
        .join(' ')
    : '';

const visibilityOf = (access) => (access === 'public' ? 'public' : 'private');

module.exports = {
  API,
  USER_AGENT,
  TOKEN_PATTERN,
  addBrewPageHeaders,
  handleBrewPageErrors,
  namespaceFor,
  blank,
  ttlParam,
  visibilityParam,
  checkedLink,
  noticeText,
  ownerToken,
  visibilityOf,
};
