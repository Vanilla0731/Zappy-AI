/*
** EPITECH PROJECT, 2025
** Zappy-AI
** File description:
** get_macos_path
*/

#include "exec.h"
#include <mach-o/dyld.h>

char *get_main_py_path(void)
{
    char *dirc;
    char *dname;
    char exe_path[PATH_MAX];
    char real_exe_path[PATH_MAX];
    static char abs_path[PATH_MAX];
    uint32_t size = sizeof(exe_path);

    if (_NSGetExecutablePath(exe_path, &size) != 0)
        return NULL;
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
