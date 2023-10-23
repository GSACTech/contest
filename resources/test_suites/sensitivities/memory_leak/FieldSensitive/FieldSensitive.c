#include <stdlib.h>

struct Data {
  int *first_data;
  int *second_data;
};

int main() {
  int size = 5;
  struct Data data;
  data.second_data = malloc(size * sizeof(int));
  data.first_data = malloc(size * sizeof(int)); // Allocate memory
  *data.second_data = 15;
  *data.first_data = 10;
  free(data.second_data);
} // Lost the address of allocated memory
