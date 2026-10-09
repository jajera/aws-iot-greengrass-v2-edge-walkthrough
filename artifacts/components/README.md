# Custom components

```text
artifacts/components/
  recipes/                 # YAML recipes (ARTIFACT_BUCKET placeholder in S3 URIs)
  artifacts/
    com.example.GgEdgeLoop/1.0.1/loop.py      # local deploy (Loop component)
    com.example.GgEdgeLoop/1.1.0/loop.py      # cloud deploy + cloud commands
    com.example.ZoneAnomaly/1.0.0/infer.py    # ONNX inference (Edge inference)
```

- **GgEdgeLoop 1.0.1** — button → green RGB via IPC pubsub, deployed locally with
  `greengrass-cli`.
- **GgEdgeLoop 1.1.0** — same loop plus `gg-edge/cloud/command/+` → RGB (blue by
  default) and an ack on `gg-edge/cloud/ack/<thing>`. Registered from S3 and
  deployed to the Thing group (`deploy-cloud` page).
- **ZoneAnomaly 1.0.0** — scores `gg-edge/telemetry/+` with per-zone ONNX models
  trained in SageMaker (`artifacts/ml/zone-anomaly/`). Publishes
  `gg-edge/inference/<thing>` and drives the RGB red on anomaly (`inference` page).

Replace `ARTIFACT_BUCKET` in recipe `URI` fields before `create-component-version`.
