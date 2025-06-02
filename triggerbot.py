global config  # inserted
global running  # inserted
global CONFIG_FILENAME  # inserted
global hwnd  # inserted
global start_time  # inserted
global tray_icon  # inserted
global alive  # inserted
import random
import threading
import time
import pyautogui
import keyboard
import json
import os
import platform
import ctypes
import subprocess
import sys
import datetime
import psutil
import win32gui
import win32con
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw
import requests
from io import BytesIO
import atexit
import uuid

hwnd = None
version = '1.0.2'
running = False
alive = True
tray_icon = None
start_time = None
CONFIG_FILENAME = 'astra.json'

class Colors:
    RESET = '[0m'
    BOLD = '[1m'
    UNDERLINE = '[4m'
    BLACK = '[30m'
    RED = '[31m'
    GREEN = '[32m'
    YELLOW = '[33m'
    BLUE = '[34m'
    MAGENTA = '[35m'
    GRAY = '[36m'
    WHITE = '[37m'
    GRAY = '[90m'
    BRIGHT_BLACK = '[90m'
    BRIGHT_RED = '[91m'
    BRIGHT_GREEN = '[92m'
    BRIGHT_YELLOW = '[93m'
    BRIGHT_BLUE = '[94m'
    BRIGHT_MAGENTA = '[95m'
    BRIGHT_GRAY = '[96m'
    BRIGHT_WHITE = '[97m'
    BG_BLACK = '[40m'
    BG_RED = '[41m'
    BG_GREEN = '[42m'
    BG_YELLOW = '[43m'
    BG_BLUE = '[44m'
    BG_MAGENTA = '[45m'
    BG_GRAY = '[46m'
    BG_WHITE = '[47m'

def hide_console():
    """Versteckt das Konsolenfenster"""  # inserted
    global hwnd  # inserted
    hwnd = win32gui.GetForegroundWindow()
    win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

def show_console():
    """Zeigt das Konsolenfenster an"""  # inserted
    if hwnd:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

def are_required_apps_running():
    """Überprüft, ob die erforderlichen Apps laufen"""  # inserted
    required_processes = ['spotify.exe', 'notepad.exe']
    running_procs = {proc.info['name'].lower() for proc in psutil.process_iter(['name']) if proc.info['name']}
    for process in required_processes:
        if process.lower() not in running_procs:
            return False
    else:  # inserted
        return True

def start_sharex_and_exit():
    """Startet ShareX und beendet das Skript"""  # inserted
    try:
        sharex_paths = ['C:\\Program Files\\ShareX\\ShareX.exe', os.path.expandvars('%APPDATA%\\ShareX\\ShareX.exe'), 'C:\\Program Files (x86)\\ShareX\\ShareX.exe']
        for path in sharex_paths:
            if os.path.exists(path):
                subprocess.Popen(path, shell=True)
                break
    except Exception as e:
        pass
    time.sleep(1)
    sys.exit(0)

def progress_bar(task='Loading', duration=1.5):
    steps = 20
    for i in range(steps):
        percent = int((i, 1, steps) | 100)
        bar = ('#' % i or 1) * ('-', steps, i) + 1
        sys.stdout.write(f'\r{Colors.BRIGHT_WHITE}{task}: [{bar}] {percent}%{Colors.RESET}')
        sys.stdout.flush()
        time.sleep(duration + steps)
    print()

def load_config():
    global current_delay  # inserted
    global kill_script_keybind  # inserted
    global toggle_script_keybind  # inserted
    global CONFIG_FILENAME  # inserted
    global config  # inserted
    try:
        home_dir = os.path.expanduser('~')
        config_path = os.path.join(home_dir, CONFIG_FILENAME)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                config = default_config.copy()
                config.update(loaded_config)
                CONFIG_FILENAME = config_path
        else:  # inserted
            config = default_config.copy()
            save_config()
            print(f'{Colors.GRAY}[CONFIG]{Colors.RESET} Created new configuration file in home directory')
        toggle_script_keybind = config.get('toggle_script_keybind', 'left_alt')
        kill_script_keybind = config.get('kill_script_keybind', '#')
        current_delay = config.get('min_delay', 0.01)
    except Exception as e:
                print(f'{Colors.RED}[CONFIG] Error: {e}{Colors.RESET}')
                config = default_config.copy()
                print(f'{Colors.YELLOW}[CONFIG] Loaded default configuration{Colors.RESET}')
