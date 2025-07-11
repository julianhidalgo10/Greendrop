#include <stdio.h>
#include <string.h>

int get_manual_state() {
    FILE *file = fopen("data/system_state.txt", "r");
    if (!file) return 0;

    char line[16];
    fgets(line, sizeof(line), file);
    fclose(file);

    if (strncmp(line, "ON", 2) == 0) return 1;
    return 0;
}

int is_manual_override_enabled() {
    return get_manual_state();
}