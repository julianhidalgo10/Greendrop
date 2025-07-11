#include <stdio.h>
#include "sensor.h"
#include "relay.h"
#include "logger.h"
#include "config.h"
#include "state.h"

void run_controller_cycle() {
    int humedad = read_humidity();
    int umbral = read_threshold();

    printf("🌡️  Humedad actual: %d%% | Umbral: %d%%\n", humedad, umbral);

    if (is_manual_override_enabled()) {
        printf("🛠️  Riego forzado por usuario (web).\n");
        activate_relay();
    } else {
        if (humedad < umbral) {
            activate_relay();
        } else {
            deactivate_relay();
        }
    }

    log_data(humedad, umbral);
}