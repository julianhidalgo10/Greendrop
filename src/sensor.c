#include <stdlib.h>
#include <time.h>

int read_humidity() {
    srand(time(NULL));
    return (rand() % 100);  // Simula humedad 0-99%
}