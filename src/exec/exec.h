/*
** EPITECH PROJECT, 2025
** Zappy-AI
** File description:
** exec
*/

#ifndef ZAP_AI_EXEC_H_
    #define ZAP_AI_EXEC_H_
    #include <stdio.h>
    #include <string.h>
    #include <stddef.h>
    #include <stdlib.h>
    #include <unistd.h>
    #include <libgen.h>
    #include <limits.h>
    #include <unistd.h>
    #include <sys/wait.h>

void free_args(char ***args);
char *get_main_py_path(void);

#endif /* !EXEC_H_ */
