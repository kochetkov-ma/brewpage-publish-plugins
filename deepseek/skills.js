import { fileURLToPath } from 'node:url';
import * as filesystemSkills from '@deepseek-ai/dsh-skill-filesystem';

export const name = 'brewpage-skills';
export const inject = ['skills'];

export function apply(ctx) {
  ctx.plugin(filesystemSkills, {
    providerName: 'brewpage-bundled',
    includeDefaultRoots: false,
    customSkillDirs: [fileURLToPath(new URL('./skills', import.meta.url))],
    watch: false,
  });
}
