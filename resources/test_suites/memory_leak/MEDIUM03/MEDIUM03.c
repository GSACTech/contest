/*
 *  Based on CVE-2023-28096
 */

#include <malloc.h>
#include <stdio.h>

typedef struct cJSON {
  struct cJSON *child;
} cJSON;

void parse_object(cJSON **item, char value) {
  cJSON *child = NULL;
  if (value != '{') {
    goto fail;
  }

  child = malloc(sizeof(cJSON));
  (*item)->child = child;
  if (!(*item)->child) {
    goto fail;
  }
fail:
  if ((*item)->child != NULL) {
    free(child);
    child = NULL;
  }
}

int main() {
  cJSON *p = malloc(sizeof(cJSON)); // Memory allocation
  char value = '1';
  parse_object(&p, value);
} // Allocated memory for 'p' is not freed
