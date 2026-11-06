"use strict";
const helpers = require("/usr/local/lib/node_modules/n8n/node_modules/n8n-core/dist/execution-engine/node-execution-context/utils/request-helpers/factory.js");
const original = helpers.getRequestHelperFunctions;
let transportCalls = 0;
process.on("exit", () => {
  const expected = process.env.BREWPAGE_NATIVE_FIXTURE.startsWith("invalid-")
    ? 0
    : 1;
  if (process.argv.includes("execute") && transportCalls !== expected)
    process.exitCode = 42;
});
helpers.getRequestHelperFunctions = (...args) => ({
  ...original(...args),
  httpRequest: async (options) => {
    transportCalls++;
    if (
      options.url !== "https://brewpage.app/api/html" ||
      options.headers["User-Agent"] !==
        "brewpage-n8n/0.1.3 (+https://brewpage.app)"
    ) {
      throw new Error("Unexpected native request");
    }
    if (process.env.BREWPAGE_NATIVE_FIXTURE === "error") {
      throw new Error("OWNER_SENTINEL MANAGE_SENTINEL PRIVATE_SENTINEL");
    }
    return {
      id: "AbCdEf1234",
      namespace: "my",
      link: "https://my-abcdefghij.brewpage.app/",
      access: "unlisted",
      expiresAt: "2026-12-01T00:00:00Z",
      ownerToken: "OWNER_SENTINEL",
      managementLink: "MANAGE_SENTINEL",
      content: "PRIVATE_SENTINEL",
    };
  },
});
