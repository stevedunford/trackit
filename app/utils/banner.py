from colorama import Fore, Style


BANNER_WIDTH = 60


def title_banner(name, width=BANNER_WIDTH):
    if len(name) % 2:
        name += " "  # add a space to make the name length even
    spacer = " " * int((width - len(name)) / 2)
    print(f"{Fore.BLUE}╔" + "═" * width + "╗")
    print(f"║{Fore.GREEN}" + spacer + f"{name}" + spacer + f"{Fore.BLUE}║")
    print("╚" + "═" * width + f"╝{Style.RESET_ALL}")
    print()


if __name__ == "__main__":
    pass
