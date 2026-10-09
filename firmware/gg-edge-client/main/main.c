/* Greengrass V2 client device: discover core, MQTT to Moquette, sense→actuate. */
#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "esp_http_client.h"
#include "nvs_flash.h"
#include "driver/gpio.h"
#include "driver/temperature_sensor.h"
#include "esp_timer.h"
#include "led_strip.h"
#include "mqtt_client.h"
#include "cJSON.h"

static const char *TAG = "gg-edge";

/* Dim levels — WS2812 on DevKitC-1 is bright at full scale. */
#define RGB_LEVEL 40

static led_strip_handle_t s_led;
static temperature_sensor_handle_t s_tsens;
static char s_rgb_state[16] = "off";

static void rgb_color(uint8_t r, uint8_t g, uint8_t b)
{
    if (!s_led) {
        return;
    }
    ESP_ERROR_CHECK(led_strip_set_pixel(s_led, 0, r, g, b));
    ESP_ERROR_CHECK(led_strip_refresh(s_led));
}

extern const uint8_t device_pem_crt_start[] asm("_binary_device_pem_crt_start");
extern const uint8_t device_pem_crt_end[] asm("_binary_device_pem_crt_end");
extern const uint8_t private_pem_key_start[] asm("_binary_private_pem_key_start");
extern const uint8_t private_pem_key_end[] asm("_binary_private_pem_key_end");
extern const uint8_t AmazonRootCA1_pem_start[] asm("_binary_AmazonRootCA1_pem_start");
extern const uint8_t AmazonRootCA1_pem_end[] asm("_binary_AmazonRootCA1_pem_end");

#define WIFI_CONNECTED_BIT BIT0
static EventGroupHandle_t s_wifi_events;
static esp_mqtt_client_handle_t s_mqtt;
static char s_core_host[128];
static int s_core_port = 8883;
static char *s_core_ca_pem;

static void wifi_event_handler(void *arg, esp_event_base_t base, int32_t id, void *data)
{
    if (base == WIFI_EVENT && id == WIFI_EVENT_STA_START) {
        esp_wifi_connect();
    } else if (base == WIFI_EVENT && id == WIFI_EVENT_STA_DISCONNECTED) {
        esp_wifi_connect();
    } else if (base == IP_EVENT && id == IP_EVENT_STA_GOT_IP) {
        xEventGroupSetBits(s_wifi_events, WIFI_CONNECTED_BIT);
    }
}

static void wifi_init(void)
{
    s_wifi_events = xEventGroupCreate();
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());
    esp_netif_create_default_wifi_sta();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    ESP_ERROR_CHECK(esp_wifi_init(&cfg));
    ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &wifi_event_handler, NULL));
    ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &wifi_event_handler, NULL));
    wifi_config_t wifi_config = {0};
    strncpy((char *)wifi_config.sta.ssid, CONFIG_ESP_WIFI_SSID, sizeof(wifi_config.sta.ssid));
    strncpy((char *)wifi_config.sta.password, CONFIG_ESP_WIFI_PASSWORD, sizeof(wifi_config.sta.password));
    ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
    ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
    ESP_ERROR_CHECK(esp_wifi_start());
    xEventGroupWaitBits(s_wifi_events, WIFI_CONNECTED_BIT, false, true, portMAX_DELAY);
    ESP_LOGI(TAG, "wifi connected");
}

typedef struct {
    char *buf;
    int len;
} http_buf_t;

static esp_err_t discover_http_handler(esp_http_client_event_t *evt)
{
    http_buf_t *hb = evt->user_data;
    if (evt->event_id == HTTP_EVENT_ON_DATA) {
        hb->buf = realloc(hb->buf, hb->len + evt->data_len + 1);
        if (!hb->buf) {
            return ESP_FAIL;
        }
        memcpy(hb->buf + hb->len, evt->data, evt->data_len);
        hb->len += evt->data_len;
        hb->buf[hb->len] = 0;
    }
    return ESP_OK;
}

static bool parse_discovery(const char *json)
{
    cJSON *root = cJSON_Parse(json);
    if (!root) {
        return false;
    }
    cJSON *groups = cJSON_GetObjectItem(root, "GGGroups");
    if (!cJSON_IsArray(groups) || cJSON_GetArraySize(groups) < 1) {
        cJSON_Delete(root);
        return false;
    }
    cJSON *g0 = cJSON_GetArrayItem(groups, 0);
    cJSON *cas = cJSON_GetObjectItem(g0, "CAs");
    if (cJSON_IsArray(cas) && cJSON_GetArraySize(cas) > 0) {
        const char *ca = cJSON_GetArrayItem(cas, 0)->valuestring;
        free(s_core_ca_pem);
        s_core_ca_pem = strdup(ca);
    }
    cJSON *cores = cJSON_GetObjectItem(g0, "Cores");
    if (!cJSON_IsArray(cores) || cJSON_GetArraySize(cores) < 1) {
        cJSON_Delete(root);
        return false;
    }
    cJSON *c0 = cJSON_GetArrayItem(cores, 0);
    cJSON *connectivity = cJSON_GetObjectItem(c0, "Connectivity");
    if (!cJSON_IsArray(connectivity) || cJSON_GetArraySize(connectivity) < 1) {
        cJSON_Delete(root);
        return false;
    }
    cJSON *ep = cJSON_GetArrayItem(connectivity, 0);
    const char *host = cJSON_GetObjectItem(ep, "HostAddress")->valuestring;
    int port = cJSON_GetObjectItem(ep, "PortNumber")->valueint;
    strncpy(s_core_host, host, sizeof(s_core_host) - 1);
    s_core_port = port;
    ESP_LOGI(TAG, "discovered core %s:%d", s_core_host, s_core_port);
    cJSON_Delete(root);
    return s_core_ca_pem != NULL;
}

