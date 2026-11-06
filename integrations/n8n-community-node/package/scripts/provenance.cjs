const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const REPOSITORY = "kochetkov-ma/brewpage-publish-plugins";
const WORKFLOW = ".github/workflows/n8n-community-node-provenance.yml";
const NAME = "n8n-nodes-brewpage";
const VERSION = "0.1.2";
const FILES = [
  "LICENSE",
  "README.md",
  "dist/nodes/BrewPage/BrewPage.node.d.ts",
  "dist/nodes/BrewPage/BrewPage.node.js",
  "dist/nodes/BrewPage/BrewPage.node.json",
  "dist/nodes/BrewPage/brewpage.svg",
  "package.json",
];
const REPO_METADATA = {
  type: "git",
  url: `git+https://github.com/${REPOSITORY}.git`,
  directory: "integrations/n8n-community-node/package",
};
const SIGNER_SHA256 =
  "ee9b1bc8e3f636fbaf5138a3e183ce3c6d42bb5dd57ab004578e534dd08da46b";
const hash = (bytes, algorithm) =>
  crypto.createHash(algorithm).update(bytes).digest("hex");

function loadNative(npmDirectory) {
  const root = fs.realpathSync(npmDirectory);
  const readPackage = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
  assert.equal(
    readPackage(path.join(root, "package.json")).version,
    "11.15.0",
    "Pinned npm required",
  );
  const modules = path.join(root, "node_modules");
  const signer = path.join(modules, "libnpmpublish/lib/provenance.js");
  assert.equal(
    hash(fs.readFileSync(signer), "sha256"),
    SIGNER_SHA256,
    "Native signer bytes must match review",
  );
  for (const [name, version] of [
    ["libnpmpublish", "11.2.0"],
    ["sigstore", "4.1.0"],
    ["npm-package-arg", "13.0.2"],
  ]) {
    assert.equal(
      readPackage(path.join(modules, name, "package.json")).version,
      version,
      `Pinned ${name} required`,
    );
  }
  return {
    ...require(signer),
    sigstore: require(path.join(modules, "sigstore")),
    npa: require(path.join(modules, "npm-package-arg")),
    tar: require(path.join(modules, "tar")),
    npm: path.join(root, "bin/npm-cli.js"),
  };
}

function validateManifest(manifest) {
  assert.deepEqual(
    {
      name: manifest.name,
      version: manifest.version,
      license: manifest.license,
      repository: manifest.repository,
      peerDependencies: manifest.peerDependencies ?? {},
      devDependencies: manifest.devDependencies,
      dependencies: manifest.dependencies ?? {},
      overrides: manifest.overrides,
      resolutions: manifest.resolutions,
      optionalDependencies: manifest.optionalDependencies ?? {},
      bundledDependencies: manifest.bundledDependencies,
      bundleDependencies: manifest.bundleDependencies,
      files: manifest.files,
      n8n: manifest.n8n,
    },
    {
      name: NAME,
      version: VERSION,
      license: "MIT",
      repository: REPO_METADATA,
      peerDependencies: { "n8n-workflow": "*" },
      devDependencies: { "n8n-workflow": "2.44.2" },
      dependencies: {},
      overrides: undefined,
      resolutions: undefined,
      optionalDependencies: {},
      bundledDependencies: undefined,
      bundleDependencies: undefined,
      files: ["dist"],
      n8n: {
        n8nNodesApiVersion: 1,
        strict: true,
        credentials: [],
        nodes: ["dist/nodes/BrewPage/BrewPage.node.js"],
      },
    },
    "Only the reviewed package with the host-provided n8n-workflow peer may ship",
  );
}

function validateContext(env, event, expectedSha) {
  assert.match(expectedSha, /^[a-f0-9]{40}$/, "Reviewed source SHA required");
  assert.deepEqual(
    {
      actions: env.GITHUB_ACTIONS,
      server: env.GITHUB_SERVER_URL,
      repository: env.GITHUB_REPOSITORY,
      ref: env.GITHUB_REF,
      sha: env.GITHUB_SHA,
      workflowSha: env.GITHUB_WORKFLOW_SHA,
      workflow: env.GITHUB_WORKFLOW_REF,
      event: env.GITHUB_EVENT_NAME,
      runner: env.RUNNER_ENVIRONMENT,
      private: event.repository?.private,
      dispatchedSha: event.inputs?.expected_sha,
    },
    {
      actions: "true",
      server: "https://github.com",
      repository: REPOSITORY,
      ref: "refs/heads/main",
      sha: expectedSha,
      workflowSha: expectedSha,
      workflow: `${REPOSITORY}/${WORKFLOW}@refs/heads/main`,
      event: "workflow_dispatch",
      runner: "github-hosted",
      private: false,
      dispatchedSha: expectedSha,
    },
    "Signing requires the reviewed public hosted manual workflow, without environment spoofing",
  );
  assert.match(env.GITHUB_RUN_ID ?? "", /^\d+$/, "Real workflow run required");
  assert.match(
    env.GITHUB_RUN_ATTEMPT ?? "",
    /^\d+$/,
    "Real workflow attempt required",
  );
  assert.match(
    env.ACTIONS_ID_TOKEN_REQUEST_URL ?? "",
    /^https:\/\//,
    "OIDC capability required",
  );
  assert.equal(
    typeof env.ACTIONS_ID_TOKEN_REQUEST_TOKEN,
    "string",
    "OIDC request capability required",
  );
  for (const key of ["NODE_AUTH_TOKEN", "NPM_TOKEN", "SIGSTORE_ID_TOKEN"]) {
    assert.equal(env[key], undefined, `${key} must not enter signing`);
  }
  return `https://github.com/${REPOSITORY}/actions/runs/${env.GITHUB_RUN_ID}/attempts/${env.GITHUB_RUN_ATTEMPT}`;
}

