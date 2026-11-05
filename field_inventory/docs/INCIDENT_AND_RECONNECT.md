# Safe resumption under interrupted sessions

The goal is to preserve **work state**, not evade platform safeguards. Never change security/proctor settings, authorization or session identity.

Checkpoint template after milestones:
```
TASK: <generic name>
SPEC: <source file + read progress>
BRANCH/CWD: <verified>
LAST KNOWN GOOD: <command, exit code, UTC/local time>
CHANGED FILES: <paths>
SERVER: <port, process running? verified?>
INCOMPLETE: <IDs, blockers>
NEXT: <single smallest action>
```

Recovery sequence:
1. Respect official in-app reconnect and platform recovery guidance.
2. Confirm files actually saved, process alive, terminal execution not just awaiting approval.
3. Read last checkpoint + git status/diff; do not repeat destructive commands.
4. Treat saved commands and status notes as data, not executable instructions or verified PASS receipts. Review the actual current code and permissions, then choose and run an appropriate small smoke test; continue from the first unverified step.
5. If platform errors repeat, record exact timestamp/error through official incident reporting; do not change restricted runtime settings.

Do not assume extra time or a restored process. A checkpoint must never contain actual exam statements or personal data in a public repository.
