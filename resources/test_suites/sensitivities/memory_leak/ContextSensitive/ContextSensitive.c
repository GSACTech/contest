#include <stdlib.h>

int *foo(int size) {
  if (size > 1) {
    int *data = malloc(size * sizeof(int)); // Allocate memory is 'size' which is greater than 1
    return data;
  }
  return NULL;
}

void bad(int size) {
  int *data = foo(size); // 'size' is 5
  if (data) {
    *data = 9;
  }
} // Lost the address of allocated memory

void good(int size) {
  int *data = foo(size); // 'size' is 1
  if (data) {
    *data = 5;
  }
}

int main() {
  int size = 5;
  good(1);
  bad(size);
}
