import pygame
import random
import sys
import json
import os
import time

pygame.init()

WIDTH = 600
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fun Games Arcade - Play fun without WIFI")

clock = pygame.time.Clock()

MIXER_READY = False
try:
    pygame.mixer.init()
    MIXER_READY = True
except Exception:
    MIXER_READY = False

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

ACCOUNTS_DIR = os.path.join(DATA_DIR, "accounts")
os.makedirs(ACCOUNTS_DIR, exist_ok=True)

SESSION_FILE = os.path.join(DATA_DIR, "session.json")

DAILY_CHALLENGE_FILE = os.path.join(DATA_DIR, "daily_challenges.json")


def safe_set_window_icon():
    
    try:
        if not hasattr(pygame, "image") or not hasattr(pygame.display, "set_icon"):
            return
        icon_path = os.path.join(BASE_DIR, "arcade_icon.ico")
        if os.path.exists(icon_path):
            pygame_icon = pygame.image.load(icon_path)
            pygame.display.set_icon(pygame_icon)
    except Exception:
        pass

safe_set_window_icon()

CHEAT_HISTORY = {
    "IAMNOOB": {"active": False, "powerups_added": 0},
    "GIVEMECOINS": {"active": False, "coins_added": 0},
    "LEVELUPS": {"active": False, "xp_added": 0},
    "UNLOCKALL": {"active": False, "unlocked": False},
    "GODMODE": {"active": False, "powerups_added": 0, "coins_added": 0, "xp_added": 0}
}

pygame.display.set_mode((WIDTH, HEIGHT))
safe_set_window_icon()

def get_account_file(username):
    
    return os.path.join(ACCOUNTS_DIR, f"{username}.json")

def get_default_account_data(username):
    
    return {
        "username": username,
        "created_at": time.time(),
        "last_played": time.time(),
        "player_data": {
            "coins": 0,
            "xp": 0,
            "level": 1,
            "challenge_mode": False,
            "total_games_played": 0,
            "total_score": 0,
            "inventory": {
                "SNAKE_FOOD": 0,
                "SNAKE_INVINCIBLE": 0,
                "TICTACTOE_BOARD": 0,
                "MINESWEEPER_SCAN": 0,
                "TETRIS_CHOICE": 0,
                "FLAPPY_WIDE_GAP": 0,
                "2048_DELETE": 0,
                "PONG_BIG_PADDLE": 0,
                "BRICK_MULTI_BALL": 0,
                "RACING_SHIELD": 0,
                "MEMORY_EXTRA_TIME": 0,
                "WORDLE_EXTRA_GUESS": 0,
                "WORDLE_HINT": 0,
                "INVADERS_EXTRA_LIFE": 0
            },
            "cosmetics": {
                "theme": "DEFAULT",
                "custom_theme": {
                    "background": [12, 14, 25],
                    "panel": [30, 33, 50],
                    "accent": [80, 120, 255]
                },
                "snake_color": "GREEN",
                "paddle_color": "BLUE",
                "ball_color": "WHITE",
                "player_color": "BLUE",
                "car_color": "BLUE",
                "bird_color": "YELLOW"
            },
            "unlocked": {
                "themes": ["DEFAULT"],
                "colors": ["GREEN", "BLUE", "WHITE", "YELLOW"],
                "features": []
            },
            "completed_challenges": []
        },
        "highscores": {
            "SNAKE": 0,
            "TIC TAC TOE": 0,
            "MINESWEEPER": 0,
            "MEMORY CARDS": 0,
            "TETRIS": 0,
            "RACING": 0,
            "FLAPPY BIRD": 0,
            "BRICK BREAKER": 0,
            "2048": 0,
            "PONG": 0,
            "WORDLE": 0,
            "WORDLE_WINS": 0,
            "PAC-MAN": 0,
            "SPACE INVADERS": 0,
            "FRUIT NINJA": 0
        },
        "achievements": {},
        "statistics": {
            "total_coins_earned": 0,
            "total_xp_earned": 0,
            "total_wins": 0,
            "total_losses": 0,
            "games_played": {
                "SNAKE": 0,
                "TIC TAC TOE": 0,
                "MINESWEEPER": 0,
                "MEMORY CARDS": 0,
                "TETRIS": 0,
                "RACING": 0,
                "FLAPPY BIRD": 0,
                "BRICK BREAKER": 0,
                "2048": 0,
                "PONG": 0,
                "WORDLE": 0,
                "SPACE INVADERS": 0,
                "PAC-MAN": 0,
                "FRUIT NINJA": 0
            }
        }
    }

def create_account(username):
    
    if not username or len(username) < 2:
        return False, "Username must be at least 2 characters!"
    
    if not username.isalnum():
        return False, "Username can only contain letters and numbers!"
    
    if os.path.exists(get_account_file(username)):
        return False, "Account already exists!"
    
    account_data = get_default_account_data(username)
    
    for achievement_id in ACHIEVEMENTS:
        account_data["achievements"][achievement_id] = False
    
    try:
        with open(get_account_file(username), "w") as file:
            json.dump(account_data, file, indent=4)
        return True, "Account created successfully!"
    except Exception as e:
        return False, f"Error creating account: {str(e)}"

def normalize_account_data(account_data, username):
    
    default_data = get_default_account_data(username)
    merged = default_data.copy()
    merged.update(account_data or {})

    merged["player_data"] = default_data["player_data"].copy()
    merged["player_data"].update(account_data.get("player_data", {}) if account_data else {})

    for inventory_key, default_value in default_data["player_data"]["inventory"].items():
        merged["player_data"]["inventory"].setdefault(inventory_key, default_value)

    merged["player_data"]["cosmetics"] = default_data["player_data"]["cosmetics"].copy()
    saved_cosmetics = account_data.get("player_data", {}).get("cosmetics", {}) if account_data else {}
    if isinstance(saved_cosmetics, dict):
        merged["player_data"]["cosmetics"].update(saved_cosmetics)
    custom_theme = default_data["player_data"]["cosmetics"]["custom_theme"].copy()
    if isinstance(saved_cosmetics.get("custom_theme"), dict):
        custom_theme.update(saved_cosmetics["custom_theme"])
    merged["player_data"]["cosmetics"]["custom_theme"] = custom_theme

    merged["player_data"]["unlocked"] = default_data["player_data"]["unlocked"].copy()
    user_unlocked = account_data.get("player_data", {}).get("unlocked", {}) if account_data else {}
    for key, value in user_unlocked.items():
        if isinstance(value, list):
            merged["player_data"]["unlocked"][key] = value

    merged["highscores"] = default_data["highscores"].copy()
    if account_data and isinstance(account_data.get("highscores"), dict):
        merged["highscores"].update(account_data["highscores"])

    merged["achievements"] = dict(load_achievements())
    if account_data and isinstance(account_data.get("achievements"), dict):
        merged["achievements"].update(account_data["achievements"])

    stats = default_data.get("statistics", {}).copy()
    if account_data and isinstance(account_data.get("statistics"), dict):
        stats.update(account_data["statistics"])
    stats["games_played"] = default_data["statistics"]["games_played"].copy()
    if account_data and isinstance(account_data.get("statistics"), dict):
        saved_games = account_data["statistics"].get("games_played", {})
        if isinstance(saved_games, dict):
            stats["games_played"].update(saved_games)
    merged["statistics"] = stats

    if "completed_challenges" not in merged["player_data"]:
        merged["player_data"]["completed_challenges"] = []

    return merged


def load_account(username):
    
    try:
        with open(get_account_file(username), "r") as file:
            account_data = json.load(file)
            return normalize_account_data(account_data, username)
    except Exception:
        return None

def save_account(username, data):
    
    try:
        data["last_played"] = time.time()
        with open(get_account_file(username), "w") as file:
            json.dump(data, file, indent=4)
        return True
    except:
        return False

def list_accounts():
    
    accounts = []
    if os.path.exists(ACCOUNTS_DIR):
        for file in os.listdir(ACCOUNTS_DIR):
            if file.endswith(".json"):
                accounts.append(file.replace(".json", ""))
    return sorted(accounts)

def delete_account(username):
    
    try:
        if os.path.exists(get_account_file(username)):
            os.remove(get_account_file(username))
            return True, "Account deleted!"
        return False, "Account not found!"
    except Exception as e:
        return False, f"Error deleting account: {str(e)}"

def switch_account(username):
    
    global player_data, highscores, achievements
    
    current_user = get_current_session()
    if current_user:
        save_current_account(current_user)
    
    account_data = load_account(username)
    if not account_data:
        return False, "Account not found!"
    
    player_data = account_data["player_data"]
    highscores = account_data["highscores"]
    achievements = account_data["achievements"]
    
    save_session(username)
    
    return True, f"Welcome back, {username}!"

def save_current_account(username):
    
    account_data = load_account(username)
    if account_data:
        account_data["player_data"] = player_data
        account_data["highscores"] = highscores
        account_data["achievements"] = achievements

        account_data["statistics"]["total_coins_earned"] = player_data["coins"]
        account_data["statistics"]["total_xp_earned"] = player_data["xp"]
        save_account(username, account_data)
        return True
    return False

def save_session(username):
    
    try:
        with open(SESSION_FILE, "w") as file:
            json.dump({"username": username, "timestamp": time.time()}, file, indent=4)
        return True
    except:
        return False

def get_current_session():
    
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, "r") as file:
                data = json.load(file)
                return data.get("username")
    except:
        pass
    return None

def clear_session():
    
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        return True
    except:
        return False

def logout_account():
    
    global player_data, highscores, achievements
    
    current_user = get_current_session()
    if current_user:
        save_current_account(current_user)
        clear_session()
        
        player_data = DEFAULT_PLAYER_DATA.copy()
        highscores = DEFAULT_HIGHSCORES.copy()
        achievements = load_achievements()
        
        return True, f"Logged out successfully!"
    return False, "No account logged in!"

def delete_account_with_data(username):
    
    current_user = get_current_session()
    if current_user == username:
        logout_account()
    
    return delete_account(username)

BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (190, 190, 190)

GREEN = (50, 200, 50)
DARK_GREEN = (30, 150, 30)

RED = (220, 50, 50)
LIGHT_RED = (240, 80, 80)

BLUE = (60, 120, 220)
LIGHT_BLUE = (90, 150, 255)

YELLOW = (240, 200, 50)

PURPLE = (150, 80, 190)
LIGHT_PURPLE = (190, 110, 230)

CYAN = (50, 220, 220)
ORANGE = (240, 150, 40)
LIGHT_ORANGE = (209, 140, 88)

BUTTON_GREEN = (40, 170, 70)
BUTTON_GREEN_HOVER = (60, 210, 90)

BUTTON_BLUE = (50, 100, 200)
BUTTON_BLUE_HOVER = (70, 130, 240)

BUTTON_RED = (180, 50, 50)
BUTTON_RED_HOVER = (230, 70, 70)

BUTTON_PURPLE = (140, 70, 170)
BUTTON_PURPLE_HOVER = (180, 90, 220)

BUTTON_ORANGE = (200, 110, 30)
BUTTON_ORANGE_HOVER = (240, 140, 40)

BUTTON_GRAY = (90, 90, 90)
BUTTON_GRAY_HOVER = (130, 130, 130)

THEME_STYLES = {
    "DEFAULT": {"background": (12, 14, 25), "panel": (30, 33, 50), "accent": (80, 120, 255)},
    "DARK": {"background": (10, 10, 20), "panel": (25, 25, 38), "accent": (120, 130, 170)},
    "NEON": {"background": (20, 10, 30), "panel": (35, 18, 48), "accent": (0, 255, 170)},
    "RETRO": {"background": (30, 20, 10), "panel": (55, 35, 20), "accent": (255, 175, 55)},
    "OCEAN": {"background": (10, 20, 40), "panel": (18, 40, 65), "accent": (50, 200, 230)},
}


def get_theme_style(theme=None):
    
    theme = theme or player_data["cosmetics"].get("theme", "DEFAULT")
    if theme == "CUSTOM":
        custom = player_data["cosmetics"].get("custom_theme", {})
        style = {}
        for key in ("background", "panel", "accent"):
            color = custom.get(key)
            if (
                isinstance(color, (list, tuple))
                and len(color) == 3
                and all(isinstance(component, int) and 0 <= component <= 255 for component in color)
            ):
                style[key] = tuple(color)
            else:
                style[key] = THEME_STYLES["DEFAULT"][key]
        return style
    return THEME_STYLES.get(theme, THEME_STYLES["DEFAULT"])

SOUND_ON = True
FULLSCREEN = False

CHEAT_CODES = {
    "IAMNOOB": {"description": "Make game easier (1 use)", "used": False, "effects": []},
    "GIVEMECOINS": {"description": "Get 100 coins", "used": False, "effects": []},
    "LEVELUPS": {"description": "Get 100 XP", "used": False, "effects": []},
    "UNLOCKALL": {"description": "Unlock all themes and colors", "used": False, "effects": []},
    "GODMODE": {"description": "Enable god mode in games (1 use)", "used": False, "effects": []},
    "RESET": {"description": "Reset all cheat code uses", "used": False, "effects": []}
}

ACTIVE_CHEAT_EFFECTS = {
    "powerup_bonus": 0,
    "coins_bonus": 0,
    "xp_bonus": 0,
    "unlocked_all": False
}

def process_cheat_code(code):
    global player_data, highscores, CHEAT_HISTORY
    
    if code not in CHEAT_CODES:
        return False, "Invalid cheat code!"
    
    if CHEAT_CODES[code].get("used", False) and code != "RESET":
        return False, f"Cheat '{code}' already used!"
    
    if code == "IAMNOOB":
        CHEAT_CODES[code]["used"] = True
        CHEAT_HISTORY["IAMNOOB"]["active"] = True
        CHEAT_HISTORY["IAMNOOB"]["powerups_added"] = 3
        
        for item in player_data["inventory"]:
            player_data["inventory"][item] += 3
        save_player_data(player_data)
        return True, "Game made easier! +3 of all powerups!"
    
    elif code == "GIVEMECOINS":
        CHEAT_CODES[code]["used"] = True
        CHEAT_HISTORY["GIVEMECOINS"]["active"] = True
        CHEAT_HISTORY["GIVEMECOINS"]["coins_added"] = 100
        add_coins(100)
        return True, "Received 100 coins!"
    
    elif code == "LEVELUPS":
        CHEAT_CODES[code]["used"] = True
        CHEAT_HISTORY["LEVELUPS"]["active"] = True
        CHEAT_HISTORY["LEVELUPS"]["xp_added"] = 100
        add_xp(100)
        return True, "Received 100 XP!"
    
    elif code == "UNLOCKALL":
        CHEAT_CODES[code]["used"] = True
        CHEAT_HISTORY["UNLOCKALL"]["active"] = True
        CHEAT_HISTORY["UNLOCKALL"]["unlocked"] = True
        
        all_themes = ["DEFAULT", "DARK", "NEON", "RETRO", "OCEAN", "CUSTOM"]
        for theme in all_themes:
            if theme not in player_data["unlocked"]["themes"]:
                player_data["unlocked"]["themes"].append(theme)
        
        all_colors = ["GREEN", "BLUE", "WHITE", "YELLOW", "GOLD", "PURPLE", "PINK", "RED", "ORANGE"]
        for color in all_colors:
            if color not in player_data["unlocked"]["colors"]:
                player_data["unlocked"]["colors"].append(color)
        
        all_features = ["AUTO_SAVE", "STATS", "DAILY_BONUS"]
        for feature in all_features:
            if feature not in player_data["unlocked"]["features"]:
                player_data["unlocked"]["features"].append(feature)
        
        save_player_data(player_data)
        return True, "All themes, colors, and features unlocked!"
    
    elif code == "GODMODE":
        CHEAT_CODES[code]["used"] = True
        CHEAT_HISTORY["GODMODE"]["active"] = True
        CHEAT_HISTORY["GODMODE"]["powerups_added"] = 10
        CHEAT_HISTORY["GODMODE"]["coins_added"] = 500
        CHEAT_HISTORY["GODMODE"]["xp_added"] = 500
        
        for item in player_data["inventory"]:
            player_data["inventory"][item] += 10
        add_coins(500)
        add_xp(500)
        save_player_data(player_data)
        return True, "GOD MODE activated! +10 all powerups, +500 coins, +500 XP!"
    
    elif code == "RESET":
        return reset_cheat_effects()
    
    return False, "Unknown cheat code!"

def reset_cheat_effects():
    
    global player_data, CHEAT_HISTORY
    
    try:
        if CHEAT_HISTORY["IAMNOOB"]["active"]:
            powerups_to_remove = CHEAT_HISTORY["IAMNOOB"]["powerups_added"]
            for item in player_data["inventory"]:
                player_data["inventory"][item] = max(0, player_data["inventory"][item] - powerups_to_remove)
            CHEAT_HISTORY["IAMNOOB"]["active"] = False
            CHEAT_HISTORY["IAMNOOB"]["powerups_added"] = 0
        
        if CHEAT_HISTORY["GIVEMECOINS"]["active"]:
            coins_to_remove = CHEAT_HISTORY["GIVEMECOINS"]["coins_added"]
            player_data["coins"] = max(0, player_data["coins"] - coins_to_remove)
            CHEAT_HISTORY["GIVEMECOINS"]["active"] = False
            CHEAT_HISTORY["GIVEMECOINS"]["coins_added"] = 0
        
        if CHEAT_HISTORY["LEVELUPS"]["active"]:
            xp_to_remove = CHEAT_HISTORY["LEVELUPS"]["xp_added"]
            player_data["xp"] = max(0, player_data["xp"] - xp_to_remove)
            CHEAT_HISTORY["LEVELUPS"]["active"] = False
            CHEAT_HISTORY["LEVELUPS"]["xp_added"] = 0
        
        if CHEAT_HISTORY["GODMODE"]["active"]:
            powerups_to_remove = CHEAT_HISTORY["GODMODE"]["powerups_added"]
            for item in player_data["inventory"]:
                player_data["inventory"][item] = max(0, player_data["inventory"][item] - powerups_to_remove)
            
            coins_to_remove = CHEAT_HISTORY["GODMODE"]["coins_added"]
            player_data["coins"] = max(0, player_data["coins"] - coins_to_remove)
            
            xp_to_remove = CHEAT_HISTORY["GODMODE"]["xp_added"]
            player_data["xp"] = max(0, player_data["xp"] - xp_to_remove)
            
            CHEAT_HISTORY["GODMODE"]["active"] = False
            CHEAT_HISTORY["GODMODE"]["powerups_added"] = 0
            CHEAT_HISTORY["GODMODE"]["coins_added"] = 0
            CHEAT_HISTORY["GODMODE"]["xp_added"] = 0
        
        if CHEAT_HISTORY["UNLOCKALL"]["active"]:
            CHEAT_HISTORY["UNLOCKALL"]["active"] = False
            CHEAT_HISTORY["UNLOCKALL"]["unlocked"] = False
        
        for cheat in CHEAT_CODES:
            CHEAT_CODES[cheat]["used"] = False
        
        save_player_data(player_data)
        
        new_level = get_level_from_xp(player_data["xp"])
        player_data["level"] = new_level
        save_player_data(player_data)
        
        return True, "All cheat effects removed and cheats reset!"
        
    except Exception as e:
        return False, f"Error resetting cheats: {str(e)}"

def reset_all_cheats():
    for cheat in CHEAT_CODES:
        CHEAT_CODES[cheat]["used"] = False
    return True, "All cheat codes reset!"

font = pygame.font.SysFont("Arial", 25)
small_font = pygame.font.SysFont("Arial", 18)
big_font = pygame.font.SysFont("Arial", 55, bold=True)
button_font = pygame.font.SysFont("Arial", 25, bold=True)

def draw_text(text, font_type, color, x, y):
    surface = font_type.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)


def draw_button(rect, text, normal_color, hover_color):
    mouse = pygame.mouse.get_pos()

    if rect.collidepoint(mouse):
        color = hover_color
    else:
        color = normal_color

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=12
    )
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=12)

    surface = button_font.render(text, True, WHITE)
    text_rect = surface.get_rect(center=rect.center)

    screen.blit(surface, text_rect)


def draw_panel(rect, fill_color, border_color=None, border_width=2, radius=16):
    pygame.draw.rect(screen, fill_color, rect, border_radius=radius)
    if border_color is not None:
        pygame.draw.rect(screen, border_color, rect, border_width, border_radius=radius)


def draw_gradient_background(top_color=(10, 12, 22), bottom_color=(22, 18, 36), glow_color=(80, 120, 255)):
    for y in range(HEIGHT):
        t = y / max(1, HEIGHT)
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    glow = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (glow_color[0], glow_color[1], glow_color[2], 45), (60, -80, WIDTH - 120, 280))
    screen.blit(glow, (0, 0))


def quit_game():
    pygame.quit()
    sys.exit()

def settings_menu():
    
    global SOUND_ON, FULLSCREEN, screen
    
    theme_style = get_theme_style()
    settings_panel = pygame.Rect(WIDTH - 280, 50, 260, 510)
    close_button = pygame.Rect(WIDTH - 55, 15, 30, 30)
    sound_button = pygame.Rect(WIDTH - 260, 80, 220, 35)
    fullscreen_button = pygame.Rect(WIDTH - 260, 130, 220, 35)
    challenge_button = pygame.Rect(WIDTH - 260, 180, 220, 35)
    cheat_input_rect = pygame.Rect(WIDTH - 260, 270, 220, 35)
    cheat_submit_rect = pygame.Rect(WIDTH - 260, 315, 220, 35)
    
    cheat_input = ""
    message = ""
    message_color = WHITE
    message_time = 0
    
    while True:
        current_time = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                
                if event.key == pygame.K_BACKSPACE:
                    cheat_input = cheat_input[:-1]
                elif event.key == pygame.K_RETURN:
                    if cheat_input:
                        success, msg = process_cheat_code(cheat_input.upper())
                        if success:
                            message = msg
                            message_color = GREEN
                            message_time = current_time
                            cheat_input = ""
                        else:
                            message = msg
                            message_color = RED
                            message_time = current_time
                elif len(cheat_input) < 20:
                    cheat_input += event.unicode.upper()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if close_button.collidepoint(event.pos):
                        return
                    
                    if sound_button.collidepoint(event.pos):
                        SOUND_ON = not SOUND_ON
                        if not SOUND_ON and MIXER_READY:
                            pygame.mixer.music.pause()
                        elif SOUND_ON:
                            play_menu_music()
                        message = f"Sound: {'ON' if SOUND_ON else 'OFF'}"
                        message_color = YELLOW
                        message_time = current_time
                    
                    if fullscreen_button.collidepoint(event.pos):
                        FULLSCREEN = not FULLSCREEN
                        if FULLSCREEN:
                            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                        else:
                            screen = pygame.display.set_mode((WIDTH, HEIGHT))
                        message = f"Fullscreen: {'ON' if FULLSCREEN else 'OFF'}"
                        message_color = YELLOW
                        message_time = current_time

                    if challenge_button.collidepoint(event.pos):
                        player_data["challenge_mode"] = not player_data.get("challenge_mode", False)
                        save_player_data(player_data)
                        current_user = get_current_session()
                        if current_user:
                            save_current_account(current_user)
                        message = f"Challenge mode: {'ON' if player_data['challenge_mode'] else 'OFF'}"
                        message_color = YELLOW
                        message_time = current_time
                    if cheat_submit_rect.collidepoint(event.pos) and cheat_input:
                        success, msg = process_cheat_code(cheat_input.upper())
                        if success:
                            message = msg
                            message_color = GREEN
                            message_time = current_time
                            cheat_input = ""
                        else:
                            message = msg
                            message_color = RED
                            message_time = current_time
        
        pygame.draw.rect(screen, theme_style["panel"], settings_panel, border_radius=15)
        pygame.draw.rect(screen, theme_style["accent"], settings_panel, 2, border_radius=15)
        
        draw_text("SETTINGS", big_font, WHITE, WIDTH - 150, 45)
        
        pygame.draw.rect(screen, theme_style["background"], close_button, border_radius=8)
        pygame.draw.rect(screen, theme_style["accent"], close_button, 2, border_radius=8)
        draw_text("✕", font, WHITE, WIDTH - 40, 30)
        
        sound_text = f"🔊 Sound: {'ON' if SOUND_ON else 'OFF'}"
        sound_color = GREEN if SOUND_ON else RED
        if sound_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, theme_style["background"], sound_button, border_radius=8)
        else:
            pygame.draw.rect(screen, theme_style["panel"], sound_button, border_radius=8)
        draw_text(sound_text, small_font, sound_color, WIDTH - 150, 97)
        
        fullscreen_text = f"🖥️ Fullscreen: {'ON' if FULLSCREEN else 'OFF'}"
        fullscreen_color = GREEN if FULLSCREEN else RED
        if fullscreen_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, theme_style["background"], fullscreen_button, border_radius=8)
        else:
            pygame.draw.rect(screen, theme_style["panel"], fullscreen_button, border_radius=8)
        draw_text(fullscreen_text, small_font, fullscreen_color, WIDTH - 150, 147)
        
        challenge_enabled = player_data.get("challenge_mode", False)
        challenge_color = BUTTON_RED if challenge_enabled else BUTTON_GRAY
        challenge_hover = BUTTON_RED_HOVER if challenge_enabled else BUTTON_GRAY_HOVER
        draw_button(
            challenge_button,
            f"CHALLENGE: {'ON' if challenge_enabled else 'OFF'}",
            challenge_color,
            challenge_hover,
        )
        draw_text("+50% coins and XP - harder games", small_font, YELLOW, WIDTH - 150, 230)

        draw_text("CHEAT CODES", font, YELLOW, WIDTH - 150, 252)
        
        pygame.draw.rect(screen, (30, 35, 60), cheat_input_rect, border_radius=8)
        pygame.draw.rect(screen, (100, 100, 150), cheat_input_rect, 2, border_radius=8)
        display_text = cheat_input if cheat_input else "Enter cheat code..."
        text_color = WHITE if cheat_input else GRAY
        draw_text(display_text, small_font, text_color, WIDTH - 150, 287)
        
        
        if cheat_submit_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, BUTTON_GREEN_HOVER, cheat_submit_rect, border_radius=8)
        else:
            pygame.draw.rect(screen, BUTTON_GREEN, cheat_submit_rect, border_radius=8)
        draw_text("SUBMIT", small_font, WHITE, WIDTH - 150, 332)
        
        
        draw_text("Secret codes work here...", small_font, GRAY, WIDTH - 150, 375)
        
        
        if message:
            if current_time - message_time < 3000:
                draw_text(message, small_font, message_color, WIDTH - 150, 440)
            else:
                message = ""
        
        
        draw_text("ESC to close", small_font, GRAY, WIDTH - 150, 535)
        
        pygame.display.flip()
        clock.tick(60)



