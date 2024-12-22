#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>

char**
getStringList()
{
    printf("sizeof(char*) = %lu\n", sizeof(char*));
    size_t arr = sizeof(char*) *  4;
    printf("alloc = %lu\n", arr);
    void *raw = malloc(arr);
    char** data = (char**)raw;

    data[0] = "Hello";
    data[1] = "World";
    data[2] = "123";
    data[3] = NULL;

    return data;
}

int
main(int argc, char* argv[], char *env[])
{
    char** list = getStringList();
    for(char** line = list; *line != NULL; line++)
    {
        puts(*line);
    }

    char* second[] = {
        "red", "green", "blue"
    };
    printf("sizeof(second) = %lu", sizeof(second));
}


