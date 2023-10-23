#include <stdlib.h>

struct char2 {
  char *a;
  char *b;
};

int foo(char *arg) {
  *arg = 'a';
  return 0;
}

int main() {
  char *a = (char *)malloc(sizeof(char));
  char *b = (char *)malloc(sizeof(char));

  free(a); // Free allocated memory for 'a'
  foo(b);
  foo(a); // Use after free in 'foo' function
  free(b);
  return 0;
}
