const assert = require("node:assert/strict");
const { test } = require("node:test");
const { runtime } = require("./handler.js");
const config = require("./plugin.json");

const INPUT = { content: "<h1>Fixture</h1>", format: "html", visibility: "private", ttl_days: 15 };
const PAGE = {
  link: "https://html-fixture.brewpage.app/",
  expiresAt: "2026-12-03T10:00:00Z",
  manageUrl: "https://brewpage.app/?ownerToken=fixture-owner&link=fixture",
  ownerToken: "fixture-owner",
};
const PRIVATE_REQUIRED = "Nothing was published. BrewPage needs an authenticated AnythingLLM conversation with private, saved replies.";
const UNKNOWN = "BrewPage publication outcome is unconfirmed. Do not retry or switch transport; reconcile this request before another write.";
const PRIVATE_LINES = [
  `Private management link: ${PAGE.manageUrl}`,
  `Private owner token: ${PAGE.ownerToken}`,
  "Save this private reply to manage or remove the page. Never share the management link or owner token publicly.",
];

function invocation() {
  const logs = [];
  const notices = [];
  const host = {
    handlerProps: { invocation: { user_id: 7, workspace_id: 11, workspace: { id: 11 }, closed: false } },
    trackedChatId: 19,
    socket: { send() {} },
    skipHandleExecution: false,
    functions: new Map(),
  };
  const skill = { ...runtime, config, super: host, introspect: value => notices.push(value), logger: value => logs.push(value) };
  host.functions.set(config.hubId, skill);
  return { skill, host, logs, notices };
}

test("publishing requires the registered private host context and returns its complete owner receipt directly", async t => {
  // GIVEN a real-shaped registered invocation and every unsupported context variant.
  const requests = [];
  t.mock.method(globalThis, "fetch", async (url, options) => {
    requests.push({ url, ...options });
    return Response.json(PAGE);
  });
  const refused = [
    ["no host", f => { f.skill.super = null; }],
    ["anonymous", f => { f.host.handlerProps.invocation.user_id = null; }],
    ["wrong workspace", f => { f.host.handlerProps.invocation.workspace.id = 12; }],
    ["closed invocation", f => { f.host.handlerProps.invocation.closed = true; }],
    ["unsaved chat", f => { f.host.trackedChatId = null; }],
    ["no interactive channel", f => { f.host.socket = null; }],
    ["unknown result path", f => { delete f.host.skipHandleExecution; }],
    ["unregistered copy", f => { f.host.functions.set(config.hubId, {}); }],
  ];
  // WHEN unsupported calls precede one supported publication.
  const denied = [];
  for (const [label, alter] of refused) {
    const f = invocation();
    alter(f);
    denied.push({ label, result: await f.skill.handler(INPUT), writes: requests.length, logs: f.logs, notices: f.notices });
  }
  const f = invocation();
  const result = await f.skill.handler(INPUT);
  // THEN every unsupported call makes zero requests and the supported reply retains both owner capabilities.
  assert.deepEqual(denied, refused.map(([label]) => ({ label, result: PRIVATE_REQUIRED, writes: 0, logs: [], notices: [] })), "unsupported contexts stop before HTTP");
  assert.deepEqual({ result, direct: f.host.skipHandleExecution, notices: f.notices, logs: f.logs, requests }, {
    result: [`Published: ${PAGE.link} (expires ${PAGE.expiresAt}). Share this link as is.`, ...PRIVATE_LINES].join("\n"),
    direct: true,
    notices: ["Publishing to BrewPage..."],
    logs: [],
    requests: [{ url: "https://brewpage.app/api/html?ttl=15", method: "POST", redirect: "error", headers: {
      "Content-Type": "application/json", "User-Agent": "anythingllm-brewpage-skill/1.1.0",
    }, body: JSON.stringify({ content: INPUT.content, format: "html" }) }],
  }, "one private create has the exact HTTP input and direct final receipt");
});

test("failures expose only safe outcomes and preserve recoverable fields without replaying publication", async t => {
  // GIVEN untrusted failure bodies, thrown errors, and an incomplete successful receipt.
  const responses = [
    () => new Response("private-server-text fixture-secret", { status: 400 }),
    () => new Response("private-server-text fixture-secret", { status: 503 }),
    () => { throw new Error("private-exception fixture-secret"); },
    () => new Response("private-malformed-json fixture-secret", { status: 200 }),
    () => Response.json({ ...PAGE, expiresAt: null }),
  ];
  const observations = [];
  // WHEN each original request runs once in its own invocation.
  for (const response of responses) {
    let writes = 0;
    t.mock.method(globalThis, "fetch", async () => { writes += 1; return response(); });
    const f = invocation();
    observations.push({ result: await f.skill.handler(INPUT), writes, direct: f.host.skipHandleExecution, logs: f.logs });
    t.mock.restoreAll();
  }
  const refusal = "BrewPage refused publication (HTTP 400). No automatic retry was made.";
  const incomplete = [
    "BrewPage accepted the publication but returned an incomplete receipt. Do not retry or switch transport; reconcile this request.",
    `Reader link: ${PAGE.link}`, ...PRIVATE_LINES,
  ].join("\n");
  // THEN exact static diagnostics replace arbitrary text and issued owner capabilities survive a partial receipt.
  assert.deepEqual(observations, [
    { result: refusal, writes: 1, direct: true, logs: [refusal] },
    { result: UNKNOWN, writes: 1, direct: true, logs: [UNKNOWN] },
    { result: UNKNOWN, writes: 1, direct: true, logs: [UNKNOWN] },
    { result: UNKNOWN, writes: 1, direct: true, logs: [UNKNOWN] },
    { result: incomplete, writes: 1, direct: true, logs: [] },
  ], "error bodies and exception messages never enter replies or logs, and no request is replayed");
});
