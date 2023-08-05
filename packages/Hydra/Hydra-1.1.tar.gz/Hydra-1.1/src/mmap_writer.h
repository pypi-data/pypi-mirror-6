
int open_mmap_file_rw(char* filename, long bytesize);
int open_mmap_file_ro(char* filepath);
char* map_file_rw(int fd, long filesize);
char* map_file_ro(int fd, long filesize);
void turn_bits_on(char *map, int index, char bitmask);
void flush_to_disk(int fd);
void close_file(int fd);
void unmap_file(char* map);
void bulkload_file(char* buffer, char* filename);
