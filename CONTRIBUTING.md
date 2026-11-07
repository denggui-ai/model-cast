# Contributing

- Keep user portraits, product images, generated outputs, quota ledgers, credentials, and local run data out of commits.
- Use synthetic fixtures for tests; never embed private event logs or local filesystem paths.
- Run the full test suite and `git diff --check` before submitting changes.
- Do not weaken explicit image-generation authorization, quota, source-image preservation, or receipt validation gates.
- Changes to fixed prompts, workflow states, package schemas, or third-party vendored code require focused review and provenance updates.
