#!/usr/bin/env python3
"""Score zone telemetry on the core with the SageMaker-trained ONNX models.

gg-edge/telemetry/<thing> -> onnxruntime (per-zone Gaussian density,
                             log-likelihood vs the k-sigma threshold)
  -> gg-edge/inference/<thing>   every scored sample (bridged to IoT Core)
  -> gg-edge/actuator/<thing>    red on / off when the anomaly state changes
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import queue
import sys
import threading
import time
import traceback

import numpy as np
import onnxruntime as ort

import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    BinaryMessage,
    PublishMessage,
    PublishToTopicRequest,
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
)

TELEMETRY_FILTER = "gg-edge/telemetry/+"
INFERENCE_PREFIX = "gg-edge/inference"
ACTUATOR_PREFIX = "gg-edge/actuator"
SOURCE = "com.example.ZoneAnomaly"
TIMEOUT = 10

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
log = logging.getLogger("ZoneAnomaly")


class ZoneModels:
    def __init__(self, model_dir: str):
        with open(os.path.join(model_dir, "manifest.json"), encoding="utf-8") as f:
            self.manifest = json.load(f)
        self.features = self.manifest["features"]
        self.score_output = self.manifest["scoreOutput"]
        self.min_uptime_s = int(self.manifest.get("minUptimeS", 0))
        self.zones = self.manifest["zones"]
        self.sessions: dict[str, ort.InferenceSession] = {}
        for thing, zone in self.zones.items():
            path = os.path.join(model_dir, zone["model"])
            self.sessions[thing] = ort.InferenceSession(
                path, providers=["CPUExecutionProvider"]
            )
            log.info(
                "loaded %s for %s: %s samples, mean %.2f C, sigma %.2f C, threshold %.3f",
                zone["model"], thing, zone["samples"], zone["meanTempC"],
                zone["sigmaTempC"], zone["threshold"],
            )

    def score(self, thing: str, payload: dict) -> tuple[bool, float] | None:
        session = self.sessions.get(thing)
        if session is None:
            return None
        x = np.array([[float(payload[k]) for k in self.features]], dtype=np.float32)
        (score,) = session.run([self.score_output], {session.get_inputs()[0].name: x})
        value = float(np.ravel(score)[0])
        return value < self.zones[thing]["threshold"], value


class Handler:
    def __init__(self, out_q: queue.Queue):
        self.out_q = out_q

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:
            msg = event.binary_message
            self.out_q.put((msg.context.topic, json.loads(msg.message.decode())))
        except Exception:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        log.error("telemetry stream error: %s", error)
        return False

    def on_stream_closed(self) -> None:
        log.warning("telemetry subscription closed")


def publish(ipc_client, topic: str, body: dict) -> None:
    request = PublishToTopicRequest()
    request.topic = topic
    request.publish_message = PublishMessage()
    request.publish_message.binary_message = BinaryMessage()
    request.publish_message.binary_message.message = json.dumps(body).encode()
    op = ipc_client.new_publish_to_topic()
    op.activate(request)
    op.get_response().result(TIMEOUT)


class Debounce:
    """Flip state only after N consecutive samples agree."""

    def __init__(self, n: int):
        self.n = n
        self.state: dict[str, bool] = {}
        self.streak: dict[str, int] = {}

    def update(self, thing: str, anomaly: bool) -> bool | None:
        current = self.state.get(thing, False)
        if anomaly == current:
            self.streak[thing] = 0
            return None
        self.streak[thing] = self.streak.get(thing, 0) + 1
        if self.streak[thing] < self.n:
            return None
        self.state[thing] = anomaly
        self.streak[thing] = 0
        return anomaly


def handle(ipc_client, models: ZoneModels, debounce: Debounce, topic: str, payload: dict) -> None:
    thing = topic.rsplit("/", 1)[-1]
    if int(payload.get("uptimeS", 0)) < models.min_uptime_s:
        return
    result = models.score(thing, payload)
    if result is None:
        log.warning("no model for %s; retrain with its telemetry", thing)
        return
    anomaly, score = result
    publish(ipc_client, f"{INFERENCE_PREFIX}/{thing}", {
        "thing": thing,
        "tempC": payload.get("tempC"),
        "score": round(score, 4),
        "anomaly": anomaly,
        "model": models.manifest.get("trainingJob", ""),
        "ts": int(time.time() * 1000),
    })
    log.info("scored %s tempC=%s score=%.4f anomaly=%s", thing, payload.get("tempC"), score, anomaly)
    changed = debounce.update(thing, anomaly)
    if changed is None:
        return
    command = {
        "state": "on" if changed else "off",
        "color": "red",
        "source": SOURCE,
        "target": thing,
        "reason": f"anomaly score {score:.4f} at tempC {payload.get('tempC')}",
    }
    publish(ipc_client, f"{ACTUATOR_PREFIX}/{thing}", command)
    log.info("published actuator command on %s/%s: %s", ACTUATOR_PREFIX, thing, command)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--consecutive", type=int, default=2)
    args = parser.parse_args()

    models = ZoneModels(args.model_dir)
    debounce = Debounce(args.consecutive)
    ipc_client = awsiot.greengrasscoreipc.connect()
    out_q: queue.Queue = queue.Queue()

    def worker() -> None:
        while True:
            topic, payload = out_q.get()
            try:
                handle(ipc_client, models, debounce, topic, payload)
            except Exception:
                traceback.print_exc()

    threading.Thread(target=worker, daemon=True).start()
    request = SubscribeToTopicRequest()
    request.topic = TELEMETRY_FILTER
    op = ipc_client.new_subscribe_to_topic(Handler(out_q))
    op.activate(request)
    op.get_response().result(TIMEOUT)
    log.info("subscribed to %s; zones %s", TELEMETRY_FILTER, sorted(models.sessions))
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
