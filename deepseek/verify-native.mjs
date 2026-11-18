import assert from 'node:assert/strict';
import { readFile, readdir } from 'node:fs/promises';
import { join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Context } from '@deepseek-ai/cordis';
import SkillRegistry from '@deepseek-ai/dsh-skill';
import * as brewpage from 'dsh-brewpage';

const installed = new URL('./node_modules/dsh-brewpage/', import.meta.url);
const upstream = new URL('skills/brewpage-publish/upstream/', installed);

function verifyHistorical(active, source) {
  assert.match(active, /Read `upstream\/SKILL.md` completely/, 'historical native body loads the complete workflow');
  assert.match(source, /Step 4: Ask Namespace/, 'historical consent workflow remains available');
}

async function verifyRecipes(active, source) {
  const files = await readdir(upstream, { recursive: true, withFileTypes: true });
  const members = files.filter(file => file.isFile())
    .map(file => relative(fileURLToPath(upstream), join(file.parentPath, file.name))).sort();
  const recipes = ['custom-domain', 'ownership', 'page-data', 'publishing'].map(name => `references/${name}.md`);
  assert.deepEqual(members, ['LICENSE', 'README.md', 'SKILL.md', ...recipes, 'scripts/brewpage-lib.sh', 'scripts/brewpage-run.sh',
    'scripts/history.py', 'scripts/publish.mjs'], 'installed source has exactly the eleven canonical members');
  const linked = [...new Set([...source.matchAll(/\]\((references\/[a-z-]+\.md)\)/g)].map(match => match[1]))].sort();
  assert.deepEqual(linked, recipes, 'the installed workflow links all four recipes');
  assert.match(active, /Read \[the bundled workflow\]\(upstream\/SKILL.md\)/, 'native activation points to the installed workflow');
  assert.match(active, /verified private delivery of any credential-bearing result/, 'native MCP writes enforce the private result boundary');
  assert.match(active, /Choose the isolated native runner before dispatch/, 'native transport fallback is selected before writing');
  const transport = await readFile(new URL('cordis.patch.yml', installed), 'utf8');
  assert.match(transport, /^\s*args: \['-y', 'brewpage-mcp@3\.0\.0'\]$/m, 'candidate pins the exact MCP registry version');
}

const ctx = new Context();
try {
  // GIVEN native registry plus the installed bundle, without a model adapter.
  await ctx.plugin(SkillRegistry);
  await ctx.plugin(brewpage);

  // WHEN the native provider discovers and loads its packaged skill.
  const skills = await ctx.skills.list({ cwd: process.cwd() });
  const skill = await ctx.skills.get('brewpage-publish', { cwd: process.cwd() });
  const source = await readFile(new URL('SKILL.md', upstream), 'utf8');
  const { version } = JSON.parse(await readFile(new URL('package.json', installed), 'utf8'));

  // THEN the native skill is invocable and retains the upstream consent workflow.
  assert.deepEqual(skills.map(s => [s.name, s.provider, s.invocation]), [
    ['brewpage-publish', 'brewpage-bundled', { modelInvocable: true, userInvocable: true }],
  ], 'native registry must expose exactly the packaged publishing skill');
  const contract = { '1.1.0': verifyRecipes }[version] ?? verifyHistorical;
  await contract(skill.content, source);
  process.stdout.write('PASS native skill discovery, invocation policy and body loading\n');
} finally {
  await ctx.fiber.dispose();
}
