/*
 * CVE-2022-26878
 */

#include <stdlib.h>

int main() {
  char *buffer_first = (char *)malloc(40);
  char *buffer_second = (char *)malloc(40);
  int pkt_type = 5;

  for (int i = 0; i < 10; ++i) {
    buffer_first[i] = 'a';
    buffer_second[i] = 'b';
  }

  switch (pkt_type) {
  case 1:
  case 2:
  case 3:
  case 4:
    free(buffer_first);
    break;
  default:
    free(buffer_second);
    break;
  }
} // Allocated memory for 'buffer_first' is not freed
