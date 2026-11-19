# Publish to BrewPage: AnythingLLM agent skill

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for
[BrewPage](https://brewpage.app).

A custom [AnythingLLM agent skill](https://docs.anythingllm.com/agent/custom/introduction) that publishes
HTML or Markdown to BrewPage and returns a shareable HTTPS link. No BrewPage account, API key or setup arguments.
This candidate targets authenticated interactive conversations in AnythingLLM 1.20.0.

## Install

- From the AnythingLLM Community Hub: import the reviewed version of "Publish to BrewPage" when available.
- By hand: copy `plugin.json` and `handler.js` into
  `<AnythingLLM storage>/plugins/agent-skills/brewpage-publish/` (the folder name must equal `hubId`),
  then enable the skill under Agent Skills.

AnythingLLM assigns Hub imports their own installed ID. Keep that ID when enabling the skill.
For a same-item update on 1.20.0, back up the installed BrewPage skill and its local settings
outside the skills directory. Remove only that installation under Agent Skills, reimport the
reviewed update, and enable it. A reimport over the existing installation can report success
while retaining the old handler. Verify the installed version and handler checksum against
the reviewed update, then start a new conversation.

Needs a Node.js runtime with global `fetch`. Anonymous, single-user, scheduled and unknown conversation
contexts stop before making a BrewPage request. Desktop compatibility has not been qualified.

## Use

Ask an agent (`@agent`) to publish something, for example "publish this report as a web page".

| Parameter | Values | Default |
| --- | --- | --- |
| `content` | full HTML document or Markdown text | required |
| `format` | `html` or `markdown` | `html` |
| `visibility` | `private` (unlisted, anyone with the link can open it) or `public` (gallery and search) | `private` |
| `ttl_days` | 1-30 | 15 |

Before publishing, the skill checks its own installed registration, authenticated user, workspace,
active reply channel and saved chat. It uses the host's direct-result path so the complete receipt
reaches that private conversation without another model rewrite or tool call. The host's normal chat
history owns storage; the skill adds no credential store.

The single `POST https://brewpage.app/api/html` returns the reader link, expiry, private management link
and owner token. Save that private reply to change or remove the page. Anyone with the management
link can edit or delete it; never post it or the token publicly. Only the reader link is shareable.
Never publish secrets or personal data as `public`. A refused or unconfirmed write is never retried
automatically or moved to another transport. Reconcile an unconfirmed or incomplete receipt before
another write. API reference: [llms.txt](https://brewpage.app/llms.txt).

The integration targets the [1.20.0 host source](https://github.com/Mintplex-Labs/anything-llm/tree/160afa00ac0eca6315aabe662b2e7673c8c96172).
Local fixture checks establish the adapter contract; an actual AnythingLLM installation and its private
chat persistence still require native qualification before advertising support as verified.

## License

MIT
