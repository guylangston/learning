#include <stdio.h>

#define COUNT_OF(arr) (sizeof(arr)/sizeof(0[arr]))

int
main(int argc, char* argv[])
{
    // QUESTION: How to loop over arrays
    // ANSWER: For string arrays have a NULL element
    for(char** curr = argv; *curr != NULL; curr++)
    {
        printf("ARG: %p => %s\n", curr,*curr);
    }

    // ANSWER: Other arrays don't have a null eddr
    int iarr[] = { 1, 2, 3, 4, 0 };
    int another = 123;
    printf("sizeof(iarr) = %lu\n", sizeof(iarr));
    size_t iarr_size = COUNT_OF(iarr);
    for(size_t idx = 0; idx < iarr_size; idx++)
    {
        int val = iarr[idx];
        printf("iarr[%zu]: %d\n", idx, val);
    }
    return 1;
}
