#!/usr/bin/env python3
"""SageMaker training entry point (scikit-learn container, script mode).

Input channel "train" = the S3 telemetry archive written by the IoT rule
(one JSON object per message under telemetry/thing=<thing>/dt=<date>/).
Output = /opt/ml/model/{manifest.json,<thing>.onnx} -> model.tar.gz in S3.

Model per zone: a one-component GaussianMixture (Gaussian density) over
tempC, exported to ONNX with log-likelihood output. A reading is anomalous
when its log-likelihood is below the density at k standard deviations, so
the score keeps falling the further a zone drifts from what it learned.
The ESP32-S3 sensor reports in coarse steps; reg_covar floors the variance
so a very steady zone does not alarm on one quantization step.

Runs locally too:
  SM_CHANNEL_TRAIN=./sample SM_MODEL_DIR=./out python train.py
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from collections import defaultdict

import numpy as np
from sklearn.mixture import GaussianMixture
from skl2onnx import to_onnx

FEATURES = ["tempC"]


def load_samples(root: str, min_uptime_s: int) -> dict[str, list[list[float]]]:
    zones: dict[str, list[list[float]]] = defaultdict(list)
    skipped = 0
    for dirpath, _, files in os.walk(root):
        for name in files:
            try:
                with open(os.path.join(dirpath, name), encoding="utf-8") as f:
                    msg = json.load(f)
                if int(msg.get("uptimeS", 0)) < min_uptime_s:
                    skipped += 1
                    continue
                zones[msg["thing"]].append([float(msg[k]) for k in FEATURES])
            except (OSError, ValueError, KeyError, TypeError):
                skipped += 1
    print(f"loaded {sum(len(v) for v in zones.values())} samples "
          f"from {len(zones)} zones; skipped {skipped}")
    return zones


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-samples", type=int, default=120)
    parser.add_argument("--min-uptime-s", type=int, default=300)
    parser.add_argument("--k-sigma", type=float, default=4.0)
    parser.add_argument("--reg-covar", type=float, default=0.1)
    parser.add_argument("--train", default=os.environ.get("SM_CHANNEL_TRAIN", "/opt/ml/input/data/train"))
    parser.add_argument("--model-dir", default=os.environ.get("SM_MODEL_DIR", "/opt/ml/model"))
    args = parser.parse_args()

    zones = load_samples(args.train, args.min_uptime_s)
    os.makedirs(args.model_dir, exist_ok=True)
    manifest = {
        "features": FEATURES,
        "algorithm": "GaussianMixture(n_components=1) log-likelihood",
        "scoreOutput": "score_samples",
        "kSigma": args.k_sigma,
        "minUptimeS": args.min_uptime_s,
        "trainingJob": os.environ.get("TRAINING_JOB_NAME", "local"),
        "trainedAt": int(time.time()),
        "zones": {},
    }
    for thing, rows in sorted(zones.items()):
        if len(rows) < args.min_samples:
            print(f"skip {thing}: {len(rows)} samples < {args.min_samples}")
            continue
        x = np.asarray(rows, dtype=np.float32)
        model = GaussianMixture(
            n_components=1, covariance_type="full",
            reg_covar=args.reg_covar, random_state=42,
        ).fit(x)
        variance = float(model.covariances_[0][0][0])
        sigma = math.sqrt(variance)
        threshold = -0.5 * math.log(2 * math.pi * variance) - 0.5 * args.k_sigma ** 2
        onx = to_onnx(
            model, x[:1],
            options={id(model): {"score_samples": True}},
            target_opset={"": 17, "ai.onnx.ml": 3},
        )
        filename = f"{thing}.onnx"
        with open(os.path.join(args.model_dir, filename), "wb") as f:
            f.write(onx.SerializeToString())
        flagged = int((model.score_samples(x) < threshold).sum())
        manifest["zones"][thing] = {
            "model": filename,
            "samples": len(rows),
            "meanTempC": float(model.means_[0][0]),
            "sigmaTempC": sigma,
            "medianTempC": float(np.median(x[:, 0])),
            "threshold": threshold,
            "trainFlagged": flagged,
        }
        print(f"trained {thing}: samples={len(rows)} mean={model.means_[0][0]:.2f} "
              f"sigma={sigma:.2f} alarm beyond ±{args.k_sigma * sigma:.2f} C "
              f"threshold={threshold:.3f} flagged={flagged}")

    if not manifest["zones"]:
        raise SystemExit("no zone had enough samples; collect more telemetry first")
    with open(os.path.join(args.model_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
