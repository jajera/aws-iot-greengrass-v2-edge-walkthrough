"""CloudWatch alarm (via SNS) -> cloud command to the zone on the Greengrass core.

ALARM -> {"state": "on",  "color": "blue"} on gg-edge/cloud/command/<thing>
OK    -> {"state": "off", "color": "blue"}
The thing name comes from the alarm metric name ChipTempC-<thing>.
"""

import json
import os

import boto3

METRIC_PREFIX = "ChipTempC-"
iot_data = boto3.client(
    "iot-data", endpoint_url=f"https://{os.environ['IOT_DATA_ENDPOINT']}"
)


def lambda_handler(event, context):
    published = []
    for record in event.get("Records", []):
        alarm = json.loads(record["Sns"]["Message"])
        metric = alarm.get("Trigger", {}).get("MetricName", "")
        new_state = alarm.get("NewStateValue")
        if not metric.startswith(METRIC_PREFIX) or new_state not in ("ALARM", "OK"):
            print(f"ignore {alarm.get('AlarmName')} metric={metric} state={new_state}")
            continue
        thing = metric[len(METRIC_PREFIX):]
        command = {
            "state": "on" if new_state == "ALARM" else "off",
            "color": "blue",
            "reason": f"{alarm.get('AlarmName')} {new_state}",
        }
        topic = f"gg-edge/cloud/command/{thing}"
        iot_data.publish(topic=topic, qos=1, payload=json.dumps(command).encode())
        print(f"published {topic}: {json.dumps(command)}")
        published.append(topic)
    return {"published": published}
