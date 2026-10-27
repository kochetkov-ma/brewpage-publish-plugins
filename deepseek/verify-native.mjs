import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { Context } from '@deepseek-ai/cordis';
import SkillRegistry from '@deepseek-ai/dsh-skill';
import * as brewpage from 'dsh-brewpage';

const ctx = new Context();
try {
  // GIVEN native registry plus the installed bundle, without a model adapter.
  await ctx.plugin(SkillRegistry);
  await ctx.plugin(brewpage);

  // WHEN the native provider discovers and loads its packaged skill.
  const skills = await ctx.skills.list({ cwd: process.cwd() });
  const skill = await ctx.skills.get('brewpage-publish', { cwd: process.cwd() });
  const source = await readFile(new URL('./node_modules/dsh-brewpage/skills/brewpage-publish/upstream/SKILL.md', import.meta.url), 'utf8');

  // THEN the native skill is invocable and retains the upstream consent workflow.
  assert.deepEqual(skills.map(s => [s.name, s.provider, s.invocation]), [
    ['brewpage-publish', 'brewpage-bundled', { modelInvocable: true, userInvocable: true }],
  ], 'native registry must expose exactly the packaged publishing skill');
  assert.match(skill.content, /Read `upstream\/SKILL.md` completely/, 'native body must load the complete existing workflow');
  assert.match(source, /Step 4: Ask Namespace/, 'unchanged consent workflow must remain available');
  process.stdout.write('PASS native skill discovery, invocation policy and body loading\n');
} finally {
  await ctx.fiber.dispose();
}