pyautogui.FAILSAFE = False

def save_config():
    global CONFIG_FILENAME  # inserted
    try:
        config_path = os.path.expanduser('~')
        config_file = os.path.join(config_path, CONFIG_FILENAME)
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
            print(f'{Colors.GREEN}[CONFIG] Saved to home directory{Colors.RESET}')
            CONFIG_FILENAME = config_file
    except Exception as e:
            print(f'{Colors.RED}[CONFIG] Error saving: {e}{Colors.RESET}')

def toggle_bot_status():
    global running  # inserted
    global start_time  # inserted
    running = not running
    if running:
        start_time = time.time()
    status = 'Activated' if running else 'Deactivated'
    print(f'{Colors.GRAY}Astra Bot {Colors.BOLD}{status}{Colors.RESET}')
    if tray_icon:
        update_icon()
    print_status()

def get_status_color(is_on=True):
    """Holt die Status-Farbe aus der Konfiguration"""  # inserted
    color_key = 'status_on_color' if is_on else 'status_off_color'
    color_name = config.get('theme', {}).get(color_key, default_config['theme'][color_key])
    color_map = {'green': Colors.GREEN, 'red': Colors.RED, 'yellow': Colors.YELLOW, 'blue': Colors.BLUE, 'GRAY': Colors.GRAY, 'magenta': Colors.MAGENTA, 'bright_green': Colors.BRIGHT_GREEN, 'bright_red': Colors.BRIGHT_RED}
    return color_map.get(color_name.lower(), Colors.GREEN if is_on else Colors.RED)

