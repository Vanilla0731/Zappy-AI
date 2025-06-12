/*
** EPITECH PROJECT, 2025
** python_exec
** File description:
** test
*/

#include "exec.h"

static int copy_main_py(char **args)
{
    char *main_py = get_main_py_path();

    if (!main_py) {
        perror("get_main_py_path");
        free(args[0]);
        free(args[1]);
        return 84;
    }
    args[2] = strdup(main_py);
    if (!args[2]) {
        perror("strdup");
        free(args[0]);
        free(args[1]);
        return 84;
    }
    return 0;
}

static int build_inner_args(char **args)
{
    args[0] = strdup("/usr/bin/env");
    if (!args[0]) {
        perror("strdup");
        return 84;
    }
    args[1] = strdup("python3");
    if (!args[1]) {
        perror("strdup");
        free(args[0]);
        return 84;
    }
    return copy_main_py(args);
}

static char **build_args(int ac, char **av)
{
    char **args = (char **)malloc(sizeof(char *) * ((size_t)(ac) + 3));

    if (!args) {
        perror("malloc");
        return NULL;
    }
    if (build_inner_args(args) != 0) {
        free(args);
        return NULL;
    }
    for (int i = 1; i < ac; ++i) {
        args[i + 2] = av[i];
    }
    args[ac + 2] = NULL;
    return args;
}

static int exec_python(char **args)
{
    int status;
    pid_t pid = fork();

    if (pid == -1) {
        perror("fork");
        return 84;
    }
    if (pid == 0) {
        execvp(args[0], args);
        perror("execvp");
        exit(84);
    }
    if (waitpid(pid, &status, 0) == -1) {
        perror("waitpid");
        return 84;
    }
    if (WIFEXITED(status)) {
        return WEXITSTATUS(status);
    }
    return 84;
}

int main(int ac, char **av)
{
    int ret;
    char **args = build_args(ac, av);

    if (!args) {
        return 84;
    }
    ret = exec_python(args);
    for (int i = 0; i < 3; ++i) {
        free(args[i]);
    }
    free(args);
    return ret == 0 ? 0 : 84;
}
