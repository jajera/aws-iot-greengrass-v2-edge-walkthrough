---
inclusion: always
---

# AWS source lock

Behavioural claims about AWS IoT Greengrass V2, IoT Core, certificates, discovery,
and pricing must be grounded.

## Prefer

1. Facts verified in this account and listed below.
2. Links to current AWS documentation (use aws-docs MCP: search → read).
3. Explicit **unverified** markers for steps not yet run.

## Do not

- Invent CLI flags, component names, or discovery URLs from memory.
- Cite blog posts as authoritative over AWS docs for API behaviour.
- Treat Greengrass V1 docs as applicable to V2 without a callout.

## Verified facts

Evidence pass: **2026-10-04**, profile **`lab`**, region **`ap-southeast-2`**,
AWS CLI **2.37.4**. Do **not** put real AWS account IDs, STS ARNs, or Data-ATS
endpoint host prefixes in `src/content/docs/**` — always use placeholders
(`123456789012`, `example123abc-ats…`).

### Identities (`cloud.mdx`)

- Data-ATS endpoint shape verified (`*-ats.iot.ap-southeast-2.amazonaws.com`)
- Things created: `gg-edge-wt-dev-core`, `gg-edge-wt-dev-esp32-1` (renamed from
  unnumbered `…-esp32`; Auth uses `CLIENT_THING_PREFIX` = `…-esp32`)
- Thing group: `gg-edge-wt-dev-cores`
- Role alias: `gg-edge-wt-dev-token-alias` → IAM role
  `gg-edge-wt-dev-token-exchange` (trust: `credentials.iot.amazonaws.com`)
- Greengrass account service role association uses CLI
  **`aws greengrassv2 associate-service-role-to-account`** (not
  `put-service-role-for-account` — that name is invalid on CLI 2.37.x).
- Verify with `aws greengrassv2 get-service-role-for-account` → role
  `gg-edge-wt-dev-gg-service` associated at `2026-10-04T10:35:08Z`.
- Cert PEMs written under gitignored `certs/core/` and `certs/client/`.

### Nucleus (`nucleus.mdx`) — evidence **2026-10-08**

- Host: NUC6CAYB, Ubuntu **24.04.5**, hostname `nuc-gg-edge`, OpenJDK
  **21.0.12.1**, Python **3.12.3** (distro default — lab pin; no deadsnakes).
- Workstation ESP-IDF evidence **2026-10-09**: IDF **v5.3.2** with Python
  **3.12.3** (`~/.espressif/python_env/idf5.3_py3.12_env`).
