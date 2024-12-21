# Exploring linux named pipes `mkfifo`

```
man 3 mkfifo
```

- Create a pipe bound to a filename (length 0)
- Write to pipe (write blocks until the data is read)
- In another process, read from pipe
