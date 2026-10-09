#!/usr/bin/env python3
"""Greenhouse zone loop on the core.

Local:  gg-edge/sensor (button)          -> gg-edge/actuator/<thing> (green)
Cloud:  gg-edge/cloud/command/<thing>    -> gg-edge/actuator/<thing> (blue)
                                         -> gg-edge/cloud/ack/<thing>

The MQTT bridge carries cloud/command from IoT Core into Pubsub and carries
cloud/ack back to IoT Core, so the cloud sees that the edge acted.
"""

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
    BinaryMessage,
    PublishMessage,
    PublishToTopicRequest,
    SubscribeToTopicRequest,
    SubscriptionResponseMessage,
)

SENSOR_TOPIC = "gg-edge/sensor"
ACTUATOR_PREFIX = "gg-edge/actuator"
COMMAND_FILTER = "gg-edge/cloud/command/+"
COMMAND_PREFIX = "gg-edge/cloud/command/"
ACK_PREFIX = "gg-edge/cloud/ack"
SOURCE = "com.example.GgEdgeLoop"
TIMEOUT = 10

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
log = logging.getLogger("GgEdgeLoop")


class Handler:
    """Enqueue (kind, topic, payload); never publish on the IPC callback thread."""

    def __init__(self, kind: str, out_q: queue.Queue):
        self.kind = kind
        self.out_q = out_q

    def on_stream_event(self, event: SubscriptionResponseMessage) -> None:
        try:
            msg = event.binary_message
            topic = msg.context.topic if msg.context else ""
            text = msg.message.decode("utf-8")
            log.info("%s event on %s: %s", self.kind, topic, text)
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                payload = {"raw": text}
            self.out_q.put((self.kind, topic, payload))
        except Exception:
            traceback.print_exc()

    def on_stream_error(self, error: Exception) -> bool:
        log.error("%s stream error: %s", self.kind, error)
        return False

    def on_stream_closed(self) -> None:
        log.warning("%s subscription closed", self.kind)


def publish(ipc_client, topic: str, body: dict) -> None:
    request = PublishToTopicRequest()
    request.topic = topic
    request.publish_message = PublishMessage()
    request.publish_message.binary_message = BinaryMessage()
    request.publish_message.binary_message.message = json.dumps(body).encode()
    op = ipc_client.new_publish_to_topic()
    op.activate(request)
    op.get_response().result(TIMEOUT)


def on_sensor(ipc_client, payload: dict) -> None:
    thing = payload.get("thing")
    if not isinstance(thing, str) or not thing:
        log.warning("skip actuator: sensor payload missing thing: %s", payload)
        return
    command = {
        "state": "off" if payload.get("event") == "release" else "on",
        "color": "green",
        "source": SOURCE,
        "target": thing,
        "echo": payload,
    }
    topic = f"{ACTUATOR_PREFIX}/{thing}"
    publish(ipc_client, topic, command)
    log.info("published actuator command on %s: %s", topic, command)


def on_cloud_command(ipc_client, topic: str, payload: dict) -> None:
    thing = topic[len(COMMAND_PREFIX):] if topic.startswith(COMMAND_PREFIX) else ""
    if not thing or "/" in thing:
        log.warning("skip cloud command: bad topic %s", topic)
        return
    state = payload.get("state")
    if state not in ("on", "off"):
        log.warning("skip cloud command: state must be on|off: %s", payload)
        return
    command = {
        "state": state,
        "color": payload.get("color", "blue"),
        "source": "cloud",
        "target": thing,
        "reason": payload.get("reason", ""),
    }
    actuator_topic = f"{ACTUATOR_PREFIX}/{thing}"
    publish(ipc_client, actuator_topic, command)
    log.info("cloud command -> %s: %s", actuator_topic, command)
    ack = {
        "thing": thing,
        "applied": command,
        "core": SOURCE,
        "ts": int(time.time() * 1000),
    }
    ack_topic = f"{ACK_PREFIX}/{thing}"
    publish(ipc_client, ack_topic, ack)
    log.info("ack -> %s", ack_topic)


def worker(ipc_client, out_q: queue.Queue) -> None:
    while True:
        kind, topic, payload = out_q.get()
        try:
            if kind == "sensor":
                on_sensor(ipc_client, payload)
            elif kind == "command":
                on_cloud_command(ipc_client, topic, payload)
        except Exception:
            traceback.print_exc()


def subscribe(ipc_client, topic: str, handler: Handler):
    request = SubscribeToTopicRequest()
    request.topic = topic
    op = ipc_client.new_subscribe_to_topic(handler)
    op.activate(request)
    op.get_response().result(TIMEOUT)
    log.info("subscribed to %s", topic)
    return op


def main() -> None:
    ipc_client = awsiot.greengrasscoreipc.connect()
    out_q: queue.Queue = queue.Queue()
    threading.Thread(target=worker, args=(ipc_client, out_q), daemon=True).start()
    ops = [
        subscribe(ipc_client, SENSOR_TOPIC, Handler("sensor", out_q)),
        subscribe(ipc_client, COMMAND_FILTER, Handler("command", out_q)),
    ]
    log.info("publishing on %s/<thing> and %s/<thing>", ACTUATOR_PREFIX, ACK_PREFIX)
    while ops:
        time.sleep(10)


if __name__ == "__main__":
    main()
