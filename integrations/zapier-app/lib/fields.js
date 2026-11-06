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
    'Days until the publication is deleted for good: 1 to 30, default 15. Up to 90 with an owner token from a free profile.',
};

module.exports = { visibility, ttl };
