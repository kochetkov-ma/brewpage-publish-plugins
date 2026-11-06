const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const { NodeOperationError } = require("n8n-workflow");
const { BrewPage } = require("../dist/nodes/BrewPage/BrewPage.node.js");

const NOT_CONFIRMED =
  "Publication was not confirmed. Check nonempty content (up to 5 MiB), format, access and lifetime (1–30 days). Check for an existing publication before retrying.";

const input = {
  operation: "publish",
  content: "<h1>Fixture</h1>",
  format: "html",
  access: "unlisted",
  ttl: 15,
};
const reply = {
  id: "AbCdEf1234",
  namespace: "my",
  link: "https://my-abcdefghij.brewpage.app/",
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
    compiled.match(/\brequire\s*\([^)]*\)|\bimport\s*(?:\(|["'{*])/g),
    ['require("n8n-workflow")'],
    "Compiled node loads only the host-provided n8n-workflow peer",
  );
  const cases = [
    ["html", "unlisted", 1, "my", "https://my-abcdefghij.brewpage.app/", false],
    [
      "markdown",
      "unlisted",
      15,
      "my",
      "https://brewpage.app/my/AbCdEf1234",
      false,
    ],
    [
      "html",
      "public",
      30,
      "public",
      "https://brewpage.app/public/AbCdEf1234",
      false,
    ],
    [
      "markdown",
      "public",
      7,
      "public",
      "https://brewpage.app/public/AbCdEf1234",
      true,
    ],
    ["html", "public", 2, "public", "https://abcdefghij.brewpage.app/", true],
    [
      "markdown",
      "unlisted",
      3,
      "team",
      "https://brewpage.app/team/AbCdEf1234",
      true,
    ],
    [
      "html",
      "unlisted",
      4,
      "-team",
      "https://n-team-abcdefghij.brewpage.app/",
      true,
    ],
  ].map(([format, access, ttl, namespace, link, merged]) => ({
    format,
    access,
    ttl,
    namespace,
    link,
    merged,
  }));
  assert.equal(
    cases.length,
    7,
    "Fixture covers every format x access and each create link shape",
  );
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
          namespace: row.namespace,
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
            "User-Agent": "brewpage-n8n/0.1.3 (+https://brewpage.app)",
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

test("invalid inputs and unsafe or failed responses throw one sanitized NodeOperationError without retries", async () => {
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
      "https://my-abcdefghij.brewpage.app/?ownerToken=OWNER_SENTINEL",
      "https://brewpage.app/api/abcdefghij",
      "https://brewpage.app/api/AbCdEf1234",
      "https://brewpage.app/my/AbCdEf1234/extra",
      "https://brewpage.app/my/ZzZzZz9999",
      "https://brewpage.app/public/AbCdEf1234",
      "https://abcdefghij.brewpage.app/",
      "https://team-abcdefghij.brewpage.app/",
      "https://my-abcdefghij.brewpage.app/index.html",
      "https://my-abcdefghij.evil.test/",
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
      "http://my-abcdefghij.brewpage.app/",
      "https://user:pass@my-abcdefghij.brewpage.app/",
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
      name: "public namespace for unlisted",
      response: {
        ...reply,
        namespace: "public",
        link: "https://brewpage.app/public/AbCdEf1234",
      },
      calls: 1,
    },
    {
      name: "missing id",
      response: {
        ...reply,
        id: undefined,
        link: "https://brewpage.app/my/AbCdEf1234",
      },
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
    49,
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
        // THEN one n8n error with a fixed message and no original cause is thrown.
        const serialized = JSON.parse(JSON.stringify(error));
        assert.deepEqual(
          {
            type: error instanceof NodeOperationError,
            node: error.node.name,
            level: error.level,
            serialized: {
              ...serialized,
              timestamp: typeof serialized.timestamp,
            },
          },
          {
            type: true,
            node: "BrewPage",
            level: "warning",
            serialized: {
              message: NOT_CONFIRMED,
              timestamp: "number",
              name: "NodeOperationError",
              context: { itemIndex: 0 },
              cause: { name: "Error", message: NOT_CONFIRMED },
            },
          },
          `${row.name}: fixed n8n error`,
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
