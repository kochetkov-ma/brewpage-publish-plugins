'use strict';

const { version } = require('./package.json');
const { version: platformVersion } = require('zapier-platform-core');
const authentication = require('./authentication');
const { addBrewPageHeaders, handleBrewPageErrors } = require('./lib/brewpage');
const publishPage = require('./creates/publish_page');
const uploadFile = require('./creates/upload_file');
const createJson = require('./creates/create_json');

module.exports = {
  version,
  platformVersion,
  flags: { cleanInputData: false },
  authentication,
  beforeRequest: [addBrewPageHeaders],
  afterResponse: [handleBrewPageErrors],
  triggers: {},
  searches: {},
  creates: {
    [publishPage.key]: publishPage,
    [uploadFile.key]: uploadFile,
    [createJson.key]: createJson,
  },
};
