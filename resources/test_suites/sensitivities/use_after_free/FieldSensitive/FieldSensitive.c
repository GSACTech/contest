#include <stdlib.h>

struct char2 {
  char *a;
  char *b;
};

int main() {
  struct char2 c2;
  c2.a = (char *)malloc(sizeof(char));
  c2.b = (char *)malloc(sizeof(char));
  free(c2.a);  // Free allocated memory for 'c2.a'
  *c2.a = 'a'; // Use after free
  *c2.b = 'b';
  free(c2.b);
  return 0;
}
