#include <stdlib.h>

struct char2 {
  char *a;
  char *b;
};

int main() {
  struct char2 *c2 = malloc(sizeof(struct char2));
  c2->a = (char *)malloc(sizeof(char)); // Memory allocation
  *c2->a = 'a';
  free(c2); // lost access to 'c2->a', so it can't be deallocated anymore
  return 0;
}
