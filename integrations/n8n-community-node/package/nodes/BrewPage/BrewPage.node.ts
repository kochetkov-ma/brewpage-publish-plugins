import {
  NodeConnectionTypes,
  NodeOperationError,
  type IExecuteFunctions,
  type INodeExecutionData,
  type INodeType,
  type INodeTypeDescription,
} from "n8n-workflow";

const USER_AGENT = "brewpage-n8n/0.1.2 (+https://brewpage.app)";
const NOT_CONFIRMED =
  "Publication was not confirmed. Check nonempty content (up to 5 MiB), format, access and lifetime (1–30 days). Check for an existing publication before retrying.";
const MAX_BYTES = 5 * 1024 * 1024;
const RESERVED_HOST_LABELS = [
  "unlock",
  "www",
  "api",
  "admin",
  "assets",
  "static",
  "cdn",
  "status",
  "health",
  "metrics",
  "grafana",
  "prometheus",
  "monitoring",
  "autoconfig",
  "autodiscover",
  "fe-bounces",
  "account",
];

export class BrewPage implements INodeType {
  description: INodeTypeDescription = {
    displayName: "BrewPage",
    name: "brewPage",
    icon: { light: "file:brewpage.svg", dark: "file:brewpage.svg" },
    subtitle: '={{$parameter["operation"]}}',
    group: ["output"],
    version: 1,
    description:
      "Publish temporary HTML and Markdown reports without credentials",
    defaults: { name: "BrewPage" },
    inputs: [NodeConnectionTypes.Main],
    outputs: [NodeConnectionTypes.Main],
    usableAsTool: true,
    properties: [
      {
        displayName: "Operation",
        name: "operation",
        type: "options",
        noDataExpression: true,
        options: [
          {
            name: "Publish Report",
            value: "publish",
            action: "Publish a report",
            description: "Create a temporary reader link",
          },
        ],
        default: "publish",
      },
      {
        displayName: "Access",
        name: "access",
        type: "options",
        default: "unlisted",
        options: [
          {
            name: "Unlisted",
            value: "unlisted",
            description: "Anyone with the link can read it",
          },
          {
            name: "Public",
            value: "public",
            description: "Discoverable in the gallery; anyone can read it",
          },
        ],
        description:
          "Unlisted is not private. Publish only content intended for sharing.",
      },
      {
        displayName: "Format",
        name: "format",
        type: "options",
        default: "html",
        options: [
          { name: "HTML", value: "html" },
          { name: "Markdown", value: "markdown" },
        ],
      },
      {
        displayName: "Content",
        name: "content",
        type: "string",
        typeOptions: { rows: 8 },
        required: true,
        default: "",
        description:
          "HTML or Markdown report, up to 5 MiB in UTF-8. Do not include secrets or personal data.",
      },
      {
        displayName: "Lifetime (Days)",
        name: "ttl",
        type: "number",
        default: 15,
        typeOptions: { minValue: 1, maxValue: 30, numberPrecision: 0 },
        description:
          "Requested retention, 1–30 days. Existing identical content may keep its earlier expiry.",
      },
      {
        displayName:
          "Ownership tokens are discarded. This node cannot update or delete publications. Content expires automatically. Disable workflow execution saving and avoid pinned data for sensitive inputs.",
        name: "retentionNotice",
        type: "notice",
        default: "",
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const output: INodeExecutionData[] = [];
    for (let index = 0; index < items.length; index++) {
      let item: INodeExecutionData | undefined;
      try {
        item = await publishItem(this, index);
      } catch {
        item = undefined;
      }
      // Fixed message only: transport errors may carry tokens or content.
      if (!item)
        throw new NodeOperationError(this.getNode(), NOT_CONFIRMED, {
          itemIndex: index,
        });
      output.push(item);
    }
    return [output];
  }
}

async function publishItem(
  context: IExecuteFunctions,
  index: number,
): Promise<INodeExecutionData | undefined> {
  const operation = context.getNodeParameter("operation", index);
  const content = context.getNodeParameter("content", index);
  const format = context.getNodeParameter("format", index);
  const access = context.getNodeParameter("access", index);
  const ttl = context.getNodeParameter("ttl", index);
  if (
    typeof content !== "string" ||
    content.trim().length === 0 ||
    Buffer.byteLength(content, "utf8") > MAX_BYTES ||
    operation !== "publish" ||
    typeof format !== "string" ||
    !["html", "markdown"].includes(format) ||
    typeof access !== "string" ||
    !["unlisted", "public"].includes(access) ||
    typeof ttl !== "number" ||
    !Number.isInteger(ttl) ||
    ttl < 1 ||
    ttl > 30
  ) {
    return undefined;
  }
  const response: unknown = await context.helpers.httpRequest({
    method: "POST",
    url: "https://brewpage.app/api/html",
    qs: {
      ttl,
      format,
      verbatim: true,
      ...(access === "public" ? { ns: "public" } : {}),
    },
    headers: { "User-Agent": USER_AGENT, Accept: "application/json" },
    body: { content, format },
    json: true,
    timeout: 60000,
    maxResponseBodyBytes: 65536,
    disableFollowRedirect: true,
  });
  if (!response || typeof response !== "object") return undefined;
  const result = response as Record<string, unknown>;
  if (typeof result.link !== "string") return undefined;
  const link = new URL(result.link);
  const validPath =
    link.hostname === "brewpage.app"
      ? /^\/public\/[A-Za-z0-9]{10}\/?$/.test(link.pathname)
      : /^(?:[a-z0-9-]{1,33}-)?[a-z0-9]{10}\.brewpage\.app$/.test(
          link.hostname,
        ) && link.pathname === "/";
  const reservedHost = RESERVED_HOST_LABELS.includes(
    link.hostname.split(".")[0],
  );
  if (
    link.protocol !== "https:" ||
    link.username ||
    link.password ||
    link.port ||
    link.search ||
    link.hash ||
    reservedHost ||
    !validPath ||
    result.access !== access ||
    typeof result.expiresAt !== "string" ||
    !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,9})?Z$/.test(
      result.expiresAt,
    ) ||
    !Number.isFinite(Date.parse(result.expiresAt)) ||
    new Date(result.expiresAt).toISOString().slice(0, 19) !==
      result.expiresAt.slice(0, 19)
  ) {
    return undefined;
  }
  const action = (result.result as { action?: unknown } | undefined)?.action;
  return {
    json: {
      link: link.href,
      access,
      format,
      expiresAt: result.expiresAt,
      requestedTtlDays: ttl,
      reusedExisting: action === "merged",
    },
    pairedItem: { item: index },
  };
}
