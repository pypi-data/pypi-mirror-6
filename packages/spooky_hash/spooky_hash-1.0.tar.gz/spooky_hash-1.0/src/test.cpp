#include <cstdio>
#include "SpookyV2.h"
int main() {
    printf("%08x\n", SpookyHash::Hash32("helloworld", 10, 0));
    printf("%016llx\n", SpookyHash::Hash64("helloworld", 10, 0));

    SpookyHash h;
    h.Init(0, 0);
    h.Update("hello", 5);
    h.Update("world", 5);
    uint64_t hash1, hash2;
    h.Final(&hash1, &hash2);
    printf("%016llx\t%016llx\n", hash1, hash2);
    for (int i = 0; i < 8; ++i)
        printf("%02x", ((unsigned char*)&hash1)[i]);
    for (int i = 0; i < 8; ++i)
        printf("%02x", ((unsigned char*)&hash2)[i]);
    printf("\n");

}