- Manual provision via
  [manual-installation](https://docs.aws.amazon.com/greengrass/v2/developerguide/manual-installation.html):
  `--init-config` + `config.yaml` (not interactive `--provision false` prompts).
- Installer zip `greengrass-nucleus-latest.zip` →
  `java -jar …/Greengrass.jar --version` → **AWS Greengrass v2.18.3**.
- systemd unit **`greengrass.service`** (enabled, active); root `/greengrass/v2`.
- `--deploy-dev-tools` **not** available without `--provision true`; no
  `/greengrass/v2/bin/greengrass-cli` after manual install (deploy
  `aws.greengrass.Cli` separately when needed).
- Cloud: `get-core-device` → `gg-edge-wt-dev-core`, status **HEALTHY**,
  `coreVersion` **2.18.3**, platform linux/amd64.
- Docs keep placeholder endpoint prefixes (`example123abc…`); live values stay in
  gitignored `walkthrough.env`.

### Client-device deployment (`deploy.mdx`) — evidence **2026-10-09**

- `create-deployment` → `gg-edge-client-device-support` on thing group
  `gg-edge-wt-dev-cores`; `coreDeviceExecutionStatus` **SUCCEEDED**.
- Component pins (public latest at evidence time): Nucleus **2.18.3**, Auth
  **2.5.7**, Moquette **2.3.7**, Bridge **2.3.4**, IPDetector **2.2.5**.
- Public component name is **`aws.greengrass.clientdevices.IPDetector`** (not
  `aws.greengrass.IPDetector`).
- Verify with `list-installed-components` (manual provision has no CLI until
  `aws.greengrass.Cli` is deployed). All four client-support components
  **RUNNING**; core remains **HEALTHY**.
- Auth `selectionRule` is `thingName: <CLIENT_THING_PREFIX>*` so numbered
  clients (`…-esp32-1`, optional `…-esp32-2`) match without a separate Auth
  group. One client is enough for the happy path.

### Associate + discovery (`associate.mdx`) — evidence **2026-10-09**

- Associated `gg-edge-wt-dev-esp32-1` and `gg-edge-wt-dev-esp32-2` to core
  `gg-edge-wt-dev-core` (primary renamed from `…-esp32` → `…-esp32-1`).
- Discovery curl (client cert, port **8443**) for **both** Things returned
  connectivity `HostAddress` = NUC LAN IP, `PortNumber` **8883**.
- Second client Thing + PEMs under gitignored `certs/client-2/`.

### Concept pages and edge components (authored **2026-10-09**)

- Concept pages: `how-aws-describes-greengrass.mdx`, `compare-iot-core.mdx`.
- Edge inference: **SageMaker Edge Manager EOL 2024-04-26** — lab trains in SageMaker
  and ships ONNX in a custom component (`com.example.ZoneAnomaly`). Docs cite
  [edge-eol](https://docs.aws.amazon.com/sagemaker/latest/dg/edge-eol.html) and
  [perform-machine-learning-inference](https://docs.aws.amazon.com/greengrass/v2/developerguide/perform-machine-learning-inference.html).
- Contrast vs AWS Skill Builder “Deploying Greengrass Components”: that lab uses
  EC2 + auto-provision + `/tmp` threshold logs; this repo keeps NUC + ESP32
  clients + IPC closed loop.
- Cli must be deployed **with** the client-device stack (Thing-group deploy
  replaces root components). Template:
  `artifacts/deployments/client-device-support-with-cli.json`.
- Evidence **2026-10-09**: deployment `2ab5a9fe-…` → Cli **2.18.3** RUNNING
  alongside Auth/Moquette/Bridge/IPDetector (SUCCEEDED).
- Evidence **2026-10-09**: local `greengrass-cli` merge
  `com.example.GgEdgeLoop=1.0.0` → **RUNNING** after
  `pip install --break-system-packages awsiotsdk` on Ubuntu 24.04; log shows
  `subscribed to gg-edge/sensor`. Without the SDK the component is **BROKEN**.
- Evidence **2026-10-09**: end-to-end BOOT → RGB — `GgEdgeLoop` **1.0.1**
  publishes `gg-edge/actuator/<thing>`; bridge maps `gg-edge/actuator/+`;
  firmware BOOT GPIO 0, RGB GPIO 48 (DevKitC-1 v1.0). Example logs in
  `prove-lan.mdx` / `flash.mdx` (NUC LAN IP shown as documentation address `192.0.2.10`; no certs/CA PEMs).

### Wire into AWS (authored **2026-10-10**)

Doc-verified facts used on the integration pages:

- IoT rule names: `[a-zA-Z0-9_]+`
  ([create-topic-rule](https://docs.aws.amazon.com/cli/latest/reference/iot/create-topic-rule.html));
  pages use `${PROJECT_NAME}_${ENVIRONMENT}` with `-` → `_`.
- Rule actions: `s3` (bucketName, key, roleArn)
  ([s3-rule-action](https://docs.aws.amazon.com/iot/latest/developerguide/s3-rule-action.html)),
  `dynamoDBv2` (putItem.tableName, roleArn — each selected field becomes an
  attribute)
  ([dynamodb-v2-rule-action](https://docs.aws.amazon.com/iot/latest/developerguide/dynamodb-v2-rule-action.html)),
  `cloudwatchMetric` (no dimensions; substitution allowed in metricName)
  ([cloudwatch-metrics-rule-action](https://docs.aws.amazon.com/iot/latest/developerguide/cloudwatch-metrics-rule-action.html)).
- Substitution templates evaluate against the original payload; `topic(n)` is
  1-indexed; `${parse_time("yyyy-MM-dd", timestamp())}` is valid
  ([iot-substitution-templates](https://docs.aws.amazon.com/iot/latest/developerguide/iot-substitution-templates.html)).
- MQTT bridge: wildcards supported with IotCore as source; Pubsub as source
  needs Nucleus 2.6+. Actuator mirror uses a direct `Pubsub → IotCore` mapping
  (`ActuatorPubsubToIotCore`), not a LocalMqtt hop.
- IPC pubsub authorization: subscribe resources with `+` must appear literally;
  `*` glob works for publish resources.
- Recipe: `{artifacts:decompressedPath}` — ZIP unarchives into a folder named
  after the file
  ([component-recipe-reference](https://docs.aws.amazon.com/greengrass/v2/developerguide/component-recipe-reference.html)).
- LogManager log groups `/aws/greengrass/UserComponent/<region>/<component>`
  and `/aws/greengrass/GreengrassSystemComponent/<region>/System`
  ([monitor-logs](https://docs.aws.amazon.com/greengrass/v2/developerguide/monitor-logs.html)).
- SageMaker scikit-learn image `1.4-2-cpu-py3` in `ap-southeast-2` is hosted by
  registry `783357654285` (SDK lookup table
  [`sklearn.json`](https://github.com/aws/sagemaker-python-sdk/blob/master/sagemaker-core/src/sagemaker/core/image_uri_config/sklearn.json),
  checked 2026-10-10). Script-mode hyperparameters `sagemaker_program`,
  `sagemaker_submit_directory`, `sagemaker_region` are JSON-encoded strings.
  Execution role per
  [sagemaker-roles](https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html).
- Lambda runtime `python3.14`. SNS-wrapped CloudWatch alarm message carries
  `AlarmName`, `NewStateValue`, `Trigger.MetricName`.
- SNS DeleteTopic also deletes the topic's subscriptions
  ([API_DeleteTopic](https://docs.aws.amazon.com/sns/latest/api/API_DeleteTopic.html)).

Evidence **2026-10-10** (local, no AWS):

- Firmware with `esp_driver_tsens`: both boards publish
  `gg-edge/telemetry/<thing>` every 10 s, e.g.
  `{"thing":"gg-edge-wt-dev-esp32-1","tempC":28.90,"rssi":-29,"uptimeS":13,"rgb":"off"}`;
  chip temperature about 28.9 °C (esp32-1) / 26.5 °C (esp32-2), steps of
  about 0.4–1 °C.
- `train.py` on synthetic telemetry (sklearn 1.4.2, skl2onnx 1.18.0,
  protobuf 4.25.3): σ 0.53 → band ±2.1 °C, 0 training samples flagged, 33 °C
  flagged; ONNX `score_samples` matches the closed-form log-likelihood under
  onnxruntime. IsolationForest / OneClassSVM rejected (saturation / quantized
  data).
- `GgEdgeLoop` 1.1.0, `ZoneAnomaly` 1.0.0, and the Lambda handler unit-tested
  with fake IPC / boto3 clients.
- NUC6CAY (Celeron J3455, SSE4.2, **no AVX**, Ubuntu 24.04.5, Python 3.12.3):
  `python3.12-venv` was not preinstalled (installed via `apt-get install
  python3-venv`). The recipe's pins `onnxruntime==1.31.0 numpy==2.2.6
  awsiotsdk==1.31.0` install from wheels in about 30 s. `infer.ZoneModels`
  loads the per-zone ONNX from `train.py` and scores correctly (mean → not
  anomalous; ±2.5 °C → anomalous); 1000 scores in 0.09 s.


### Deploy from the cloud (`deploy-cloud.mdx`) — evidence **2026-10-10**

- Artifact bucket `gg-edge-wt-dev-gg-artifacts-<account>` created; TES inline
  policy `…-gg-artifacts-s3` attached.
- `com.example.GgEdgeLoop` **1.1.0** `create-component-version` → `DEPLOYABLE`
  in seconds; artifact at
  `s3://…/artifacts/com.example.GgEdgeLoop/1.1.0/loop.py`.
- Local `greengrass-cli --remove com.example.GgEdgeLoop` required before cloud
  deploy (otherwise conflict).
- Public versions resolved: Cli **2.18.3**, LogManager **2.3.14**.
- Thing-group deployment `gg-edge-greenhouse` → `SUCCEEDED` (~30–45 s).
- NUC: GgEdgeLoop **1.1.0** RUNNING (cloud artifact path under
  `/greengrass/v2/packages/artifacts/…`); LogManager **2.3.14** RUNNING;
  Bridge routes include `TelemetryLocalToIotCore`, `ActuatorPubsubToIotCore`,
  `CommandIotCoreToPubsub`. Bridge `configurationUpdate` must
  `reset: ["/mqttTopicMapping"]` or prior `ActuatorLocalToIotCore` lingers.
- CloudWatch log groups created:
  `/aws/greengrass/UserComponent/ap-southeast-2/com.example.GgEdgeLoop` and
  `/aws/greengrass/GreengrassSystemComponent/ap-southeast-2/System`. First
  upload within one `periodicUploadIntervalSec` (60).

### Archive telemetry (`archive.mdx`) — evidence **2026-10-10**

- Data bucket `gg-edge-wt-dev-gg-data-<account>` created; lifecycle
  `expire-telemetry-30d` on `telemetry/` (CLI may print
  `TransitionDefaultMinimumObjectSize`).
- IAM role `gg-edge-wt-dev-iot-rules` + inline `iot-rule-s3`
  (`s3:PutObject` on `telemetry/*`). Fresh role: `create-topic-rule` can fail
  with unable-to-assume for a few seconds — retry.
- Rule `gg_edge_wt_dev_telemetry_s3` → objects
  `telemetry/thing=<thing>/dt=<UTC-date>/<ts>.json` (~104 B). `dt=` is UTC
  (`parse_time` on rule `timestamp()`), not local wall clock.
- Sample body:
  `{"thing":"gg-edge-wt-dev-esp32-1","tempC":29.9,"rssi":-28,"uptimeS":6653,"rgb":"off","ts":1791585400137}`.
- Both zones writing within ~60 s of rule create (~8 objects each after ~70 s).

### Zone state (`zone-state.mdx`) — evidence **2026-10-10**

- Table `gg-edge-wt-dev-zone-state` PAY_PER_REQUEST, keys `thing` (HASH) +
  `kind` (RANGE). Inline policy `iot-rule-dynamodb` on
  `gg-edge-wt-dev-iot-rules`.
- Rules `gg_edge_wt_dev_telemetry_ddb` and `gg_edge_wt_dev_actuator_ddb`.
- Telemetry items within ~15–20 s: esp32-1 `tempC` 29.9 / esp32-2 26.5
  (rssi ~−28, `rgb` off). Values drift with uptime.
- Actuator after BOOT press/release on esp32-1:
  `state=off`, `color=green`, `source=com.example.GgEdgeLoop` — proves
  `ActuatorPubsubToIotCore` + dynamoDBv2 path.
- Session vars must set
  `ZONE_TABLE=${PROJECT_NAME}-${ENVIRONMENT}-zone-state` (example file;
  page default if unset).

### Raise an alarm (`alarm.mdx`) — evidence **2026-10-10**

- Inline `iot-rule-cloudwatch` on `gg-edge-wt-dev-iot-rules`; rule
  `gg_edge_wt_dev_telemetry_cw` → namespace `GgEdge/Greenhouse`, metric
  `ChipTempC-<thing>`. Datapoints within ~3 min (esp32-1 ~29.9 °C).
- SNS topic `gg-edge-wt-dev-zone-alarms`. Email subscribe skipped when
  `ALERT_EMAIL` is still `you@example.com` — operator must set a real inbox
  and confirm.
- Alarms `…-hot-gg-edge-wt-dev-esp32-{1,2}` at baseline+2 °C (31.9 / 29.5).
  Both reached `OK`. `set-alarm-state` → ALARM history entry proven.

### Cloud commands (`command.mdx`) — evidence **2026-10-10**

- Rule `gg_edge_wt_dev_ack_ddb`. Manual `iot-data publish` →
  DynamoDB `kind=cloud-ack` (`state=on`, `color=blue`, `reason=manual test`)
  and `kind=actuator` (`source=cloud`).
- Lambda `gg-edge-wt-dev-alarm-to-command` runtime **python3.14**, env
  `IOT_DATA_ENDPOINT`. SNS lambda subscription on `…-zone-alarms`.
- `set-alarm-state` ALARM → Lambda publishes command → actuator
  `reason: … ALARM`; later OK → `state=off` / `reason: … OK` in logs and DDB
  within ~1 min.

### Edge inference (`inference.mdx`) — evidence **2026-10-10**

- Account had **0** quota for `ml.m5.large for training job usage` (and spot).
  `create-training-job` → `ResourceLimitExceeded`. Quota increase requested
  (`L-611FA074` → 2, PENDING).
- Local fallback: `train.py` on Python **3.12** with lake sync →
  `zone-anomaly-local-20261009231335`; esp32-1 mean 30.00 σ 0.43 / esp32-2
  mean 27.15 σ 0.58; `model.tar.gz` uploaded under `ml/output/…/output/`.
- Component `com.example.ZoneAnomaly` **1.0.0** DEPLOYABLE; Thing-group deploy
  `SUCCEEDED`; component **RUNNING** with GgEdgeLoop 1.1.0.
- Rule `gg_edge_wt_dev_inference_ddb`. Normal score e.g. tempC 30.9
  score −2.26 anomaly false. Injected 36.5 °C → score −112.84 anomaly true;
  actuator `color=red` `source=com.example.ZoneAnomaly`.

### Teardown (`teardown.mdx`) — evidence **2026-10-10**

- Deleted: CW alarms, SNS topic, Lambda + role + log group, all six
  `gg_edge_wt_dev_*` rules, IoT rule role, DynamoDB `zone-state`, SageMaker
  training role, data + artifact S3 buckets, private components, TES
  artifacts-s3 policy, Greengrass log groups, certs (core + 2 clients), Things
  + group, role alias, IoT policies, TES role, service role
  (`disassociate-service-role-from-account`).
- Empty Thing-group deploy `gg-edge-empty` → `SUCCEEDED` before
  `delete-component`.
- Post-check: no `gg-edge-wt` Things/rules/buckets/roles/Lambda/SNS/alarms;
  `list-core-devices` empty for this lab.
- Nucleus `systemctl stop/disable` not run remotely (SSH key denied) — operator
  must stop on the NUC.

## Unverified / TODO evidence

- SageMaker scikit-learn container installing `requirements.txt` end-to-end
  once training quota is approved.
- Approximate monthly cost at idle for one core + clients (date-stamped).
