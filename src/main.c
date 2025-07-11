#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include "controller.h"

int main() {
    printf("🟢 GreenDrop iniciado...\n");

    while (1) {
        run_controller_cycle();
        sleep(60); // ciclo cada 60 segundos
    }

    return 0;
}