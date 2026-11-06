'use strict';

const { API, TOKEN_PATTERN, ownerToken } = require('./lib/brewpage');

// Blank token = anonymous publishing; a set token must be well-formed and active.
const test = async (z, bundle) => {
  const token = ownerToken(bundle);
  if (!token) {
    const response = await z.request({ url: `${API}/limits` });
    return { reach: response.data.reach, connection: 'Anonymous publishing' };
  }
  if (!TOKEN_PATTERN.test(token)) {
    throw new z.errors.Error(
      'Your owner token does not appear to be valid. It is 32 letters and digits.',
      'INVALID_OWNER_TOKEN',
      401,
    );
  }
  const response = await z.request({
    url: `${API}/publications`,
    params: { limit: '1' },
    skipThrowForStatus: true,
  });
  if (response.status === 403) {
    throw new z.errors.Error(
      'Your owner token is revoked or expired. Mint a new one at https://account.brewpage.app.',
      'OWNER_TOKEN_REJECTED',
      401,
    );
  }
  response.throwForStatus();
  const limits = await z.request({ url: `${API}/limits` });
  const profile = limits.data.reach === 'profile';
  return {
    reach: limits.data.reach,
    connection: profile ? 'Profile owner token' : 'Owner token',
  };
};

module.exports = {
  type: 'custom',
  fields: [
    {
      key: 'ownerToken',
      label: 'Owner token',
      type: 'password',
      required: false,
      helpText:
        'Optional. Leave blank to publish without an account; each publication then returns its own owner token. To group publications under one owner, paste an owner token returned by an earlier publish, or sign in free at [account.brewpage.app](https://account.brewpage.app) and mint one there.',
    },
  ],
  test,
  connectionLabel: '{{connection}}',
};
