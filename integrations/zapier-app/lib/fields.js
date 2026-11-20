'use strict';

const visibility = {
  key: 'visibility',
  label: 'Visibility',
  type: 'string',
  required: false,
  default: 'private',
  choices: [
    { value: 'private', label: 'Private (unlisted link)', sample: 'private' },
    {
      value: 'public',
      label: 'Public (listed in the gallery)',
      sample: 'public',
    },
  ],
  helpText:
    'Private is unlisted and not indexed, but anyone with the link can open it. Public is listed in the [BrewPage gallery](https://brewpage.app/galleries) and search engines can index it.',
};

const ttl = {
  key: 'ttl',
  label: 'Lifetime (days)',
  type: 'integer',
  required: false,
  helpText:
    'Days until the publication is deleted for good, default 15: up to 30 days without an account, up to 90 with a free profile (its owner token).',
};

module.exports = { visibility, ttl };
