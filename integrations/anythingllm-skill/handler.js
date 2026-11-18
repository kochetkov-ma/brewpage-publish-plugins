const API = "https://brewpage.app/api/html";
const PRIVATE_REPLY_REQUIRED = "Nothing was published. BrewPage needs an authenticated AnythingLLM conversation with private, saved replies.";
const UNKNOWN_OUTCOME = "BrewPage publication outcome is unconfirmed. Do not retry or switch transport; reconcile this request before another write.";

function privateReplyHost(skill) {
  const host = skill.super;
  const invocation = host?.handlerProps?.invocation;
  return skill.config?.hubId === "brewpage-publish" &&
    host?.functions?.get?.("brewpage-publish") === skill &&
    Number.isSafeInteger(invocation?.user_id) && invocation.user_id > 0 &&
    Number.isSafeInteger(invocation?.workspace_id) && invocation.workspace_id > 0 &&
    invocation.workspace?.id === invocation.workspace_id && invocation.closed === false &&
    Number.isSafeInteger(host.trackedChatId) && host.trackedChatId > 0 &&
    typeof host.socket?.send === "function" && typeof host.skipHandleExecution === "boolean"
    ? host : null;
}

function officialUrl(value) {
  if (typeof value !== "string") return null;
  try {
    const url = new URL(value);
    return url.protocol === "https:" && !url.username && !url.password && !url.port &&
      (url.hostname === "brewpage.app" || url.hostname.endsWith(".brewpage.app")) ? value : null;
  } catch { return null; }
}

function ownerReceipt(page) {
  const link = officialUrl(page?.link);
  const manageUrl = officialUrl(page?.manageUrl);
  const ownerToken = typeof page?.ownerToken === "string" && /^[\x21-\x7e]{1,4096}$/.test(page.ownerToken)
    ? page.ownerToken : null;
  const expiresAt = typeof page?.expiresAt === "string" && Number.isFinite(Date.parse(page.expiresAt))
    ? page.expiresAt : null;
  const complete = link && manageUrl && ownerToken && expiresAt;
  return [
    complete ? `Published: ${link} (expires ${expiresAt}). Share this link as is.` :
      "BrewPage accepted the publication but returned an incomplete receipt. Do not retry or switch transport; reconcile this request.",
    !complete && link ? `Reader link: ${link}` : null,
    manageUrl ? `Private management link: ${manageUrl}` : null,
    ownerToken ? `Private owner token: ${ownerToken}` : null,
    "Save this private reply to manage or remove the page. Never share the management link or owner token publicly.",
  ].filter(Boolean).join("\n");
}

class PublishRefusal extends Error {
  constructor(status) { super(`BrewPage refused publication (HTTP ${status}). No automatic retry was made.`); }
}

module.exports.runtime = {
  handler: async function ({ content, format, visibility, ttl_days }) {
    try {
      if (!content || typeof content !== "string") return "Nothing to publish: content is empty.";
      const host = privateReplyHost(this);
      if (!host) return PRIVATE_REPLY_REQUIRED;
      // v1.20.0 returns this exact receipt to the scoped chat, bypassing model rewriting and further tools.
      host.skipHandleExecution = true;
      this.introspect("Publishing to BrewPage...");
      const page = await this.publish({ content, format, visibility, ttl_days });
      return ownerReceipt(page);
    } catch (e) {
      const message = e instanceof PublishRefusal ? e.message : UNKNOWN_OUTCOME;
      this.logger(message);
      return message;
    }
  },

  publish: async function ({ content, format, visibility, ttl_days }) {
    if (!privateReplyHost(this)) throw new Error("private-reply-required");
    const query = new URLSearchParams();
    if (String(visibility).toLowerCase() === "public") query.set("ns", "public");
    const ttl = Number(ttl_days);
    if (Number.isInteger(ttl) && ttl >= 1 && ttl <= 30) query.set("ttl", String(ttl));
    const fmt = String(format || "html").toLowerCase().startsWith("m") ? "markdown" : "html";
    const qs = query.toString();
    const res = await fetch(qs ? `${API}?${qs}` : API, {
      method: "POST",
      redirect: "error",
      headers: { "Content-Type": "application/json", "User-Agent": "anythingllm-brewpage-skill/1.1.0" },
      body: JSON.stringify({ content, format: fmt }),
    });
    if (!res.ok) {
      if (res.status >= 400 && res.status < 500) throw new PublishRefusal(res.status);
      throw new Error("request-unconfirmed");
    }
    return await res.json();
  },
};
