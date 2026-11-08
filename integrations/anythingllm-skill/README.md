# Publish to BrewPage: AnythingLLM agent skill

Part of [BrewPage publishing plugins](https://github.com/kochetkov-ma/brewpage-publish-plugins#readme) for
[BrewPage](https://brewpage.app).

A custom [AnythingLLM agent skill](https://docs.anythingllm.com/agent/custom/introduction) that publishes
HTML or Markdown to BrewPage and returns a shareable HTTPS link. No account, API key or setup arguments.

## Install

- From the AnythingLLM Community Hub: import "Publish to BrewPage" (once listed).
- By hand: copy `plugin.json` and `handler.js` into
  `<AnythingLLM storage>/plugins/agent-skills/brewpage-publish/` (the folder name must equal `hubId`),
  then enable the skill under Agent Skills.

Needs a Node.js runtime with global `fetch` (Node 18+, as in current AnythingLLM builds).

## Use

Ask an agent (`@agent`) to publish something, for example "publish this report as a web page".

| Parameter | Values | Default |
| --- | --- | --- |
| `content` | full HTML document or Markdown text | required |
| `format` | `html` or `markdown` | `html` |
| `visibility` | `private` (unlisted, anyone with the link can open it) or `public` (gallery and search) | `private` |
| `ttl_days` | 1-30 | 15 |

The skill sends `POST https://brewpage.app/api/html` and replies with the reader link and expiry.
The owner token in the API response is never returned to the chat, so pages published by the skill
cannot be edited or deleted later; they expire on their own. Never publish secrets or personal data
as `public`. API reference: [llms.txt](https://brewpage.app/llms.txt).

## License

MIT
