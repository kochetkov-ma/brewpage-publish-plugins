// BrewPage publish skill for AnythingLLM: POST /api/html, return the reader link.
const API = "https://brewpage.app/api/html";

module.exports.runtime = {
  handler: async function ({ content, format, visibility, ttl_days }) {
    try {
      if (!content || typeof content !== "string") return "Nothing to publish: content is empty.";
      this.introspect("Publishing to BrewPage...");
      const page = await this.publish({ content, format, visibility, ttl_days });
      return `Published: ${page.link} (expires ${page.expiresAt}). Share this link as is.`;
    } catch (e) {
      this.logger(`brewpage-publish failed: ${e.message}`);
      return `BrewPage publish failed: ${e.message}`;
    }
  },

  // Full API response; the owner token in it stays out of chat.
  publish: async function ({ content, format, visibility, ttl_days }) {
    const query = new URLSearchParams();
    if (String(visibility).toLowerCase() === "public") query.set("ns", "public");
    const ttl = Number(ttl_days);
    if (Number.isInteger(ttl) && ttl >= 1 && ttl <= 30) query.set("ttl", String(ttl));
    const fmt = String(format || "html").toLowerCase().startsWith("m") ? "markdown" : "html";
    const qs = query.toString();
    const res = await fetch(qs ? `${API}?${qs}` : API, {
      method: "POST",
      headers: { "Content-Type": "application/json", "User-Agent": "anythingllm-brewpage-skill/1.0.0" },
      body: JSON.stringify({ content, format: fmt }),
    });
    const text = await res.text();
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${text.slice(0, 300)}`);
    return JSON.parse(text);
  },
};
