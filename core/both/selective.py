#!/usr/bin/env python3
import subprocess
import sys
import os

# ===== Color Codes =====
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def get_tools_by_category():
    """Parse list-tools.txt into categories and their tools."""
    categories = {}
    current_category = None

    try:
        with open('core/tools/list-tools.txt', 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Detect category headers
                if line.startswith('#'):
                    current_category = line[1:].strip()
                    categories[current_category] = []
                elif current_category:
                    categories[current_category].append(line)

    except FileNotFoundError:
        print(f"{RED}❌ Error: core/tools/list-tools.txt not found.{RESET}")
        return {}
    except Exception as e:
        print(f"{YELLOW}⚠️ Error reading tools list: {e}{RESET}")
        return {}

    return categories


def display_categories(categories):
    """Show all tool categories."""
    print(f"\n{CYAN}{BOLD}📂 Available Categories{RESET}")
    print(f"{CYAN}{'='*50}{RESET}")
    for i, category in enumerate(categories.keys(), 1):
        print(f"{YELLOW}{i}){RESET} {MAGENTA}{category}{RESET} ({GREEN}{len(categories[category])} tools{RESET})")
    return list(categories.keys())


def display_tools(category, tools):
    """Show all tools within a category."""
    print(f"\n{CYAN}{BOLD}🧰 Tools in {category}{RESET}")
    print(f"{CYAN}{'='*50}{RESET}")
    for i, tool in enumerate(tools, 1):
        print(f"{YELLOW}{i}){RESET} {tool}")
    return tools


def install_tools(tools):
    """Install one or multiple tools using apt-get."""
    success_count = 0
    fail_count = 0
    failed_tools = []

    for tool in tools:
        try:
            print(f"\n{CYAN}🔧 Installing {tool}...{RESET}")
            subprocess.run(['apt-get', 'install', '-y', tool], check=True)
            print(f"{GREEN}✅ {tool} installed successfully!{RESET}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"{RED}❌ Error installing {tool}: {e}{RESET}")
            fail_count += 1
            failed_tools.append(tool)
        except Exception as e:
            print(f"{YELLOW}⚠️ Unexpected error installing {tool}: {e}{RESET}")
            fail_count += 1
            failed_tools.append(tool)

    print(f"\n{CYAN}{BOLD}📋 Installation Summary{RESET}")
    print(f"{CYAN}{'='*50}{RESET}")
    print(f"{GREEN}✅ Successfully installed: {success_count}{RESET}")
    print(f"{RED}❌ Failed to install: {fail_count}{RESET}")

    if failed_tools:
        print(f"\n{RED}🚫 Failed tools:{RESET}")
        for tool in failed_tools:
            print(f"- {tool}")

    return success_count, fail_count


def main():
    """Main interactive menu."""
    print(f"\n{CYAN}{'='*50}{RESET}")
    print(f"{BOLD}{MAGENTA}🧩 Selective Installation Menu{RESET}")
    print(f"{CYAN}{'='*50}{RESET}")

    if os.geteuid() != 0:
        print(f"{YELLOW}⚠️  This script requires root privileges. Please run with sudo.{RESET}")
        return

    categories = get_tools_by_category()

    if not categories:
        print(f"{RED}No categories found. Exiting.{RESET}")
        return

    category_names = display_categories(categories)

    while True:
        print(f"\n{CYAN}Options:{RESET}")
        print(f"➡️  Enter the number of the category to explore")
        print(f"➡️  Enter '{YELLOW}0{RESET}{CYAN}' to return to the main menu{RESET}")

        choice = input(f"\n{MAGENTA}Enter your choice: {RESET}").strip()

        if choice == '0':
            print(f"{GREEN}↩️ Returning to main menu...{RESET}")
            return

        try:
            category_index = int(choice) - 1
            if 0 <= category_index < len(category_names):
                selected_category = category_names[category_index]
                tools = categories[selected_category]

                while True:
                    display_tools(selected_category, tools)
                    print(f"\n{CYAN}Options:{RESET}")
                    print("➡️  Enter the number of the tool to install")
                    print("➡️  Enter multiple numbers separated by commas (e.g., 1,3,5)")
                    print(f"➡️  Enter '{YELLOW}all{RESET}{CYAN}' to install all tools in this category")
                    print(f"➡️  Enter '{YELLOW}0{RESET}{CYAN}' to go back")

                    tool_choice = input(f"\n{MAGENTA}Enter your choice: {RESET}").strip()

                    if tool_choice == '0':
                        break
                    elif tool_choice.lower() == 'all':
                        confirm = input(f"{CYAN}⚙️ Install ALL {len(tools)} tools in {selected_category}? (y/n): {RESET}").lower()
                        if confirm == 'y':
                            install_tools(tools)
                        else:
                            print(f"{RED}❎ Operation cancelled.{RESET}")
                    else:
                        try:
                            selected_indices = [int(x.strip()) - 1 for x in tool_choice.split(',')]
                            selected_tools = [tools[i] for i in selected_indices if 0 <= i < len(tools)]

                            if not selected_tools:
                                print(f"{RED}Invalid selection. Please try again.{RESET}")
                                continue

                            print(f"\n{CYAN}Selected tools: {', '.join(selected_tools)}{RESET}")
                            confirm = input(f"{CYAN}Proceed with installation? (y/n): {RESET}").lower()

                            if confirm == 'y':
                                install_tools(selected_tools)
                            else:
                                print(f"{RED}❎ Operation cancelled.{RESET}")
                        except (ValueError, IndexError):
                            print(f"{YELLOW}⚠️ Invalid input. Enter valid numbers separated by commas.{RESET}")
            else:
                print(f"{RED}⚠️ Invalid category number. Try again.{RESET}")
        except ValueError:
            print(f"{RED}⚠️ Invalid input. Please enter a valid number.{RESET}")


if __name__ == "__main__":
    main()
