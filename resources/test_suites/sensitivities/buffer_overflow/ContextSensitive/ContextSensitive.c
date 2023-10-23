#include <stdlib.h>

int *foo(int size) {
  int *data = (int *)malloc(size * sizeof(int));
  return data;
}

int main() {
  int size = 5;
  int *first_data = foo(size++);  // Call of 'foo(5)'
  int *second_data = foo(size--); // Call of 'foo(6)'

  for (int i = 0; i <= size; i++) {
    // Length of 'first_data' is 5 and 'size' also is 5
    first_data[i] = i; // buffer-overflow
  }
  for (int i = 0; i <= size; i++) {
    // Length of 'second_data' is 6
    second_data[i] = i;
  }
  free(first_data);
  free(second_data);
}
