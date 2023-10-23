#include <stdlib.h>
#include <time.h>

struct char2 {
  char *a;
  char *b;
};

int main() {
  char *a = (char *)malloc(sizeof(char));
  char *b = (char *)malloc(sizeof(char));
  *a = 'a';
  *b = 'b';
  time_t seconds = time(NULL) % 3;
  free(a); // Free allocated memory for 'a'
  free(b);
  if (seconds >= 0 && seconds <= 2)
    *a = 'b'; // Use after free
  if (seconds >= 3)
    *b = 'a';
  return 0;
}
