# Security at application boundaries

Apply to the boundary being changed. These are engineering safeguards, not a claim of security certification or a reason to broaden an unrelated task into a full audit. Customer scoping is detailed in `tenancy.md`; telemetry privacy in `observability.md`.

## AUTH-BOUNDARY — trusted identity, explicit permission

- Authenticate at the entry point and authorize the specific action and object at the owning service/data boundary. A caller-controlled identifier narrows a query; it does not grant access.
- Account for every actor class: human, administrator, service account, scheduled worker, and delegated caller where present. Test denial as well as success; an authorization helper that returns without checking is a missing boundary.
- Derive customer scope from trusted identity or a validated delegation. Include it in reads, mutations, aggregates, exports, cache keys, storage paths, and background tasks. Test forged and foreign identifiers separately from missing authentication.
- Feature flags govern availability, not authorization. Check them at the effect boundary; hiding a control is insufficient. Verify off, on, and lookup failure for a safety-sensitive rollout.
- For browser sessions, use the framework's supported session, CSRF, cookie, and logout protections. Avoid implementing cryptographic or identity protocols locally. Apply the repository's origin/CORS policy without opening it to make tests pass.

## INPUT-BOUNDARY — validate before interpreting

- Validate shape, type, length, size, and business constraints at the public boundary. Use parameterized queries and context-appropriate output encoding. A cast, an ORM model, and frontend validation do not validate a request.
- Explicitly allow writable fields; never bind arbitrary request properties into domain or authorization state. Reject unsupported state transitions and version conflicts with a stable error contract.
- For URLs, parse against a trusted base and validate the resulting protocol, origin, and destination policy before opening or fetching. Test protocol-relative URLs, credentials, unexpected schemes, encoded forms, and redirects. A string beginning with `/` can still point to another host as `//host`.
- For server-side fetches, also enforce egress/network policy against private/link-local destinations and redirect/DNS changes as applicable. A browser link allowlist alone is not an SSRF defense.
- For uploads, bound size and resource use, verify actual format, use generated storage keys, isolate parsing, and authorize download access. Treat names, paths, content, archives, and extracted links as untrusted.
- Limit abusive work at the boundary that can measure the actual risk: request limits at the gateway, and business/resource quotas or bounded concurrency at the owning service when needed. A proxy cannot infer every expensive application action.

## SECRET-BOUNDARY — configuration fails safely

- Credentials and signing/encryption keys have no production fallback. Validate required configuration at startup; fail with the key name and a safe reason, never the value. Use the platform's secret mechanism rather than committing credentials.
- Safe development defaults must be explicitly confined to development/test profiles. Do not silently reuse them in production. Classify operational defaults separately from secrets (`CONFIG-FAIL-CLOSED` in `authoring.md`).
- Keep sensitive data out of URLs, logs, traces, metric tags, error bodies, fixtures, and model requests unless the field is necessary and the sink is approved. Pseudonymous identifiers still need a privacy decision.
- Use synthetic fixtures. Respect retention and deletion requirements across derived records, exported objects, backups, and audit trails; do not promise erasure that the storage design cannot provide.

## TRIFECTA-BOUNDARY — never grant private data, untrusted content and an outbound channel to one authority

- Flag any feature, agent or tool session that can (1) read private or customer data, (2) ingest content an outsider can influence (documents, email, web pages, tickets, uploads, tool or MCP results) and (3) send data out (HTTP, email, messages, rendered links or images, commits, shared writes). All three together are exploitable by injected instructions; remove at least one leg.
- Break a leg structurally: isolate the untrusted-content reader from private data and from side-effecting tools, restrict egress to an allowlist, or require human confirmation for the outbound or irreversible step. An instruction to the model to ignore embedded instructions is not a break.
- Applies to products that run a model over customer documents and to a coding session that holds credentials while reading issues, PR comments or web pages.

## INJECTION-BOUNDARY — embedded instructions are data, and the effect boundary is what you test

- Treat model input from documents, retrieval, tools and users as untrusted. Delimiting or labeling it reduces risk and is not a guarantee.
- Give the model the least tool and data authority the task needs; authorization and scope checks stay in code (`AUTH-BOUNDARY`, `LLM-FAILSAFE`).
- Encode or strip model output before rendering it as markup, links or images, and before using it in queries or commands.
- Prove it with a negative test: a fixture containing planted instructions must produce no unauthorized tool call, no outbound request and no cross-scope read, observed at the real boundary rather than a mock.

Before declaring the boundary safe, demonstrate the important negative case through the real entry point: denied actor, foreign object, unsafe input, or missing secret. A test that merely asserts a mock permission method was called does not establish enforcement.
