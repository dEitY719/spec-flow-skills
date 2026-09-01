/**
 * spec-flow plugin for OpenCode.ai
 *
 * Auto-registers the skills directory via the config hook (no symlinks needed).
 *
 * Like the sibling harness and notes plugins, this one injects no per-session
 * bootstrap context. The spec-flow skills are task-triggered — you reach for one
 * when a PRD, a TRD, or a finished PR is in front of you — so OpenCode's native
 * `skill` tool discovering them is all that is needed.
 */

import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export const SpecFlowPlugin = async () => {
  const specFlowSkillsDir = path.resolve(__dirname, '../../skills');

  return {
    // Inject skills path into live config so OpenCode discovers spec-flow
    // skills without requiring manual symlinks or config file edits.
    // This works because Config.get() returns a cached singleton — modifications
    // here are visible when skills are lazily discovered later.
    config: async (config) => {
      config.skills = config.skills || {};
      config.skills.paths = config.skills.paths || [];
      if (!config.skills.paths.includes(specFlowSkillsDir)) {
        config.skills.paths.push(specFlowSkillsDir);
      }
    },
  };
};
