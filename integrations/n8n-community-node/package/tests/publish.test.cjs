const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const { BrewPage } = require("../dist/nodes/BrewPage/BrewPage.node.js");

const input = {
  operation: "publish",
  content: "<h1>Fixture</h1>",
  format: "html",
  access: "unlisted",
  ttl: 15,
};
const reply = {
  link: "https://abcdefghij.brewpage.app/",
  access: "unlisted",
  expiresAt: "2026-12-01T00:00:00Z",
  ownerToken: "OWNER_SENTINEL",
  managementLink: "MANAGE_SENTINEL",
  content: "PRIVATE_SENTINEL",
};
function context(parameters, response, calls) {
  return {
    getInputData: () => [{ json: { source: "INPUT_SENTINEL" } }],
    getNodeParameter: (name) => parameters[name],
    getNode: () => ({
      name: "BrewPage",
      type: "n8n-nodes-brewpage.brewPage",
      typeVersion: 1,
      position: [0, 0],
      parameters: { content: "PRIVATE_SENTINEL" },
    }),
    helpers: {
      httpRequest: async (options) => {
        calls.push(options);
        return typeof response === "function" ? response() : response;
      },
    },
  };
}

test("HTML and Markdown publish exact bounded requests and only safe reader metadata", async () => {
  // GIVEN supported formats, access choices and TTL boundaries.
  const compiled = fs.readFileSync(
    require.resolve("../dist/nodes/BrewPage/BrewPage.node.js"),
    "utf8",
  );
  assert.deepEqual(
    compiled.match(/\brequire\s*\(|\bimport\s*(?:\(|["'{*])/g),
    null,
    "Compiled node has no external module load or import",
  );
  const cases = [
    {
      format: "html",
      access: "unlisted",
      ttl: 1,
      link: "https://abcdefghij.brewpage.app/",
      merged: false,
    },
    {
      format: "markdown",
      access: "public",
      ttl: 30,
      link: "https://brewpage.app/public/AbCdEf1234",
      merged: true,
    },
  ];
  assert.equal(cases.length, 2, "Fixture covers both formats and access modes");
  for (const row of cases) {
    const parameters = {
      ...input,
      format: row.format,
      access: row.access,
      ttl: row.ttl,
    };
    const calls = [];
    // WHEN native execute receives a service response containing ownership fields.
    const result = await new BrewPage().execute.call(
      context(
        parameters,
        {
          ...reply,
          access: row.access,
          link: row.link,
          result: { action: row.merged ? "merged" : "created" },
        },
        calls,
      ),
    );
    // THEN request and full output match their allowlists exactly.
    assert.deepEqual(
      calls,
      [
        {
          method: "POST",
          url: "https://brewpage.app/api/html",
          qs: {
            ttl: row.ttl,
            format: row.format,
            verbatim: true,
            ...(row.access === "public" ? { ns: "public" } : {}),
          },
          headers: {
            "User-Agent": "brewpage-n8n/0.1.0 (+https://brewpage.app)",
            Accept: "application/json",
          },
          body: { content: input.content, format: row.format },
          json: true,
          timeout: 60000,
          maxResponseBodyBytes: 65536,
          disableFollowRedirect: true,
        },
      ],
      "Only fixed endpoint, explicit access, TTL, format and User-Agent are sent",
    );
    assert.deepEqual(
      result,
      [
        [
          {
            json: {
              link: row.link,
              access: row.access,
              format: row.format,
              expiresAt: reply.expiresAt,
              requestedTtlDays: row.ttl,
              reusedExisting: row.merged,
            },
            pairedItem: { item: 0 },
          },
        ],
      ],
      "Safe metadata is returned without ownership, source, content or raw response",
    );
  }
});

test("invalid inputs and unsafe or failed responses return one sanitized error without retries", async () => {
  // GIVEN invalid expressions and hostile responses carrying synthetic secrets.
  const cases = [
    { name: "empty", patch: { content: "" }, calls: 0 },
    {
      name: "oversize unicode",
      patch: { content: "😀".repeat(1310721) },
      calls: 0,
    },
    { name: "fractional ttl", patch: { ttl: 1.5 }, calls: 0 },
    { name: "high ttl", patch: { ttl: 31 }, calls: 0 },
    { name: "low ttl", patch: { ttl: 0 }, calls: 0 },
    { name: "format", patch: { format: "txt" }, calls: 0 },
    { name: "access", patch: { access: "protected" }, calls: 0 },
    { name: "format array expression", patch: { format: ["html"] }, calls: 0 },
    {
      name: "access array expression",
      patch: { access: ["public"] },
      calls: 0,
    },
    {
      name: "format object expression",
      patch: { format: { value: "html" } },
      calls: 0,
    },
    {
      name: "access object expression",
      patch: { access: { value: "public" } },
      calls: 0,
    },
    { name: "operation", patch: { operation: "delete" }, calls: 0 },
    ...[
      "https://evil.test/",
      "https://brewpage.app/manage/OWNER_SENTINEL",
      "https://abcdefghij.brewpage.app/?ownerToken=OWNER_SENTINEL",
      "https://brewpage.app/api/abcdefghij",
      ...[
        "unlock",
        "www",
        "api",
        "admin",
        "assets",
        "static",
        "cdn",
        "status",
        "health",
        "metrics",
        "grafana",
        "prometheus",
        "monitoring",
        "autoconfig",
        "autodiscover",
        "fe-bounces",
        "account",
      ].map((label) => `https://${label}.brewpage.app/`),
      "http://abcdefghij.brewpage.app/",
      "https://user:pass@abcdefghij.brewpage.app/",
    ].map((link) => ({ name: link, response: { ...reply, link }, calls: 1 })),
    {
      name: "impossible date",
      response: { ...reply, expiresAt: "2026-02-30T00:00:00Z" },
      calls: 1,
    },
    {
      name: "missing expiry",
      response: { ...reply, expiresAt: undefined },
      calls: 1,
    },
    {
      name: "access mismatch",
      response: { ...reply, access: "public" },
      calls: 1,
    },
    {
      name: "transport",
      response: () => {
        throw new Error("OWNER_SENTINEL MANAGE_SENTINEL PRIVATE_SENTINEL");
      },
      calls: 1,
    },
  ];
  assert.equal(
    cases.length,
    39,
    "Fixture matrix covers every reserved backend label and required rejection",
  );
  for (const row of cases) {
    const calls = [];
    // WHEN execution fails validation or receives an unsafe service result.
    await assert.rejects(
      new BrewPage().execute.call(
        context({ ...input, ...row.patch }, row.response ?? reply, calls),
      ),
      (error) => {
        // THEN serialized errors and stack contain no supplied synthetic secrets.
        assert.deepEqual(
          {
            name: error.name,
            message: error.message,
            cause: error.cause,
            enumerableKeys: Object.keys(error),
          },
          {
            name: "Error",
            message:
              "Publication was not confirmed. Check nonempty content (up to 5 MiB), format, access and lifetime (1–30 days). Check for an existing publication before retrying.",
            cause: undefined,
            enumerableKeys: [],
          },
          `${row.name}: fixed error`,
        );
        assert.deepEqual(
          (JSON.stringify(error) + error.stack).match(
            /OWNER_SENTINEL|MANAGE_SENTINEL|PRIVATE_SENTINEL/g,
          ),
          null,
          `${row.name}: ownership and content redacted`,
        );
        return true;
      },
      `${row.name}: rejects`,
    );
    assert.equal(
      calls.length,
      row.calls,
      `${row.name}: no invalid call or automatic retry`,
    );
  }
});
