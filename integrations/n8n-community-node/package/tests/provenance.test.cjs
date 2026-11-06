const { test } = require("node:test");
const assert = require("node:assert/strict");
const {
  validateContext,
  validateStatement,
  validateManifest,
  validateBaseline,
  validateHandoff,
  REPO_METADATA,
} = require("../scripts/provenance.cjs");

test("pure signing guard accepts exact hosted identity and rejects altered authority", () => {
  // GIVEN synthetic validation data only; no environment mutation or signing.
  const sha = "a".repeat(40);
  const env = {
    GITHUB_ACTIONS: "true",
    GITHUB_SERVER_URL: "https://github.com",
    GITHUB_REPOSITORY: "kochetkov-ma/brewpage-publish-plugins",
    GITHUB_REF: "refs/heads/main",
    GITHUB_SHA: sha,
    GITHUB_WORKFLOW_SHA: sha,
    GITHUB_WORKFLOW_REF:
      "kochetkov-ma/brewpage-publish-plugins/.github/workflows/n8n-community-node-provenance.yml@refs/heads/main",
    GITHUB_EVENT_NAME: "workflow_dispatch",
    RUNNER_ENVIRONMENT: "github-hosted",
    GITHUB_RUN_ID: "123",
    GITHUB_RUN_ATTEMPT: "1",
    ACTIONS_ID_TOKEN_REQUEST_URL: "https://example.invalid/oidc",
    ACTIONS_ID_TOKEN_REQUEST_TOKEN: "SYNTHETIC_NOT_A_TOKEN",
  };
  const event = {
    repository: { private: false },
    inputs: { expected_sha: sha },
  };
  // WHEN the exact context is validated without contacting any provider.
  const run = validateContext(env, event, sha);
  // THEN only the selected immutable public workflow qualifies.
  assert.equal(
    run,
    "https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/runs/123/attempts/1",
    "Exact run identity required",
  );
  const cases = [
    { GITHUB_ACTIONS: "false" },
    { GITHUB_SERVER_URL: "https://example.invalid" },
    { GITHUB_REPOSITORY: "someone/other" },
    { GITHUB_SHA: "b".repeat(40) },
    { GITHUB_WORKFLOW_SHA: "b".repeat(40) },
    { GITHUB_REF: "refs/heads/other" },
    { GITHUB_WORKFLOW_REF: "other/workflow" },
    { GITHUB_EVENT_NAME: "push" },
    { RUNNER_ENVIRONMENT: "self-hosted" },
    { NODE_AUTH_TOKEN: "SYNTHETIC_NOT_A_TOKEN" },
    { NPM_TOKEN: "SYNTHETIC_NOT_A_TOKEN" },
    { SIGSTORE_ID_TOKEN: "SYNTHETIC_NOT_A_TOKEN" },
    { GITHUB_RUN_ID: "invalid" },
    { ACTIONS_ID_TOKEN_REQUEST_URL: undefined },
  ];
  assert.equal(
    cases.length,
    14,
    "Authority rejection matrix must remain complete",
  );
  for (const change of cases)
    assert.throws(
      () => validateContext({ ...env, ...change }, event, sha),
      { code: "ERR_ASSERTION" },
      `Reject ${Object.keys(change)[0]}`,
    );
  for (const changedEvent of [
    { ...event, repository: { private: true } },
    { ...event, inputs: { expected_sha: "b".repeat(40) } },
  ])
    assert.throws(
      () => validateContext(env, changedEvent, sha),
      { code: "ERR_ASSERTION" },
      "Reject private or stale dispatched source",
    );
});

