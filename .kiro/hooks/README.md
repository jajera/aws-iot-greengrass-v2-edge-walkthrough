# Hooks

Kiro v1 hooks ([reference](https://kiro.dev/docs/hooks/)).

| File | Trigger | Blocks | Purpose |
| --- | --- | --- | --- |
| `guard-aws-mutations.json` | `PreToolUse` | yes | Refuses mutating AWS CLI / IaC apply-destroy unless `GG_EDGE_ALLOW_AWS=1` |
| `cite-aws-claims.json` | `PostFileSave` | no | Reminds the agent to ground AWS claims after editing `src/content/docs/**/*.mdx` |
| `format-markdown-tables.json` | `PostFileSave` | no | Repairs broken GFM tables in dirty Markdown |

Opt in for a deliberate demo apply:

```bash
export GG_EDGE_ALLOW_AWS=1
```

Test the guard without Kiro:

```bash
echo '{"command":"aws iot create-thing --thing-name demo"}' | python3 .kiro/hooks/guard-aws-mutations.py; echo "exit=$?"   # 2
echo '{"command":"aws sts get-caller-identity"}' | python3 .kiro/hooks/guard-aws-mutations.py; echo "exit=$?" # 0
```
