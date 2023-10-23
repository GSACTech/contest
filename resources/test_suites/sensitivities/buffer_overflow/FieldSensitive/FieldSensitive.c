#include <stdlib.h>

struct Data {
  int *first_data;
  int *second_data;
};

void foo(struct Data *data, int size) {
  data->second_data = (int *)malloc(size * sizeof(int)); // Allocated 20 bytes of memory
  size++;
  data->first_data = (int *)malloc(size * sizeof(int)); // Allocated 24 bytes of memory
}

int main() {
  int size = 5;
  struct Data data;
  foo(&data, size);
  for (int i = 0; i <= size; i++) {
    data.first_data[i] = i;
  }
  // Length of 'second_data' is 5 and 'size' also is 5
  for (int i = 0; i <= size; i++) {
    data.second_data[i] = i; // buffer-overflow
  }
  free(data.first_data);
  free(data.second_data);
}