os.makedirs(DATA_DIR, exist_ok=True)

HIGHSCORE_FILE = os.path.join(DATA_DIR, "highscores.json")
PLAYER_DATA_FILE = os.path.join(DATA_DIR, "player_data.json")

DEFAULT_HIGHSCORES = {
    "SNAKE": 0,
    "TIC TAC TOE": 0,
    "MINESWEEPER": 0,
    "MEMORY CARDS": 0,
    "TETRIS": 0,
    "RACING": 0,
    "FLAPPY BIRD": 0,
    "BRICK BREAKER": 0,
    "2048": 0,
    "PONG": 0,
    "WORDLE": 0,
    "WORDLE_WINS": 0,
    "SPACE INVADERS": 0,
    "PAC-MAN": 0,
    "FRUIT NINJA": 0,
}

GAME_REWARDS = {
    "SNAKE": {"coins": 10, "xp": 10},
    "TIC TAC TOE": {"coins": 10, "xp": 10},
    "MINESWEEPER": {"coins": 15, "xp": 15},
    "MEMORY CARDS": {"coins": 15, "xp": 15},
    "TETRIS": {"coins": 15, "xp": 15},
    "RACING": {"coins": 15, "xp": 15},
    "FLAPPY BIRD": {"coins": 15, "xp": 15},
    "BRICK BREAKER": {"coins": 15, "xp": 15},
    "2048": {"coins": 15, "xp": 15},
    "PONG": {"coins": 15, "xp": 15},
    "WORDLE": {"coins": 20, "xp": 20},
    "SPACE INVADERS": {"coins": 15, "xp": 15},
    "PAC-MAN": {"coins": 15, "xp": 15},
    "FRUIT NINJA": {"coins": 15, "xp": 15},
}


def load_highscores():
    if not os.path.exists(HIGHSCORE_FILE):
        save_highscores(DEFAULT_HIGHSCORES.copy())
        return DEFAULT_HIGHSCORES.copy()

    try:
        with open(HIGHSCORE_FILE, "r") as file:
            scores = json.load(file)

        for game in DEFAULT_HIGHSCORES:
            if game not in scores:
                scores[game] = DEFAULT_HIGHSCORES[game]

        return scores

    except (json.JSONDecodeError, OSError):
        return DEFAULT_HIGHSCORES.copy()


def save_highscores(scores):
    try:
        with open(HIGHSCORE_FILE, "w") as file:
            json.dump(scores, file, indent=4)
    except OSError as error:
        print("Could not save high scores:", error)


highscores = load_highscores()



DEFAULT_PLAYER_DATA = {
    "coins": 0,
    "xp": 0,
    "level": 1,
    "challenge_mode": False,
    "total_games_played": 0,
    "total_score": 0,
    "completed_challenges": [],
    "inventory": {
        "SNAKE_FOOD": 0,
        "SNAKE_INVINCIBLE": 0,
        "TICTACTOE_BOARD": 0,
        "MINESWEEPER_SCAN": 0,
        "TETRIS_CHOICE": 0,
        "FLAPPY_WIDE_GAP": 0,
        "2048_DELETE": 0,
        "PONG_BIG_PADDLE": 0,
        "BRICK_MULTI_BALL": 0,
        "RACING_SHIELD": 0,
        "MEMORY_EXTRA_TIME": 0,
        "WORDLE_EXTRA_GUESS": 0,
        "WORDLE_HINT": 0,
        "INVADERS_EXTRA_LIFE": 0,
    },
    "cosmetics": {
        "theme": "DEFAULT",
        "custom_theme": {
            "background": [12, 14, 25],
            "panel": [30, 33, 50],
            "accent": [80, 120, 255]
        },
        "snake_color": "GREEN",
        "paddle_color": "BLUE",
        "ball_color": "WHITE",
        "player_color": "BLUE",
        "car_color": "BLUE",
        "bird_color": "YELLOW"
    },
    "unlocked": {
        "themes": ["DEFAULT"],
        "colors": ["GREEN", "BLUE", "WHITE", "YELLOW"],
        "features": []
    }
}


def load_player_data():
    if not os.path.exists(PLAYER_DATA_FILE):
        save_player_data(DEFAULT_PLAYER_DATA.copy())
        return DEFAULT_PLAYER_DATA.copy()

    try:
        with open(PLAYER_DATA_FILE, "r") as file:
            data = json.load(file)

        if "xp" not in data:
            data["xp"] = 0
        if "level" not in data:
            data["level"] = 1
        if "challenge_mode" not in data:
            data["challenge_mode"] = False
        if "total_games_played" not in data:
            data["total_games_played"] = 0
        if "total_score" not in data:
            data["total_score"] = 0
        saved_cosmetics = data.get("cosmetics", {})
        cosmetics = DEFAULT_PLAYER_DATA["cosmetics"].copy()
        if isinstance(saved_cosmetics, dict):
            cosmetics.update(saved_cosmetics)
        custom_theme = DEFAULT_PLAYER_DATA["cosmetics"]["custom_theme"].copy()
        saved_custom_theme = cosmetics.get("custom_theme", {})
        if isinstance(saved_custom_theme, dict):
            custom_theme.update(saved_custom_theme)
        cosmetics["custom_theme"] = custom_theme
        data["cosmetics"] = cosmetics
        if "unlocked" not in data:
            data["unlocked"] = DEFAULT_PLAYER_DATA["unlocked"].copy()
        if "inventory" not in data:
            data["inventory"] = {}
        if "completed_challenges" not in data:
            data["completed_challenges"] = []

        for item_id in DEFAULT_PLAYER_DATA["inventory"]:
            if item_id not in data["inventory"]:
                data["inventory"][item_id] = 0

        return data

    except (json.JSONDecodeError, OSError):
        return DEFAULT_PLAYER_DATA.copy()


