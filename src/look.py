##
## EPITECH PROJECT, 2025
## Zappy-AI
## File description:
## look_function
##

def check_parsing(tab: list) -> int:
    isValid = ["player", "food", "thystame", ""]
    for node in tab:
        for part in node:
            if part in isValid:
                continue
            else:
                print("error")
    return 0

def main() -> int:
    str = "player,,,thystame,,food food,,,,,thystame,,,,,,"
    s = []
    values = str.split(",")
    for value in values:
        s.append(value.split(" "))
    check_parsing(s)
    return 0

if __name__ == "__main__":
    main()
