#include <stdio.h>
#include <time.h>

void log_data(int humedad, int umbral) {
    FILE *file = fopen("data/log.csv", "a");
    if (!file) return;

    time_t now = time(NULL);
    fprintf(file, "%ld,%d,%d\n", now, humedad, umbral);
    fclose(file);
}