def save_player_data(data):
    try:
        with open(PLAYER_DATA_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except OSError as error:
        print("Could not save player data:", error)


player_data = load_player_data()



DAILY_BONUS_FILE = os.path.join(DATA_DIR, "daily_bonus.json")


def get_daily_bonus():
    
    if "DAILY_BONUS" not in player_data["unlocked"]["features"]:
        return None, "Locked"

    try:
        if os.path.exists(DAILY_BONUS_FILE):
            with open(DAILY_BONUS_FILE, "r") as file:
                data = json.load(file)
                last_claim = data.get("last_claim", 0)
                streak = data.get("streak", 0)
        else:
            last_claim = 0
            streak = 0
    except:
        last_claim = 0
        streak = 0

    current_time = time.time()
    time_since_last = current_time - last_claim

    day_in_second = 24 * 60 * 60

    if time_since_last >= day_in_second:
        if time_since_last > 2 * day_in_second:
            streak = 0

        streak += 1
        bonus = 50 + streak * 10
        return bonus, streak
    else:
        remaining = day_in_second - time_since_last
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        return None, f"{hours}h {minutes}m"


def claim_daily_bonus():
    
    bonus, streak_or_time = get_daily_bonus()

    if bonus is None:
        return False, 0, 0

    add_coins(bonus)

    data = {
        "last_claim": time.time(),
        "streak": streak_or_time
    }

    try:
        with open(DAILY_BONUS_FILE, "w") as file:
            json.dump(data, file)
    except:
        pass

    return True, bonus, streak_or_time




def get_xp_for_level(level):
    
    if level <= 1:
        return 0
    elif level == 2:
        return 100
    elif level == 3:
        return 250
    elif level == 4:
        return 500
    elif level == 5:
        return 1000
    else:
        return int(1000 * (1.5 ** (level - 5)))


def get_total_xp_for_level(level):
    
    total = 0
    for i in range(2, level + 1):
        total += get_xp_for_level(i)
    return total


def get_level_from_xp(xp):
    
    level = 1
    while True:
        next_level_xp = get_total_xp_for_level(level + 1)
        if xp >= next_level_xp:
            level += 1
        else:
            break
    return level


def get_xp_required(level):
    return 100 + (level - 1) * 50


def get_next_level_xp():
    
    current_level = player_data["level"]
    next_level_xp = get_total_xp_for_level(current_level + 1)
    return next_level_xp


def get_xp_progress():
    
    current_level = player_data["level"]
    current_xp = player_data["xp"]
    current_level_xp = get_total_xp_for_level(current_level)
    next_level_xp = get_total_xp_for_level(current_level + 1)

    if next_level_xp <= current_level_xp:
        return 100

    progress = (current_xp - current_level_xp) / (next_level_xp - current_level_xp) * 100
    return min(100, max(0, progress))


def get_color_from_choice(choice):
    
    COLOR_MAP = {
        "GREEN": (50, 200, 50),
        "BLUE": (60, 120, 220),
        "WHITE": (255, 255, 255),
        "YELLOW": (240, 200, 50),
        "GOLD": (255, 215, 0),
        "PURPLE": (150, 80, 190),
        "PINK": (255, 105, 180),
        "RED": (220, 50, 50),
        "ORANGE": (240, 150, 40)
    }
    return COLOR_MAP.get(choice, (255, 255, 255))


def calculate_xp_reward(game_name, score):
    
    base_xp = {
        "SNAKE": 10,
        "TIC TAC TOE": 5,
        "MINESWEEPER": 15,
        "MEMORY CARDS": 10,
        "TETRIS": 15,
        "RACING": 10,
        "FLAPPY BIRD": 10,
        "BRICK BREAKER": 15,
        "2048": 20,
        "PONG": 10,
        "WORDLE": 25,
        "SPACE INVADERS": 15,
        "PAC-MAN": 15,
        "FRUIT NINJA": 15
    }

    base = base_xp.get(game_name, 10)

    if score > 0:
        if game_name == "MEMORY CARDS":
            if score <= 10:
                bonus = 20
            elif score <= 20:
                bonus = 10
            elif score <= 30:
                bonus = 5
            else:
                bonus = 0
        else:
            high_score = highscores.get(game_name, 0)
            if high_score > 0:
                ratio = score / high_score
                if ratio >= 0.5:
                    bonus = 15
                elif ratio >= 0.25:
                    bonus = 5
                else:
                    bonus = 0
            else:
                bonus = 5 if score > 0 else 0

        if update_highscore(game_name, score):
            bonus += 25
    else:
        bonus = 0

    return base + bonus



def challenge_reward(amount):
    
    if player_data.get("challenge_mode", False):
        return int(round(amount * 1.5))
    return amount


def add_xp(amount):
    
    global player_data

    amount = challenge_reward(amount)
    player_data["xp"] += amount
    old_level = player_data["level"]
    new_level = get_level_from_xp(player_data["xp"])

    if new_level > old_level:
        player_data["level"] = new_level
        save_player_data(player_data)
        check_level_unlocks(new_level)
        return True, new_level

    save_player_data(player_data)
    return False, old_level


def check_level_unlocks(level):
    
    global player_data

    UNLOCKABLE_FEATURES = {
        "THEME_DARK": {"name": "Dark Theme", "description": "A sleek dark theme for the arcade", "level_required": 2, "type": "theme", "id": "DARK"},
        "THEME_NEON": {"name": "Neon Theme", "description": "Glowing neon colors everywhere!", "level_required": 5, "type": "theme", "id": "NEON"},
        "THEME_RETRO": {"name": "Retro Theme", "description": "Classic retro arcade look", "level_required": 8, "type": "theme", "id": "RETRO"},
        "THEME_OCEAN": {"name": "Ocean Theme", "description": "Blue ocean vibes", "level_required": 12, "type": "theme", "id": "OCEAN"},
        "COLOR_GOLD": {"name": "Gold Color", "description": "Shiny gold for your player", "level_required": 3, "type": "color", "id": "GOLD"},
        "COLOR_PURPLE": {"name": "Purple Color", "description": "Royal purple for your player", "level_required": 6, "type": "color", "id": "PURPLE"},
        "COLOR_PINK": {"name": "Pink Color", "description": "Pretty pink for your player", "level_required": 10, "type": "color", "id": "PINK"},
        "FEATURE_AUTO_SAVE": {"name": "Auto-Save", "description": "Automatically save your progress", "level_required": 4, "type": "feature", "id": "AUTO_SAVE"},
        "FEATURE_STATS": {"name": "Advanced Stats", "description": "View detailed game statistics", "level_required": 7, "type": "feature", "id": "STATS"},
        "FEATURE_DAILY_BONUS": {"name": "Daily Bonus", "description": "Get bonus coins every day", "level_required": 9, "type": "feature", "id": "DAILY_BONUS"}
    }

    unlocked_anything = False

    for feature_id, feature in UNLOCKABLE_FEATURES.items():
        if feature["level_required"] <= level:
            if feature["type"] == "theme":
                if feature["id"] not in player_data["unlocked"]["themes"]:
                    player_data["unlocked"]["themes"].append(feature["id"])
                    unlocked_anything = True
            elif feature["type"] == "color":
                if feature["id"] not in player_data["unlocked"]["colors"]:
                    player_data["unlocked"]["colors"].append(feature["id"])
                    unlocked_anything = True
            elif feature["type"] == "feature":
                if feature["id"] not in player_data["unlocked"]["features"]:
                    player_data["unlocked"]["features"].append(feature["id"])
                    unlocked_anything = True

    if unlocked_anything:
        save_player_data(player_data)
        return True
    return False


def reward_game_played(game_name, coins=0, xp=0):
    global player_data

    add_coins(coins)
    add_xp(xp)
    player_data["total_games_played"] += 1

    save_player_data(player_data)

    check_level_unlocks(player_data["level"])


def add_coins(amount):
    global player_data
    player_data["coins"] += challenge_reward(amount)
    save_player_data(player_data)


def spend_coins(amount):
    global player_data
    if player_data["coins"] < amount:
        return False
    player_data["coins"] -= amount
    save_player_data(player_data)
    return True


def get_coins():
    return player_data["coins"]


def use_powerup(item_id):
    global player_data

    if item_id not in player_data["inventory"]:
        return False
    if player_data["inventory"][item_id] <= 0:
        return False

    player_data["inventory"][item_id] -= 1
    save_player_data(player_data)
    return True


def update_highscore(game, score):
    global highscores

    if score > highscores[game]:
        highscores[game] = score
        save_highscores(highscores)
        return True
    return False


def update_low_score(game, score):
    global highscores

    if highscores[game] == 0 or score < highscores[game]:
        highscores[game] = score
        save_highscores(highscores)
        return True
    return False



SHOP_ITEMS = {
    "SNAKE_FOOD": {
        "name": "Extra Food",
        "description": "Spawns an extra food item in Snake",
        "price": 100,
        "level_required": 1
    },
    "SNAKE_INVINCIBLE": {
        "name": "Snake Invincibility",
        "description": "Become invincible for 10 seconds",
        "price": 300,
        "level_required": 3
    },
    "TICTACTOE_BOARD": {
        "name": "Bigger Board",
        "description": "Play Tic Tac Toe on a 4x4 board",
        "price": 500,
        "level_required": 5
    },
    "MINESWEEPER_SCAN": {
        "name": "Bomb Scanner",
        "description": "Reveal all mines around a cell",
        "price": 250,
        "level_required": 2
    },
    "TETRIS_CHOICE": {
        "name": "Block Choice",
        "description": "Choose your next Tetris piece (3 uses)",
        "price": 400,
        "level_required": 4
    },
    "FLAPPY_WIDE_GAP": {
        "name": "Wide Pipe Gap",
        "description": "Makes pipe gaps 30% wider",
        "price": 250,
        "level_required": 2
    },
    "2048_DELETE": {
        "name": "Delete Tile",
        "description": "Remove a 2 or 4 tile (3 uses)",
        "price": 300,
        "level_required": 3
    },
    "PONG_BIG_PADDLE": {
        "name": "Big Paddle",
        "description": "Paddle is 50% wider in Pong",
        "price": 200,
        "level_required": 2
    },
    "BRICK_MULTI_BALL": {
        "name": "Multi Ball",
        "description": "Split ball into 3 (1 use)",
        "price": 350,
        "level_required": 4
    },
    "RACING_SHIELD": {
        "name": "Racing Shield",
        "description": "Survive one crash (1 use)",
        "price": 250,
        "level_required": 3
    },
    "MEMORY_EXTRA_TIME": {
        "name": "Extra Time",
        "description": "Reveal 4 extra cards for 1 second",
        "price": 150,
        "level_required": 2
    },
    "WORDLE_EXTRA_GUESS": {
        "name": "Extra Guess",
        "description": "Get one additional guess in Wordle",
        "price": 200,
        "level_required": 2
    },
    "INVADERS_EXTRA_LIFE": {
        "name": "Invaders Extra Life",
        "description": "Start Space Invaders with one extra life",
        "price": 250,
        "level_required": 2
    },
    "WORDLE_HINT": {
        "name": "Wordle Hint",
        "description": "Reveal one letter in the word (1 use)",
        "price": 300,
        "level_required": 4
    },
    "THEME_DARK": {
        "name": "Dark Theme",
        "description": "A calm dark palette for the arcade",
        "price": 250,
        "level_required": 1,
        "type": "theme",
        "theme_id": "DARK"
    },
    "THEME_OCEAN": {
        "name": "Ocean Theme",
        "description": "Deep blue backgrounds and bright aqua accents",
        "price": 350,
        "level_required": 1,
        "type": "theme",
        "theme_id": "OCEAN"
    },
    "THEME_RETRO": {
        "name": "Retro Theme",
        "description": "Warm vintage arcade colors",
        "price": 350,
        "level_required": 1,
        "type": "theme",
        "theme_id": "RETRO"
    },
    "THEME_NEON": {
        "name": "Neon Theme",
        "description": "Bright neon accents on a midnight background",
        "price": 450,
        "level_required": 1,
        "type": "theme",
        "theme_id": "NEON"
    },
    "CUSTOM_THEME_KIT": {
        "name": "Custom Theme Builder",
        "description": "Unlock the builder to create your own palette",
        "price": 600,
        "level_required": 1,
        "type": "theme_builder",
        "theme_id": "CUSTOM"
    },
}


def is_shop_item_owned(item_id, item):
    if item.get("type") in ("theme", "theme_builder"):
        return item["theme_id"] in player_data["unlocked"]["themes"]
    return player_data["inventory"].get(item_id, 0) > 0


def shop_menu():
    shop_items = list(SHOP_ITEMS.items())
    selected = 0
    scroll = 0
    message = ""
    message_time = 0

    while True:
        theme_style = get_theme_style()
        screen.fill(theme_style["background"])

        draw_text("SHOP", big_font, theme_style["accent"], WIDTH // 2, 45)
        draw_text(f"Coins: {get_coins()}", font, theme_style["accent"], WIDTH // 2, 90)
        draw_text(f"Level {player_data['level']}", small_font, WHITE, WIDTH // 2, 112)

        visible_items = shop_items[scroll:scroll + 5]

        for index, (item_id, item) in enumerate(visible_items):
            real_index = scroll + index
            y = 140 + index * 70

            rect = pygame.Rect(45, y, 510, 60)

            owned = is_shop_item_owned(item_id, item)
            can_buy = owned or player_data["level"] >= item.get("level_required", 1)

            if real_index == selected:
                color = theme_style["panel"]
                border_color = theme_style["accent"] if can_buy else RED
                pygame.draw.rect(screen, color, rect, border_radius=10)
                pygame.draw.rect(screen, border_color, rect, 2, border_radius=10)
            else:
                color = theme_style["panel"] if can_buy else (50, 30, 30)
                pygame.draw.rect(screen, color, rect, border_radius=10)

            draw_text(item["name"], font, WHITE if can_buy else GRAY, 155, y + 20)

            if item.get("type") in ("theme", "theme_builder") and owned:
                status = "ACTIVE" if player_data["cosmetics"].get("theme") == item["theme_id"] else "OWNED"
                draw_text(status, small_font, GREEN, 470, y + 20)
                draw_text("Click / Enter to enable", small_font, GRAY, 175, y + 45)
            elif can_buy:
                draw_text(f"{item['price']} coins", small_font, YELLOW, 470, y + 20)
                if item.get("type") in ("theme", "theme_builder"):
                    draw_text("Buy to unlock", small_font, GRAY, 155, y + 45)
                else:
                    draw_text(f"Owned: {player_data['inventory'].get(item_id, 0)}", small_font, GRAY, 155, y + 45)
            else:
                draw_text(f"🔒 Level {item.get('level_required', 1)}", small_font, RED, 470, y + 20)

        current_id, current_item = shop_items[selected]
        current_owned = is_shop_item_owned(current_id, current_item)
        can_buy = current_owned or player_data["level"] >= current_item.get("level_required", 1)

        if can_buy:
            draw_text(current_item["description"], small_font, WHITE, WIDTH // 2, 500)
            draw_text("ENTER = BUY    ESC = BACK", small_font, GRAY, WIDTH // 2, 525)
        else:
            draw_text(f"Requires Level {current_item.get('level_required', 1)}", small_font, RED, WIDTH // 2, 500)
            draw_text("ESC = BACK", small_font, GRAY, WIDTH // 2, 525)

        if message:
            if pygame.time.get_ticks() - message_time < 2000:
                draw_text(message, small_font, GREEN, WIDTH // 2, 115)
            else:
                message = ""

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected -= 1
                    if selected < 0:
                        selected = len(shop_items) - 1
                    if selected < scroll:
                        scroll = selected
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected += 1
                    if selected >= len(shop_items):
                        selected = 0
                        scroll = 0
                    elif selected >= scroll + 5:
                        scroll += 1
                if event.key == pygame.K_RETURN:
                    item_id = shop_items[selected][0]
                    item = SHOP_ITEMS[item_id]

                    if not is_shop_item_owned(item_id, item) and player_data["level"] < item.get("level_required", 1):
                        message = f"NEED LEVEL {item.get('level_required', 1)}!"
                        message_time = pygame.time.get_ticks()
                    elif buy_item(item_id):
                        message = "THEME BUILDER READY!" if item.get("type") == "theme_builder" else "PURCHASED / THEME ENABLED!"
                        message_time = pygame.time.get_ticks()
                        if item.get("type") == "theme_builder":
                            custom_theme_builder()
                    else:
                        message = "NOT ENOUGH COINS!"
                        message_time = pygame.time.get_ticks()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for index, (item_id, item) in enumerate(shop_items[scroll:scroll + 5]):
                        real_index = scroll + index
                        y = 140 + index * 70
                        rect = pygame.Rect(45, y, 510, 60)
                        if rect.collidepoint(event.pos):
                            selected = real_index
                            if not is_shop_item_owned(item_id, item) and player_data["level"] < item.get("level_required", 1):
                                message = f"NEED LEVEL {item.get('level_required', 1)}!"
                                message_time = pygame.time.get_ticks()
                            elif buy_item(item_id):
                                message = "THEME BUILDER READY!" if item.get("type") == "theme_builder" else "PURCHASED / THEME ENABLED!"
                                message_time = pygame.time.get_ticks()
                                if item.get("type") == "theme_builder":
                                    custom_theme_builder()
                            else:
                                message = "NOT ENOUGH COINS!"
                                message_time = pygame.time.get_ticks()

        clock.tick(60)


def buy_item(item_id):
    if item_id not in SHOP_ITEMS:
        return False

    item = SHOP_ITEMS[item_id]

    if item.get("type") in ("theme", "theme_builder"):
        theme_id = item["theme_id"]
        if theme_id not in player_data["unlocked"]["themes"]:
            if not spend_coins(item["price"]):
                return False
            player_data["unlocked"]["themes"].append(theme_id)
        player_data["cosmetics"]["theme"] = theme_id
        save_player_data(player_data)
        current_user = get_current_session()
        if current_user:
            save_current_account(current_user)
        return True

    if not spend_coins(item["price"]):
        return False

    player_data["inventory"][item_id] += 1
    save_player_data(player_data)
    current_user = get_current_session()
    if current_user:
        save_current_account(current_user)
    return True



MUSIC_DIR = os.path.join(BASE_DIR, "Music")

GAME_MUSIC = {
    "MENU": os.path.join(MUSIC_DIR, "MenuBackgroundMusic.mp3"),
    "SNAKE": os.path.join(MUSIC_DIR, "SnakeGameBackgroundMusic.mp3"),
    "TIC TAC TOE": os.path.join(MUSIC_DIR, "TicTacToeGameBackgroundMusic.mp3"),
    "MINESWEEPER": os.path.join(MUSIC_DIR, "MinesweeperGameBackgroundMusic.mp3"),
    "MEMORY CARDS": os.path.join(MUSIC_DIR, "MemoryCardGameBackgroundMusic.mp3"),
    "TETRIS": os.path.join(MUSIC_DIR, "TetrisGameBackgroundMusic.mp3"),
    "RACING": os.path.join(MUSIC_DIR, "RacingGameBackgroundMusic.mp3"),
    "FLAPPY BIRD": os.path.join(MUSIC_DIR, "FlappyBirdGameBackgroundMusic.mp3"),
    "BRICK BREAKER": os.path.join(MUSIC_DIR, "BrickBreakerGameBackgroundMusic.mp3"),
    "2048": os.path.join(MUSIC_DIR, "2048GameBackgroundMusic.mp3"),
    "PONG": os.path.join(MUSIC_DIR, "PongGameBackgroundMusic.mp3"),
    "WORDLE": os.path.join(MUSIC_DIR, "WordleGameBackgroundMusic.mp3"),
    "SPACE INVADERS": os.path.join(MUSIC_DIR, "SpaceInvadersGameBackgroundMusic.mp3"),
    "PAC-MAN": os.path.join(MUSIC_DIR, "PacmanGameBackgroundMusic.mp3"),
    "FRUIT NINJA": os.path.join(MUSIC_DIR, "FruitNinjaGameBackgroundMusic.mp3")
}

CURRENT_MUSIC_FILE = None


def play_music(game):
    global CURRENT_MUSIC_FILE

    if not SOUND_ON or not MIXER_READY:
        return

    music_file = GAME_MUSIC.get(game)

    if music_file is None or not os.path.exists(music_file):
        return

    try:
        if CURRENT_MUSIC_FILE == music_file and pygame.mixer.music.get_busy():
            return
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        CURRENT_MUSIC_FILE = music_file
    except pygame.error as error:
        print(f"Could not play {game} music:", error)

def play_menu_music():
    play_music("MENU")

def stop_music():
    global CURRENT_MUSIC_FILE

    if MIXER_READY:
        pygame.mixer.music.stop()
    CURRENT_MUSIC_FILE = None



ACHIEVEMENT_FILE = os.path.join(DATA_DIR, "achievements.json")

ACHIEVEMENTS = {
    "FIRST_GAME": {"name": "First Game", "description": "Play your first game", "game": "ANY", "target": 1},
    "SNAKE_10": {"name": "Snake Beginner", "description": "Score 10 in Snake", "game": "SNAKE", "target": 10},
    "SNAKE_25": {"name": "Snake Master", "description": "Score 25 in Snake", "game": "SNAKE", "target": 25},
    "TETRIS_1000": {"name": "Tetris Player", "description": "Score 1,000 in Tetris", "game": "TETRIS", "target": 1000},
    "TETRIS_10000": {"name": "Tetris Legend", "description": "Score 10,000 in Tetris", "game": "TETRIS", "target": 10000},
    "RACING_500": {"name": "Speed Demon", "description": "Score 500 in Racing", "game": "RACING", "target": 500},
    "RACING_2000": {"name": "Racing Champion", "description": "Score 2,000 in Racing", "game": "RACING", "target": 2000},
    "MINESWEEPER_1": {"name": "Mine Hunter", "description": "Win Minesweeper once", "game": "MINESWEEPER", "target": 1},
    "MINESWEEPER_10": {"name": "Mine Expert", "description": "Win Minesweeper 10 times", "game": "MINESWEEPER", "target": 10},
    "TICTACTOE_5": {"name": "Tic Tac Toe Player", "description": "Win 5 Tic Tac Toe games", "game": "TIC TAC TOE", "target": 5},
    "MEMORY_30": {"name": "Memory Player", "description": "Finish Memory Cards in 30 moves", "game": "MEMORY CARDS", "target": 30},
    "MEMORY_20": {"name": "Memory Master", "description": "Finish Memory Cards in 20 moves", "game": "MEMORY CARDS", "target": 20},
    "FLAPPY_10": {"name": "Flappy Beginner", "description": "Score 10 in Flappy Bird", "game": "FLAPPY BIRD", "target": 10},
    "FLAPPY_25": {"name": "Flappy Flyer", "description": "Score 25 in Flappy Bird", "game": "FLAPPY BIRD", "target": 25},
    "FLAPPY_50": {"name": "Flappy Master", "description": "Score 50 in Flappy Bird", "game": "FLAPPY BIRD", "target": 50},
    "BREAKOUT_500": {"name": "Brick Breaker", "description": "Score 500 in Brick Breaker", "game": "BRICK BREAKER", "target": 500},
    "BREAKOUT_2000": {"name": "Brick Destroyer", "description": "Score 2,000 in Brick Breaker", "game": "BRICK BREAKER", "target": 2000},
    "BREAKOUT_LEVEL5": {"name": "Brick Master", "description": "Reach level 5 in Brick Breaker", "game": "BRICK BREAKER", "target": 5},
    "2048_512": {"name": "Getting Started", "description": "Reach 512 in 2048", "game": "2048", "target": 512},
    "2048_1024": {"name": "2048 Player", "description": "Reach 1,024 in 2048", "game": "2048", "target": 1024},
    "2048_2048": {"name": "2048 Master", "description": "Reach 2,048 in 2048", "game": "2048", "target": 2048},
    "2048_4096": {"name": "Beyond 2048", "description": "Reach 4,096 in 2048", "game": "2048", "target": 4096},
    "PONG_1": {"name": "First Victory", "description": "Win your first Pong match", "game": "PONG", "target": 1},
    "PONG_5": {"name": "Pong Player", "description": "Win 5 Pong matches", "game": "PONG", "target": 5},
    "PONG_10": {"name": "Pong Master", "description": "Win 10 Pong matches", "game": "PONG", "target": 10},
    "WORDLE_1": {"name": "Wordle Beginner", "description": "Win your first Wordle game", "game": "WORDLE", "target": 1},
    "WORDLE_5": {"name": "Wordle Player", "description": "Win 5 Wordle games", "game": "WORDLE", "target": 5},
    "WORDLE_10": {"name": "Wordle Master", "description": "Win 10 Wordle games", "game": "WORDLE", "target": 10},
    "WORDLE_PERFECT": {"name": "Perfect Wordle", "description": "Win Wordle in 1 guess!", "game": "WORDLE", "target": 1},
    "SPACE_INVADERS_500": {"name": "Alien Hunter", "description": "Score 500 in Space Invaders", "game": "SPACE INVADERS", "target": 500},
    "SPACE_INVADERS_2000": {"name": "Defender of Earth", "description": "Score 2,000 in Space Invaders", "game": "SPACE INVADERS", "target": 2000},
    "PACMAN_500": {"name": "Maze Muncher", "description": "Score 500 in Pac-Man", "game": "PAC-MAN", "target": 500},
    "PACMAN_2000": {"name": "Ghost Chaser", "description": "Score 2,000 in Pac-Man", "game": "PAC-MAN", "target": 2000},
}


def load_achievements():
    if not os.path.exists(ACHIEVEMENT_FILE):
        achievements = {}
        for achievement_id in ACHIEVEMENTS:
            achievements[achievement_id] = False
        save_achievements(achievements)
        return achievements

    try:
        with open(ACHIEVEMENT_FILE, "r") as file:
            achievements = json.load(file)

        for achievement_id in ACHIEVEMENTS:
            if achievement_id not in achievements:
                achievements[achievement_id] = False

        return achievements

    except:
        achievements = {}
        for achievement_id in ACHIEVEMENTS:
            achievements[achievement_id] = False
        return achievements


def save_achievements(achievements):
    try:
        with open(ACHIEVEMENT_FILE, "w") as file:
            json.dump(achievements, file, indent=4)
    except OSError as error:
        print("Could not save achievements:", error)


achievements = load_achievements()

achievement_notification = None
achievement_notification_time = 0


def unlock_achievement(achievement_id):
    global achievement_notification
    global achievement_notification_time

    if achievement_id not in achievements:
        return
    if achievements[achievement_id]:
        return

    achievements[achievement_id] = True
    save_achievements(achievements)

    achievement_notification = ACHIEVEMENTS[achievement_id]["name"]
    achievement_notification_time = pygame.time.get_ticks()


def draw_achievement_notification():
    global achievement_notification
    global achievement_notification_time

    if achievement_notification is None:
        return

    current_time = pygame.time.get_ticks()

    if current_time - achievement_notification_time > 3000:
        achievement_notification = None
        return

    notification_rect = pygame.Rect(100, 15, 400, 70)

    pygame.draw.rect(screen, (40, 40, 55), notification_rect, border_radius=12)
    pygame.draw.rect(screen, YELLOW, notification_rect, 3, border_radius=12)

    draw_text("★ ACHIEVEMENT UNLOCKED! ★", small_font, YELLOW, WIDTH // 2, 35)
    draw_text(achievement_notification, font, WHITE, WIDTH // 2, 62)


def check_achievements(breakout_level=0, pong_wins=0):
    
    global highscores

    
    total_played = player_data.get("total_games_played", 0)
    if total_played > 0:
        unlock_achievement("FIRST_GAME")

    
    if highscores["SNAKE"] >= 10:
        unlock_achievement("SNAKE_10")
    if highscores["SNAKE"] >= 25:
        unlock_achievement("SNAKE_25")

    if highscores.get("SPACE INVADERS", 0) >= 500:
        unlock_achievement("SPACE_INVADERS_500")
    if highscores.get("SPACE INVADERS", 0) >= 2000:
        unlock_achievement("SPACE_INVADERS_2000")
    if highscores.get("PAC-MAN", 0) >= 500:
        unlock_achievement("PACMAN_500")
    if highscores.get("PAC-MAN", 0) >= 2000:
        unlock_achievement("PACMAN_2000")

    
    if highscores["TETRIS"] >= 1000:
        unlock_achievement("TETRIS_1000")
    if highscores["TETRIS"] >= 10000:
        unlock_achievement("TETRIS_10000")

    
    if highscores["RACING"] >= 500:
        unlock_achievement("RACING_500")
    if highscores["RACING"] >= 2000:
        unlock_achievement("RACING_2000")

    
    if highscores["MINESWEEPER"] >= 1:
        unlock_achievement("MINESWEEPER_1")
    if highscores["MINESWEEPER"] >= 10:
        unlock_achievement("MINESWEEPER_10")

    
    if highscores["TIC TAC TOE"] >= 5:
        unlock_achievement("TICTACTOE_5")

    
    memory_score = highscores["MEMORY CARDS"]
    if memory_score > 0:
        if memory_score <= 30:
            unlock_achievement("MEMORY_30")
        if memory_score <= 20:
            unlock_achievement("MEMORY_20")

    
    if highscores["FLAPPY BIRD"] >= 10:
        unlock_achievement("FLAPPY_10")
    if highscores["FLAPPY BIRD"] >= 25:
        unlock_achievement("FLAPPY_25")
    if highscores["FLAPPY BIRD"] >= 50:
        unlock_achievement("FLAPPY_50")

    
    if highscores["BRICK BREAKER"] >= 500:
        unlock_achievement("BREAKOUT_500")
    if highscores["BRICK BREAKER"] >= 2000:
        unlock_achievement("BREAKOUT_2000")
    if breakout_level >= 5:
        unlock_achievement("BREAKOUT_LEVEL5")

    
    if highscores["2048"] >= 512:
        unlock_achievement("2048_512")
    if highscores["2048"] >= 1024:
        unlock_achievement("2048_1024")
    if highscores["2048"] >= 2048:
        unlock_achievement("2048_2048")
    if highscores["2048"] >= 4096:
        unlock_achievement("2048_4096")

    
    if pong_wins >= 1:
        unlock_achievement("PONG_1")
    if pong_wins >= 5:
        unlock_achievement("PONG_5")
    if pong_wins >= 10:
        unlock_achievement("PONG_10")

    
    wordle_wins = highscores.get("WORDLE_WINS", 0)
    if wordle_wins >= 1:
        unlock_achievement("WORDLE_1")
    if wordle_wins >= 5:
        unlock_achievement("WORDLE_5")
    if wordle_wins >= 10:
        unlock_achievement("WORDLE_10")



CHALLENGE_TYPES = {
    "EASY": {
        "icon": "⭐",
        "color": GREEN,
        "xp_reward": 25,
        "coins_reward": 50,
        "description": "Easy challenge"
    },
    "MEDIUM": {
        "icon": "⭐⭐",
        "color": YELLOW,
        "xp_reward": 50,
        "coins_reward": 100,
        "description": "Medium challenge"
    },
    "HARD": {
        "icon": "⭐⭐⭐",
        "color": RED,
        "xp_reward": 100,
        "coins_reward": 200,
        "description": "Hard challenge"
    },
    "EXPERT": {
        "icon": "🏆",
        "color": PURPLE,
        "xp_reward": 200,
        "coins_reward": 400,
        "description": "Expert challenge"
    }
}


DAILY_CHALLENGES = {
    
    "SNAKE_SCORE_10": {
        "name": "Snake Beginner",
        "description": "Score 10 points in Snake",
        "game": "SNAKE",
        "target": 10,
        "type": "score",
        "difficulty": "EASY"
    },
    "SNAKE_SCORE_25": {
        "name": "Snake Master",
        "description": "Score 25 points in Snake",
        "game": "SNAKE",
        "target": 25,
        "type": "score",
        "difficulty": "MEDIUM"
    },
    "SNAKE_SCORE_50": {
        "name": "Snake Legend",
        "description": "Score 50 points in Snake",
        "game": "SNAKE",
        "target": 50,
        "type": "score",
        "difficulty": "HARD"
    },
    
    
    "TETRIS_SCORE_1000": {
        "name": "Tetris Player",
        "description": "Score 1,000 points in Tetris",
        "game": "TETRIS",
        "target": 1000,
        "type": "score",
        "difficulty": "EASY"
    },
    "TETRIS_SCORE_5000": {
        "name": "Tetris Pro",
        "description": "Score 5,000 points in Tetris",
        "game": "TETRIS",
        "target": 5000,
        "type": "score",
        "difficulty": "MEDIUM"
    },
    "TETRIS_SCORE_10000": {
        "name": "Tetris Master",
        "description": "Score 10,000 points in Tetris",
        "game": "TETRIS",
        "target": 10000,
        "type": "score",
        "difficulty": "HARD"
    },
    
    
    "FLAPPY_SCORE_10": {
        "name": "Flappy Novice",
        "description": "Score 10 in Flappy Bird",
        "game": "FLAPPY BIRD",
        "target": 10,
        "type": "score",
        "difficulty": "EASY"
    },
    "FLAPPY_SCORE_25": {
        "name": "Flappy Flyer",
        "description": "Score 25 in Flappy Bird",
        "game": "FLAPPY BIRD",
        "target": 25,
        "type": "score",
        "difficulty": "MEDIUM"
    },
    "FLAPPY_SCORE_50": {
        "name": "Flappy Master",
        "description": "Score 50 in Flappy Bird",
        "game": "FLAPPY BIRD",
        "target": 50,
        "type": "score",
        "difficulty": "HARD"
    },
    
    
    "RACING_SCORE_500": {
        "name": "Speed Racer",
        "description": "Score 500 in Racing",
        "game": "RACING",
        "target": 500,
        "type": "score",
        "difficulty": "EASY"
    },
    "RACING_SCORE_1000": {
        "name": "Racing Pro",
        "description": "Score 1,000 in Racing",
        "game": "RACING",
        "target": 1000,
        "type": "score",
        "difficulty": "MEDIUM"
    },
    "RACING_SCORE_2000": {
        "name": "Racing Champion",
        "description": "Score 2,000 in Racing",
        "game": "RACING",
        "target": 2000,
        "type": "score",
        "difficulty": "HARD"
    },
    
    
    "MINESWEEPER_WIN_1": {
        "name": "Mine Hunter",
        "description": "Win 1 Minesweeper game",
        "game": "MINESWEEPER",
        "target": 1,
        "type": "wins",
        "difficulty": "EASY"
    },
    "MINESWEEPER_WIN_3": {
        "name": "Mine Expert",
        "description": "Win 3 Minesweeper games",
        "game": "MINESWEEPER",
        "target": 3,
        "type": "wins",
        "difficulty": "MEDIUM"
    },
    "MINESWEEPER_WIN_5": {
        "name": "Mine Legend",
        "description": "Win 5 Minesweeper games",
        "game": "MINESWEEPER",
        "target": 5,
        "type": "wins",
        "difficulty": "HARD"
    },
    
    
    "WORDLE_WIN_1": {
        "name": "Wordle Novice",
        "description": "Win 1 Wordle game",
        "game": "WORDLE",
        "target": 1,
        "type": "wins",
        "difficulty": "EASY"
    },
    "WORDLE_WIN_3": {
        "name": "Wordle Player",
        "description": "Win 3 Wordle games",
        "game": "WORDLE",
        "target": 3,
        "type": "wins",
        "difficulty": "MEDIUM"
    },
    "WORDLE_WIN_5": {
        "name": "Wordle Master",
        "description": "Win 5 Wordle games",
        "game": "WORDLE",
        "target": 5,
        "type": "wins",
        "difficulty": "HARD"
    },
    "WORDLE_PERFECT_1": {
        "name": "Perfect Wordler",
        "description": "Win a Wordle game in 1 guess",
        "game": "WORDLE",
        "target": 1,
        "type": "perfect",
        "difficulty": "EXPERT"
    },
    
    
    "PONG_WIN_1": {
        "name": "Pong Beginner",
        "description": "Win 1 Pong match",
        "game": "PONG",
        "target": 1,
        "type": "wins",
        "difficulty": "EASY"
    },
    "PONG_WIN_3": {
        "name": "Pong Player",
        "description": "Win 3 Pong matches",
        "game": "PONG",
        "target": 3,
        "type": "wins",
        "difficulty": "MEDIUM"
    },
    "PONG_WIN_5": {
        "name": "Pong Champion",
        "description": "Win 5 Pong matches",
        "game": "PONG",
        "target": 5,
        "type": "wins",
        "difficulty": "HARD"
    },
    
    
    "BRICK_SCORE_500": {
        "name": "Brick Breaker Novice",
        "description": "Score 500 in Brick Breaker",
        "game": "BRICK BREAKER",
        "target": 500,
        "type": "score",
        "difficulty": "EASY"
    },
    "BRICK_SCORE_1000": {
        "name": "Brick Breaker Pro",
        "description": "Score 1,000 in Brick Breaker",
        "game": "BRICK BREAKER",
        "target": 1000,
        "type": "score",
        "difficulty": "MEDIUM"
    },
    "BRICK_SCORE_2000": {
        "name": "Brick Breaker Master",
        "description": "Score 2,000 in Brick Breaker",
        "game": "BRICK BREAKER",
        "target": 2000,
        "type": "score",
        "difficulty": "HARD"
    },
    
    
    "2048_512": {
        "name": "2048 Starter",
        "description": "Reach 512 in 2048",
        "game": "2048",
        "target": 512,
        "type": "score",
        "difficulty": "EASY"
    },
    "2048_1024": {
        "name": "2048 Player",
        "description": "Reach 1,024 in 2048",
        "game": "2048",
        "target": 1024,
        "type": "score",
        "difficulty": "MEDIUM"
    },
    "2048_2048": {
        "name": "2048 Master",
        "description": "Reach 2,048 in 2048",
        "game": "2048",
        "target": 2048,
        "type": "score",
        "difficulty": "HARD"
    },
    "2048_4096": {
        "name": "2048 Legend",
        "description": "Reach 4,096 in 2048",
        "game": "2048",
        "target": 4096,
        "type": "score",
        "difficulty": "EXPERT"
    },
    
    
    "MEMORY_30": {
        "name": "Memory Novice",
        "description": "Finish Memory Cards in 30 moves",
        "game": "MEMORY CARDS",
        "target": 30,
        "type": "low_score",
        "difficulty": "EASY"
    },
    "MEMORY_20": {
        "name": "Memory Pro",
        "description": "Finish Memory Cards in 20 moves",
        "game": "MEMORY CARDS",
        "target": 20,
        "type": "low_score",
        "difficulty": "MEDIUM"
    },
    "MEMORY_15": {
        "name": "Memory Master",
        "description": "Finish Memory Cards in 15 moves",
        "game": "MEMORY CARDS",
        "target": 15,
        "type": "low_score",
        "difficulty": "HARD"
    },
    
    
    "TICTACTOE_WIN_3": {
        "name": "Tic Tac Toe Player",
        "description": "Win 3 Tic Tac Toe games",
        "game": "TIC TAC TOE",
        "target": 3,
        "type": "wins",
        "difficulty": "EASY"
    },
    "TICTACTOE_WIN_5": {
        "name": "Tic Tac Toe Pro",
        "description": "Win 5 Tic Tac Toe games",
        "game": "TIC TAC TOE",
        "target": 5,
        "type": "wins",
        "difficulty": "MEDIUM"
    },
    "TICTACTOE_WIN_10": {
        "name": "Tic Tac Toe Champion",
        "description": "Win 10 Tic Tac Toe games",
        "game": "TIC TAC TOE",
        "target": 10,
        "type": "wins",
        "difficulty": "HARD"
    }
}

def get_daily_challenges():
    
    today = time.strftime("%Y-%m-%d")
    
    if os.path.exists(DAILY_CHALLENGE_FILE):
        try:
            with open(DAILY_CHALLENGE_FILE, "r") as file:
                data = json.load(file)
                if data.get("date") == today:
                    return data.get("challenges", [])
        except:
            pass
    
    
    challenges = generate_daily_challenges()
    
    try:
        with open(DAILY_CHALLENGE_FILE, "w") as file:
            json.dump({"date": today, "challenges": challenges}, file, indent=4)
    except:
        pass
    
    return challenges

def generate_daily_challenges():
    
    challenges = []
    
    easy = []
    medium = []
    hard = []
    expert = []
    
    for challenge_id, challenge in DAILY_CHALLENGES.items():
        difficulty = challenge["difficulty"]
        if difficulty == "EASY":
            easy.append(challenge_id)
        elif difficulty == "MEDIUM":
            medium.append(challenge_id)
        elif difficulty == "HARD":
            hard.append(challenge_id)
        elif difficulty == "EXPERT":
            expert.append(challenge_id)
    
    if easy:
        challenges.append(random.choice(easy))
    if medium:
        challenges.append(random.choice(medium))
    if hard:
        challenges.append(random.choice(hard))
    if expert and random.random() < 0.3:
        challenges.append(random.choice(expert))
    
    return challenges

def check_challenge_progress(challenge_id, game_name, score):
    
    if challenge_id not in DAILY_CHALLENGES:
        return False
    
    challenge = DAILY_CHALLENGES[challenge_id]
    
    if challenge["game"] != game_name:
        return False
    
    challenge_type = challenge["type"]
    target = challenge["target"]
    
    if challenge_type == "score" or challenge_type == "perfect":
        return score >= target
    elif challenge_type == "low_score":
        return score <= target and score > 0
    elif challenge_type == "wins":
        wins = highscores.get(game_name, 0)
        return wins >= target
    
    return False

def complete_challenge(challenge_id):
    
    global player_data
    
    if challenge_id not in DAILY_CHALLENGES:
        return False, "Challenge not found!"
    
    challenge = DAILY_CHALLENGES[challenge_id]
    difficulty = challenge["difficulty"]
    difficulty_data = CHALLENGE_TYPES[difficulty]
    
    xp_reward = difficulty_data["xp_reward"]
    coins_reward = difficulty_data["coins_reward"]
    
    add_xp(xp_reward)
    add_coins(coins_reward)
    
    if "completed_challenges" not in player_data:
        player_data["completed_challenges"] = []
    
    if challenge_id not in player_data["completed_challenges"]:
        player_data["completed_challenges"].append(challenge_id)
        save_player_data(player_data)
    
    return True, (
        f"Challenge Complete! +{challenge_reward(coins_reward)} coins, "
        f"+{challenge_reward(xp_reward)} XP"
    )

def is_challenge_completed(challenge_id):
    
    completed = player_data.get("completed_challenges", [])
    return challenge_id in completed



def daily_challenge_menu():
    
    challenges = get_daily_challenges()
    back_button = pygame.Rect(190, 530, 220, 45)
    refresh_button = pygame.Rect(190, 480, 220, 40)
    
    message = ""
    message_time = 0
    message_color = WHITE
    
    while True:
        current_time = pygame.time.get_ticks()
        screen.fill(get_theme_style()["background"])
        
        draw_text("DAILY CHALLENGES", big_font, YELLOW, WIDTH // 2, 40)
        draw_text(f"Complete challenges for bonus rewards!", small_font, WHITE, WIDTH // 2, 80)
        
        completed_count = sum(1 for c in challenges if is_challenge_completed(c))
        draw_text(f"Progress: {completed_count}/{len(challenges)}", font, GREEN, WIDTH // 2, 110)
        
        y = 150
        for i, challenge_id in enumerate(challenges):
            if challenge_id not in DAILY_CHALLENGES:
                continue
            
            challenge = DAILY_CHALLENGES[challenge_id]
            difficulty = challenge["difficulty"]
            difficulty_data = CHALLENGE_TYPES[difficulty]
            completed = is_challenge_completed(challenge_id)
            
            rect = pygame.Rect(50, y, 500, 65)
            
            if completed:
                pygame.draw.rect(screen, (30, 60, 40), rect, border_radius=10)
                pygame.draw.rect(screen, GREEN, rect, 2, border_radius=10)
                icon = "✅"
            else:
                pygame.draw.rect(screen, (30, 33, 50), rect, border_radius=10)
                pygame.draw.rect(screen, (60, 60, 80), rect, 1, border_radius=10)
                icon = difficulty_data["icon"]
            
            draw_text(f"{icon} {challenge['name']}", font, difficulty_data["color"] if not completed else WHITE, 170, y + 15)
            draw_text(challenge["description"], small_font, WHITE, 170, y + 40)
            
            if not completed:
                draw_text(f"+{challenge_reward(difficulty_data['coins_reward'])}🪙", small_font, YELLOW, 480, y + 15)
                draw_text(f"+{challenge_reward(difficulty_data['xp_reward'])}⭐", small_font, GREEN, 480, y + 40)
            else:
                draw_text("COMPLETED!", small_font, GREEN, 480, y + 30)
            
            y += 80
        
        if message:
            if current_time - message_time < 3000:
                draw_text(message, font, message_color, WIDTH // 2, 470)
            else:
                message = ""
        
        draw_button(refresh_button, "REFRESH CHALLENGES", BUTTON_BLUE, BUTTON_BLUE_HOVER)
        draw_button(back_button, "BACK", BUTTON_GRAY, BUTTON_GRAY_HOVER)
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if back_button.collidepoint(event.pos):
                        return
                    
                    if refresh_button.collidepoint(event.pos):
                        if os.path.exists(DAILY_CHALLENGE_FILE):
                            os.remove(DAILY_CHALLENGE_FILE)
                        challenges = get_daily_challenges()
                        message = "Challenges refreshed!"
                        message_color = GREEN
                        message_time = current_time
        
        clock.tick(60)



def launch_game(game):
    game_name = game[0]
    game_function = game[3]

    stop_music()
    game_function()

    reward = GAME_REWARDS.get(game_name, {"coins": 5, "xp": 5})
    reward_game_played(game_name, reward["coins"], reward["xp"])
    
    
    challenges = get_daily_challenges()
    for challenge_id in challenges:
        if not is_challenge_completed(challenge_id):
            score = highscores.get(game_name, 0)
            if check_challenge_progress(challenge_id, game_name, score):
                success, msg = complete_challenge(challenge_id)
                if success:
                    draw_text(f"🏆 {msg}", font, YELLOW, WIDTH // 2, 50)
                    pygame.display.flip()
                    pygame.time.wait(1500)
    
    current_user = get_current_session()
    if current_user:
        save_current_account(current_user)



def start_menu():
    start_button = pygame.Rect(190, 140, 220, 50)
    shop_button = pygame.Rect(190, 200, 220, 50)
    profile_button = pygame.Rect(190, 260, 220, 50)
    challenges_button = pygame.Rect(190, 320, 220, 45)
    account_button = pygame.Rect(190, 375, 220, 45)
    daily_button = pygame.Rect(190, 430, 220, 45)

    daily_message = ""
    daily_message_time = 0

    play_menu_music()
    while True:
        current_time = pygame.time.get_ticks()

        screen.fill(get_theme_style()["background"])

        draw_text("MINI GAMES", big_font, GREEN, WIDTH // 2, 90)

        draw_button(start_button, "START GAME", BUTTON_GREEN, BUTTON_GREEN_HOVER)
        draw_button(shop_button, "SHOP", BUTTON_ORANGE, BUTTON_ORANGE_HOVER)
        draw_button(profile_button, "PROFILE", BUTTON_PURPLE, BUTTON_PURPLE_HOVER)
        draw_button(challenges_button, "DAILY CHALLENGES", BUTTON_BLUE, BUTTON_BLUE_HOVER)
        draw_button(account_button, "ACCOUNTS", BUTTON_BLUE, BUTTON_BLUE_HOVER)

        if "DAILY_BONUS" in player_data["unlocked"]["features"]:
            bonus, streak_or_time = get_daily_bonus()
            if bonus is not None:
                draw_button(daily_button, f"DAILY BONUS (+{bonus})", BUTTON_GREEN, BUTTON_GREEN_HOVER)
            else:
                draw_button(daily_button, f"DAILY BONUS ({streak_or_time})", BUTTON_GRAY, BUTTON_GRAY_HOVER)

        current_user = get_current_session()
        if current_user:
            draw_text(f"✓ {current_user}", small_font, GREEN, WIDTH // 2, 480)
        else:
            draw_text("Not logged in", small_font, RED, WIDTH // 2, 480)

        draw_text(f"Level {player_data['level']}", small_font, YELLOW, WIDTH // 2, 500)
        if player_data.get("challenge_mode", False):
            draw_text("CHALLENGE MODE: +50% REWARDS", small_font, RED, WIDTH // 2, 565)

        bar_width = 200
        bar_height = 10
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 515

        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=5)
        progress = get_xp_progress()
        fill_width = int(bar_width * progress / 100)
        if fill_width > 0:
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_width, bar_height), border_radius=5)

        draw_text(f"Coins: {get_coins()}", small_font, YELLOW, WIDTH // 2, 540)

        if daily_message:
            if current_time - daily_message_time < 2000:
                draw_text(daily_message, small_font, YELLOW, WIDTH // 2, 560)
            else:
                daily_message = ""

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if start_button.collidepoint(event.pos):
                        return
                    if shop_button.collidepoint(event.pos):
                        shop_menu()
                    if profile_button.collidepoint(event.pos):
                        profile_menu()
                    if challenges_button.collidepoint(event.pos):
                        daily_challenge_menu()
                    if account_button.collidepoint(event.pos):
                        account_menu()
                    if daily_button.collidepoint(event.pos) and "DAILY_BONUS" in player_data["unlocked"]["features"]:
                        success, bonus, streak = claim_daily_bonus()
                        if success:
                            daily_message = f"★ +{bonus} COINS! {streak} DAY STREAK! ★"
                            daily_message_time = pygame.time.get_ticks()
                        else:
                            daily_message = "Already claimed today!"
                            daily_message_time = pygame.time.get_ticks()



def achievement_menu():
    back_button = pygame.Rect(190, 480, 220, 45)
    scroll = 0
    achievement_list = list(ACHIEVEMENTS.items())

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_UP:
                    scroll -= 40
                if event.key == pygame.K_DOWN:
                    scroll += 40
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if back_button.collidepoint(event.pos):
                        return
                if event.button == 4:
                    scroll -= 40
                if event.button == 5:
                    scroll += 40

        total_height = len(achievement_list) * 75
        max_scroll = max(0, total_height - 350)
        scroll = max(0, min(scroll, max_scroll))

        screen.fill((12, 14, 25))

        draw_text("ACHIEVEMENTS", big_font, YELLOW, WIDTH // 2, 45)

        unlocked_count = sum(1 for value in achievements.values() if value)
        draw_text(f"{unlocked_count} / {len(ACHIEVEMENTS)} Unlocked", font, WHITE, WIDTH // 2, 90)

        start_y = 125

        for index, (achievement_id, achievement) in enumerate(achievement_list):
            y = start_y + index * 75 - scroll

            if y < 105 or y > 465:
                continue

            unlocked = achievements[achievement_id]

            rect = pygame.Rect(60, y, 480, 60)

            if unlocked:
                pygame.draw.rect(screen, (35, 80, 45), rect, border_radius=10)
                pygame.draw.rect(screen, GREEN, rect, 2, border_radius=10)
                icon = "✓"
                icon_color = GREEN
            else:
                pygame.draw.rect(screen, (40, 40, 50), rect, border_radius=10)
                pygame.draw.rect(screen, DARK_GRAY, rect, 2, border_radius=10)
                icon = "?"
                icon_color = GRAY

            draw_text(icon, font, icon_color, 90, y + 30)
            draw_text(achievement["name"], font, WHITE, 230, y + 20)
            draw_text(achievement["description"], small_font, GRAY, 280, y + 44)

        draw_button(back_button, "BACK", BUTTON_GRAY, BUTTON_GRAY_HOVER)
        draw_text("↑ ↓ / Mouse Wheel = Scroll", small_font, GRAY, WIDTH // 2, 535)

        pygame.display.flip()
        clock.tick(60)



def custom_theme_builder():
    if "CUSTOM" not in player_data["unlocked"]["themes"]:
        return

    slots = ("background", "panel", "accent")
    palette = [
        ("MIDNIGHT", (12, 14, 25)),
        ("NAVY", (18, 35, 75)),
        ("OCEAN", (10, 80, 105)),
        ("FOREST", (20, 75, 45)),
        ("PLUM", (65, 30, 85)),
        ("CHARCOAL", (45, 48, 58)),
        ("GOLD", (190, 125, 25)),
        ("CORAL", (190, 65, 70)),
        ("NEON", (20, 150, 115)),
    ]
    slot_buttons = [
        (pygame.Rect(45 + index * 175, 140, 160, 42), slot)
        for index, slot in enumerate(slots)
    ]
    color_buttons = [
        (pygame.Rect(65 + (index % 3) * 160, 220 + (index // 3) * 60, 130, 45), name, color)
        for index, (name, color) in enumerate(palette)
    ]
    back_button = pygame.Rect(200, 540, 200, 42)
    selected_slot = "background"

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.collidepoint(event.pos):
                    return
                for rect, slot in slot_buttons:
                    if rect.collidepoint(event.pos):
                        selected_slot = slot
                        break
                for rect, _, color in color_buttons:
                    if rect.collidepoint(event.pos):
                        player_data["cosmetics"]["custom_theme"][selected_slot] = list(color)
                        player_data["cosmetics"]["theme"] = "CUSTOM"
                        save_player_data(player_data)
                        current_user = get_current_session()
                        if current_user:
                            save_current_account(current_user)
                        break

        style = get_theme_style("CUSTOM")
        screen.fill(style["background"])
        draw_text("CUSTOM THEME BUILDER", big_font, WHITE, WIDTH // 2, 55)
        draw_text("Choose a color slot, then pick a palette color.", small_font, LIGHT_GRAY, WIDTH // 2, 100)

        for rect, slot in slot_buttons:
            active = selected_slot == slot
            pygame.draw.rect(screen, style["panel"], rect, border_radius=8)
            pygame.draw.rect(screen, style["accent"] if active else GRAY, rect, 2, border_radius=8)
            draw_text(slot.upper(), small_font, WHITE, rect.centerx, rect.centery)

        for rect, name, color in color_buttons:
            pygame.draw.rect(screen, color, rect, border_radius=8)
            active = color == style[selected_slot]
            pygame.draw.rect(screen, WHITE if active else DARK_GRAY, rect, 3 if active else 1, border_radius=8)
            draw_text(name, small_font, WHITE, rect.centerx, rect.centery)

        preview_rect = pygame.Rect(100, 425, 400, 75)
        pygame.draw.rect(screen, style["panel"], preview_rect, border_radius=12)
        pygame.draw.rect(screen, style["accent"], preview_rect, 3, border_radius=12)
        draw_text("PREVIEW", font, style["accent"], preview_rect.centerx, preview_rect.centery)
        draw_button(back_button, "DONE", BUTTON_GRAY, BUTTON_GRAY_HOVER)
        pygame.display.flip()
        clock.tick(60)


def profile_menu():
    back_button = pygame.Rect(200, 545, 200, 42)
    builder_button = pygame.Rect(320, 495, 240, 38)

    themes = ["DEFAULT", "DARK", "NEON", "RETRO", "OCEAN", "CUSTOM"]
    theme_buttons = [
        (pygame.Rect(300 + (index % 3) * 92, 200 + (index // 3) * 58, 84, 48), theme)
        for index, theme in enumerate(themes)
    ]

    colors = ["GREEN", "BLUE", "WHITE", "YELLOW", "GOLD", "PURPLE", "PINK", "RED", "ORANGE"]
    color_buttons = [
        (pygame.Rect(320 + (index % 3) * 72, 365 + (index // 3) * 40, 32, 30), color)
        for index, color in enumerate(colors)
    ]
    stat_scroll = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_UP:
                    stat_scroll -= 50
                if event.key == pygame.K_DOWN:
                    stat_scroll += 50
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_button.collidepoint(event.pos):
                    return
                if builder_button.collidepoint(event.pos) and "CUSTOM" in player_data["unlocked"]["themes"]:
                    custom_theme_builder()
                for rect, theme in theme_buttons:
                    if rect.collidepoint(event.pos) and theme in player_data["unlocked"]["themes"]:
                        player_data["cosmetics"]["theme"] = theme
                        save_player_data(player_data)
                        current_user = get_current_session()
                        if current_user:
                            save_current_account(current_user)
                for rect, color in color_buttons:
                    if rect.collidepoint(event.pos) and color in player_data["unlocked"]["colors"]:
                        for cosmetic in ("snake_color", "paddle_color", "ball_color",
                                         "player_color", "car_color", "bird_color"):
                            player_data["cosmetics"][cosmetic] = color
                        save_player_data(player_data)
            if event.type == pygame.MOUSEWHEEL:
                stat_scroll -= event.y * 30

        style = get_theme_style()
        screen.fill(style["background"])

        current_user = get_current_session()
        draw_text(
            f"Account: {current_user}" if current_user else "No account logged in",
            small_font, GREEN if current_user else RED, WIDTH // 2, 15,
        )
        draw_text("PROFILE", big_font, WHITE, WIDTH // 2, 50)
        draw_text(f"Level {player_data['level']}", font, YELLOW, WIDTH // 2, 90)

        bar_width = 300
        bar_height = 20
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 115
        pygame.draw.rect(screen, style["panel"], (bar_x, bar_y, bar_width, bar_height), border_radius=10)
        progress = get_xp_progress()
        fill_width = int(bar_width * progress / 100)
        if fill_width > 0:
            pygame.draw.rect(screen, style["accent"], (bar_x, bar_y, fill_width, bar_height), border_radius=10)
        draw_text(
            f"{player_data['xp']} / {get_next_level_xp()} XP",
            small_font, WHITE, WIDTH // 2, bar_y + bar_height + 18,
        )

        draw_text("STATISTICS", font, WHITE, 100, 170)
        stats = [
            f"Games Played: {player_data['total_games_played']}",
            f"Total Score: {player_data['total_score']}",
            f"Coins: {player_data['coins']}",
            f"Level: {player_data['level']}",
            f"XP: {player_data['xp']}",
        ]
        for index, stat in enumerate(stats):
            y = 200 + stat_scroll + index * 25
            if 170 < y < 470:
                draw_text(stat, small_font, WHITE, 100, y)

        draw_text("THEMES", font, WHITE, 430, 175)
        for rect, theme in theme_buttons:
            unlocked = theme in player_data["unlocked"]["themes"]
            active = player_data["cosmetics"].get("theme") == theme
            theme_color = get_theme_style(theme)["panel"] if unlocked else style["panel"]
            pygame.draw.rect(screen, theme_color, rect, border_radius=8)
            pygame.draw.rect(
                screen,
                style["accent"] if active else (GRAY if unlocked else DARK_GRAY),
                rect, 3 if active else 1, border_radius=8,
            )
            draw_text(theme if unlocked else "LOCKED", small_font, WHITE if unlocked else GRAY,
                      rect.centerx, rect.centery)

        draw_text("PLAYER COLORS", font, WHITE, 430, 345)
        for rect, color in color_buttons:
            unlocked = color in player_data["unlocked"]["colors"]
            active = player_data["cosmetics"].get("snake_color") == color
            pygame.draw.rect(screen, get_color_from_choice(color) if unlocked else style["panel"], rect, border_radius=6)
            if active:
                pygame.draw.rect(screen, style["accent"], rect, 3, border_radius=6)
            elif not unlocked:
                draw_text("x", small_font, GRAY, rect.centerx, rect.centery)

        if "CUSTOM" in player_data["unlocked"]["themes"]:
            draw_button(builder_button, "CUSTOMIZE THEME", BUTTON_PURPLE, BUTTON_PURPLE_HOVER)
        else:
            pygame.draw.rect(screen, style["panel"], builder_button, border_radius=10)
            draw_text("BUY BUILDER IN SHOP", small_font, GRAY, builder_button.centerx, builder_button.centery)
        draw_button(back_button, "BACK", BUTTON_GRAY, BUTTON_GRAY_HOVER)
        pygame.display.flip()
        clock.tick(60)



def account_menu():
    
    current_user = get_current_session()
    
    if current_user:
        switch_account(current_user)
    
    selected_account = None
    message = ""
    message_color = WHITE
    message_time = 0
    
    while True:
        current_time = pygame.time.get_ticks()
        screen.fill((15, 18, 30))
        
        draw_text("ACCOUNTS", big_font, YELLOW, WIDTH // 2, 40)
        
        if current_user:
            draw_text(f"✓ Logged in as: {current_user}", font, GREEN, WIDTH // 2, 85)
        else:
            draw_text("Not logged in", font, RED, WIDTH // 2, 85)
        
        accounts = list_accounts()
        
        if accounts:
            draw_text("Your Accounts:", font, WHITE, WIDTH // 2, 125)
            
            y = 160
            for i, account in enumerate(accounts):
                rect = pygame.Rect(150, y, 300, 40)
                
                if current_user == account:
                    pygame.draw.rect(screen, (40, 80, 50), rect, border_radius=8)
                    pygame.draw.rect(screen, GREEN, rect, 2, border_radius=8)
                    draw_text(f"▶ {account}", font, WHITE, WIDTH // 2, y + 20)
                elif selected_account == account:
                    pygame.draw.rect(screen, (50, 50, 80), rect, border_radius=8)
                    pygame.draw.rect(screen, YELLOW, rect, 2, border_radius=8)
                    draw_text(account, font, WHITE, WIDTH // 2, y + 20)
                else:
                    pygame.draw.rect(screen, (30, 33, 50), rect, border_radius=8)
                    draw_text(account, font, WHITE, WIDTH // 2, y + 20)
                
                y += 50
        else:
            draw_text("No accounts yet!", font, GRAY, WIDTH // 2, 200)
            draw_text("Create one below:", font, GRAY, WIDTH // 2, 230)
        
        create_btn = pygame.Rect(150, 400, 300, 40)
        login_btn = pygame.Rect(150, 450, 300, 40)
        delete_btn = pygame.Rect(150, 500, 300, 40)
        back_btn = pygame.Rect(150, 550, 300, 35)
        
        if current_user:
            draw_button(create_btn, "CREATE NEW ACCOUNT", BUTTON_GREEN, BUTTON_GREEN_HOVER)
            draw_button(login_btn, f"LOGOUT ({current_user})", BUTTON_RED, BUTTON_RED_HOVER)
        else:
            draw_button(create_btn, "CREATE ACCOUNT", BUTTON_GREEN, BUTTON_GREEN_HOVER)
            draw_button(login_btn, "LOGIN", BUTTON_BLUE, BUTTON_BLUE_HOVER)
        
        draw_button(delete_btn, "DELETE ACCOUNT", BUTTON_RED, BUTTON_RED_HOVER)
        draw_button(back_btn, "BACK", BUTTON_GRAY, BUTTON_GRAY_HOVER)
        
        if message:
            if current_time - message_time < 3000:
                draw_text(message, small_font, message_color, WIDTH // 2, 375)
            else:
                message = ""
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    y = 160
                    for i, account in enumerate(accounts):
                        rect = pygame.Rect(150, y, 300, 40)
                        if rect.collidepoint(event.pos):
                            selected_account = account
                        y += 50
                    
                    if create_btn.collidepoint(event.pos):
                        create_account_menu()
                    
                    if login_btn.collidepoint(event.pos):
                        if current_user:
                            success, msg = logout_account()
                            if success:
                                current_user = None
                                selected_account = None
                                message = msg
                                message_color = GREEN
                                message_time = current_time
                            else:
                                message = msg
                                message_color = RED
                                message_time = current_time
                        else:
                            if selected_account:
                                success, msg = switch_account(selected_account)
                                if success:
                                    current_user = selected_account
                                    message = msg
                                    message_color = GREEN
                                    message_time = current_time
                                else:
                                    message = msg
                                    message_color = RED
                                    message_time = current_time
                            else:
                                message = "Select an account first!"
                                message_color = RED
                                message_time = current_time
                    
                    if delete_btn.collidepoint(event.pos):
                        if selected_account:
                            if selected_account == current_user:
                                success, msg = delete_account_with_data(selected_account)
                                if success:
                                    current_user = None
                                    message = f"Account '{selected_account}' deleted!"
                                    message_color = GREEN
                                    message_time = current_time
                                    selected_account = None
                                    accounts = list_accounts()
                                else:
                                    message = msg
                                    message_color = RED
                                    message_time = current_time
                            else:
                                success, msg = delete_account(selected_account)
                                if success:
                                    message = f"Account '{selected_account}' deleted!"
                                    message_color = GREEN
                                    message_time = current_time
                                    selected_account = None
                                    accounts = list_accounts()
                                else:
                                    message = msg
                                    message_color = RED
                                    message_time = current_time
                        else:
                            message = "Select an account first!"
                            message_color = RED
                            message_time = current_time
                    
                    if back_btn.collidepoint(event.pos):
                        if current_user:
                            save_current_account(current_user)
                        return

def create_account_menu():
    
    username = ""
    message = ""
    message_color = WHITE
    message_time = 0
    
    while True:
        current_time = pygame.time.get_ticks()
        screen.fill((15, 18, 30))
        
        draw_text("CREATE ACCOUNT", big_font, YELLOW, WIDTH // 2, 60)
        
        draw_text("Username (letters and numbers only):", font, WHITE, WIDTH // 2, 140)
        
        input_rect = pygame.Rect(150, 180, 300, 50)
        pygame.draw.rect(screen, (30, 33, 50), input_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, input_rect, 2, border_radius=10)
        
        display_text = username if username else "Enter username..."
        draw_text(display_text, font, WHITE if username else GRAY, WIDTH // 2, 205)
        
        draw_text(f"{len(username)}/20", small_font, GRAY, WIDTH // 2, 250)
        
        create_btn = pygame.Rect(150, 320, 300, 50)
        back_btn = pygame.Rect(150, 390, 300, 45)
        
        draw_button(create_btn, "CREATE", BUTTON_GREEN, BUTTON_GREEN_HOVER)
        draw_button(back_btn, "BACK", BUTTON_GRAY, BUTTON_GRAY_HOVER)
        
        if message:
            if current_time - message_time < 3000:
                draw_text(message, font, message_color, WIDTH // 2, 300)
            else:
                message = ""
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_RETURN:
                    if username:
                        success, msg = create_account(username)
                        if success:
                            message = msg
                            message_color = GREEN
                            message_time = current_time
                            switch_account(username)
                            pygame.time.wait(500)
                            return
                        else:
                            message = msg
                            message_color = RED
                            message_time = current_time
                    else:
                        message = "Please enter a username!"
                        message_color = RED
                        message_time = current_time
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    if len(username) < 20 and event.unicode.isalnum():
                        username += event.unicode.upper()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if create_btn.collidepoint(event.pos):
                        if username:
                            success, msg = create_account(username)
                            if success:
                                message = msg
                                message_color = GREEN
                                message_time = current_time
                                switch_account(username)
                                pygame.time.wait(500)
                                return
                            else:
                                message = msg
                                message_color = RED
                                message_time = current_time
                        else:
                            message = "Please enter a username!"
                            message_color = RED
                            message_time = current_time
                    if back_btn.collidepoint(event.pos):
                        return



def game_select_menu():
    games = [
        ("SNAKE", "S", "Eat the food and don't hit yourself!", snake_game, GREEN),
        ("TIC TAC TOE", "X", "Get three in a row!", tic_tac_toe, BLUE),
        ("MINESWEEPER", "!", "Find the mines without exploding!", minesweeper, RED),
        ("MEMORY CARDS", "?", "Find all the matching pairs!", memory_game, PURPLE),
        ("TETRIS", "T", "Clear lines and survive!", tetris_game, ORANGE),
        ("RACING", "R", "Avoid traffic and drive as far as possible!", racing_game, CYAN),
        ("FLAPPY BIRD", "F", "Fly through the pipes!", flappy_bird, YELLOW),
        ("BRICK BREAKER", "B", "Break all the bricks and don't lose the ball!", brick_breaker, LIGHT_BLUE),
        ("2048", "🔢", "Join numbers into a big number!", game_2048, LIGHT_PURPLE),
        ("PONG", "🏓", "Try to catch the ball and throw it away!", pong_game, LIGHT_ORANGE),
        ("WORDLE", "W", "Guess the 5-letter word!", wordle_game, (83, 141, 78)),
        ("SPACE INVADERS", "A", "Defend Earth from waves of aliens!", space_invaders_game, (80, 220, 180)),
        ("PAC-MAN", "P", "Eat the pellets and avoid the ghosts!", pacman_game, (255, 215, 0)),
        ("FRUIT NINJA", "F", "Slice fruit as it flies across the screen!", fruit_ninja_game, (255, 100, 90)),
    ]

    selected = 0
    display_selected = 0.0
    animation_speed = 8

    play_button = pygame.Rect(WIDTH // 2 - 110, 420, 220, 60)
    achievement_button = pygame.Rect(WIDTH // 2 - 110, 475, 220, 45)
    settings_button = pygame.Rect(WIDTH - 45, 15, 30, 30)  

    play_menu_music()
    while True:
        dt = clock.get_time() / 1000
        display_selected += (selected - display_selected) * min(1, dt * animation_speed)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_LEFT:
                    selected -= 1
                    if selected < 0:
                        selected = len(games) - 1
                elif event.key == pygame.K_RIGHT:
                    selected += 1
                    if selected >= len(games):
                        selected = 0
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    launch_game(games[selected])
                    play_menu_music()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_button.collidepoint(event.pos):
                        launch_game(games[selected])
                        play_menu_music()
                    elif achievement_button.collidepoint(event.pos):
                        achievement_menu()
                    elif settings_button.collidepoint(event.pos):
                        settings_menu()

        theme_style = get_theme_style()
        screen.fill(theme_style["background"])

        draw_text("GAME SELECT", big_font, WHITE, WIDTH // 2, 50)
        draw_text(f"{selected + 1} / {len(games)}", font, GRAY, WIDTH // 2, 100)
        draw_text(f"Level {player_data['level']}", small_font, YELLOW, WIDTH // 2, 125)
        if player_data.get("challenge_mode", False):
            draw_text("CHALLENGE MODE", small_font, RED, WIDTH // 2, 150)

        
        mouse_pos = pygame.mouse.get_pos()
        if settings_button.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (60, 70, 120), settings_button, border_radius=8)
        else:
            pygame.draw.rect(screen, (40, 50, 80), settings_button, border_radius=8)
        draw_text("⚙️", small_font, WHITE, WIDTH - 30, 30)

        center_x = WIDTH // 2
        center_y = 245
        card_width = 300
        card_height = 220

        for i, game in enumerate(games):
            name = game[0]
            icon = game[1]
            color = game[4]

            distance = i - display_selected

            if distance > len(games) / 2:
                distance -= len(games)
            if distance < -len(games) / 2:
                distance += len(games)

            if abs(distance) > 2:
                continue

            card_x = center_x + distance * 360 - card_width / 2
            scale = 1.0 - min(abs(distance) * 0.18, 0.45)
            current_width = int(card_width * scale)
            current_height = int(card_height * scale)
            card_y = center_y - current_height // 2

            rect = pygame.Rect(int(card_x), int(card_y), current_width, current_height)

            if i == selected:
                glow_rect = rect.inflate(20, 20)
                pygame.draw.rect(screen, color, glow_rect, border_radius=25)
                pygame.draw.rect(screen, (25, 28, 45), rect, border_radius=20)
                pygame.draw.rect(screen, color, rect, 5, border_radius=20)

                draw_text(icon, big_font, color, rect.centerx, rect.centery - 30)
                draw_text(name, font, WHITE, rect.centerx, rect.centery + 30)
            else:
                pygame.draw.rect(screen, (30, 32, 50), rect, border_radius=20)
                pygame.draw.rect(screen, (70, 70, 90), rect, 3, border_radius=20)
                draw_text(icon, font, color, rect.centerx, rect.centery)

        selected_game = games[selected]
        name = selected_game[0]
        description = selected_game[2]
        color = selected_game[4]

        draw_text(name, font, color, WIDTH // 2, 350)
        draw_text(description, small_font, WHITE, WIDTH // 2, 380)

        best_score = highscores[name]

        if name == "MEMORY CARDS":
            score_text = f"Best: {best_score} moves"
        elif name in ("TIC TAC TOE", "MINESWEEPER"):
            score_text = f"Wins: {best_score}"
        else:
            score_text = f"Best: {best_score}"

        draw_text(score_text, small_font, YELLOW, WIDTH // 2, 405)

        mouse = pygame.mouse.get_pos()

        if play_button.collidepoint(mouse):
            button_color = color
        else:
            button_color = (
                max(20, color[0] - 40),
                max(20, color[1] - 40),
                max(20, color[2] - 40)
            )

        pygame.draw.rect(screen, button_color, play_button, border_radius=15)
        pygame.draw.rect(screen, WHITE, play_button, 2, border_radius=15)
        draw_text("PLAY", font, WHITE, play_button.centerx, play_button.centery)

        draw_button(achievement_button, "ACHIEVEMENTS", BUTTON_PURPLE, BUTTON_PURPLE_HOVER)

        draw_text("<", big_font, WHITE, 45, center_y)
        draw_text(">", big_font, WHITE, WIDTH - 45, center_y)

        bar_width = 200
        bar_height = 8
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 525

        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=4)
        progress = get_xp_progress()
        fill_width = int(bar_width * progress / 100)
        if fill_width > 0:
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_width, bar_height), border_radius=4)

        draw_achievement_notification()

        pygame.display.flip()
        clock.tick(60)



def create_food(snake):
    while True:
        x = random.randrange(0, WIDTH, 20)
        y = random.randrange(0, 400, 20)
        if (x, y) not in snake:
            return x, y


def snake_game():
    play_music("SNAKE")

    invincible_active = False
    invincible_timer = 0
    invincible_duration = 10000

    extra_food_active = False

    snake = [(300, 200), (280, 200), (260, 200)]
    direction = (20, 0)

    food = create_food(snake)
    extra_food = None

    score = 0

    has_invincible = player_data["inventory"].get("SNAKE_INVINCIBLE", 0) > 0
    has_extra_food = player_data["inventory"].get("SNAKE_FOOD", 0) > 0

    powerup_used_this_game = {
        "invincible": False,
        "extra_food": False
    }

    while True:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return

                if event.key == pygame.K_1 and has_invincible and not powerup_used_this_game["invincible"]:
                    if use_powerup("SNAKE_INVINCIBLE"):
                        invincible_active = True
                        invincible_timer = current_time
                        powerup_used_this_game["invincible"] = True
                        has_invincible = player_data["inventory"].get("SNAKE_INVINCIBLE", 0) > 0

                if event.key == pygame.K_2 and has_extra_food and not powerup_used_this_game["extra_food"]:
                    if use_powerup("SNAKE_FOOD"):
                        extra_food_active = True
                        extra_food = create_food(snake)
                        powerup_used_this_game["extra_food"] = True
                        has_extra_food = player_data["inventory"].get("SNAKE_FOOD", 0) > 0

                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    if direction != (0, 20):
                        direction = (0, -20)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    if direction != (0, -20):
                        direction = (0, 20)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    if direction != (20, 0):
                        direction = (-20, 0)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    if direction != (-20, 0):
                        direction = (20, 0)

        if invincible_active:
            if current_time - invincible_timer > invincible_duration:
                invincible_active = False

        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        if (new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= 400):
            if not invincible_active:
                break
            else:
                if new_head[0] < 0:
                    new_head = (0, new_head[1])
                    direction = (20, 0)
                elif new_head[0] >= WIDTH:
                    new_head = (WIDTH - 20, new_head[1])
                    direction = (-20, 0)
                elif new_head[1] < 0:
                    new_head = (new_head[0], 0)
                    direction = (0, 20)
                elif new_head[1] >= 400:
                    new_head = (new_head[0], 400 - 20)
                    direction = (0, -20)

        if new_head in snake and not invincible_active:
            break

        snake.insert(0, new_head)

        ate_food = False
        if new_head == food:
            score += 1
            food = create_food(snake)
            ate_food = True

        if extra_food_active and new_head == extra_food:
            score += 1
            extra_food = None
            extra_food_active = False
            ate_food = True

        if not ate_food:
            snake.pop()

        screen.fill(BLACK)

        for i, (x, y) in enumerate(snake):
            if i == 0 and invincible_active:
                pygame.draw.rect(screen, YELLOW, (x, y, 20, 20))
                pygame.draw.rect(screen, (255, 255, 100), (x-2, y-2, 24, 24), 2)
            else:
                color = GREEN if i == 0 else DARK_GREEN
                pygame.draw.rect(screen, color, (x, y, 20, 20))

        pygame.draw.rect(screen, RED, (food[0], food[1], 20, 20))

        if extra_food_active and extra_food:
            pygame.draw.rect(screen, LIGHT_RED, (extra_food[0], extra_food[1], 20, 20))
            pygame.draw.rect(screen, YELLOW, (extra_food[0]-2, extra_food[1]-2, 24, 24), 2)

        draw_text(f"Score: {score}", font, WHITE, 70, 20)
        draw_text(f"Best: {highscores['SNAKE']}", small_font, YELLOW, 180, 20)

        powerup_y = 50
        if invincible_active:
            draw_text("✦ INVINCIBLE", small_font, YELLOW, 70, powerup_y)
            powerup_y += 25
        if extra_food_active:
            draw_text("✦ EXTRA FOOD", small_font, ORANGE, 70, powerup_y)

        if has_invincible and not powerup_used_this_game["invincible"]:
            draw_text("Press 1: Invincible", small_font, YELLOW, WIDTH - 150, 20)
        if has_extra_food and not powerup_used_this_game["extra_food"]:
            draw_text("Press 2: Extra Food", small_font, ORANGE, WIDTH - 150, 45)

        draw_text("ESC = Menu", small_font, GRAY, 530, 20)

        pygame.display.flip()
        clock.tick(13 if player_data.get("challenge_mode", False) else 10)

    new_record = update_highscore("SNAKE", score)
    check_achievements()
    snake_game_over(score, new_record)


def snake_game_over(score, new_record=False):
    xp_earned = calculate_xp_reward("SNAKE", score)
    level_up, new_level = add_xp(xp_earned)

    player_data["total_games_played"] += 1
    player_data["total_score"] += score
    save_player_data(player_data)

    coins_earned = score // 5 + 5
    add_coins(coins_earned)

    play_button = pygame.Rect(190, 220, 220, 60)
    menu_button = pygame.Rect(190, 300, 220, 50)

    level_up_text = ""
    level_up_timer = 0

    if level_up:
        level_up_text = f"★ LEVEL UP! Level {new_level} ★"
        level_up_timer = pygame.time.get_ticks()

    while True:
        current_time = pygame.time.get_ticks()
        if level_up_text and current_time - level_up_timer > 3000:
            level_up_text = ""

        screen.fill(BLACK)

        draw_text("GAME OVER", big_font, RED, WIDTH // 2, 60)
        draw_text(f"Score: {score}", font, WHITE, WIDTH // 2, 120)
        draw_text(f"Best: {highscores['SNAKE']}", font, YELLOW, WIDTH // 2, 155)

        draw_text(f"+{challenge_reward(xp_earned)} XP", font, GREEN, WIDTH // 2 - 80, 190)
        draw_text(f"+{challenge_reward(coins_earned)} Coins", font, YELLOW, WIDTH // 2 + 80, 190)

        if level_up_text:
            draw_text(level_up_text, font, YELLOW, WIDTH // 2, 220)

        if new_record:
            draw_text("★ NEW HIGH SCORE! ★", font, YELLOW, WIDTH // 2, 250)

        draw_button(play_button, "PLAY AGAIN", BUTTON_GREEN, BUTTON_GREEN_HOVER)
        draw_button(menu_button, "GAME MENU", BUTTON_GRAY, BUTTON_GRAY_HOVER)

        bar_width = 300
        bar_height = 15
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 380

        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height), border_radius=8)
        progress = get_xp_progress()
        fill_width = int(bar_width * progress / 100)
        if fill_width > 0:
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, fill_width, bar_height), border_radius=8)

        draw_text(f"Level {player_data['level']}", small_font, WHITE, WIDTH // 2, bar_y - 15)
        draw_text(f"{player_data['xp']} / {get_next_level_xp()} XP", small_font, GRAY, WIDTH // 2, bar_y + bar_height + 15)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_button.collidepoint(event.pos):
                        snake_game()
                        return
                    if menu_button.collidepoint(event.pos):
                        return



def tic_tac_toe():
    play_music("TIC TAC TOE")

    challenge_enabled = player_data.get("challenge_mode", False)
    has_bigger_board = player_data["inventory"].get("TICTACTOE_BOARD", 0) > 0
    use_bigger_board = False
    board_size = 3
    win_count = 3

    if challenge_enabled:
        board_size = 4
        win_count = 4

    if has_bigger_board and not challenge_enabled:
        if use_powerup("TICTACTOE_BOARD"):
            board_size = 4
            win_count = 4
            use_bigger_board = True

    board = [["" for _ in range(board_size)] for _ in range(board_size)]
    current_player = "X"
    winner = None

    cell_size = 80
    gap = 5
    total_size = board_size * cell_size + (board_size - 1) * gap
    board_x = (WIDTH - total_size) // 2
    board_y = 70

    def check_winner_board():
        for row in board:
            if all(cell == current_player for cell in row):
                return current_player

        for col in range(board_size):
            if all(board[row][col] == current_player for row in range(board_size)):
                return current_player

        if all(board[i][i] == current_player for i in range(board_size)):
            return current_player
        if all(board[i][board_size-1-i] == current_player for i in range(board_size)):
            return current_player

        if all(cell != "" for row in board for cell in row):
            return "DRAW"

        return None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and winner is None:
                    mx, my = event.pos
                    if board_x <= mx < board_x + total_size and board_y <= my < board_y + total_size:
                        col = (mx - board_x) // (cell_size + gap)
                        row = (my - board_y) // (cell_size + gap)
                        if row < board_size and col < board_size and board[row][col] == "":
                            board[row][col] = current_player
                            winner = check_winner_board()
                            if winner is None:
                                current_player = "O" if current_player == "X" else "X"

        screen.fill(BLACK)

        draw_text("TIC TAC TOE", big_font, WHITE, WIDTH // 2, 30)

        if use_bigger_board:
            draw_text("★ BIGGER BOARD ACTIVE", small_font, YELLOW, WIDTH // 2, 55)
        elif challenge_enabled:
            draw_text("CHALLENGE MODE: 4x4 BOARD", small_font, YELLOW, WIDTH // 2, 55)

        for row in range(board_size):
            for col in range(board_size):
                x = board_x + col * (cell_size + gap)
                y = board_y + row * (cell_size + gap)
                rect = pygame.Rect(x, y, cell_size, cell_size)
                pygame.draw.rect(screen, DARK_GRAY, rect, border_radius=5)
                pygame.draw.rect(screen, WHITE, rect, 2, border_radius=5)

                if board[row][col] == "X":
                    draw_text("X", big_font, RED, x + cell_size//2, y + cell_size//2)
                elif board[row][col] == "O":
                    draw_text("O", big_font, BLUE, x + cell_size//2, y + cell_size//2)

        draw_text(f"Wins: {highscores['TIC TAC TOE']}", small_font, YELLOW, WIDTH // 2, 500)

        if winner == "DRAW":
            draw_text("DRAW!", font, YELLOW, WIDTH // 2, 440)
        elif winner:
            update_highscore("TIC TAC TOE", highscores["TIC TAC TOE"] + 1)
            check_achievements()
            draw_text(f"{winner} WINS!", font, GREEN, WIDTH // 2, 440)
        else:
            draw_text(f"{current_player}'s turn", font, WHITE, WIDTH // 2, 440)

        pygame.display.flip()

        if winner:
            pygame.time.wait(1500)
            return

        clock.tick(60)



def minesweeper():
    play_music("MINESWEEPER")

    ROWS = 10
    COLS = 10
    MINES = 20 if player_data.get("challenge_mode", False) else 15
    CELL = 35

    has_scanner = player_data["inventory"].get("MINESWEEPER_SCAN", 0) > 0
    scanner_uses = 3
    scanner_active = False
    scanner_cells = []

    board_width = COLS * CELL
    board_height = ROWS * CELL
    board_x = (WIDTH - board_width) // 2
    board_y = 70

    board = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    revealed = [[False for _ in range(COLS)] for _ in range(ROWS)]
    flagged = [[False for _ in range(COLS)] for _ in range(ROWS)]

    mine_positions = set()
    game_started = False
    first_click = True

    def place_mines(safe_row, safe_col):
        nonlocal mine_positions
        
        safe_zone = set()
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = safe_row + dr, safe_col + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    safe_zone.add((nr, nc))
        
        mine_positions.clear()
        attempts = 0
        max_attempts = 1000
        
        while len(mine_positions) < MINES and attempts < max_attempts:
            row = random.randrange(ROWS)
            col = random.randrange(COLS)
            if (row, col) not in safe_zone and (row, col) not in mine_positions:
                mine_positions.add((row, col))
            attempts += 1
        
        while len(mine_positions) < MINES:
            row = random.randrange(ROWS)
            col = random.randrange(COLS)
            if (row, col) != (safe_row, safe_col) and (row, col) not in mine_positions:
                mine_positions.add((row, col))

    def initialize_board():
        for row in range(ROWS):
            for col in range(COLS):
                if board[row][col] == -1:
                    continue
                count = 0
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < ROWS and 0 <= nc < COLS and board[nr][nc] == -1:
                            count += 1
                board[row][col] = count

    def reveal_cell(row, col):
        if row < 0 or row >= ROWS or col < 0 or col >= COLS:
            return
        if revealed[row][col] or flagged[row][col]:
            return
        
        revealed[row][col] = True
        
        if board[row][col] == 0:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < ROWS and 0 <= nc < COLS:
                        if not revealed[nr][nc] and not flagged[nr][nc]:
                            reveal_cell(nr, nc)

    def check_win():
        for row in range(ROWS):
            for col in range(COLS):
                if board[row][col] != -1 and not revealed[row][col]:
                    return False
        return True

    game_over = False
    won = False
    scan_trigger_time = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return
                if event.key == pygame.K_s and has_scanner and scanner_uses > 0 and not game_over and not scanner_active:
                    scanner_active = True
                    scanner_cells = []
                    for row in range(ROWS):
                        for col in range(COLS):
                            if not revealed[row][col] and board[row][col] >= 0:
                                scanner_cells.append((row, col))
                                if len(scanner_cells) >= 3:
                                    break
                        if len(scanner_cells) >= 3:
                            break
                    for row, col in scanner_cells:
                        revealed[row][col] = True
                    scanner_uses -= 1
                    if scanner_uses == 0:
                        has_scanner = False
                    scan_trigger_time = pygame.time.get_ticks()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button not in (1, 3):
                    continue
                if game_over:
                    continue

                mx, my = event.pos
                if board_x <= mx < board_x + board_width and board_y <= my < board_y + board_height:
                    col = (mx - board_x) // CELL
                    row = (my - board_y) // CELL

                    if event.button == 1:
                        if not flagged[row][col]:
                            if first_click:
                                place_mines(row, col)
                                for r in range(ROWS):
                                    for c in range(COLS):
                                        if (r, c) in mine_positions:
                                            board[r][c] = -1
                                        else:
                                            board[r][c] = 0
                                initialize_board()
                                first_click = False
                                game_started = True
                            
                            if board[row][col] == -1:
                                game_over = True
                                won = False
                                for r, c in mine_positions:
                                    revealed[r][c] = True
                            else:
                                reveal_cell(row, col)
                                if check_win():
                                    game_over = True
                                    won = True
                                    update_highscore("MINESWEEPER", highscores["MINESWEEPER"] + 1)
                                    check_achievements()
                    elif event.button == 3:
                        if not game_started:
                            pass
                        if not revealed[row][col]:
                            flagged[row][col] = not flagged[row][col]

        if scanner_active and pygame.time.get_ticks() - scan_trigger_time > 1500:
            for row, col in scanner_cells:
                revealed[row][col] = False
            scanner_active = False
            scanner_cells = []

        screen.fill(BLACK)

        draw_text("MINESWEEPER", big_font, WHITE, WIDTH // 2, 30)
        draw_text(f"Wins: {highscores['MINESWEEPER']}", small_font, YELLOW, WIDTH // 2, 500)

        if has_scanner and scanner_uses > 0:
            draw_text(f"🔍 Scanner: {scanner_uses} uses", small_font, GREEN, WIDTH // 2, 55)
            draw_text("Press S to scan", small_font, WHITE, WIDTH // 2, 70)

        number_colors = {1: BLUE, 2: GREEN, 3: RED, 4: PURPLE, 5: DARK_GREEN, 6: CYAN, 7: BLACK, 8: GRAY}

        for row in range(ROWS):
            for col in range(COLS):
                x = board_x + col * CELL
                y = board_y + row * CELL
                rect = pygame.Rect(x, y, CELL, CELL)

                if revealed[row][col]:
                    pygame.draw.rect(screen, LIGHT_GRAY, rect)
                    pygame.draw.rect(screen, DARK_GRAY, rect, 1)
                    value = board[row][col]
                    if value > 0:
                        draw_text(str(value), small_font, number_colors.get(value, BLACK), x + CELL//2, y + CELL//2)
                    elif value == -1:
                        pygame.draw.circle(screen, RED, (x + CELL//2, y + CELL//2), 9)
                else:
                    pygame.draw.rect(screen, DARK_GRAY, rect)
                    pygame.draw.rect(screen, WHITE, rect, 1)
                    if flagged[row][col]:
                        draw_text("F", small_font, RED, x + CELL//2, y + CELL//2)

        if game_over and not won:
            for row, col in mine_positions:
                x = board_x + col * CELL
                y = board_y + row * CELL
                if not flagged[row][col]:
                    pygame.draw.circle(screen, RED, (x + CELL//2, y + CELL//2), 9)

        if not game_started and not game_over:
            draw_text("Click a cell to start", font, YELLOW, WIDTH // 2, 440)
            draw_text("First click is always safe!", small_font, GREEN, WIDTH // 2, 465)
        elif game_over:
            draw_text("YOU WIN!" if won else "BOOM! YOU LOST!", font, GREEN if won else RED, WIDTH // 2, 440)
        else:
            draw_text("Left = Reveal | Right = Flag | S = Scan", small_font, WHITE, WIDTH // 2, 440)

        draw_text("ESC = Menu", small_font, GRAY, WIDTH // 2, 465)

        if game_started and not game_over:
            flagged_count = sum(1 for row in range(ROWS) for col in range(COLS) if flagged[row][col])
            remaining = MINES - flagged_count
            draw_text(f"Mines: {remaining}", small_font, RED, 70, 50)

        pygame.display.flip()
        clock.tick(60)



def memory_game():
    play_music("MEMORY CARDS")

    ROWS = 4
    COLS = 4

    CARD_WIDTH = 110
    CARD_HEIGHT = 75
    GAP = 10

    board_width = COLS * CARD_WIDTH + (COLS - 1) * GAP
    start_x = (WIDTH - board_width) // 2
    start_y = 80

    symbols = ["*", "H", "D", "C", "O", "^", "#", "X"]
    cards = symbols * 2
    random.shuffle(cards)

    revealed = [False] * len(cards)
    matched = [False] * len(cards)

    first_card = None
    second_card = None

    waiting = False
    waiting_start = 0

    moves = 0
    matches = 0

    symbol_colors = [YELLOW, RED, LIGHT_RED, GREEN, BLUE, LIGHT_BLUE, WHITE, PURPLE]

    def get_card_rect(index):
        row = index // COLS
        col = index % COLS
        x = start_x + col * (CARD_WIDTH + GAP)
        y = start_y + row * (CARD_HEIGHT + GAP)
        return pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    while True:
        current_time = pygame.time.get_ticks()

        if waiting:
            match_reveal_time = 500 if player_data.get("challenge_mode", False) else 800
            if current_time - waiting_start >= match_reveal_time:
                if cards[first_card] == cards[second_card]:
                    matched[first_card] = True
                    matched[second_card] = True
                    matches += 1

                revealed[first_card] = False
                revealed[second_card] = False

                first_card = None
                second_card = None
                waiting = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not waiting:
                    for i in range(len(cards)):
                        rect = get_card_rect(i)
                        if rect.collidepoint(event.pos):
                            if revealed[i] or matched[i]:
                                break
                            revealed[i] = True
                            if first_card is None:
                                first_card = i
                            elif second_card is None:
                                second_card = i
                                moves += 1
                                waiting = True
                                waiting_start = pygame.time.get_ticks()
                            break

        screen.fill(BLACK)

        draw_text("MEMORY CARDS", big_font, WHITE, WIDTH // 2, 30)
        draw_text(f"Moves: {moves}", small_font, WHITE, 70, 505)
        draw_text(f"Best: {highscores['MEMORY CARDS']}", small_font, YELLOW, 210, 505)
        draw_text(f"Matches: {matches}/8", small_font, GREEN, 350, 505)

        for i in range(len(cards)):
            rect = get_card_rect(i)

            if matched[i]:
                pygame.draw.rect(screen, (40, 100, 50), rect, border_radius=8)
                pygame.draw.rect(screen, GREEN, rect, 3, border_radius=8)
                symbol = cards[i]
                symbol_index = symbols.index(symbol)
                draw_text(symbol, big_font, symbol_colors[symbol_index], rect.centerx, rect.centery)
            elif revealed[i]:
                pygame.draw.rect(screen, WHITE, rect, border_radius=8)
                pygame.draw.rect(screen, BLUE, rect, 3, border_radius=8)
                symbol = cards[i]
                symbol_index = symbols.index(symbol)
                draw_text(symbol, big_font, symbol_colors[symbol_index], rect.centerx, rect.centery)
            else:
                pygame.draw.rect(screen, (45, 70, 120), rect, border_radius=8)
                pygame.draw.rect(screen, LIGHT_BLUE, rect, 3, border_radius=8)
                draw_text("?", big_font, WHITE, rect.centerx, rect.centery)

        if matches == 8:
            new_record = update_low_score("MEMORY CARDS", moves)
            check_achievements()

            draw_text("YOU WIN!", font, GREEN, WIDTH // 2, 440)
            if new_record:
                draw_text("★ NEW RECORD! ★", font, YELLOW, WIDTH // 2, 470)

            pygame.display.flip()
            pygame.time.wait(1500)
            return

        pygame.display.flip()
        clock.tick(60)



def tetris_game():
    play_music("TETRIS")

    COLS = 10
    ROWS = 20
    CELL = 25

    BOARD_WIDTH = COLS * CELL
    BOARD_HEIGHT = ROWS * CELL
    BOARD_X = 120
    BOARD_Y = 20

    has_block_choice = player_data["inventory"].get("TETRIS_CHOICE", 0) > 0
    block_choice_uses = 3
    show_choice_menu = False
    chosen_piece = None

    TETRIS_COLORS = {
        "I": CYAN, "O": YELLOW, "T": PURPLE, "S": GREEN,
        "Z": RED, "J": BLUE, "L": ORANGE
    }

    SHAPES = {
        "I": [["....", "IIII", "....", "...."], ["..I.", "..I.", "..I.", "..I."]],
        "O": [[".OO.", ".OO.", "....", "...."]],
        "T": [[".T..", "TTT.", "....", "...."], [".T..", ".TT.", ".T..", "...."], ["....", "TTT.", ".T..", "...."], [".T..", "TT..", ".T..", "...."]],
        "S": [[".SS.", "SS..", "....", "...."], ["S...", "SS..", ".S..", "...."]],
        "Z": [["ZZ..", ".ZZ.", "....", "...."], ["..Z.", ".ZZ.", ".Z..", "...."]],
        "J": [["J...", "JJJ.", "....", "...."], [".JJ.", ".J..", ".J..", "...."], ["....", "JJJ.", "..J.", "...."], [".J..", ".J..", "JJ..", "...."]],
        "L": [["..L.", "LLL.", "....", "...."], [".L..", ".L..", ".LL.", "...."], ["....", "LLL.", "L...", "...."], ["LL..", ".L..", ".L..", "...."]]
    }

    board = [[None for _ in range(COLS)] for _ in range(ROWS)]

    def new_piece():
        if show_choice_menu and chosen_piece:
            kind = chosen_piece
        else:
            kind = random.choice(list(SHAPES.keys()))
        return {"kind": kind, "rotation": 0, "x": 3, "y": 0}

    def get_shape(piece):
        return SHAPES[piece["kind"]][piece["rotation"] % len(SHAPES[piece["kind"]])]

    def get_blocks(piece):
        blocks = []
        shape = get_shape(piece)
        for row in range(4):
            for col in range(4):
                if shape[row][col] != ".":
                    blocks.append((piece["x"] + col, piece["y"] + row))
        return blocks

    def valid_position(piece):
        for x, y in get_blocks(piece):
            if x < 0 or x >= COLS or y >= ROWS:
                return False
            if y >= 0 and board[y][x] is not None:
                return False
        return True

    def lock_piece(piece):
        color = TETRIS_COLORS[piece["kind"]]
        for x, y in get_blocks(piece):
            if y >= 0:
                board[y][x] = color

    current_piece = new_piece()
    fall_timer = 0
    score = 0
    lines = 0
    level = 1
    fall_speed = 375 if player_data.get("challenge_mode", False) else 500
    running = True

    while running:
        dt = clock.get_time()
        fall_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return

                if event.key == pygame.K_c and has_block_choice and block_choice_uses > 0 and not show_choice_menu:
                    show_choice_menu = True

                if not show_choice_menu:
                    if event.key == pygame.K_LEFT:
                        current_piece["x"] -= 1
                        if not valid_position(current_piece):
                            current_piece["x"] += 1
                    elif event.key == pygame.K_RIGHT:
                        current_piece["x"] += 1
                        if not valid_position(current_piece):
                            current_piece["x"] -= 1
                    elif event.key == pygame.K_UP:
                        old_rotation = current_piece["rotation"]
                        current_piece["rotation"] += 1
                        if not valid_position(current_piece):
                            current_piece["rotation"] = old_rotation
                    elif event.key == pygame.K_DOWN:
                        current_piece["y"] += 1
                        if not valid_position(current_piece):
                            current_piece["y"] -= 1
                            lock_piece(current_piece)
                            new_board = []
                            cleared = 0
                            for row in board:
                                if all(cell is not None for cell in row):
                                    cleared += 1
                                else:
                                    new_board.append(row)
                            while len(new_board) < ROWS:
                                new_board.insert(0, [None for _ in range(COLS)])
                            board[:] = new_board
                            lines += cleared
                            if cleared == 1:
                                score += 100
                            elif cleared == 2:
                                score += 300
                            elif cleared == 3:
                                score += 500
                            elif cleared == 4:
                                score += 800
                            level = max(1, lines // 10 + 1)
                            base_fall_speed = 500 - (level - 1) * 40
                            fall_speed = max(60, int(base_fall_speed * 0.75)) if player_data.get("challenge_mode", False) else max(80, base_fall_speed)
                            current_piece = new_piece()
                            fall_timer = 0
                            if not valid_position(current_piece):
                                running = False
                else:
                    pieces = ["I", "O", "T", "S", "Z", "J", "L"]
                    if event.key == pygame.K_1:
                        chosen_piece = "I"
                    elif event.key == pygame.K_2:
                        chosen_piece = "O"
                    elif event.key == pygame.K_3:
                        chosen_piece = "T"
                    elif event.key == pygame.K_4:
                        chosen_piece = "S"
                    elif event.key == pygame.K_5:
                        chosen_piece = "Z"
                    elif event.key == pygame.K_6:
                        chosen_piece = "J"
                    elif event.key == pygame.K_7:
                        chosen_piece = "L"
                    else:
                        continue

                    if use_powerup("TETRIS_CHOICE"):
                        block_choice_uses -= 1
                        if block_choice_uses == 0:
                            has_block_choice = False
                        show_choice_menu = False
                        current_piece = new_piece()

                    if event.key == pygame.K_ESCAPE:
                        show_choice_menu = False

        if fall_timer >= fall_speed and not show_choice_menu:
            fall_timer = 0
            current_piece["y"] += 1
            if not valid_position(current_piece):
                current_piece["y"] -= 1
                lock_piece(current_piece)
                new_board = []
                cleared = 0
                for row in board:
                    if all(cell is not None for cell in row):
                        cleared += 1
                    else:
                        new_board.append(row)
                while len(new_board) < ROWS:
                    new_board.insert(0, [None for _ in range(COLS)])
                board[:] = new_board
                lines += cleared
                if cleared == 1:
                    score += 100
                elif cleared == 2:
                    score += 300
                elif cleared == 3:
                    score += 500
                elif cleared == 4:
                    score += 800
                level = max(1, lines // 10 + 1)
                base_fall_speed = 500 - (level - 1) * 40
                fall_speed = max(60, int(base_fall_speed * 0.75)) if player_data.get("challenge_mode", False) else max(80, base_fall_speed)
                current_piece = new_piece()
                fall_timer = 0
                if not valid_position(current_piece):
                    running = False

        screen.fill(BLACK)
        draw_text("TETRIS", big_font, WHITE, 450, 50)

        pygame.draw.rect(screen, (30, 30, 30), (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT))
        for row in range(ROWS):
            for col in range(COLS):
                x = BOARD_X + col * CELL
                y = BOARD_Y + row * CELL
                pygame.draw.rect(screen, (50, 50, 50), (x, y, CELL, CELL), 1)
                if board[row][col] is not None:
                    pygame.draw.rect(screen, board[row][col], (x + 1, y + 1, CELL - 2, CELL - 2))

        color = TETRIS_COLORS[current_piece["kind"]]
        for x, y in get_blocks(current_piece):
            if y >= 0:
                pygame.draw.rect(screen, color, (BOARD_X + x * CELL + 1, BOARD_Y + y * CELL + 1, CELL - 2, CELL - 2))

        if show_choice_menu:
            pygame.draw.rect(screen, (0, 0, 0), (50, 100, 500, 350))
            draw_text("CHOOSE BLOCK", big_font, YELLOW, WIDTH // 2, 130)
            pieces = ["I", "O", "T", "S", "Z", "J", "L"]
            for i, piece in enumerate(pieces):
                color = TETRIS_COLORS[piece]
                x = 80 + i * 70
                draw_text(piece, font, color, x, 200)
                draw_text(str(i+1), small_font, GRAY, x, 240)
            draw_text("Press 1-7 to choose", small_font, WHITE, WIDTH // 2, 300)
            draw_text("ESC to cancel", small_font, GRAY, WIDTH // 2, 330)

        draw_text(f"Score: {score}", font, WHITE, 490, 150)
        draw_text(f"Best: {highscores['TETRIS']}", small_font, YELLOW, 490, 180)
        draw_text(f"Lines: {lines}", font, WHITE, 490, 220)
        draw_text(f"Level: {level}", font, WHITE, 490, 260)

        if has_block_choice and block_choice_uses > 0:
            draw_text(f"Press C: Choose Block ({block_choice_uses})", small_font, GREEN, 490, 320)

        draw_text("Left/Right Move", small_font, GRAY, 490, 360)
        draw_text("Up Rotate", small_font, GRAY, 490, 390)
        draw_text("Down Drop", small_font, GRAY, 490, 420)
        draw_text("ESC Menu", small_font, GRAY, 490, 450)

        pygame.display.flip()
        clock.tick(60)

    new_record = update_highscore("TETRIS", score)
    check_achievements()
    tetris_game_over(score, new_record)


def tetris_game_over(score, new_record=False):
    play_button = pygame.Rect(190, 220, 220, 60)
    menu_button = pygame.Rect(190, 300, 220, 50)

    while True:
        screen.fill(BLACK)

        draw_text("TETRIS GAME OVER", big_font, RED, WIDTH // 2, 90)
        draw_text(f"Score: {score}", font, WHITE, WIDTH // 2, 150)
        draw_text(f"Best: {highscores['TETRIS']}", font, YELLOW, WIDTH // 2, 185)

        if new_record:
            draw_text("★ NEW HIGH SCORE! ★", font, YELLOW, WIDTH // 2, 210)

        draw_button(play_button, "PLAY AGAIN", BUTTON_GREEN, BUTTON_GREEN_HOVER)
        draw_button(menu_button, "GAME MENU", BUTTON_GRAY, BUTTON_GRAY_HOVER)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if play_button.collidepoint(event.pos):
                        tetris_game()
                        return
                    if menu_button.collidepoint(event.pos):
                        return



def racing_game():
    play_music("RACING")

    has_shield = player_data["inventory"].get("RACING_SHIELD", 0) > 0
    shield_active = False
    shield_used = False

    ROAD_LEFT = 130
    ROAD_RIGHT = 470
    ROAD_WIDTH = ROAD_RIGHT - ROAD_LEFT
    PLAYER_WIDTH = 45
    PLAYER_HEIGHT = 80

    player_x = WIDTH // 2 - PLAYER_WIDTH // 2
    player_y = HEIGHT - 120
    player_speed = 7

    enemy_width = 45
    enemy_height = 80
    enemies = []

    score = 0
    speed = 5
    road_offset = 0
    spawn_timer = 0
    game_over = False
    new_record = False

    def create_enemy():
        lane_width = ROAD_WIDTH // 3
        lane = random.randint(0, 2)
        x = ROAD_LEFT + lane * lane_width + (lane_width - enemy_width) // 2
        enemies.append({"x": x, "y": -enemy_height})

    while True:
        dt = clock.get_time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return
                if event.key == pygame.K_s and has_shield and not shield_used and not game_over:
                    if use_powerup("RACING_SHIELD"):
                        shield_active = True
                        shield_used = True
                if game_over and event.key == pygame.K_r:
                    racing_game()
                    return

        if not game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_x += player_speed
            player_x = max(ROAD_LEFT, min(ROAD_RIGHT - PLAYER_WIDTH, player_x))

            score += 1
            speed = (7 + score // 500) if player_data.get("challenge_mode", False) else (5 + score // 500)
            road_offset += speed
            if road_offset >= 80:
                road_offset = 0

            spawn_timer += dt
            spawn_delay = max(250, 700 - score // 10) if player_data.get("challenge_mode", False) else max(350, 900 - score // 10)
            if spawn_timer >= spawn_delay:
                spawn_timer = 0
                if len(enemies) < (6 if player_data.get("challenge_mode", False) else 5):
                    create_enemy()

            for enemy in enemies:
                enemy["y"] += speed
            enemies[:] = [enemy for enemy in enemies if enemy["y"] < HEIGHT + enemy_height]

            player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
            for enemy in enemies:
                enemy_rect = pygame.Rect(enemy["x"], enemy["y"], enemy_width, enemy_height)
                if player_rect.colliderect(enemy_rect):
                    if shield_active:
                        shield_active = False
                        enemies.remove(enemy)
                    else:
                        game_over = True
                        final_score = score // 10
                        new_record = update_highscore("RACING", final_score)
                        check_achievements()

        screen.fill(GREEN)
        pygame.draw.rect(screen, DARK_GRAY, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))
        pygame.draw.rect(screen, WHITE, (ROAD_LEFT, 0, 5, HEIGHT))
        pygame.draw.rect(screen, WHITE, (ROAD_RIGHT - 5, 0, 5, HEIGHT))

        lane_width = ROAD_WIDTH // 3
        for lane in range(1, 3):
            x = ROAD_LEFT + lane * lane_width
            for y in range(-80, HEIGHT + 80, 80):
                line_y = (y + road_offset) % 80 - 80
                pygame.draw.rect(screen, WHITE, (x - 3, line_y, 6, 40))

        player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        if shield_active:
            pygame.draw.rect(screen, YELLOW, player_rect.inflate(20, 20), 3, border_radius=8)
        pygame.draw.rect(screen, BLUE, player_rect, border_radius=8)
        pygame.draw.rect(screen, LIGHT_BLUE, (player_x + 8, player_y + 10, PLAYER_WIDTH - 16, 22), border_radius=5)

        for enemy in enemies:
            x, y = enemy["x"], enemy["y"]
            pygame.draw.rect(screen, RED, (x, y, enemy_width, enemy_height), border_radius=8)
            pygame.draw.rect(screen, LIGHT_RED, (x + 8, y + 10, enemy_width - 16, 22), border_radius=5)

        draw_text(f"Score: {score // 10}", font, WHITE, 70, 30)
        draw_text(f"Best: {highscores['RACING']}", small_font, YELLOW, 70, 60)
        draw_text(f"Speed: {speed}", small_font, WHITE, 70, 85)

        if has_shield and not shield_used and not game_over:
            draw_text("Press S: Shield", small_font, YELLOW, 70, 110)
        if shield_active:
            draw_text("✦ SHIELD ACTIVE", small_font, YELLOW, 70, 110)

        if game_over:
            pygame.draw.rect(screen, BLACK, (100, 150, 400, 250), border_radius=15)
            draw_text("CRASH!", big_font, RED, WIDTH // 2, 195)
            draw_text(f"Score: {score // 10}", font, WHITE, WIDTH // 2, 255)
            draw_text(f"Best: {highscores['RACING']}", font, YELLOW, WIDTH // 2, 290)
            if new_record:
                draw_text("★ NEW HIGH SCORE! ★", font, YELLOW, WIDTH // 2, 325)
            draw_text("Press R to restart", font, GREEN, WIDTH // 2, 360)
            draw_text("ESC = Menu", small_font, GRAY, WIDTH // 2, 385)

        pygame.display.flip()
        clock.tick(60)



def flappy_bird():
    play_music("FLAPPY BIRD")

    has_wide_gap = player_data["inventory"].get("FLAPPY_WIDE_GAP", 0) > 0
    wide_gap_active = False

    if has_wide_gap:
        if use_powerup("FLAPPY_WIDE_GAP"):
            wide_gap_active = True

    BIRD_X = 140
    BIRD_SIZE = 28
    GRAVITY = 0.45
    JUMP_STRENGTH = -8

    if player_data.get("challenge_mode", False):
        PIPE_GAP = 160 if wide_gap_active else 125
    else:
        PIPE_GAP = 185 if wide_gap_active else 155
    PIPE_WIDTH = 70
    GROUND_Y = 470
    pipe_speed = 5 if player_data.get("challenge_mode", False) else 4

    bird_y = HEIGHT // 2
    bird_velocity = 0
    pipes = []
    score = 0
    spawn_timer = 0
    spawn_delay = 1500
    game_over = False
    new_record = False

    def create_pipe():
        min_height = 70
        max_height = GROUND_Y - PIPE_GAP - 70
        top_height = random.randint(min_height, max_height)
        bottom_y = top_height + PIPE_GAP
        pipes.append({"x": WIDTH, "top": top_height, "bottom": bottom_y, "passed": False})

    def reset_game():
        nonlocal bird_y, bird_velocity, pipes, score, spawn_timer, game_over, new_record
        bird_y = HEIGHT // 2
        bird_velocity = 0
        pipes = []
        score = 0
        spawn_timer = 0
        game_over = False
        new_record = False

    def check_collision():
        bird_rect = pygame.Rect(BIRD_X, int(bird_y), BIRD_SIZE, BIRD_SIZE)
        if bird_rect.bottom >= GROUND_Y or bird_rect.top <= 0:
            return True
        for pipe in pipes:
            top_rect = pygame.Rect(pipe["x"], 0, PIPE_WIDTH, pipe["top"])
            bottom_rect = pygame.Rect(pipe["x"], pipe["bottom"], PIPE_WIDTH, GROUND_Y - pipe["bottom"])
            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                return True
        return False

    while True:
        dt = clock.get_time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    if not game_over:
                        bird_velocity = JUMP_STRENGTH
                    else:
                        reset_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if not game_over:
                        bird_velocity = JUMP_STRENGTH
                    else:
                        reset_game()

        if not game_over:
            bird_velocity += GRAVITY
            bird_y += bird_velocity

            spawn_timer += dt
            if spawn_timer >= spawn_delay:
                spawn_timer = 0
                create_pipe()

            for pipe in pipes:
                pipe["x"] -= pipe_speed
                if not pipe["passed"] and pipe["x"] + PIPE_WIDTH < BIRD_X:
                    pipe["passed"] = True
                    score += 1

            pipes[:] = [pipe for pipe in pipes if pipe["x"] > -PIPE_WIDTH]

            pipe_speed = 4 + score // 10
            if player_data.get("challenge_mode", False):
                pipe_speed = 5 + score // 10
                spawn_delay = max(850, 1300 - score * 10)
            else:
                pipe_speed = 4 + score // 10
                spawn_delay = max(1100, 1500 - score * 10)

            if check_collision():
                game_over = True
                new_record = update_highscore("FLAPPY BIRD", score)
                check_achievements()

        screen.fill((100, 190, 240))

        for cloud in [(100, 100, 25, 30), (430, 150, 25, 30)]:
            pygame.draw.circle(screen, WHITE, (cloud[0], cloud[1]), cloud[2])
            pygame.draw.circle(screen, WHITE, (cloud[0]+30, cloud[1]), cloud[3])

        for pipe in pipes:
            pygame.draw.rect(screen, DARK_GREEN, (pipe["x"], 0, PIPE_WIDTH, pipe["top"]))
            pygame.draw.rect(screen, GREEN, (pipe["x"] - 5, pipe["top"] - 25, PIPE_WIDTH + 10, 25))
            pygame.draw.rect(screen, DARK_GREEN, (pipe["x"], pipe["bottom"], PIPE_WIDTH, GROUND_Y - pipe["bottom"]))
            pygame.draw.rect(screen, GREEN, (pipe["x"] - 5, pipe["bottom"], PIPE_WIDTH + 10, 25))

        pygame.draw.rect(screen, GREEN, (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
        pygame.draw.rect(screen, DARK_GREEN, (0, GROUND_Y, WIDTH, 8))

        pygame.draw.circle(screen, YELLOW, (BIRD_X + 14, int(bird_y) + 14), 14)
        pygame.draw.ellipse(screen, ORANGE, (BIRD_X - 3, int(bird_y) + 12, 18, 12))
        pygame.draw.circle(screen, WHITE, (BIRD_X + 19, int(bird_y) + 8), 7)
        pygame.draw.circle(screen, BLACK, (BIRD_X + 21, int(bird_y) + 8), 3)

        if wide_gap_active:
            draw_text("✦ WIDE GAP ACTIVE", small_font, YELLOW, WIDTH // 2, 20)

        draw_text(str(score), big_font, WHITE, WIDTH // 2, 50)
        draw_text(f"Best: {highscores['FLAPPY BIRD']}", small_font, YELLOW, 90, 25)

        if score == 0 and not game_over:
            draw_text("SPACE / CLICK = FLAP", font, WHITE, WIDTH // 2, 420)

        if game_over:
            pygame.draw.rect(screen, (20, 20, 25), (90, 150, 420, 240), border_radius=20)
            pygame.draw.rect(screen, WHITE, (90, 150, 420, 240), 3, border_radius=20)
            draw_text("GAME OVER", big_font, RED, WIDTH // 2, 195)
            draw_text(f"Score: {score}", font, WHITE, WIDTH // 2, 255)
            draw_text(f"Best: {highscores['FLAPPY BIRD']}", font, YELLOW, WIDTH // 2, 290)
            if new_record:
                draw_text("★ NEW HIGH SCORE! ★", font, YELLOW, WIDTH // 2, 325)
            draw_text("SPACE / CLICK = RESTART", small_font, GREEN, WIDTH // 2, 360)
            draw_text("ESC = Menu", small_font, GRAY, WIDTH // 2, 420)

        pygame.display.flip()
        clock.tick(60)


def brick_breaker():
    play_music("BRICK BREAKER")

    has_multi_ball = player_data["inventory"].get("BRICK_MULTI_BALL", 0) > 0
    multi_ball_used = False

    PADDLE_WIDTH = 100
    PADDLE_HEIGHT = 15
    BALL_SIZE = 14
    PADDLE_SPEED = 8
    BRICK_ROWS = 6
    BRICK_COLS = 10
    BRICK_WIDTH = 48
    BRICK_HEIGHT = 22
    BRICK_GAP = 5
    BRICK_START_Y = 80

    paddle_x = WIDTH // 2 - PADDLE_WIDTH // 2
    paddle_y = HEIGHT - 50

    class Ball:
        def __init__(self, x, y, dx, dy):
            self.x = x
            self.y = y
            self.dx = dx
            self.dy = dy
            self.active = True

        def get_rect(self):
            return pygame.Rect(int(self.x), int(self.y), BALL_SIZE, BALL_SIZE)

    initial_ball_speed = 5 if player_data.get("challenge_mode", False) else 4
    balls = [Ball(WIDTH // 2 - BALL_SIZE // 2, paddle_y - BALL_SIZE - 2, initial_ball_speed, -initial_ball_speed)]
    ball_launched = False

    brick_colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]
    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            x = (WIDTH - (BRICK_COLS * BRICK_WIDTH + (BRICK_COLS - 1) * BRICK_GAP)) // 2
            x += col * (BRICK_WIDTH + BRICK_GAP)
            y = BRICK_START_Y + row * (BRICK_HEIGHT + BRICK_GAP)
            bricks.append({
                "rect": pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT),
                "color": brick_colors[row],
                "points": (BRICK_ROWS - row) * 10
            })

    score = 0
    lives = 2 if player_data.get("challenge_mode", False) else 3
    level = 1
    game_over = False
    won = False
    new_record = False

    def reset_ball():
        nonlocal ball_launched
        balls.clear()
        balls.append(Ball(
            paddle_x + PADDLE_WIDTH // 2 - BALL_SIZE // 2,
            paddle_y - BALL_SIZE - 2,
            initial_ball_speed,
            -initial_ball_speed,
        ))
        ball_launched = False

    def create_level():
        nonlocal bricks
        bricks = []
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                x = (WIDTH - (BRICK_COLS * BRICK_WIDTH + (BRICK_COLS - 1) * BRICK_GAP)) // 2
                x += col * (BRICK_WIDTH + BRICK_GAP)
                y = BRICK_START_Y + row * (BRICK_HEIGHT + BRICK_GAP)
                bricks.append({
                    "rect": pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT),
                    "color": brick_colors[row],
                    "points": (BRICK_ROWS - row) * 10
                })

    def activate_multi_ball():
        nonlocal multi_ball_used
        if has_multi_ball and not multi_ball_used and ball_launched:
            if use_powerup("BRICK_MULTI_BALL"):
                multi_ball_used = True
                if balls:
                    main_ball = balls[0]
                    new_balls = [
                        Ball(main_ball.x, main_ball.y, main_ball.dx * 0.7, main_ball.dy),
                        Ball(main_ball.x, main_ball.y, main_ball.dx * 0.7, main_ball.dy * 1.3)
                    ]
                    main_ball.dx *= 0.7
                    main_ball.dy *= 1.3
                    balls.extend(new_balls)

    while True:
        dt = clock.get_time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return
                if event.key == pygame.K_SPACE:
                    if not game_over and not won:
                        if not ball_launched:
                            ball_launched = True
                            for ball in balls:
                                ball.dx = random.choice([-initial_ball_speed, initial_ball_speed]) if level > 1 else initial_ball_speed
                                ball.dy = -initial_ball_speed
                if event.key == pygame.K_m and has_multi_ball and not multi_ball_used:
                    activate_multi_ball()
                if game_over and event.key == pygame.K_r:
                    brick_breaker()
                    return

        if not game_over and not won:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                paddle_x -= PADDLE_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                paddle_x += PADDLE_SPEED
            paddle_x = max(0, min(WIDTH - PADDLE_WIDTH, paddle_x))

            if not ball_launched:
                for ball in balls:
                    ball.x = paddle_x + PADDLE_WIDTH // 2 - BALL_SIZE // 2
                    ball.y = paddle_y - BALL_SIZE - 2
            else:
                for ball in balls[:]:
                    if not ball.active:
                        continue

                    ball.x += ball.dx
                    ball.y += ball.dy
                    ball_rect = ball.get_rect()

                    if ball.x <= 0:
                        ball.x = 0
                        ball.dx *= -1
                    if ball.x + BALL_SIZE >= WIDTH:
                        ball.x = WIDTH - BALL_SIZE
                        ball.dx *= -1
                    if ball.y <= 0:
                        ball.y = 0
                        ball.dy *= -1

                    paddle_rect = pygame.Rect(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
                    if ball_rect.colliderect(paddle_rect) and ball.dy > 0:
                        ball.y = paddle_y - BALL_SIZE
                        paddle_center = paddle_x + PADDLE_WIDTH / 2
                        ball_center = ball.x + BALL_SIZE / 2
                        hit_position = ball_center - paddle_center
                        ball.dx = hit_position / 12
                        if abs(ball.dx) < 1:
                            ball.dx = 1 if ball.dx >= 0 else -1
                        ball.dy = -abs(ball.dy)

                    for brick in bricks[:]:
                        if ball_rect.colliderect(brick["rect"]):
                            overlap_left = ball_rect.right - brick["rect"].left
                            overlap_right = brick["rect"].right - ball_rect.left
                            overlap_top = ball_rect.bottom - brick["rect"].top
                            overlap_bottom = brick["rect"].bottom - ball_rect.top
                            min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                            if min_overlap in (overlap_left, overlap_right):
                                ball.dx *= -1
                            else:
                                ball.dy *= -1

                            score += brick["points"]
                            bricks.remove(brick)
                            break

                    if ball.y > HEIGHT:
                        ball.active = False

                balls = [ball for ball in balls if ball.active]

                if not balls:
                    lives -= 1
                    if lives <= 0:
                        game_over = True
                        new_record = update_highscore("BRICK BREAKER", score)
                        check_achievements()
                    else:
                        reset_ball()

                if len(bricks) == 0 and not game_over:
                    level += 1
                    if level > 5:
                        won = True
                        new_record = update_highscore("BRICK BREAKER", score)
                        check_achievements(level)
                    else:
                        create_level()
                        reset_ball()
                        multi_ball_used = False

        screen.fill((10, 12, 25))
        for y in range(0, HEIGHT, 20):
            pygame.draw.line(screen, (20, 25, 45), (0, y), (WIDTH, y))

        draw_text("BRICK BREAKER", big_font, WHITE, WIDTH // 2, 30)

        for brick in bricks:
            pygame.draw.rect(screen, brick["color"], brick["rect"], border_radius=5)
            pygame.draw.rect(screen, WHITE, brick["rect"], 1, border_radius=5)

        paddle_rect = pygame.Rect(int(paddle_x), paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
        pygame.draw.rect(screen, LIGHT_BLUE, paddle_rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, paddle_rect, 2, border_radius=8)

        for ball in balls:
            if ball.active:
                pygame.draw.circle(screen, WHITE, (int(ball.x + BALL_SIZE / 2), int(ball.y + BALL_SIZE / 2)), BALL_SIZE // 2)

        draw_text(f"Score: {score}", small_font, WHITE, 70, 525)
        draw_text(f"Best: {highscores['BRICK BREAKER']}", small_font, YELLOW, 210, 525)
        draw_text(f"Lives: {lives}", small_font, RED, 370, 525)
        draw_text(f"Level: {level}", small_font, GREEN, 500, 525)

        if has_multi_ball and not multi_ball_used and ball_launched:
            draw_text("Press M: Multi-Ball", small_font, YELLOW, WIDTH // 2, 500)

        if not ball_launched and not game_over and not won:
            draw_text("SPACE / CLICK = LAUNCH", font, YELLOW, WIDTH // 2, 440)
            draw_text("← → or A D = MOVE", small_font, WHITE, WIDTH // 2, 470)

        if game_over:
            pygame.draw.rect(screen, (20, 20, 30), (90, 150, 420, 250), border_radius=20)
            pygame.draw.rect(screen, RED, (90, 150, 420, 250), 3, border_radius=20)
            draw_text("GAME OVER", big_font, RED, WIDTH // 2, 200)
            draw_text(f"Score: {score}", font, WHITE, WIDTH // 2, 260)
            draw_text(f"Best: {highscores['BRICK BREAKER']}", font, YELLOW, WIDTH // 2, 295)
            if new_record:
                draw_text("★ NEW HIGH SCORE! ★", font, YELLOW, WIDTH // 2, 330)
            draw_text("Press R to restart", font, GREEN, WIDTH // 2, 365)
            draw_text("ESC = Menu", small_font, GRAY, WIDTH // 2, 390)

        if won:
            pygame.draw.rect(screen, (20, 40, 25), (90, 150, 420, 250), border_radius=20)
            pygame.draw.rect(screen, GREEN, (90, 150, 420, 250), 3, border_radius=20)
            draw_text("YOU WIN!", big_font, GREEN, WIDTH // 2, 200)
            draw_text("ALL LEVELS CLEARED!", font, WHITE, WIDTH // 2, 260)
            draw_text(f"Score: {score}", font, WHITE, WIDTH // 2, 300)
            draw_text(f"Best: {highscores['BRICK BREAKER']}", font, YELLOW, WIDTH // 2, 335)
            if new_record:
                draw_text("★ NEW HIGH SCORE! ★", font, YELLOW, WIDTH // 2, 370)
            draw_text("ESC = Menu", small_font, GRAY, WIDTH // 2, 400)

        pygame.display.flip()
        clock.tick(60)



def game_2048():
    play_music("2048")

    SIZE = 4
    BOARD_SIZE = 400
    CELL_SIZE = 90
    GAP = 10
    BOARD_X = (WIDTH - BOARD_SIZE) // 2
    BOARD_Y = 105

    has_delete = player_data["inventory"].get("2048_DELETE", 0) > 0
    delete_uses = 3

    TILE_COLORS = {
        0: (45, 45, 55), 2: (238, 228, 218), 4: (237, 224, 200),
        8: (242, 177, 121), 16: (245, 149, 99), 32: (246, 124, 95),
        64: (246, 94, 59), 128: (237, 207, 114), 256: (237, 204, 97),
        512: (237, 200, 80), 1024: (237, 197, 63), 2048: (237, 194, 46),
        4096: (60, 190, 170)
    }
    TILE_TEXT_COLORS = {2: (70, 65, 60), 4: (70, 65, 60)}

    def new_board():
        board = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
        add_tile(board)
        add_tile(board)
        return board

    def empty_cells(board):
        return [(row, col) for row in range(SIZE) for col in range(SIZE) if board[row][col] == 0]

    def add_tile(board):
        cells = empty_cells(board)
        if not cells:
            return
        row, col = random.choice(cells)
        four_tile_chance = 0.2 if player_data.get("challenge_mode", False) else 0.1
        board[row][col] = 2 if random.random() >= four_tile_chance else 4

    def compress_line(line):
        values = [value for value in line if value != 0]
        while len(values) < SIZE:
            values.append(0)
        return values

    def merge_line(line):
        line = compress_line(line)
        score_gain = 0
        for i in range(SIZE - 1):
            if line[i] != 0 and line[i] == line[i + 1]:
                line[i] *= 2
                score_gain += line[i]
                line[i + 1] = 0
        return compress_line(line), score_gain

    def move_left(board):
        changed = False
        score_gain = 0
        for row in range(SIZE):
            old_line = board[row][:]
            new_line, gain = merge_line(old_line)
            board[row] = new_line
            if new_line != old_line:
                changed = True
            score_gain += gain
        return changed, score_gain

    def move_right(board):
        changed = False
        score_gain = 0
        for row in range(SIZE):
            old_line = board[row][:]
            new_line, gain = merge_line(old_line[::-1])
            new_line = new_line[::-1]
            board[row] = new_line
            if new_line != old_line:
                changed = True
            score_gain += gain
        return changed, score_gain

    def move_up(board):
        changed = False
        score_gain = 0
        for col in range(SIZE):
            old_line = [board[row][col] for row in range(SIZE)]
            new_line, gain = merge_line(old_line)
            for row in range(SIZE):
                board[row][col] = new_line[row]
            if new_line != old_line:
                changed = True
            score_gain += gain
        return changed, score_gain

    def move_down(board):
        changed = False
        score_gain = 0
        for col in range(SIZE):
            old_line = [board[row][col] for row in range(SIZE)]
            new_line, gain = merge_line(old_line[::-1])
            new_line = new_line[::-1]
            for row in range(SIZE):
                board[row][col] = new_line[row]
            if new_line != old_line:
                changed = True
            score_gain += gain
        return changed, score_gain

    def can_move(board):
        if empty_cells(board):
            return True
        for row in range(SIZE):
            for col in range(SIZE - 1):
                if board[row][col] == board[row][col + 1]:
                    return True
        for row in range(SIZE - 1):
            for col in range(SIZE):
                if board[row][col] == board[row + 1][col]:
                    return True
        return False

    def has_2048(board):
        return any(2048 in row for row in board)

    def get_text_color(value):
        return TILE_TEXT_COLORS.get(value, WHITE)

    board = new_board()
    score = 0
    won = False
    game_over = False
    new_record = False
    running = True
    delete_mode = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return

                if event.key == pygame.K_d and has_delete and delete_uses > 0 and not game_over:
                    delete_mode = not delete_mode

                if not game_over:
                    changed = False
                    gain = 0

                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        if not delete_mode:
                            changed, gain = move_left(board)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if not delete_mode:
                            changed, gain = move_right(board)
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        if not delete_mode:
                            changed, gain = move_up(board)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if not delete_mode:
                            changed, gain = move_down(board)

                    if changed and not delete_mode:
                        score += gain
                        add_tile(board)
                        if has_2048(board):
                            won = True
                        if not can_move(board):
                            game_over = True
                            new_record = update_highscore("2048", score)
                            check_achievements()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and delete_mode and not game_over:
                    mx, my = event.pos
                    if BOARD_X <= mx < BOARD_X + BOARD_SIZE and BOARD_Y <= my < BOARD_Y + BOARD_SIZE:
                        col = (mx - BOARD_X - GAP) // (CELL_SIZE + GAP)
                        row = (my - BOARD_Y - GAP) // (CELL_SIZE + GAP)
                        if 0 <= row < SIZE and 0 <= col < SIZE:
                            value = board[row][col]
                            if value in (2, 4):
                                if use_powerup("2048_DELETE"):
                                    board[row][col] = 0
                                    delete_uses -= 1
                                    if delete_uses == 0:
                                        has_delete = False
                                    new_board_temp = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
                                    for r in range(SIZE):
                                        new_row = [board[r][c] for c in range(SIZE) if board[r][c] != 0]
                                        for c in range(len(new_row)):
                                            new_board_temp[r][c] = new_row[c]
                                    board = new_board_temp
                                    delete_mode = False

        screen.fill((15, 18, 30))
        draw_text("2048", big_font, WHITE, WIDTH // 2, 40)
        draw_text(f"Score: {score}", font, WHITE, 150, 85)
        draw_text(f"Best: {highscores['2048']}", font, YELLOW, 450, 85)

        pygame.draw.rect(screen, (75, 70, 65), (BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE), border_radius=10)

        for row in range(SIZE):
            for col in range(SIZE):
                value = board[row][col]
                x = BOARD_X + GAP + col * (CELL_SIZE + GAP)
                y = BOARD_Y + GAP + row * (CELL_SIZE + GAP)
                tile_rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                tile_color = TILE_COLORS.get(value, (60, 190, 170))
                pygame.draw.rect(screen, tile_color, tile_rect, border_radius=8)
                if value != 0:
                    text_color = get_text_color(value)
                    tile_font = small_font if value >= 1000 else font
                    draw_text(str(value), tile_font, text_color, tile_rect.centerx, tile_rect.centery)

        if has_delete and delete_uses > 0:
            draw_text(f"Press D: Delete Tile ({delete_uses})", small_font, GREEN, WIDTH // 2, 500)

        if delete_mode:
            draw_text("Click a 2 or 4 tile to delete it", font, YELLOW, WIDTH // 2, 520)
            draw_text("ESC to cancel", small_font, GRAY, WIDTH // 2, 545)

        if not game_over and not delete_mode:
            draw_text("ARROW KEYS / WASD = MOVE", small_font, GRAY, WIDTH // 2, 535)
            draw_text("ESC = MENU", small_font, GRAY, WIDTH // 2, 560)

        if game_over:
            pygame.draw.rect(screen, (25, 25, 35), (90, 180, 420, 200), border_radius=20)
            pygame.draw.rect(screen, RED, (90, 180, 420, 200), 3, border_radius=20)
            draw_text("GAME OVER", big_font, RED, WIDTH // 2, 225)
            draw_text(f"Score: {score}", font, WHITE, WIDTH // 2, 285)
            draw_text(f"Best: {highscores['2048']}", font, YELLOW, WIDTH // 2, 320)
            if new_record:
                draw_text("★ NEW HIGH SCORE! ★", small_font, YELLOW, WIDTH // 2, 350)
            draw_text("ESC = MENU", small_font, GRAY, WIDTH // 2, 375)

        pygame.display.flip()
        clock.tick(60)




pong_wins = 0

def pong_game():
    global pong_wins
    play_music("PONG")

    has_big_paddle = player_data["inventory"].get("PONG_BIG_PADDLE", 0) > 0
    big_paddle_active = False

    if has_big_paddle:
        if use_powerup("PONG_BIG_PADDLE"):
            big_paddle_active = True

    PADDLE_WIDTH = 15
    PADDLE_HEIGHT = 150 if big_paddle_active else 100

    BALL_SIZE = 16
    PLAYER_SPEED = 7
    CPU_SPEED = 7 if player_data.get("challenge_mode", False) else 5
    
    
    TOTAL_MATCHES = 4
    WIN_SCORE = 12 if player_data.get("challenge_mode", False) else 10

    player_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
    cpu_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
    ball_x = WIDTH // 2
    ball_y = HEIGHT // 2
    ball_dx = 6
    ball_dy = 4
    
    
    player_score = 0  
    cpu_score = 0     
    player_matches_won = 0
    cpu_matches_won = 0
    current_match = 1
    match_in_progress = True
    match_ended = False
    
    game_over = False
    new_record = False
    final_result = None  

    def reset_ball(direction):
        nonlocal ball_x, ball_y, ball_dx, ball_dy
        ball_x = WIDTH // 2
        ball_y = HEIGHT // 2
        ball_speed = 7 if player_data.get("challenge_mode", False) else 6
        vertical_speed = 5 if player_data.get("challenge_mode", False) else 4
        ball_dx = ball_speed * direction
        ball_dy = random.choice([-vertical_speed, -3, 3, vertical_speed])

    def reset_match():
        
        
        nonlocal player_y, cpu_y, player_score, cpu_score, match_in_progress, match_ended
        player_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        cpu_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        player_score = 0
        cpu_score = 0
        match_in_progress = True
        match_ended = False
        reset_ball(random.choice([-1, 1]))

    def reset_full_game():
        
        nonlocal player_y, cpu_y, player_score, cpu_score, player_matches_won, cpu_matches_won
        nonlocal current_match, match_in_progress, match_ended, game_over, final_result, new_record
        player_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        cpu_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        player_score = 0
        cpu_score = 0
        player_matches_won = 0
        cpu_matches_won = 0
        current_match = 1
        match_in_progress = True
        match_ended = False
        game_over = False
        final_result = None
        new_record = False
        reset_ball(1)

    
    reset_ball(1)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return
                if event.key == pygame.K_r and game_over:
                    
                    reset_full_game()
                    continue
                
                if event.key == pygame.K_SPACE and match_ended and not game_over:
                    current_match += 1
                    if current_match > TOTAL_MATCHES:
                        
                        game_over = True
                        
                        final_score = player_matches_won * 1000 + cpu_matches_won * 100 + current_match
                        new_record = update_highscore("PONG", final_score)
                        
                        
                        if player_matches_won > cpu_matches_won:
                            final_result = "WIN"
                            pong_wins += 1
                        elif player_matches_won < cpu_matches_won:
                            final_result = "LOSE"
                        else:
                            final_result = "DRAW"
                        
                        check_achievements(pong_wins=pong_wins)
                    else:
                        reset_match()

        keys = pygame.key.get_pressed()

        if not game_over and match_in_progress and not match_ended:
            
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player_y -= PLAYER_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player_y += PLAYER_SPEED
            player_y = max(0, min(HEIGHT - PADDLE_HEIGHT, player_y))

            
            cpu_center = cpu_y + PADDLE_HEIGHT // 2
            if ball_y > cpu_center + 10:
                cpu_y += CPU_SPEED
            elif ball_y < cpu_center - 10:
                cpu_y -= CPU_SPEED
            cpu_y = max(0, min(HEIGHT - PADDLE_HEIGHT, cpu_y))

            
            ball_x += ball_dx
            ball_y += ball_dy

            
            if ball_y <= 0 or ball_y >= HEIGHT - BALL_SIZE:
                ball_dy *= -1

            
            player_rect = pygame.Rect(30, int(player_y), PADDLE_WIDTH, PADDLE_HEIGHT)
            cpu_rect = pygame.Rect(WIDTH - 45, int(cpu_y), PADDLE_WIDTH, PADDLE_HEIGHT)
            ball_rect = pygame.Rect(int(ball_x), int(ball_y), BALL_SIZE, BALL_SIZE)

            if ball_rect.colliderect(player_rect) and ball_dx < 0:
                ball_x = player_rect.right + 1
                ball_dx *= -1
                paddle_center = player_y + PADDLE_HEIGHT / 2
                difference = ball_y + BALL_SIZE / 2 - paddle_center
                ball_dy = difference * 0.12
                
                if abs(ball_dx) < 8:
                    ball_dx *= 1.05

            if ball_rect.colliderect(cpu_rect) and ball_dx > 0:
                ball_x = cpu_rect.left - BALL_SIZE - 1
                ball_dx *= -1
                paddle_center = cpu_y + PADDLE_HEIGHT / 2
                difference = ball_y + BALL_SIZE / 2 - paddle_center
                ball_dy = difference * 0.12
                if abs(ball_dx) < 8:
                    ball_dx *= 1.05

            
            if ball_x > WIDTH:
                player_score += 1
                if player_score >= WIN_SCORE:
                    
                    player_matches_won += 1
                    match_ended = True
                    match_in_progress = False
                else:
                    reset_ball(-1)
            elif ball_x < -BALL_SIZE:
                cpu_score += 1
                if cpu_score >= WIN_SCORE:
                    
                    cpu_matches_won += 1
                    match_ended = True
                    match_in_progress = False
                else:
                    reset_ball(1)

        
        screen.fill((10, 12, 25))
        draw_text("PONG", big_font, WHITE, WIDTH // 2, 25)

        
        draw_text(f"Match {current_match}/{TOTAL_MATCHES}", small_font, WHITE, WIDTH // 2, 55)
        draw_text(f"Player: {player_matches_won} | CPU: {cpu_matches_won}", small_font, YELLOW, WIDTH // 2, 75)

        if big_paddle_active:
            draw_text("✦ BIG PADDLE ACTIVE", small_font, YELLOW, WIDTH // 2, 90)

        
        draw_text(str(player_score), big_font, GREEN, WIDTH // 2 - 100, 115)
        draw_text(str(cpu_score), big_font, RED, WIDTH // 2 + 100, 115)

        
        for y in range(150, HEIGHT, 30):
            pygame.draw.rect(screen, GRAY, (WIDTH // 2 - 2, y, 4, 15))

        
        pygame.draw.rect(screen, GREEN, (30, int(player_y), PADDLE_WIDTH, PADDLE_HEIGHT), border_radius=5)
        pygame.draw.rect(screen, RED, (WIDTH - 45, int(cpu_y), PADDLE_WIDTH, PADDLE_HEIGHT), border_radius=5)
        pygame.draw.rect(screen, WHITE, (int(ball_x), int(ball_y), BALL_SIZE, BALL_SIZE), border_radius=4)

        
        if match_ended and not game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            if player_score >= WIN_SCORE:
                draw_text("YOU WON THIS MATCH!", big_font, GREEN, WIDTH // 2, 200)
            else:
                draw_text("YOU LOST THIS MATCH!", big_font, RED, WIDTH // 2, 200)
            
            draw_text(f"Match {current_match} - Player: {player_score} | CPU: {cpu_score}", font, WHITE, WIDTH // 2, 270)
            draw_text(f"Overall: Player {player_matches_won} - {cpu_matches_won} CPU", font, YELLOW, WIDTH // 2, 310)
            
            if current_match < TOTAL_MATCHES:
                draw_text("Press SPACE for next match", font, GREEN, WIDTH // 2, 370)
            else:
                draw_text("Press SPACE to see final result", font, GREEN, WIDTH // 2, 370)
            
            draw_text("ESC = Menu", small_font, GRAY, WIDTH // 2, 410)

        
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            
            draw_text("GAME OVER", big_font, YELLOW, WIDTH // 2, 160)
            
            
            if final_result == "WIN":
                draw_text("🏆 YOU WIN THE SERIES! 🏆", big_font, GREEN, WIDTH // 2, 220)
            elif final_result == "LOSE":
                draw_text("💀 YOU LOSE THE SERIES! 💀", big_font, RED, WIDTH // 2, 220)
            else:
                draw_text("🤝 IT'S A DRAW! 🤝", big_font, YELLOW, WIDTH // 2, 220)
            
            draw_text(f"Final Score: Player {player_matches_won} - {cpu_matches_won} CPU", font, WHITE, WIDTH // 2, 290)
            
            if new_record:
                draw_text("★ NEW HIGH SCORE! ★", font, YELLOW, WIDTH // 2, 330)
            
            draw_text("Press R to play again", font, GREEN, WIDTH // 2, 390)
            draw_text("ESC = Menu", small_font, GRAY, WIDTH // 2, 420)

        
        if not game_over and not match_ended:
            draw_text("W / S or UP / DOWN = MOVE", small_font, GRAY, WIDTH // 2, HEIGHT - 25)

        pygame.display.flip()
        clock.tick(60)



def wordle_game():
    play_music("WORDLE")
    
    WORDS = [
        "APPLE", "HOUSE", "MONEY", "PHONE", "WATER", "HAPPY", "SMILE", 
        "MUSIC", "GREEN", "LIGHT", "WORLD", "PEACE", "HEART", "STONE", 
        "CLOUD", "DREAM", "FLAME", "GRACE", "HONOR", "JOYCE", "KINGS", 
        "LOVER", "MAGIC", "NIGHT", "OCEAN", "POWER", "QUEEN", "RIVER", 
        "SUNNY", "TIGER", "UNITY", "VIVID", "WOMAN", "YOUTH", "ZEBRA",
        "BREAD", "CHAIR", "DANCE", "EAGLE", "FAITH", "GHOST", "HEAVY",
        "IMAGE", "JUICE", "KNIFE", "LUNAR", "MIRTH", "NOBLE", "ORBIT",
        "PIANO", "QUIET", "RADIO", "SNAKE", "TRAIN", "ULTRA", "VOICE",
        "WHALE", "XENON", "YACHT", "ZESTY", "BLACK", "CANDY", "DRINK",
        "EVERY", "FRUIT", "GRAND", "HUMAN", "IRONY", "JOKER", "KNOCK",
        "LASER", "MOUNT", "NOVEL", "OPTIC", "PURSE", "QUEST", "REALM",
        "SCOPE", "TRUTH", "USUAL", "VALUE", "WITCH", "YOUNG", "ZONES"
    ]
    
    has_extra_guess = player_data["inventory"].get("WORDLE_EXTRA_GUESS", 0) > 0
    has_hint = player_data["inventory"].get("WORDLE_HINT", 0) > 0
    extra_guess_used = False
    hint_used = False
    hint_letter = None
    
    target_word = random.choice(WORDS)
    attempts = 0
    max_attempts = 5 if player_data.get("challenge_mode", False) else 6
    max_attempts_original = max_attempts
    game_over = False
    won = False
    new_record = False
    
    GRID_X = (WIDTH - (5 * 70)) // 2
    GRID_Y = 100
    CELL_SIZE = 60
    GAP = 10
    
    GREEN_WORDLE = (83, 141, 78)
    YELLOW_WORDLE = (181, 159, 59)
    GRAY_WORDLE = (58, 58, 60)
    DARK_GRAY_WORDLE = (30, 30, 32)
    
    guess_history = []
    current_guess = ""
    
    def check_wordle_achievements(attempts_used, won_game):
        global highscores
        
        if not won_game:
            return
        
        if "WORDLE_WINS" not in highscores:
            highscores["WORDLE_WINS"] = 0
        
        win_count = highscores["WORDLE_WINS"] + 1
        highscores["WORDLE_WINS"] = win_count
        save_highscores(highscores)
        
        if win_count >= 1:
            unlock_achievement("WORDLE_1")
        if win_count >= 5:
            unlock_achievement("WORDLE_5")
        if win_count >= 10:
            unlock_achievement("WORDLE_10")
        
        if attempts_used == 1:
            unlock_achievement("WORDLE_PERFECT")
    
    def get_feedback(guess):
        feedback = []
        target = list(target_word)
        guess_list = list(guess)
        
        for i in range(5):
            if guess_list[i] == target[i]:
                feedback.append("GREEN")
                target[i] = None
                guess_list[i] = None
            else:
                feedback.append(None)
        
        for i in range(5):
            if feedback[i] is None and guess_list[i] is not None:
                if guess_list[i] in target:
                    feedback[i] = "YELLOW"
                    target[target.index(guess_list[i])] = None
                else:
                    feedback[i] = "GRAY"
        
        return feedback
    
    def check_win(guess):
        return guess == target_word
    
    def show_hint():
        nonlocal hint_used, hint_letter
        if has_hint and not hint_used and not game_over:
            if use_powerup("WORDLE_HINT"):
                hint_used = True
                all_guesses = [g[0] for g in guess_history]
                for i, letter in enumerate(target_word):
                    position_guessed = False
                    for guess in all_guesses:
                        if guess[i] == letter:
                            position_guessed = True
                            break
                    if not position_guessed:
                        hint_letter = (i, letter)
                        break
    
    def draw_letter_keyboard():
        keyboard_rows = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
            ["Z", "X", "C", "V", "B", "N", "M"]
        ]
        
        letter_colors = {}
        for guess, feedback in guess_history:
            for i, letter in enumerate(guess):
                color = feedback[i]
                if color == "GREEN":
                    letter_colors[letter] = GREEN_WORDLE
                elif color == "YELLOW" and letter_colors.get(letter) != GREEN_WORDLE:
                    letter_colors[letter] = YELLOW_WORDLE
                elif color == "GRAY" and letter not in letter_colors:
                    letter_colors[letter] = GRAY_WORDLE
        
        for row_index, row in enumerate(keyboard_rows):
            row_width = len(row) * 35
            row_start_x = (WIDTH - row_width) // 2
            
            for col_index, letter in enumerate(row):
                x = row_start_x + col_index * 35
                y = 500 + row_index * 40
                rect = pygame.Rect(x, y, 30, 35)
                
                color = letter_colors.get(letter, DARK_GRAY_WORDLE)
                pygame.draw.rect(screen, color, rect, border_radius=5)
                pygame.draw.rect(screen, (80, 80, 80), rect, 1, border_radius=5)
                draw_text(letter, small_font, WHITE, x + 15, y + 17)
        
        if has_hint and not hint_used and not game_over:
            draw_text("Press H for Hint", small_font, YELLOW, WIDTH // 2, 485)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_game()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    stop_music()
                    return
                
                if game_over:
                    if event.key == pygame.K_r:
                        wordle_game()
                        return
                    continue
                
                if event.key == pygame.K_h and has_hint and not hint_used:
                    show_hint()
                
                if event.key == pygame.K_BACKSPACE:
                    current_guess = current_guess[:-1]
                
                elif event.key == pygame.K_RETURN:
                    if len(current_guess) == 5:
                        if current_guess.upper() in WORDS or current_guess.upper() == target_word:
                            attempts += 1
                            feedback = get_feedback(current_guess.upper())
                            guess_history.append((current_guess.upper(), feedback))
                            
                            if check_win(current_guess.upper()):
                                won = True
                                game_over = True
                                score = (max_attempts - attempts + 1) * 10
                                if attempts == 1:
                                    score += 50
                                new_record = update_highscore("WORDLE", score)
                                check_wordle_achievements(attempts, True)
                                
                            elif attempts >= max_attempts:
                                if has_extra_guess and not extra_guess_used and use_powerup("WORDLE_EXTRA_GUESS"):
                                    extra_guess_used = True
                                    max_attempts += 1
                                else:
                                    game_over = True
                                    won = False
                            
                            current_guess = ""
                        else:
                            draw_text("Not a valid word!", small_font, RED, WIDTH // 2, 90)
                            pygame.display.flip()
                            pygame.time.wait(500)
                    else:
                        draw_text("Enter 5 letters!", small_font, RED, WIDTH // 2, 90)
                        pygame.display.flip()
                        pygame.time.wait(500)
                
                elif event.unicode.isalpha():
                    if len(current_guess) < 5:
                        current_guess += event.unicode.upper()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    keyboard_rows = [
                        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
                        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
                        ["Z", "X", "C", "V", "B", "N", "M"]
                    ]
                    
                    for row_index, row in enumerate(keyboard_rows):
                        row_width = len(row) * 35
                        row_start_x = (WIDTH - row_width) // 2
                        for col_index, letter in enumerate(row):
                            x = row_start_x + col_index * 35
                            y = 500 + row_index * 40
                            if x <= mx <= x + 30 and y <= my <= y + 35:
                                if len(current_guess) < 5 and not game_over:
                                    current_guess += letter
                                break
        
        screen.fill(BLACK)
        
        draw_text("WORDLE", big_font, WHITE, WIDTH // 2, 40)
        
        draw_text(f"Attempts: {attempts}/{max_attempts}", font, YELLOW, WIDTH // 2, 75)
        draw_text(f"Best: {highscores['WORDLE']}", small_font, WHITE, WIDTH // 2, 95)
        
        if hint_used and hint_letter:
            i, letter = hint_letter
            draw_text(f"Hint: Letter {i+1} is '{letter}'", font, YELLOW, WIDTH // 2, 420)
        
        for row in range(max_attempts):
            for col in range(5):
                x = GRID_X + col * (CELL_SIZE + GAP)
                y = GRID_Y + row * (CELL_SIZE + GAP)
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                
                color = DARK_GRAY_WORDLE
                text = ""
                text_color = WHITE
                
                if row < len(guess_history):
                    guess, feedback = guess_history[row]
                    text = guess[col]
                    
                    if feedback[col] == "GREEN":
                        color = GREEN_WORDLE
                    elif feedback[col] == "YELLOW":
                        color = YELLOW_WORDLE
                    elif feedback[col] == "GRAY":
                        color = GRAY_WORDLE
                        text_color = GRAY
                
                elif row == len(guess_history) and not game_over:
                    if col < len(current_guess):
                        text = current_guess[col]
                        color = (50, 50, 55)
                    else:
                        color = (30, 30, 35)
                
                pygame.draw.rect(screen, color, rect, border_radius=5)
                pygame.draw.rect(screen, (80, 80, 80), rect, 2, border_radius=5)
                
                if text:
                    draw_text(text, font, text_color, rect.centerx, rect.centery)
        
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            if won:
                draw_text("YOU WIN!", big_font, GREEN_WORDLE, WIDTH // 2, 250)
                score = (max_attempts - attempts + 1) * 10
                if attempts == 1:
                    draw_text("★ PERFECT! ★", font, YELLOW, WIDTH // 2, 310)
                draw_text(f"Score: {score}", font, WHITE, WIDTH // 2, 350)
                if new_record:
                    draw_text("★ NEW HIGH SCORE! ★", font, YELLOW, WIDTH // 2, 390)
            else:
                draw_text("YOU LOSE!", big_font, RED, WIDTH // 2, 250)
                draw_text(f"The word was: {target_word}", font, WHITE, WIDTH // 2, 310)
                draw_text(f"Best: {highscores['WORDLE']}", font, YELLOW, WIDTH // 2, 350)
            
            draw_text("Press R to play again", font, GREEN, WIDTH // 2, 420)
            draw_text("ESC = Menu", small_font, GRAY, WIDTH // 2, 460)
            
            if won:
                xp_earned = calculate_xp_reward("WORDLE", score)
                coins_earned = 20 + (max_attempts - attempts) * 2
                add_xp(xp_earned)
                add_coins(coins_earned)
                
                player_data["total_games_played"] += 1
                player_data["total_score"] += score
                save_player_data(player_data)
        
        draw_letter_keyboard()
        
        if has_hint and not hint_used and not game_over:
            draw_text("Press H for Hint", small_font, YELLOW, WIDTH - 100, 30)
        if has_extra_guess and not extra_guess_used and not game_over:
            draw_text(f"Extra guess available", small_font, GREEN, WIDTH - 100, 50)
        
        pygame.display.flip()
        clock.tick(60)

def space_invaders_game():
    play_music("SPACE INVADERS")

    ship_color = (90, 230, 190)
    alien_colors = ((100, 220, 110), (240, 190, 70), (220, 100, 130))

    def create_wave(wave_number):
        rows = min(5, 2 + wave_number)
        aliens = []
        for row in range(rows):
            for column in range(8):
                aliens.append({
                    "rect": pygame.Rect(62 + column * 58, 65 + row * 38, 34, 24),
                    "row": row,
                })
        return aliens

    while True:
        score = 0
        wave = 1
        base_lives = 2 if player_data.get("challenge_mode", False) else 3
        lives = base_lives + int(use_powerup("INVADERS_EXTRA_LIFE"))
        ship = pygame.Rect(WIDTH // 2 - 24, HEIGHT - 65, 48, 24)
        player_bullets = []
        alien_bullets = []
        aliens = create_wave(wave)
        alien_direction = 1
        alien_speed = 52.0 if player_data.get("challenge_mode", False) else 38.0
        shot_cooldown = 0.0
        alien_shot_timer = 0.0
        invulnerable_until = 0.0
        game_over = False
        stars = [
            (random.randrange(WIDTH), random.randrange(25, HEIGHT - 80))
            for _ in range(45)
        ]
        play_again_button = pygame.Rect(100, 390, 180, 52)
        menu_button = pygame.Rect(320, 390, 180, 52)

        while not game_over:
            dt = min(clock.tick(60) / 1000, 0.05)
            now = pygame.time.get_ticks() / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    stop_music()
                    return

            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                ship.x -= int(320 * dt)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                ship.x += int(320 * dt)
            ship.x = max(12, min(WIDTH - ship.width - 12, ship.x))

            shot_cooldown = max(0.0, shot_cooldown - dt)
            if keys[pygame.K_SPACE] and shot_cooldown == 0:
                player_bullets.append(
                    pygame.Rect(ship.centerx - 3, ship.top - 13, 6, 14)
                )
                shot_cooldown = 0.24

            for bullet in player_bullets:
                bullet.y -= int(480 * dt)
            player_bullets = [bullet for bullet in player_bullets if bullet.bottom > 0]

            next_edge = any(
                alien["rect"].right >= WIDTH - 12 if alien_direction > 0
                else alien["rect"].left <= 12
                for alien in aliens
            )
            if next_edge:
                alien_direction *= -1
                for alien in aliens:
                    alien["rect"].y += 16
            else:
                for alien in aliens:
                    alien["rect"].x += int(alien_direction * alien_speed * dt)

            alien_shot_timer += dt
            shot_interval = max(0.22, 0.65 - wave * 0.04) if player_data.get("challenge_mode", False) else max(0.3, 0.9 - wave * 0.04)
            if aliens and alien_shot_timer >= shot_interval:
                shooter = random.choice(aliens)["rect"]
                alien_bullets.append(
                    pygame.Rect(shooter.centerx - 3, shooter.bottom, 6, 13)
                )
                alien_shot_timer = 0.0

            for bullet in alien_bullets:
                bullet.y += int((280 if player_data.get("challenge_mode", False) else 230) * dt)
            alien_bullets = [bullet for bullet in alien_bullets if bullet.top < HEIGHT]

            remaining_bullets = []
            for bullet in player_bullets:
                hit_alien = None
                for alien in aliens:
                    if bullet.colliderect(alien["rect"]):
                        hit_alien = alien
                        break
                if hit_alien is None:
                    remaining_bullets.append(bullet)
                else:
                    aliens.remove(hit_alien)
                    score += 10 * (5 - hit_alien["row"])
            player_bullets = remaining_bullets

            if now >= invulnerable_until:
                for bullet in alien_bullets:
                    if bullet.colliderect(ship):
                        alien_bullets.remove(bullet)
                        lives -= 1
                        invulnerable_until = now + 1.0
                        break

            if any(alien["rect"].bottom >= ship.top for alien in aliens):
                game_over = True
            elif lives <= 0:
                game_over = True
            elif not aliens:
                score += 100 * wave
                wave += 1
                aliens = create_wave(wave)
                alien_speed += 12

            screen.fill((7, 11, 25))
            for star_x, star_y in stars:
                screen.set_at((star_x, star_y), (55, 75, 105))

            pygame.draw.line(screen, (35, 55, 80), (0, HEIGHT - 34), (WIDTH, HEIGHT - 34), 2)
            for alien in aliens:
                rect = alien["rect"]
                color = alien_colors[alien["row"] % len(alien_colors)]
                pygame.draw.ellipse(screen, color, rect)
                pygame.draw.rect(screen, color, (rect.x + 5, rect.y + 13, 24, 8))
                pygame.draw.rect(screen, (7, 11, 25), (rect.x + 9, rect.y + 8, 4, 4))
                pygame.draw.rect(screen, (7, 11, 25), (rect.x + 21, rect.y + 8, 4, 4))

            for bullet in player_bullets:
                pygame.draw.rect(screen, (140, 255, 220), bullet, border_radius=3)
            for bullet in alien_bullets:
                pygame.draw.rect(screen, (255, 105, 115), bullet, border_radius=3)

            if now >= invulnerable_until or int(now * 12) % 2 == 0:
                pygame.draw.polygon(screen, ship_color, [
                    (ship.centerx, ship.top),
                    (ship.right, ship.bottom),
                    (ship.left, ship.bottom),
                ])
                pygame.draw.rect(screen, WHITE, (ship.centerx - 3, ship.top + 8, 6, 12))

            draw_text("SPACE INVADERS", font, WHITE, WIDTH // 2, 22)
            draw_text(f"Score: {score}", small_font, YELLOW, 85, 22)
            draw_text(f"Best: {highscores.get('SPACE INVADERS', 0)}", small_font, WHITE, WIDTH - 95, 22)
            draw_text(f"Wave: {wave}", small_font, CYAN, WIDTH // 2, 47)
            draw_text(f"Lives: {lives}", small_font, GREEN, 65, HEIGHT - 17)
            draw_text("A/D or LEFT/RIGHT: Move     SPACE: Fire     ESC: Menu",
                      small_font, LIGHT_GRAY, WIDTH // 2, HEIGHT - 17)

            pygame.display.flip()

        old_best = highscores.get("SPACE INVADERS", 0)
        xp_earned = calculate_xp_reward("SPACE INVADERS", score)
        new_record = score > old_best
        check_achievements()
        coins_earned = 5 + score // 100
        add_xp(xp_earned)
        add_coins(coins_earned)
        player_data["total_score"] += score
        save_player_data(player_data)

        while True:
            screen.fill((9, 13, 28))
            draw_text("EARTH NEEDS YOU!", big_font, ship_color, WIDTH // 2, 120)
            draw_text(f"Score: {score}     Wave: {wave}", font, WHITE, WIDTH // 2, 205)
            draw_text(f"Best: {highscores.get('SPACE INVADERS', 0)}", font, YELLOW, WIDTH // 2, 245)
            draw_text(
                f"+{challenge_reward(xp_earned)} XP     "
                f"+{challenge_reward(coins_earned)} Coins",
                font, GREEN, WIDTH // 2, 290,
            )
            if new_record:
                draw_text("NEW HIGH SCORE!", font, YELLOW, WIDTH // 2, 335)
            draw_button(play_again_button, "PLAY AGAIN", BUTTON_GREEN, BUTTON_GREEN_HOVER)
            draw_button(menu_button, "GAME MENU", BUTTON_GRAY, BUTTON_GRAY_HOVER)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        stop_music()
                        return
                    if event.key in (pygame.K_RETURN, pygame.K_r):
                        break
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if play_again_button.collidepoint(event.pos):
                        break
                    if menu_button.collidepoint(event.pos):
                        stop_music()
                        return
            else:
                clock.tick(60)
                continue
            break


def fruit_ninja_game():
    play_music("FRUIT NINJA")

    fruit_types = (
        {"name": "APPLE", "color": (235, 55, 65), "points": 10},
        {"name": "ORANGE", "color": (255, 155, 35), "points": 10},
        {"name": "LIME", "color": (95, 205, 70), "points": 15},
        {"name": "PLUM", "color": (165, 90, 210), "points": 15},
        {"name": "WATERMELON", "color": (45, 180, 95), "points": 20},
    )
    start_button = pygame.Rect(190, 335, 220, 58)
    play_again_button = pygame.Rect(100, 390, 180, 52)
    menu_button = pygame.Rect(320, 390, 180, 52)

    def spawn_fruit():
        radius = random.randint(21, 28)
        return {
            "x": random.randint(55, WIDTH - 55),
            "y": HEIGHT + radius,
            "vx": random.uniform(-115, 115),
            "vy": random.uniform(-680, -540),
            "radius": radius,
            "fruit": random.choice(fruit_types),
            "sliced": False,
        }

    while True:
        score = 0
        lives = 2 if player_data.get("challenge_mode", False) else 3
        fruits = []
        spawn_interval = 0.68 if player_data.get("challenge_mode", False) else 0.9
        spawn_timer = 0.0
        elapsed = 0.0
        game_over = False
        started = False
        slice_trail = []
        last_mouse_position = None

        while not game_over:
            dt = min(clock.tick(60) / 1000, 0.05)
            elapsed += dt
            spawn_timer += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        stop_music()
                        return
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE) and not started:
                        started = True
                        elapsed = 0.0
                        spawn_timer = 0.0
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not started:
                        if start_button.collidepoint(event.pos):
                            started = True
                            elapsed = 0.0
                            spawn_timer = 0.0
                    elif not game_over:
                        last_mouse_position = event.pos
                        for fruit in fruits:
                            if fruit["sliced"]:
                                continue
                            distance_squared = (
                                (fruit["x"] - event.pos[0]) ** 2
                                + (fruit["y"] - event.pos[1]) ** 2
                            )
                            if distance_squared <= fruit["radius"] ** 2:
                                fruit["sliced"] = True
                                score += fruit["fruit"]["points"]
                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    last_mouse_position = None
                    slice_trail = []
                if event.type == pygame.MOUSEMOTION and event.buttons[0] and started and not game_over:
                    current_position = event.pos
                    if last_mouse_position is None:
                        last_mouse_position = current_position
                    slice_trail.append(current_position)
                    slice_trail = slice_trail[-8:]
                    for fruit in fruits:
                        if fruit["sliced"]:
                            continue
                        dx = current_position[0] - last_mouse_position[0]
                        dy = current_position[1] - last_mouse_position[1]
                        length_squared = dx * dx + dy * dy
                        if length_squared:
                            projection = (
                                (fruit["x"] - last_mouse_position[0]) * dx
                                + (fruit["y"] - last_mouse_position[1]) * dy
                            ) / length_squared
                            projection = max(0.0, min(1.0, projection))
                            closest_x = last_mouse_position[0] + projection * dx
                            closest_y = last_mouse_position[1] + projection * dy
                            distance_squared = (
                                (fruit["x"] - closest_x) ** 2
                                + (fruit["y"] - closest_y) ** 2
                            )
                        else:
                            distance_squared = (
                                (fruit["x"] - current_position[0]) ** 2
                                + (fruit["y"] - current_position[1]) ** 2
                            )
                        if distance_squared <= (fruit["radius"] + 7) ** 2:
                            fruit["sliced"] = True
                            score += fruit["fruit"]["points"]
                    last_mouse_position = current_position

            if not started:
                screen.fill((16, 20, 36))
                draw_text("FRUIT NINJA", big_font, (255, 125, 90), WIDTH // 2, 125)
                draw_text("Click and drag across flying fruit to slice it.", font, WHITE, WIDTH // 2, 215)
                draw_text("Click or drag to slice fruit before it falls.", small_font, YELLOW, WIDTH // 2, 260)
                draw_button(start_button, "START", BUTTON_GREEN, BUTTON_GREEN_HOVER)
                draw_text("ESC = Menu", small_font, GRAY, WIDTH // 2, 425)
                pygame.display.flip()
                continue

            if spawn_timer >= spawn_interval:
                fruits.append(spawn_fruit())
                spawn_timer = 0.0
                base_spawn_interval = 0.68 if player_data.get("challenge_mode", False) else 0.9
                minimum_spawn_interval = 0.3 if player_data.get("challenge_mode", False) else 0.38
                spawn_interval = max(minimum_spawn_interval, base_spawn_interval - score * 0.002)

            missed_fruits = []
            for fruit in fruits:
                fruit["x"] += fruit["vx"] * dt
                fruit["y"] += fruit["vy"] * dt
                fruit["vy"] += 900 * dt
                fruit["x"] = max(fruit["radius"], min(WIDTH - fruit["radius"], fruit["x"]))
                if fruit["y"] - fruit["radius"] > HEIGHT:
                    missed_fruits.append(fruit)
                    if not fruit["sliced"]:
                        lives -= 1
                elif fruit["sliced"] and fruit["y"] > HEIGHT + fruit["radius"]:
                    missed_fruits.append(fruit)
            for fruit in missed_fruits:
                fruits.remove(fruit)
            game_duration = 50 if player_data.get("challenge_mode", False) else 60
            if lives <= 0 or elapsed >= game_duration:
                game_over = True

            screen.fill((18, 22, 38))
            draw_text("FRUIT NINJA", font, WHITE, WIDTH // 2, 24)
            draw_text(f"Score: {score}", font, YELLOW, 95, 24)
            draw_text(f"Best: {highscores.get('FRUIT NINJA', 0)}", small_font, WHITE, WIDTH - 105, 24)
            draw_text(f"Lives: {lives}", small_font, (255, 110, 110), 65, 55)
            draw_text(f"Time: {max(0, int(game_duration - elapsed))}", small_font, CYAN, WIDTH - 65, 55)
            pygame.draw.line(screen, (90, 100, 125), (0, HEIGHT - 8), (WIDTH, HEIGHT - 8), 3)

            for fruit in fruits:
                if fruit["sliced"]:
                    pygame.draw.circle(
                        screen, fruit["fruit"]["color"],
                        (int(fruit["x"]), int(fruit["y"])), fruit["radius"]
                    )
                    pygame.draw.line(
                        screen, WHITE,
                        (int(fruit["x"] - 8), int(fruit["y"] - 5)),
                        (int(fruit["x"] + 8), int(fruit["y"] + 5)), 3
                    )
                else:
                    center = (int(fruit["x"]), int(fruit["y"]))
                    pygame.draw.circle(screen, fruit["fruit"]["color"], center, fruit["radius"])
                    pygame.draw.circle(
                        screen, tuple(min(255, component + 45) for component in fruit["fruit"]["color"]),
                        (center[0] - 7, center[1] - 8), max(4, fruit["radius"] // 4)
                    )
                    pygame.draw.line(
                        screen, (95, 65, 40),
                        (center[0], center[1] - fruit["radius"] + 3),
                        (center[0] + 4, center[1] - fruit["radius"] - 5), 4
                    )

            if len(slice_trail) > 1:
                pygame.draw.lines(screen, (180, 245, 255), False, slice_trail[-8:], 3)
            slice_trail = slice_trail[-8:]
            draw_text("Click and drag to slice!", small_font, LIGHT_GRAY, WIDTH // 2, HEIGHT - 28)
            pygame.display.flip()

        old_best = highscores.get("FRUIT NINJA", 0)
        xp_earned = calculate_xp_reward("FRUIT NINJA", score)
        new_record = score > old_best
        coins_earned = 5 + score // 100
        add_xp(xp_earned)
        add_coins(coins_earned)
        player_data["total_score"] += score
        save_player_data(player_data)

        while True:
            screen.fill((16, 20, 36))
            draw_text("TIME'S UP!", big_font, (255, 125, 90), WIDTH // 2, 120)
            draw_text(f"Score: {score}", font, WHITE, WIDTH // 2, 205)
            draw_text(f"Best: {highscores.get('FRUIT NINJA', 0)}", font, YELLOW, WIDTH // 2, 245)
            draw_text(
                f"+{challenge_reward(xp_earned)} XP     "
                f"+{challenge_reward(coins_earned)} Coins",
                font, GREEN, WIDTH // 2, 290,
            )
            if new_record:
                draw_text("NEW HIGH SCORE!", font, YELLOW, WIDTH // 2, 335)
            draw_button(play_again_button, "PLAY AGAIN", BUTTON_GREEN, BUTTON_GREEN_HOVER)
            draw_button(menu_button, "GAME MENU", BUTTON_GRAY, BUTTON_GRAY_HOVER)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        stop_music()
                        return
                    if event.key in (pygame.K_RETURN, pygame.K_r):
                        break
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if play_again_button.collidepoint(event.pos):
                        break
                    if menu_button.collidepoint(event.pos):
                        stop_music()
                        return
            else:
                clock.tick(60)
                continue
            break


def pacman_game():
    play_music("PAC-MAN")

    columns = 21
    rows = 21
    tile_size = 25
    maze_left = (WIDTH - columns * tile_size) // 2
    maze_top = 54
    wall_color = (30, 65, 190)
    pacman_color = (255, 220, 30)
    ghost_colors = ((255, 75, 90), (80, 220, 255), (255, 145, 210), (255, 170, 55))
    directions = {
        pygame.K_LEFT: (-1, 0),
        pygame.K_a: (-1, 0),
        pygame.K_RIGHT: (1, 0),
        pygame.K_d: (1, 0),
        pygame.K_UP: (0, -1),
        pygame.K_w: (0, -1),
        pygame.K_DOWN: (0, 1),
        pygame.K_s: (0, 1),
    }

    def create_maze():
        maze = [["#" for _ in range(columns)] for _ in range(rows)]
        for y in range(1, rows - 1):
            for x in range(1, columns - 1):
                maze[y][x] = "."

        for y in (4, 8, 12, 16):
            for x in range(1, columns - 1):
                if x not in (2, 6, 10, 14, 18):
                    maze[y][x] = "#"

        for x in (4, 8, 12, 16):
            for y in range(1, rows - 1):
                if y not in (2, 6, 10, 14, 18):
                    maze[y][x] = "#"

        maze[1][1] = " "
        for x, y in ((9, 9), (10, 9), (9, 10), (10, 10)):
            maze[y][x] = " "
        for x, y in ((1, 19), (19, 1), (19, 19), (1, 10)):
            if maze[y][x] != "#":
                maze[y][x] = "o"
        return maze

    def is_open(x, y, maze):
        return 0 <= x < columns and 0 <= y < rows and maze[y][x] != "#"

    def reset_ghosts():
        return [
            {"pos": (9, 9), "home": (9, 9), "color": ghost_colors[0]},
            {"pos": (10, 9), "home": (10, 9), "color": ghost_colors[1]},
            {"pos": (9, 10), "home": (9, 10), "color": ghost_colors[2]},
            {"pos": (10, 10), "home": (10, 10), "color": ghost_colors[3]},
        ]

    while True:
        maze = create_maze()
        player_pos = (1, 1)
        direction = (0, 0)
        queued_direction = (0, 0)
        ghosts = reset_ghosts()
        score = 0
        lives = 3
        level = 1
        power_timer = 0.0
        invulnerable_timer = 0.0
        player_move_timer = 0.0
        ghost_move_timer = 0.0
        game_over = False
        play_again_button = pygame.Rect(100, 390, 180, 52)
        menu_button = pygame.Rect(320, 390, 180, 52)

        while not game_over:
            dt = min(clock.tick(60) / 1000, 0.05)
            player_move_timer += dt
            ghost_move_timer += dt
            power_timer = max(0.0, power_timer - dt)
            invulnerable_timer = max(0.0, invulnerable_timer - dt)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        stop_music()
                        return
                    if event.key in directions:
                        queued_direction = directions[event.key]

            if player_move_timer >= 0.12:
                player_move_timer = 0.0
                move_direction = None
                for candidate in (queued_direction, direction):
                    if candidate == (0, 0):
                        continue
                    next_x = player_pos[0] + candidate[0]
                    next_y = player_pos[1] + candidate[1]
                    if is_open(next_x, next_y, maze):
                        move_direction = candidate
                        player_pos = (next_x, next_y)
                        break
                if move_direction is not None:
                    direction = move_direction

                tile = maze[player_pos[1]][player_pos[0]]
                if tile == ".":
                    score += 10
                    maze[player_pos[1]][player_pos[0]] = " "
                elif tile == "o":
                    score += 50
                    maze[player_pos[1]][player_pos[0]] = " "
                    power_timer = 7.0

                remaining_pellets = any(
                    cell in (".", "o") for row in maze for cell in row
                )
                if not remaining_pellets:
                    level += 1
                    maze = create_maze()
                    player_pos = (1, 1)
                    direction = (0, 0)
                    queued_direction = (0, 0)
                    ghosts = reset_ghosts()
                    power_timer = 0.0

            ghost_delay = (
                max(0.08, 0.24 - (level - 1) * 0.025)
                if player_data.get("challenge_mode", False)
                else max(0.12, 0.32 - (level - 1) * 0.025)
            )
            if ghost_move_timer >= ghost_delay:
                ghost_move_timer = 0.0
                distances = {player_pos: 0}
                frontier = [player_pos]
                while frontier:
                    current = frontier.pop(0)
                    for step in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        neighbor = (current[0] + step[0], current[1] + step[1])
                        if is_open(neighbor[0], neighbor[1], maze) and neighbor not in distances:
                            distances[neighbor] = distances[current] + 1
                            frontier.append(neighbor)

                for ghost in ghosts:
                    x, y = ghost["pos"]
                    options = [
                        (x + dx, y + dy)
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
                        if is_open(x + dx, y + dy, maze)
                    ]
                    if options:
                        if power_timer > 0:
                            ghost["pos"] = max(
                                options, key=lambda pos: distances.get(pos, -1)
                            )
                        else:
                            ghost["pos"] = min(
                                options, key=lambda pos: distances.get(pos, columns * rows)
                            )

            if invulnerable_timer <= 0:
                for ghost in ghosts:
                    if ghost["pos"] == player_pos:
                        if power_timer > 0:
                            score += 200
                            ghost["pos"] = ghost["home"]
                        else:
                            lives -= 1
                            player_pos = (1, 1)
                            direction = (0, 0)
                            queued_direction = (0, 0)
                            power_timer = 0.0
                            invulnerable_timer = 1.5
                            ghosts = reset_ghosts()
                            if lives <= 0:
                                game_over = True
                            break

            screen.fill((5, 5, 20))
            draw_text("PAC-MAN", font, pacman_color, WIDTH // 2, 22)
            draw_text(f"Score: {score}", small_font, WHITE, 80, 22)
            draw_text(f"Best: {highscores.get('PAC-MAN', 0)}", small_font, YELLOW, WIDTH - 95, 22)
            draw_text(f"Lives: {lives}", small_font, GREEN, 60, HEIGHT - 13)
            draw_text(f"Level: {level}", small_font, CYAN, WIDTH // 2, HEIGHT - 13)

            for y, row in enumerate(maze):
                for x, cell in enumerate(row):
                    center = (
                        maze_left + x * tile_size + tile_size // 2,
                        maze_top + y * tile_size + tile_size // 2,
                    )
                    if cell == "#":
                        wall_rect = pygame.Rect(
                            maze_left + x * tile_size,
                            maze_top + y * tile_size,
                            tile_size,
                            tile_size,
                        )
                        pygame.draw.rect(screen, wall_color, wall_rect, border_radius=5)
                        pygame.draw.rect(screen, (65, 115, 255), wall_rect, 1, border_radius=5)
                    elif cell == ".":
                        pygame.draw.circle(screen, (255, 225, 175), center, 3)
                    elif cell == "o" and int(time.time() * 5) % 2 == 0:
                        pygame.draw.circle(screen, WHITE, center, 7)

            for ghost in ghosts:
                gx, gy = ghost["pos"]
                ghost_center = (
                    maze_left + gx * tile_size + tile_size // 2,
                    maze_top + gy * tile_size + tile_size // 2,
                )
                ghost_color = (60, 80, 255) if power_timer > 0 else ghost["color"]
                pygame.draw.circle(screen, ghost_color, ghost_center, 10)
                pygame.draw.rect(
                    screen,
                    ghost_color,
                    (ghost_center[0] - 10, ghost_center[1], 20, 9),
                )
                pygame.draw.circle(screen, WHITE, (ghost_center[0] - 4, ghost_center[1] - 2), 3)
                pygame.draw.circle(screen, WHITE, (ghost_center[0] + 4, ghost_center[1] - 2), 3)
                pygame.draw.circle(screen, BLACK, (ghost_center[0] - 4, ghost_center[1] - 2), 1)
                pygame.draw.circle(screen, BLACK, (ghost_center[0] + 4, ghost_center[1] - 2), 1)

            px, py = player_pos
            player_center = (
                maze_left + px * tile_size + tile_size // 2,
                maze_top + py * tile_size + tile_size // 2,
            )
            if invulnerable_timer <= 0 or int(time.time() * 12) % 2 == 0:
                pygame.draw.circle(screen, pacman_color, player_center, 10)
                if direction != (0, 0) and int(time.time() * 8) % 2 == 0:
                    mouth_tip = (
                        player_center[0] + direction[0] * 11,
                        player_center[1] + direction[1] * 11,
                    )
                    pygame.draw.line(screen, BLACK, player_center, mouth_tip, 4)

            draw_text("Arrow keys / WASD to move   ESC to menu",
                      small_font, LIGHT_GRAY, WIDTH // 2, HEIGHT - 35)
            if power_timer > 0:
                draw_text("POWER MODE", small_font, CYAN, WIDTH - 90, HEIGHT - 13)
            pygame.display.flip()

        old_best = highscores.get("PAC-MAN", 0)
        xp_earned = calculate_xp_reward("PAC-MAN", score)
        new_record = score > old_best
        check_achievements()
        coins_earned = 5 + score // 100
        add_xp(xp_earned)
        add_coins(coins_earned)
        player_data["total_score"] += score
        save_player_data(player_data)

        while True:
            screen.fill((8, 8, 25))
            draw_text("GAME OVER", big_font, RED, WIDTH // 2, 120)
            draw_text(f"Score: {score}     Level: {level}", font, WHITE, WIDTH // 2, 205)
            draw_text(f"Best: {highscores.get('PAC-MAN', 0)}", font, YELLOW, WIDTH // 2, 245)
            draw_text(
                f"+{challenge_reward(xp_earned)} XP     "
                f"+{challenge_reward(coins_earned)} Coins",
                font, GREEN, WIDTH // 2, 290,
            )
            if new_record:
                draw_text("NEW HIGH SCORE!", font, YELLOW, WIDTH // 2, 335)
            draw_button(play_again_button, "PLAY AGAIN", BUTTON_GREEN, BUTTON_GREEN_HOVER)
            draw_button(menu_button, "GAME MENU", BUTTON_GRAY, BUTTON_GRAY_HOVER)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit_game()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        stop_music()
                        return
                    if event.key in (pygame.K_RETURN, pygame.K_r):
                        break
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if play_again_button.collidepoint(event.pos):
                        break
                    if menu_button.collidepoint(event.pos):
                        stop_music()
                        return
            else:
                clock.tick(60)
                continue
            break




session_user = get_current_session()
if session_user:
    success, msg = switch_account(session_user)
    if not success:
        clear_session()
        print("Session expired, please login again.")

while True:
    start_menu()
    game_select_menu()