test("unsigned fixture validation binds complete provenance and package metadata", () => {
  // GIVEN a synthetic unsigned statement; this test proves no signature validity.
  const sha = "a".repeat(40);
  const run =
    "https://github.com/kochetkov-ma/brewpage-publish-plugins/actions/runs/123/attempts/1";
  const subject = {
    name: "pkg:npm/n8n-nodes-brewpage@0.1.3",
    digest: { sha512: "b".repeat(128) },
  };
  const statement = {
    _type: "https://in-toto.io/Statement/v1",
    subject: [subject],
    predicateType: "https://slsa.dev/provenance/v1",
    predicate: {
      buildDefinition: {
        buildType:
          "https://slsa-framework.github.io/github-actions-buildtypes/workflow/v1",
        externalParameters: {
          workflow: {
            ref: "refs/heads/main",
            repository:
              "https://github.com/kochetkov-ma/brewpage-publish-plugins",
            path: ".github/workflows/n8n-community-node-provenance.yml",
          },
        },
        internalParameters: { github: { event_name: "workflow_dispatch" } },
        resolvedDependencies: [
          {
            uri: "git+https://github.com/kochetkov-ma/brewpage-publish-plugins@refs/heads/main",
            digest: { gitCommit: sha },
          },
        ],
      },
      runDetails: {
        builder: { id: "https://github.com/actions/runner/github-hosted" },
        metadata: { invocationId: run },
      },
    },
  };
  const manifest = {
    name: "n8n-nodes-brewpage",
    version: "0.1.3",
    license: "MIT",
    repository: REPO_METADATA,
    peerDependencies: { "n8n-workflow": "*" },
    devDependencies: { "n8n-workflow": "2.44.2" },
    files: ["dist"],
    n8n: {
      n8nNodesApiVersion: 1,
      strict: true,
      credentials: [],
      nodes: ["dist/nodes/BrewPage/BrewPage.node.js"],
    },
  };
  // WHEN exact inputs pass the pure guards.
  assert.equal(
    validateStatement(statement, subject, sha, run),
    undefined,
    "Complete reviewed statement accepted",
  );
  assert.equal(
    validateManifest(manifest),
    undefined,
    "Exact source and peer accepted",
  );
  const files = Object.fromEntries(
    [
      "LICENSE",
      "README.md",
      "dist/nodes/BrewPage/BrewPage.node.d.ts",
      "dist/nodes/BrewPage/BrewPage.node.js",
      "dist/nodes/BrewPage/BrewPage.node.json",
      "dist/nodes/BrewPage/brewpage.svg",
      "package.json",
    ].map((name) => [name, "b".repeat(64)]),
  );
  const baseline = { schema: 1, nodeSourceSha256: "a".repeat(64), files };
  const packed = {
    subject,
    sha256: "a".repeat(64),
    files: Object.keys(files),
    fileSha256: files,
  };
  const manifestProof = { ...packed, npm: "11.15.0" };
  const checks = { code: "success", native: "success" };
  assert.equal(
    validateHandoff(packed, manifestProof, checks),
    undefined,
    "Exact archive handoff with actual successful checks accepted",
  );
  assert.throws(
    () =>
      validateHandoff(
        { ...packed, sha256: "c".repeat(64) },
        manifestProof,
        checks,
      ),
    { code: "ERR_ASSERTION" },
    "Byte-different archive rejected even with identical unpacked files",
  );
  assert.throws(
    () => validateHandoff(packed, { ...manifestProof, npm: "11.12.1" }, checks),
    { code: "ERR_ASSERTION" },
    "Wrong recorded producer tuple rejected",
  );
  for (const changed of [
    { code: "success", native: "failure" },
    { code: "skipped", native: "success" },
  ])
    assert.throws(
      () => validateHandoff(packed, manifestProof, changed),
      { code: "ERR_ASSERTION" },
      "Missing successful handoff checks rejected",
    );
  assert.equal(
    validateBaseline(files, baseline, "a".repeat(64)),
    undefined,
    "Exact reviewed packed files accepted",
  );
  for (const changed of [
    { ...baseline, nodeSourceSha256: "c".repeat(64) },
    {
      ...baseline,
      files: {
        ...files,
        "dist/nodes/BrewPage/BrewPage.node.js": "c".repeat(64),
      },
    },
  ])
    assert.throws(
      () => validateBaseline(files, changed, "a".repeat(64)),
      { code: "ERR_ASSERTION" },
      "Reject altered source or compiled bytes before signing",
    );
  // THEN tampered subject, source, run and package authority fail unconditionally.
  const cases = [
    { ...statement, subject: [{ ...subject, name: "pkg:npm/other@0.1.0" }] },
    {
      ...statement,
      subject: [{ ...subject, digest: { sha512: "c".repeat(128) } }],
    },
    { ...statement, predicateType: "wrong" },
    {
      ...statement,
      predicate: {
        ...statement.predicate,
        buildDefinition: {
          ...statement.predicate.buildDefinition,
          resolvedDependencies: [],
        },
      },
    },
    { ...statement, predicate: { ...statement.predicate, runDetails: {} } },
  ];
  assert.equal(cases.length, 5, "Provenance rejection matrix remains complete");
  for (const changed of cases)
    assert.throws(
      () => validateStatement(changed, subject, sha, run),
      { code: "ERR_ASSERTION" },
      "Reject changed provenance binding",
    );
  for (const change of [
    { version: "0.1.0" },
    { repository: { ...REPO_METADATA, directory: "wrong" } },
    { peerDependencies: undefined },
    { peerDependencies: { "n8n-workflow": "2.44.2" } },
    { peerDependencies: { "n8n-workflow": "*", unexpected: "*" } },
    { dependencies: { unexpected: "1.0.0" } },
    { overrides: { qs: "6.16.2" } },
    { optionalDependencies: { unexpected: "1.0.0" } },
    { files: ["dist", ".npmrc"] },
  ])
    assert.throws(
      () => validateManifest({ ...manifest, ...change }),
      { code: "ERR_ASSERTION" },
      `Reject changed ${Object.keys(change)[0]}`,
    );
});