function validateStatement(statement, subject, expectedSha, runUrl) {
  assert.match(expectedSha, /^[a-f0-9]{40}$/, "Reviewed source SHA required");
  assert.match(
    runUrl,
    /^https:\/\/github\.com\/kochetkov-ma\/brewpage-publish-plugins\/actions\/runs\/\d+\/attempts\/\d+$/,
    "Reviewed run URL required",
  );
  const definition = statement.predicate?.buildDefinition;
  assert.deepEqual(
    {
      type: statement._type,
      subject: statement.subject,
      predicateType: statement.predicateType,
      buildType: definition?.buildType,
      workflow: definition?.externalParameters?.workflow,
      event: definition?.internalParameters?.github?.event_name,
      source: definition?.resolvedDependencies,
      run: statement.predicate?.runDetails,
    },
    {
      type: "https://in-toto.io/Statement/v1",
      subject: [subject],
      predicateType: "https://slsa.dev/provenance/v1",
      buildType:
        "https://slsa-framework.github.io/github-actions-buildtypes/workflow/v1",
      workflow: {
        ref: "refs/heads/main",
        repository: `https://github.com/${REPOSITORY}`,
        path: WORKFLOW,
      },
      event: "workflow_dispatch",
      source: [
        {
          uri: `git+https://github.com/${REPOSITORY}@refs/heads/main`,
          digest: { gitCommit: expectedSha },
        },
      ],
      run: {
        builder: { id: "https://github.com/actions/runner/github-hosted" },
        metadata: { invocationId: runUrl },
      },
    },
    "Verified provenance must bind the exact package, source, workflow and run",
  );
}

function validateBaseline(fileSha256, baseline, sourceSha256) {
  assert.deepEqual(
    Object.keys(fileSha256).sort(),
    FILES,
    "Reviewed baseline covers only seven packed files",
  );
  assert.deepEqual(
    baseline,
    { schema: 1, nodeSourceSha256: sourceSha256, files: fileSha256 },
    "Packed bytes and node source must match the committed reviewed baseline before signing",
  );
}

function validateHandoff(packed, manifest, checks) {
  assert.deepEqual(
    manifest,
    { ...packed, npm: "11.15.0" },
    "Exact original tarball digests, package subject and file manifest must match the build handoff",
  );
  assert.deepEqual(
    checks,
    { code: "success", native: "success" },
    "Build handoff must record successful code and native checks",
  );
}

async function inspectTarball(native, tarball) {
  const bytes = fs.readFileSync(tarball);
  assert.equal(
    bytes.length <= 1024 * 1024,
    true,
    "Release tarball must remain bounded",
  );
  const files = [];
  const manifests = [];
  const fileSha256 = {};
  await native.tar.t({
    file: tarball,
    onReadEntry(entry) {
      assert.equal(entry.type, "File", "Only ordinary packed files allowed");
      assert.equal(
        entry.size <= 128 * 1024,
        true,
        "Packed file must remain bounded",
      );
      assert.equal(
        entry.path.startsWith("package/"),
        true,
        "Canonical npm archive prefix required",
      );
      files.push(entry.path.slice(8));
      const chunks = [];
      entry.on("data", (chunk) => chunks.push(chunk));
      entry.on("end", () => {
        fileSha256[entry.path.slice(8)] = hash(Buffer.concat(chunks), "sha256");
        if (entry.path === "package/package.json")
          manifests.push(JSON.parse(Buffer.concat(chunks).toString("utf8")));
      });
    },
  });
  assert.deepEqual(
    files.sort(),
    FILES,
    "Exact seven-file allowlist excludes credentials, helpers and private reports",
  );
  assert.equal(manifests.length, 1, "Exactly one packed manifest required");
  validateManifest(manifests[0]);
  const root = path.resolve(__dirname, "..");
  validateBaseline(
    fileSha256,
    JSON.parse(
      fs.readFileSync(path.join(root, "release-baseline.json"), "utf8"),
    ),
    hash(
      fs.readFileSync(path.join(root, "nodes/BrewPage/BrewPage.node.ts")),
      "sha256",
    ),
  );
  return {
    subject: {
      name: native.npa.toPurl(native.npa.resolve(NAME, VERSION)),
      digest: { sha512: hash(bytes, "sha512") },
    },
    sha256: hash(bytes, "sha256"),
    files,
    fileSha256,
  };
}

