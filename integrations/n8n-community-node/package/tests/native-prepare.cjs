const fs = require("node:fs");
const workflow = JSON.parse(
  fs.readFileSync("/artifact/tests/native-workflow.json", "utf8"),
);
const expressionCases = {
  "invalid-access-array": { access: "={{ ['public'] }}" },
  "invalid-format-object": { format: "={{ ({ value: 'html' }) }}" },
};
Object.assign(
  workflow.nodes[1].parameters,
  expressionCases[process.env.BREWPAGE_NATIVE_FIXTURE],
);
fs.writeFileSync("/tmp/native-workflow.json", JSON.stringify(workflow));
