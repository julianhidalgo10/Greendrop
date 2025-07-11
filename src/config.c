#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int read_threshold() {
    FILE *file = fopen("config/config.txt", "r");
    if (!file) return 40; // valor por defecto

    char line[32];
    int value = 40;

    if (fgets(line, sizeof(line), file)) {
        sscanf(line, "threshold=%d", &value);
    }

    fclose(file);
    return value;
}