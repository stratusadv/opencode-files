---
description: Self reflect on the conversation.
agent: self-reflect
---

You performed an action and had to get corrected. Review what needed to be done better and how to improve next time.

$ARGUMENTS

Create the following todo list to self-reflect and improve next time:
1. Reflect on the conversation to pinpoint what happened.
2. Create a creation summary of what information mis-guided you or was missing.
3. Load the @skill-writing skill. Pay attention to how skills are written, including:
   - Skill file locations: project-specific skills live in `.opencode/skills/`, global skills live in `.config/opencode/skills/`
   - When uncertain about location, use the question tool to ask the user
   - Determine if the skill should live in the project root or global config
4. Update the relevant skills based on the @skill-writing best practices so you do not make this mistake again. Keep it more general so it applies to various situations.
   - General programming (python, style and best practices) live in the @python_style skill.
   - Other skills live in their respective folders.
5. Create a plan on how to improve next time.
6. Update relevant files, ensuring each skill is in the correct location based on its scope.
