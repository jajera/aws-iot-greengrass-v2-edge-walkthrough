# Config

Base settings for this walkthrough. Copy the example and edit locally:

```bash
cp config/walkthrough.env.example config/walkthrough.env
```

`walkthrough.env` is gitignored. Do not commit certificates or private keys.

| Variable | Purpose |
| --- | --- |
| `AWS_REGION` | Region for IoT Core and Greengrass |
| `AWS_PROFILE` | Named profile for AWS CLI |
| `PROJECT_NAME` | Short prefix for Things and groups |
| `ENVIRONMENT` | e.g. `dev` |
| `CORE_THING_NAME` | Greengrass core Thing (NUC) |
| `CORE_THING_GROUP` | Thing group for core deployments |
| `CLIENT_THING_NAME` | Primary ESP32-S3 client Thing (`…-esp32-1`) |
| `CLIENT_THING_PREFIX` | Auth wildcard prefix (`…-esp32`) for `…-1`, `…-2`, … |
| `CLIENT_THING_NAME_2` / `_3` | Optional zone client Things (`…-esp32-2`, `…-esp32-3`) |
| `CLIENT_CERTS_DIR` / `_2` / `_3` | Client X.509 dirs |
| `ZONE_TABLE` | DynamoDB table with latest state per zone |
| `ALARM_TOPIC` | SNS topic for zone temperature alarms |
| `COMMAND_FUNCTION` | Lambda that turns an alarm into a cloud → edge command |
| `ALERT_EMAIL` | Address subscribed to `ALARM_TOPIC` |
| `CERTS_DIR` | Local cert output root |
| `GG_ROOT` | Nucleus install path on the core host |
| `AWS_IOT_ENDPOINT` | Optional; set after `describe-endpoint` |

Load into your shell before running the walkthrough CLI commands:

```bash
set -a
# shellcheck disable=SC1091
source config/walkthrough.env
set +a
```

There are no provision/deploy wrapper scripts — use the AWS CLI commands on each
Starlight page with these variable names.
