#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>
#include "mmap_writer.h"

#define FILEPATH "/tmp/mmapped.bin"
#define NUMINTS (255)
#define FILESIZE (NUMINTS * sizeof(char))

/*
 * Create the file and reallocate NULL bytes.
 *
 * Return the file descriptor to the file
 */
int open_mmap_file_rw(char* filename, long bytesize)
{
    int fd;
    int result;

    /* Open a file for writing.
     * * - Creating the file if it doesn't exist.
     * *
     * * Note: "O_WRONLY" mode is not sufficient when mmaping.
     * */

    fd = open(filename, O_RDWR | O_CREAT, (mode_t)0600);
    if (fd == -1) {
        perror("Error opening file for writing");
        exit(EXIT_FAILURE);
    }

    /* Stretch the file size to the size of the (mmapped) array of
     * ints
     * */
    result = lseek(fd, bytesize-1, SEEK_SET);
    if (result == -1) {
        close(fd);
        perror("Error calling lseek() to 'stretch' the file");
        exit(EXIT_FAILURE);
    }

    /* Something needs to be written at the end of the file to
     * * have the file actually have the new size.
     * * Just writing an empty string at the current file position
     * will do.
     * *
     * * Note:
     * * - The current position in the file is at the end of the
     * stretched
     * * file due to the call to lseek().
     * * - An empty string is actually a single '\0' character, so a
     * zero-byte
     * * will be written at the last byte of the file.
     * */
    result = write(fd, "", 1);
    if (result != 1) {
        close(fd);
        perror("Error writing last byte of the file");
        exit(EXIT_FAILURE);
    }

    return fd;
}

int open_mmap_file_ro(char* filepath)
{
    int fd;
    fd = open(filepath, O_RDONLY);
    if (fd == -1) {
        perror("Error opening file for reading");
        exit(EXIT_FAILURE);
    }
    return fd;
}

/*
 * mmap a file descriptor in read-only mode and return a char array
 */
char* map_file_ro(int fd, long filesize)
{
    char* map;
    map = mmap(0, filesize, PROT_READ, MAP_SHARED, fd, 0);
    if (map == MAP_FAILED) {
        close(fd);
        perror("Error mmapping the file");
        exit(EXIT_FAILURE);
    }
    return map;
}

/*
 * mmap the file descriptor in r/w/ mode.  Return the char array 
 */
char* map_file_rw(int fd, long filesize)
{
    char* map;

    #ifdef __linux__
    map = (char *) mmap(0, filesize, PROT_READ | PROT_WRITE, MAP_SHARED|MAP_POPULATE, fd, 0);
    #else
    map = (char *) mmap(0, filesize, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    #endif

    if (map == MAP_FAILED) {
        close(fd);
        perror("Error mmapping the file");
        exit(EXIT_FAILURE);
    }

    return map;
}

/* 
 * Don't forget to free the mmapped memory
 */
void unmap_file(char* map) {
    if (munmap(map, FILESIZE) == -1) {
        perror("Error un-mmapping the file");
        /* Decide here whether to close(fd) and exit() or not.
         * Depends... */
    }
}

void turn_bits_on(char *map, int index, char bitmask)
{
    map[index] = map[index] | bitmask;
}

void flush_to_disk(int fd)
{
    int  result;
    result = fdatasync(fd);
    if (result == -1) {
        close(fd);
        perror("Error calling lseek() to 'stretch' the file");
        exit(EXIT_FAILURE);
    }
}

void close_file(int fd)
{
    int  result;
    flush_to_disk(fd);
    result = close(fd);
    if (result == -1) {
        close(fd);
        perror("Error calling lseek() to 'stretch' the file");
        exit(EXIT_FAILURE);
    }
}

int main(int argc, char *argv[])
{
    int fd;
    char *map; /* mmapped array of chars */
    fd = open_mmap_file_rw(FILEPATH, FILESIZE);

    map = map_file_rw(fd, FILESIZE);

    /* Now write int's to the file as if it were memory (an array of
     * ints).
     * */
    for (int i = 0; i <NUMINTS; i++) {
        turn_bits_on(map, i, (char) i);
    }

    unmap_file(map);

    /* Un-mmaping doesn't close the file, so we still need to do that.
     * */
    close(fd);

    fd = open_mmap_file_ro(FILEPATH);
    map = map_file_ro(fd, FILESIZE);

    /* Read the file int-by-int from the mmap
     * */
    for (int i = 0; i < NUMINTS; i++) {
        printf("%d\n", (unsigned int) map[i]);
    }

    if (munmap(map, FILESIZE) == -1) {
        perror("Error un-mmapping the file");
    }
    close(fd);
    return 0;
}

void bulkload_file(char* buffer, char* filename)
{
    FILE *file = fopen ( filename, "r" );
    if ( file != NULL )
    {
        char line [ 128 ]; /* or other suitable maximum line size */

        while ( fgets ( line, sizeof line, file ) != NULL ) /* read a line */
        {
            // TODO: inline the getbuckets and settinghere
        }
        fclose ( file );
    }
    else
    {
        perror ( filename ); /* why didn't the file open? */
    }
}