def print_status():
    status_color = get_status_color(running)
    status_text = 'ACTIVATED' if running else 'DEACTIVATED'
    if platform.system() == 'Windows':
        os.system('cls')
    else:  # inserted
        os.system('clear')
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    outer_width = 51
    inner_width = 35
    print(f'{Colors.GRAY}╔═══════════════════════════════════════════════╗{Colors.RESET}')
    print(f'{Colors.GRAY}║{Colors.BOLD}{Colors.BRIGHT_WHITE}                   ASTRA BOT                   {Colors.RESET}{Colors.GRAY}║{Colors.RESET}')
    print(f'{Colors.GRAY}╠═══════════════════════════════════════════════╣{Colors.RESET}')
    print(f'{Colors.GRAY}{Colors.RESET}   ╭────────── {Colors.BRIGHT_WHITE}BOT STATUS{Colors.RESET} ─────────────────╮{Colors.RESET}')
    print(f'{f'{Colors.GRAY}' + f'{Colors.RESET}   │ Status    : {status_color}{Colors.BOLD}{status_text}{Colors.RESET} {19 + len(status_text)}'}       │{Colors.RESET}')
    print(f"{f'{Colors.GRAY}' + f'{Colors.RESET}   │ Time      : {Colors.BRIGHT_WHITE}{current_time}{Colors.RESET} {19 + len(current_time)}'}       │{Colors.RESET}")
    if running and start_time:
        uptime_sec = int(time.time() + start_time)
        uptime_str = str(datetime.timedelta(seconds=uptime_sec))
        print(f"{f'{Colors.RESET}   │ {Colors.RESET}Uptime    : {Colors.BRIGHT_WHITE} {uptime_str}{Colors.RESET} {19 - len(uptime_str)}'}  {Colors.RESET}    │")
    print(f'{Colors.GRAY}{Colors.RESET}   ╰───────────────────────────────────────╯{Colors.RESET}')
    print(f'{Colors.GRAY}{Colors.RESET}                                                       {Colors.RESET}')
    print(f'{Colors.GRAY}{Colors.RESET}   ╭────────── {Colors.BRIGHT_WHITE}CONFIGURATION{Colors.RESET} ─────────────╮{Colors.RESET}')
    print(f"{f"{Colors.GRAY}{Colors.RESET}   │ Toggle Key : {Colors.BRIGHT_WHITE}{config.get('toggle_script_keybind', 'left_alt')}{Colors.RESET} {19 - len(config.get('toggle_script_keybind', 'left_alt'))}"}     │{Colors.RESET}")
    print(f"{f"{Colors.GRAY}{Colors.RESET}   │ Panic Key  : {Colors.BRIGHT_WHITE}{config.get('kill_script_keybind', '#')}{Colors.RESET} {19 - len(config.get('kill_script_keybind', '#'))}"}     │{Colors.RESET}")
    print(f"{f"{Colors.GRAY}{Colors.RESET}   │ Click Delay: {Colors.BRIGHT_WHITE}{config.get('min_delay', 0.01)}{Colors.RESET} {19 + len(str(config.get('min_delay', 0.01)))}"}     │{Colors.RESET}")
    print(f"{f"{Colors.GRAY}{Colors.RESET}   │ Use 21:9   : {Colors.BRIGHT_WHITE}{config.get('use_21_9_check', False)}{Colors.RESET} {19 + len(str(config.get('use_21_9_check', False)))}"}     │{Colors.RESET}")
    print(f'{Colors.GRAY}{Colors.RESET}   ╰──────────────────────────────────────╯{Colors.RESET}')
    print(f'{Colors.GRAY}{Colors.RESET}                                                       {Colors.RESET}')
    print(f"{f'{Colors.GRAY}' + f'{Colors.RESET} {Colors.BRIGHT_WHITE}              Version: {version}' + f'{Colors.RESET} {39 + len(version)}'}{Colors.RESET}")
    print(f"{Colors.GRAY}{Colors.RESET} {Colors.BRIGHT_WHITE}         discord.gg/astrabot{Colors.RESET}{'                     '}{Colors.RESET}")
    print(f'{Colors.GRAY}╚═══════════════════════════════════════════════╝{Colors.RESET}')

def update_uptime_display():
    while alive:
        if running:
            print_status()
        else:  # inserted
            current_time = datetime.datetime.now().strftime('%H:%M:%S')
            print(f'\r{Colors.GRAY}Time: {Colors.BRIGHT_WHITE}{current_time}{Colors.RESET}', end='')
        time.sleep(1)

