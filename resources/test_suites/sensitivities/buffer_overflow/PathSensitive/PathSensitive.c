/*
 * CVE-2023-0819
 */

#include <stdlib.h>

int main() {
  int *data;
  int size = 5;
  data = malloc(size * sizeof(int)); // Allocated 20 bytes of memory
  // Length of 'data' is 5
  for (int i = 0; i < size; i++) {
    data[i] = i;
  }
  if (data[0]) { // Condition is always false
    data[5] = data[4];
  }
  if (data[4]) {
    data[5] = data[4]; // buffer-overflow
  }
  free(data);
}
