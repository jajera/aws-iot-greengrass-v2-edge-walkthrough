#!/usr/bin/env python3
"""Closed-loop: sensor pubsub -> per-thing actuator command on the core."""

from __future__ import annotations

import json
import logging
import queue
import sys
import threading
import time
import traceback

import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    SubscriptionResponseMessage,
    PublishToTopicRequest,
    PublishMessage,
    BinaryMessage,
    SubscribeToTopicRequest,
)

SENSOR_TOPIC = "gg-edge/sensor"
ACTUATOR_PREFIX = "gg-edge/actuator"

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
log = logging.getLogger("GgEdgeLoop")

TIMEOUT = 10


class SensorHandler:
    """Receive sensor events; enqueue work (do not publish on this thread)."""

    def __init__(self, out_q: queue.Queue):
        self.out_q = out_q

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:
            message = event.binary_message.message.decode("utf-8")
            log.info("sensor event: %s", message)
            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                payload = {"raw": message}
            self.out_q.put(payload)
        except Exception:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        log.error("stream error: %s", error)
        return False

    def on_stream_closed(self) -> None:
        log.warning("sensor subscription closed")


def publish_actuator(ipc_client, payload: dict) -> None:
    thing = payload.get("thing")
    if not thing or not isinstance(thing, str):
        log.warning("skip actuator: sensor payload missing thing: %s", payload)
        return

    command = {
        "state": "on" if payload.get("event") != "release" else "off",
        "source": "com.example.GgEdgeLoop",
        "target": thing,
        "echo": payload,
    }
    topic = f"{ACTUATOR_PREFIX}/{thing}"
    body = json.dumps(command).encode("utf-8")
    request = PublishToTopicRequest()
    request.topic = topic
    request.publish_message = PublishMessage()
    request.publish_message.binary_message = BinaryMessage()
    request.publish_message.binary_message.message = body
    op = ipc_client.new_publish_to_topic()
    op.activate(request)
    op.get_response().result(TIMEOUT)
    log.info("published actuator command on %s: %s", topic, command)


def publisher_loop(ipc_client, out_q: queue.Queue) -> None:
    while True:
        payload = out_q.get()
        try:
            publish_actuator(ipc_client, payload)
        except Exception:
            traceback.print_exc()


def main() -> None:
    ipc_client = awsiot.greengrasscoreipc.connect()
    out_q: queue.Queue = queue.Queue()
    threading.Thread(
        target=publisher_loop, args=(ipc_client, out_q), daemon=True
    ).start()

    request = SubscribeToTopicRequest()
    request.topic = SENSOR_TOPIC
    handler = SensorHandler(out_q)
    operation = ipc_client.new_subscribe_to_topic(handler)
    operation.activate(request)
    operation.get_response().result(TIMEOUT)
    log.info(
        "subscribed to %s; publishing on %s/<thing>",
        SENSOR_TOPIC,
        ACTUATOR_PREFIX,
    )
    while True:
        time.sleep(10)


if __name__ == "__main__":
    main()