static bool greengrass_discover(void)
{
    char url[256];
    snprintf(url, sizeof(url),
             "https://greengrass-ats.iot.%s.amazonaws.com:8443/greengrass/discover/thing/%s",
             CONFIG_GG_REGION, CONFIG_GG_THING_NAME);

    http_buf_t hb = {0};
    esp_http_client_config_t cfg = {
        .url = url,
        .method = HTTP_METHOD_GET,
        .cert_pem = (const char *)AmazonRootCA1_pem_start,
        .client_cert_pem = (const char *)device_pem_crt_start,
        .client_key_pem = (const char *)private_pem_key_start,
        .event_handler = discover_http_handler,
        .user_data = &hb,
        .timeout_ms = 15000,
    };
    esp_http_client_handle_t client = esp_http_client_init(&cfg);
    esp_err_t err = esp_http_client_perform(client);
    int status = esp_http_client_get_status_code(client);
    esp_http_client_cleanup(client);
    if (err != ESP_OK || status != 200 || !hb.buf) {
        ESP_LOGE(TAG, "discover failed err=%s status=%d", esp_err_to_name(err), status);
        free(hb.buf);
        return false;
    }
    ESP_LOGI(TAG, "discover response: %s", hb.buf);
    bool ok = parse_discovery(hb.buf);
    free(hb.buf);
    return ok;
}

/* Actuator color tells you which layer acted: green = local button loop,
 * blue = cloud command, red = edge ML anomaly. Unknown or missing → green. */
static void rgb_set(bool on, const char *color)
{
    if (!on) {
        rgb_color(0, 0, 0);
        if (s_led) {
            ESP_ERROR_CHECK(led_strip_clear(s_led));
        }
        strlcpy(s_rgb_state, "off", sizeof(s_rgb_state));
        ESP_LOGI(TAG, "RGB -> off");
        return;
    }
    if (color && strcmp(color, "blue") == 0) {
        rgb_color(0, 0, RGB_LEVEL);
    } else if (color && strcmp(color, "red") == 0) {
        rgb_color(RGB_LEVEL, 0, 0);
    } else {
        color = "green";
        rgb_color(0, RGB_LEVEL, 0);
    }
    strlcpy(s_rgb_state, color, sizeof(s_rgb_state));
    ESP_LOGI(TAG, "RGB -> %s (on)", color);
}

static void rgb_init(void)
{
    led_strip_config_t strip_config = {
        .strip_gpio_num = CONFIG_GG_RGB_GPIO,
        .max_leds = 1,
        .led_model = LED_MODEL_WS2812,
    };
    led_strip_rmt_config_t rmt_config = {
        .resolution_hz = 10 * 1000 * 1000,
        .flags.with_dma = false,
    };
    ESP_ERROR_CHECK(led_strip_new_rmt_device(&strip_config, &rmt_config, &s_led));
    ESP_LOGI(TAG, "RGB strip on GPIO %d — boot blink", CONFIG_GG_RGB_GPIO);
    /* Self-test so wrong pin is obvious before MQTT. */
    rgb_color(RGB_LEVEL, 0, 0);
    vTaskDelay(pdMS_TO_TICKS(250));
    rgb_color(0, RGB_LEVEL, 0);
    vTaskDelay(pdMS_TO_TICKS(250));
    rgb_color(0, 0, RGB_LEVEL);
    vTaskDelay(pdMS_TO_TICKS(250));
    rgb_set(false, NULL);
}

static void tsens_init(void)
{
    temperature_sensor_config_t cfg = TEMPERATURE_SENSOR_CONFIG_DEFAULT(-10, 80);
    ESP_ERROR_CHECK(temperature_sensor_install(&cfg, &s_tsens));
    ESP_ERROR_CHECK(temperature_sensor_enable(s_tsens));
    float c = 0;
    ESP_ERROR_CHECK(temperature_sensor_get_celsius(s_tsens, &c));
    ESP_LOGI(TAG, "chip temperature sensor ready: %.1f C", c);
}

