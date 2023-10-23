#include <stdlib.h>

int main() {
  char *a = (char *)malloc(sizeof(char)); // Allocate memory

  if (a) {
    *a = 'a';
    a = (char *)malloc(sizeof(char)); // Lost the address of allocated memory
    // 'a' was overwritten
  }
  free(a);
  return 0;
}