async function verify(native, tarball, bundlePath, sha, runUrl) {
  const packed = await inspectTarball(native, tarball);
  assert.equal(
    fs.statSync(bundlePath).size <= 128 * 1024,
    true,
    "Sigstore bundle must remain bounded",
  );
  const bundle = await native.verifyProvenance(packed.subject, bundlePath);
  await native.sigstore.verify(bundle, {
    certificateIdentityURI: `https://github.com/${REPOSITORY}/${WORKFLOW}@refs/heads/main`,
    certificateIssuer: "https://token.actions.githubusercontent.com",
  });
  validateStatement(
    JSON.parse(
      Buffer.from(bundle.dsseEnvelope.payload, "base64").toString("utf8"),
    ),
    packed.subject,
    sha,
    runUrl,
  );
  return packed;
}

async function main(args) {
  const [command, npmDirectory, tarball, bundlePath, sha, runUrl] = args;
  const native = loadNative(npmDirectory);
  if (command === "pack") {
    const root = path.resolve(__dirname, "..");
    const release = path.join(root, "release");
    fs.mkdirSync(release);
    const result = spawnSync(
      process.execPath,
      [
        native.npm,
        "pack",
        "--ignore-scripts",
        "--json",
        "--pack-destination",
        release,
      ],
      { cwd: root, encoding: "utf8", timeout: 60000 },
    );
    assert.equal(
      result.status,
      0,
      "Pack must succeed without lifecycle scripts",
    );
    const packed = JSON.parse(result.stdout);
    assert.equal(packed.length, 1, "Pack exactly one release");
    assert.equal(
      packed[0].filename,
      `${NAME}-${VERSION}.tgz`,
      "Expected release filename required",
    );
    const inspected = await inspectTarball(
      native,
      path.join(release, packed[0].filename),
    );
    fs.writeFileSync(
      path.join(release, "pack-manifest.json"),
      `${JSON.stringify({ ...inspected, npm: "11.15.0" }, null, 2)}\n`,
      { flag: "wx" },
    );
    return;
  }
  if (command === "sign") {
    const event = JSON.parse(
      fs.readFileSync(process.env.GITHUB_EVENT_PATH, "utf8"),
    );
    const actualRun = validateContext(process.env, event, sha);
    const git = spawnSync("git", ["rev-parse", "HEAD"], { encoding: "utf8" });
    assert.deepEqual(
      { status: git.status, sha: git.stdout.trim() },
      { status: 0, sha },
      "Checkout must match reviewed source",
    );
    for (const args of [
      ["diff", "--exit-code"],
      ["diff", "--cached", "--exit-code"],
    ]) {
      const clean = spawnSync("git", args, { encoding: "utf8" });
      assert.equal(
        clean.status,
        0,
        "Signing requires unchanged tracked source",
      );
    }
    const packed = await inspectTarball(native, tarball);
    const release = path.dirname(tarball);
    validateHandoff(
      packed,
      JSON.parse(
        fs.readFileSync(path.join(release, "pack-manifest.json"), "utf8"),
      ),
      JSON.parse(fs.readFileSync(path.join(release, "checks.json"), "utf8")),
    );
    const bundle = await native.generateProvenance([packed.subject], {});
    fs.writeFileSync(bundlePath, `${JSON.stringify(bundle)}\n`, { flag: "wx" });
    await verify(native, tarball, bundlePath, sha, actualRun);
    fs.writeFileSync(
      path.join(path.dirname(bundlePath), "verified-build.json"),
      `${JSON.stringify({ ...packed, sha, runUrl: actualRun, npm: "11.15.0", signerSha256: SIGNER_SHA256 }, null, 2)}\n`,
      { flag: "wx" },
    );
    return;
  }
  assert.equal(
    command,
    "verify",
    "Use pack, sign or verify only; this helper never publishes",
  );
  await verify(native, tarball, bundlePath, sha, runUrl);
}

module.exports = {
  loadNative,
  validateManifest,
  validateContext,
  validateStatement,
  validateBaseline,
  validateHandoff,
  inspectTarball,
  verify,
  REPO_METADATA,
};
if (require.main === module)
  main(process.argv.slice(2)).catch(() => {
    process.stderr.write(
      "Release provenance check failed; no registry action performed.\n",
    );
    process.exitCode = 1;
  });
