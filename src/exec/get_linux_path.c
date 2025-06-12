/*
** EPITECH PROJECT, 2025
** Zappy-AI
** File description:
** get_linux_path
*/

#include "exec.h"

char *get_main_py_path(void)
{
    char *dirc;
    char *dname;
    char exe_path[PATH_MAX];
    char real_exe_path[PATH_MAX];
    static char abs_path[PATH_MAX];

    ssize_t len = readlink("/proc/self/exe", exe_path, sizeof(exe_path) - 1);
    if (len == -1)
        return NULL;
    exe_path[len] = '\0';
    if (!realpath(exe_path, real_exe_path))
        return NULL;
    dirc = strdup(real_exe_path);
    if (!dirc)
        return NULL;
    dname = dirname(dirc);
    snprintf(abs_path, sizeof(abs_path), "%s/src/main.py", dname);
    free(dirc);
    return abs_path;
}