static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    esp_mqtt_event_handle_t event = event_data;
    switch ((esp_mqtt_event_id_t)event_id) {
    case MQTT_EVENT_CONNECTED: {
        char actuator_topic[160];
        snprintf(actuator_topic, sizeof(actuator_topic),
                 "gg-edge/actuator/%s", CONFIG_GG_THING_NAME);
        ESP_LOGI(TAG, "mqtt connected to core");
        esp_mqtt_client_subscribe(s_mqtt, actuator_topic, 1);
        ESP_LOGI(TAG, "subscribed %s", actuator_topic);
        break;
    }
    case MQTT_EVENT_DATA: {
        char topic[64] = {0};
        char data[256] = {0};
        memcpy(topic, event->topic, event->topic_len < 63 ? event->topic_len : 63);
        memcpy(data, event->data, event->data_len < 255 ? event->data_len : 255);
        ESP_LOGI(TAG, "actuator msg on %s: %s", topic, data);
        cJSON *root = cJSON_Parse(data);
        if (root) {
            cJSON *state = cJSON_GetObjectItem(root, "state");
            cJSON *color = cJSON_GetObjectItem(root, "color");
            if (cJSON_IsString(state)) {
                rgb_set(strcmp(state->valuestring, "on") == 0,
                        cJSON_IsString(color) ? color->valuestring : NULL);
            }
            cJSON_Delete(root);
        }
        break;
    }
    default:
        break;
    }
}

static void mqtt_start(void)
{
    char uri[160];
    snprintf(uri, sizeof(uri), "mqtts://%s:%d", s_core_host, s_core_port);
    esp_mqtt_client_config_t cfg = {
        .broker.address.uri = uri,
        .broker.verification.certificate = s_core_ca_pem,
        .credentials.client_id = CONFIG_GG_THING_NAME,
        .credentials.authentication.certificate = (const char *)device_pem_crt_start,
        .credentials.authentication.key = (const char *)private_pem_key_start,
    };
    s_mqtt = esp_mqtt_client_init(&cfg);
    esp_mqtt_client_register_event(s_mqtt, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL);
    esp_mqtt_client_start(s_mqtt);
}

static void publish_sensor(const char *event_name)
{
    if (!s_mqtt) {
        return;
    }
    char payload[128];
    snprintf(payload, sizeof(payload),
             "{\"event\":\"%s\",\"thing\":\"%s\"}", event_name, CONFIG_GG_THING_NAME);
    int msg_id = esp_mqtt_client_publish(s_mqtt, "gg-edge/sensor", payload, 0, 1, 0);
    ESP_LOGI(TAG, "published sensor event=%s msg_id=%d", event_name, msg_id);
}

static void telemetry_task(void *arg)
{
    char topic[96];
    snprintf(topic, sizeof(topic), "gg-edge/telemetry/%s", CONFIG_GG_THING_NAME);
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(CONFIG_GG_TELEMETRY_INTERVAL_S * 1000));
        if (!s_mqtt) {
            continue;
        }
        float temp_c = 0;
        if (temperature_sensor_get_celsius(s_tsens, &temp_c) != ESP_OK) {
            ESP_LOGW(TAG, "temperature read failed");
            continue;
        }
        wifi_ap_record_t ap = {0};
        int rssi = esp_wifi_sta_get_ap_info(&ap) == ESP_OK ? ap.rssi : 0;
        long uptime_s = (long)(esp_timer_get_time() / 1000000);
        char payload[192];
        snprintf(payload, sizeof(payload),
                 "{\"thing\":\"%s\",\"tempC\":%.2f,\"rssi\":%d,\"uptimeS\":%ld,\"rgb\":\"%s\"}",
                 CONFIG_GG_THING_NAME, temp_c, rssi, uptime_s, s_rgb_state);
        int msg_id = esp_mqtt_client_publish(s_mqtt, topic, payload, 0, 0, 0);
        ESP_LOGI(TAG, "telemetry %s msg_id=%d", payload, msg_id);
    }
}

static void button_task(void *arg)
{
    gpio_config_t io = {
        .pin_bit_mask = 1ULL << CONFIG_GG_BUTTON_GPIO,
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io);

    int last = 1;
    while (1) {
        int level = gpio_get_level(CONFIG_GG_BUTTON_GPIO);
        if (level == 0 && last == 1) {
            publish_sensor("press");
            vTaskDelay(pdMS_TO_TICKS(50));
        } else if (level == 1 && last == 0) {
            publish_sensor("release");
        }
        last = level;
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}

void app_main(void)
{
    ESP_ERROR_CHECK(nvs_flash_init());
    rgb_init();
    tsens_init();
    wifi_init();
    if (!greengrass_discover()) {
        ESP_LOGE(TAG, "discovery failed — check association, IP detector, certs");
        return;
    }
    mqtt_start();
    xTaskCreate(button_task, "button", 4096, NULL, 5, NULL);
    xTaskCreate(telemetry_task, "telemetry", 4096, NULL, 4, NULL);
}
