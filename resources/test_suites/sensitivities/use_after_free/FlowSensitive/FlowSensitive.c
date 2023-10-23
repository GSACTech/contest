#include <stdlib.h>

int main() {
  char *a = (char *)malloc(sizeof(char));

  if (a != NULL) {
    *a = 'a';
    free(a);
    a = (char *)malloc(sizeof(char)); // Allocate memory
  }
  if (a != NULL) {
    free(a); // Free allocated memory
  }
  *a = 'a'; // Use after free

  return 0;
}
