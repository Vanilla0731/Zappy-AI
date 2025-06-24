#!/usr/bin/env bash

GREEN="\033[1;32m"
RED="\033[1;31m"
ILC="\033[3m"
ORG="\033[1;33m"
RST="\033[0m"

function _error()
{
    echo -e "${RED}${BOLD}[❌] ERROR:\n${RST}\t$1\n\t${ILC}\"$2\"${RST}"
    exit 84
}

function _success()
{
    echo -e "${GREEN}[✅] SUCCESS:\t${RST} ${ILC}$1${RST}"
}

function _info()
{
    echo -e "${ORG}[🚧] RUNNING:\t${RST} ${ILC}$1${RST}"
}

function _base_run()
{
    local cmake_args="$1"

    if ! { command -v cmake > /dev/null; } 2>&1; then
        _error "command 'cmake' not found" "please install 'cmake' or 'nix develop' 🤓"
    fi
    _success "command 'cmake' found, building..."
    mkdir -p build
    cd build || _error "mkdir failed"
    cmake .. -G "Unix Makefiles" $cmake_args
    if ! make -j"$(nproc)" zappy_ai; then
        _error "compilation error" "failed to compile zappy_ai"
    fi
    _success "compiled zappy_ai"
}

function _all()
{
    _base_run "-DCMAKE_BUILD_TYPE=Release -DZAP_AI_ENABLE_DEBUG=OFF"
    exit 0
}

function _debug()
{
    _base_run "-DCMAKE_BUILD_TYPE=Debug -DZAP_AI_ENABLE_DEBUG=ON"
    exit 0
}

function _tests_run()
{
    _info "no unit tests found, please run ./build.sh to build the project."
    exit 0
}

function _clean()
{
    rm -rf build
}

function _fclean()
{
    _clean
    rm -rf zappy_ai unit_tests plugins code_coverage.txt unit_tests-*.profraw unit_tests.profdata vgcore* cmake-build-debug
}

for args in "$@"
do
    case $args in
        -h|--help)
            cat << EOF
USAGE:
      $0    builds zappy_ai project

ARGUMENTS:
      $0 [-h|--help]    displays this message
      $0 [-d|--debug]   debug flags compilation
      $0 [-c|--clean]   clean the project
      $0 [-f|--fclean]  fclean the project
      $0 [-t|--tests]   run unit tests ⚠️ not implemented yet ⚠️
EOF
        exit 0
        ;;
    -c|--clean)
        _clean
        exit 0
        ;;
    -f|--fclean)
        _fclean
        exit 0
        ;;
    -d|--debug)
        _debug
        ;;
    -t|--tests)
        _tests_run
        ;;
    -r|--re)
        _fclean
        _all
        ;;
    *)
        _error "Invalid arguments: " "$args"
    esac
done

_all
