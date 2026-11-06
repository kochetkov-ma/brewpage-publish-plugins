'use strict';

const assert = require('node:assert/strict');
const nock = require('nock').default;
const zapier = require('zapier-platform-core');
const App = require('../index');

nock.disableNetConnect();

const appTester = zapier.createAppTester(App);
const TOKEN = 'AbCdEf0123456789GhIjKl0123456789';
const USER_AGENT = 'brewpage-zapier/1.0.0 (+https://brewpage.app)';

const parse = (body) => {
  try {
    return JSON.parse(body);
  } catch {
    return body;
  }
};

// Records each intercepted brewpage.app call as one comparable object.
const intercept = (method, path, status, reply) => {
  const calls = [];
  const scope = nock('https://brewpage.app')
    .intercept(path, method)
    .query(true)
    .reply(status, reply);
  scope.on('request', (req, interceptor, body) => {
    const url = new URL(req.url);
    calls.push({
      path: url.pathname + url.search,
      userAgent: req.headers.get('user-agent'),
      ownerToken: req.headers.get('x-owner-token'),
      body: parse(body),
    });
  });
  return calls;
};

const appError = (message, code, status) => (error) => {
  assert.equal(
    error.message,
    JSON.stringify({ message, code, status }),
    'Error carries the exact user-facing message, code and status',
  );
  return true;
};

const reset = () => {
  nock.cleanAll();
};

module.exports = {
  App,
  appTester,
  TOKEN,
  USER_AGENT,
  intercept,
  appError,
  reset,
  nock,
};