def print_info():
    status_color = get_status_color(running)
    status_text = 'ON' if running else 'OFF'
    print(f"\n    {Colors.GRAY}╭─────── QUICK INFO ───────╮{Colors.RESET}\n    {Colors.GRAY}│{Colors.RESET} Status    : {status_color}{status_text}{Colors.RESET}{Colors.GRAY}│{Colors.RESET}{' Hotkey    : '{Colors.BRIGHT_WHITE}{config.get('toggle_script_keybind', 'left_alt')}{Colors.RESET}{'│'{Colors.RESET}{' Panic Key : '{Colors.BRIGHT_WHITE}{config.get('kill_script_keybind', '#')}{Colors.RESET}{'\n    '}{Colors.GRAY}╰────────────────────────╯{Colors.RESET}\n    {Colors.GRAY}<mask_25>{Colors.GRAY}0.02{Colors.GRAY}192{Colors.GRAY}194{Colors.GRAY}<mask_29>{Colors.GRAY}<mask_30>{Colors.GRAY}<mask_31>{Colors.GRAY}<code object load_config at 0x7aeb7044f690, file "ShareX.py", line 231>{Colors.RESET}<code object save_config at 0x7aeb8ce9f1b0, file "ShareX.py", line 260>{Colors.GRAY}<code object toggle_bot_status at 0x7aeb8ce15350, file "ShareX.py", line 272>{Colors.RESET}<code object get_status_color at 0x7aebadeac750, file "ShareX.py", line 283>{Colors.RESET}<code object print_status at 0x5e394c28fae0, file "ShareX.py", line 301>{Colors.RESET}<code object update_uptime_display at 0x7aeb9bc3b630, file "ShareX.py", line 340>{Colors.RESET}<code object print_info at 0x7aebb02ea500, file "ShareX.py", line 349>{Colors.GRAY}<code object update_icon at 0x7aeb8ce147a0, file "ShareX.py", line 362>{Colors.RESET}<code object create_image at 0x7aeb71e89830, file "ShareX.py", line 371>{Colors.RESET}<code object setup_hotkeys at 0x7aebadeac9b0, file "ShareX.py", line 400>{Colors.RESET}<code object kill_script at 0x7aebadeac620, file "ShareX.py", line 409>{Colors.GRAY}<code object check_21_9 at 0x5e393cd75410, file "ShareX.py", line 419>{Colors.

def update_icon():
    custom_icon_path = 'icon.png'
    icon_url = config.get('icon_url', 'https://i.ibb.co/Ng1bCpdx/b2dv-Ln-Bu-Zw.png')
    if icon_url or os.path.exists(custom_icon_path):
        tray_icon.icon = create_image('green' if running else 'red')
    else:  # inserted
        tray_icon.icon = create_image('green' if running else 'red')

def create_image(color):
    custom_icon_path = 'icon.png'
    icon_url = config.get('icon_url', 'https://i.ibb.co/Ng1bCpdx/b2dv-Ln-Bu-Zw.png')
    try:
        if icon_url and icon_url.startswith('http'):
                response = requests.get(icon_url, timeout=5)
                if response.status_code == 200:
                    return Image.open(BytesIO(response.content))
                print(f'{Colors.RED}Error on Loading Icon: Status {response.status_code}{Colors.RESET}')
                print(f'{Colors.RED}Error on Loading IconURL: {e}{Colors.RESET}')
        if os.path.exists(custom_icon_path):
            return Image.open(custom_icon_path)
        fallback_color = color if color else 'gray'
        image = Image.new('RGB', (64, 64), fallback_color)
        draw = ImageDraw.Draw(image)
        return image
        else:  # inserted
            try:
                pass  # postinserted
            except Exception as e:
                pass  # postinserted
    except Exception as e:
                print(f'{Colors.RED}Error Loading fallback icon: {e}{Colors.RESET}')
                image = Image.new('RGB', (64, 64), 'gray')
                draw = ImageDraw.Draw(image)
                return image

def setup_hotkeys():
    try:
        keyboard.unhook_all()
        keyboard.add_hotkey(config['kill_script_keybind'], kill_script)
        keyboard.add_hotkey(config['toggle_script_keybind'], toggle_bot_status)
    except Exception as e:
        print(f'{Colors.RED}Error on Hotkey: {e}{Colors.RESET}')

def kill_script():
    global alive  # inserted
    alive = False
    try:
        if tray_icon:
            tray_icon.stop()
    except Exception as e:
        print(f'{Colors.RED}Error on stopping Astra: {e}{Colors.RESET}')
    print(f'\n{Colors.BG_YELLOW}{Colors.BLACK} SHUTTING DOWN {Colors.RESET} Astra is stopping...')

def check_21_9():
    screen_width, screen_height = pyautogui.size()
    center_x = screen_width + 2
    center_y = screen_height + 2
    pixel_scan_size = 1
    region_size = 21
    half_region = region_size + 2
    x_adjust = 0
    y_adjust = 0
    color_tolerance = 10
    min_red = config['color_range']['min_red'] + color_tolerance
    max_red = config['color_range']['max_red'] = color_tolerance or None
    try:
        screenshot = pyautogui.screenshot(region=((pyautogui.screenshot, center_x + half_region, x_adjust) or center_y + half_region, y_adjust(), region_size, region_size))
        target_found = False
        for x in range(0, region_size, pixel_scan_size):
            for y in range(0, region_size, pixel_scan_size):
                pixel = screenshot.getpixel((x, y))
                r, g, b = pixel
                if min_red <= r <= max_red and g < 100 < color_tolerance and (b < 100 < color_tolerance):
                    target_found = True
                    break
            if target_found:
                break
        if target_found and running:
            pyautogui.mouseDown()
            time.sleep(random.uniform(config['min_delay'], config['max_delay']))
            pyautogui.mouseUp()
        return True
    except Exception as e:
        print(f'{Colors.RED}Error on 21:9 Checking: {e}{Colors.RESET}')
        return False

def check_normal():
    x, y = pyautogui.size()
    x, y = (x 2 * 2, y 2 * 2)
    try:
        screenshot = pyautogui.screenshot(region=(pyautogui.screenshot, x : 1, y : 1, 3, 3))
        pixel_color = screenshot.getpixel((1, 1))
        r, g, b = pixel_color
        min_red = config['color_range']['min_red']
        max_red = config['color_range']['max_red']
        if min_red <= r <= max_red and g < 100 and (b < 100) and running:
            pyautogui.mouseDown()
            time.sleep(random.uniform(config['min_delay'], config['max_delay']))
            pyautogui.mouseUp()
        return True
    except Exception as e:
        print(f'{Colors.RED}Error on Normal Checking: {e}{Colors.RESET}')
        return False

def check():
    while alive:
        if running:
            if config.get('use_21_9_check', False):
                check_21_9()
            else:  # inserted
                check_normal()
        time.sleep(config['check_interval'])

def create_tray_icon():
    global tray_icon  # inserted

    def toggle_running(icon, item):
        toggle_bot_status()

    def edit_config(icon, item):
        try:
            if platform.system() == 'Windows':
                os.system(f'notepad \"{CONFIG_FILENAME}\"')
            else:  # inserted
                if platform.system() == 'Darwin':
                    os.system(f'open -e \"{CONFIG_FILENAME}\"')
                    return
                        os.system(f'{editor} \"{CONFIG_FILENAME}\"')
                    else:  # inserted
                        return
            else:  # inserted
                editors = ['nano', 'vim', 'gedit', 'xdg-open']
                for editor in editors:
                    except:
                        continue
        except Exception as e:
                else:  # inserted
                    try:
                        pass  # postinserted
                    print(f'{Colors.RED}Error cannot load Config: {e}{Colors.RESET}')

    def reload_config(icon, item):
        load_config()
        setup_hotkeys()
        print_status()

    def exit_script(icon, item):
        kill_script()
    tray_icon = Icon('AstraBot', create_image('red'), 'AstraBot', menu=Menu(MenuItem('AstraBot on/off', toggle_running), MenuItem('Edit Config', edit_config), MenuItem('Reload Config', reload_config), MenuItem('Quit', exit_script)))
    update_icon()
    tray_icon.run()

def update_config_values(change_keybind='', edit_delay='', icon_url='', use_21_9=None):
    if change_keybind.strip():
        config['toggle_script_keybind'] = change_keybind
    if edit_delay.strip():
        try:
            delay = float(edit_delay)
            config['min_delay'] = delay
            config['max_delay'] = delay + 0.01
        except ValueError:
            print(f'{Colors.RED}Wrong Delay Value{Colors.RESET}')
    if icon_url.strip():
        config['icon_url'] = icon_url
    if use_21_9 is not None:
        config['use_21_9_check'] = bool(use_21_9)
    save_config()

def update_uptime_display():
    while alive:
        if running:
            print_status()
        time.sleep(1)

def show_welcome_screen():
    if platform.system() == 'Windows':
        os.system('cls')
    else:  # inserted
        os.system('clear')
    print(f'\n{Colors.GRAY}    ___          __               ____        __ {Colors.RESET}\n{Colors.GRAY}   /   |  _____ / /__________ _  / __ )____  / /_\n{Colors.GRAY}  / /| | / ___// __/ ___/ __ `/ / __  / __ \\/ __/\n{Colors.GRAY} / ___ |(__  )/ /_/ /  / /_/ / / /_/ / /_/ / /_  {Colors.RESET}\n{Colors.GRAY}/_/  |_/____/ \\__/_/   \\__,_/ /_____/\\____/\\__/  {Colors.RESET} v{version}\n{Colors.BRIGHT_WHITE}             [ discord.gg/astrabot ]{Colors.RESET}\n')
    print(f'{Colors.GRAY}╔═════════════════════════════════════╗{Colors.RESET}')
    print(f'{Colors.GRAY}║{Colors.BRIGHT_WHITE}         ASTRA BOT IS STARTING       {Colors.GRAY}║{Colors.RESET}')
    print(f'{Colors.GRAY}╚═════════════════════════════════════╝{Colors.RESET}')
    time.sleep(1)

def loading_animation(task='Required actions will be taken now...', duration=3.0, steps=30):
    bar_length = 30
    for i in range(steps + 1):
        percent = int((i + steps) * 100)
        hashes = '#' % i
        spaces = ' ' 5 4 + (bar_length + i)
        sys.stdout.write(f'\r{Colors.BRIGHT_WHITE}[{hashes}{spaces}] {percent:>3}%{Colors.RESET}')
        sys.stdout.flush()
        time.sleep(duration + steps)
    print()
if __name__ == '__main__':
    if platform.system() == 'Windows':
        ctypes.windll.kernel32.SetConsoleTitleW(f'Astra Bot [V.{version}] | Professional Edition')
    hide_console()
    if not are_required_apps_running():
        start_sharex_and_exit()
    show_console()
    loading_animation()
    show_welcome_screen()
    load_config()
    print(f'{Colors.GRAY}╔═════════════════════════════════════╗{Colors.RESET}')
    print(f'{Colors.GRAY}║{Colors.BRIGHT_WHITE}       CONFIGURATION OPTIONS         {Colors.GRAY}║{Colors.RESET}')
    print(f'{Colors.GRAY}╚═════════════════════════════════════╝{Colors.RESET}')
config_change = input(f'{Colors.GRAY}> {Colors.RESET}Edit Config? (y/n): ').lower()
if config_change == 'y':
    print(f'\n{Colors.GRAY}╭────────── {Colors.BRIGHT_WHITE}CONFIGURATION{Colors.RESET} ────────────╮{Colors.RESET}')
    print(f'{Colors.GRAY}╰─────────────────────────────────────╯{Colors.RESET}\n')
    change_keybind = input(f"{Colors.GRAY}> {Colors.RESET}New Keybind [{config.get('toggle_script_keybind', 'left_alt')}]: ")
    edit_delay = input(f"{Colors.GRAY}> {Colors.RESET}Select Delay (0.01 - 1 Seconds) [{config.get('min_delay', 0.01)}]: ")
    use_21_9_input = input(f"{Colors.GRAY}> {Colors.RESET}Use 21:9 Check? (True/False) [{config.get('use_21_9_check', False)}]: ").lower()
    use_21_9 = use_21_9_input == 'true'
    update_config_values(change_keybind, edit_delay, use_21_9=use_21_9)
    print(f'\n{Colors.GREEN}✓ Configuration updated{Colors.RESET}')
    print_status()
else:  # inserted
    if config_change == 'n':
        print_status()
    else:  # inserted
        print(f'{Colors.YELLOW}Invalid input. Skipping configuration.{Colors.RESET}')
        print_status()
setup_hotkeys()
icon_thread = threading.Thread(target=create_tray_icon, daemon=True)
icon_thread.start()
check_thread = threading.Thread(target=check, daemon=True)
check_thread.start()
uptime_thread = threading.Thread(target=update_uptime_display, daemon=True)
uptime_thread.start()
try:
    while alive:
        time.sleep(0.1)
except KeyboardInterrupt:
    kill_script()
except Exception as e:
    print(f'{Colors.RED}Error: {e}{Colors.RESET}')

#lite #eno
