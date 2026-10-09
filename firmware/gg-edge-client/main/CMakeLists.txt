idf_component_register(
  SRCS "main.c"
  INCLUDE_DIRS "."
  REQUIRES
    mqtt
    nvs_flash
    esp_wifi
    esp_http_client
    json
    driver
    esp_driver_tsens
    esp_timer
    esp_event
    esp_netif
    led_strip
  EMBED_TXTFILES
    "certs/device.pem.crt"
    "certs/private.pem.key"
    "certs/AmazonRootCA1.pem"
)
