# LLM-backed features

Profile for a feature that sends data to a hosted model and acts on the result. Read [llm-calls.md](../llm-calls.md) for the general call rules. This profile adds only what is specific to a feature.

## Match signals

- requires: a model-provider SDK import or dependency (a chat, completions or inference client), or an `llm`, `ai` or model client module, adapter or port that wraps one.
- supporting: prompt template files or a prompts directory of versioned resources; evaluation sets or golden files; cost or budget config keyed by model name.
- Not a signal alone: a generic `model` or `models` directory (ORMs have one), or cost config with no provider client.

## Rules

- Enforce each invariant in code, not only in the prompt. See `LLM-INVARIANT-CODE` in [defect-classes.md](../defect-classes.md).
- Sanitise untrusted notes and free text that carry control markers (role tags, delimiter strings, instruction-like headers) before they reach a prompt. Strip or escape them in the sanitiser, and test with one sample of each marker.
- Keep control content that the model could echo back (verdicts, status markers) out of prompts, per [LLM-INVARIANT-CODE](../defect-classes.md).
- Seed model, prompt and config rows through migrations, not hand inserts. Every environment gets the same rows from the same migration.
- Read the model identifier and budgets from configuration, not from literals scattered through the code.
- Log no sensitive or personal text. Log identifiers, call type, token counts and error codes only, as [observability.md](../observability.md) and `LLM-USAGE` in [llm-calls.md](../llm-calls.md) require.
- Give each invariant an evaluation or fixture test that fails when the invariant is removed. Include golden cases for each control marker and for each out-of-set identifier.
- A prompt or model version change ships with an evaluation run, as `LLM-EVAL` in [llm-calls.md](../llm-calls.md) requires.
