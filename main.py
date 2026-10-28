import asyncio
import json
import requests
import websockets

CONFIG_PATH = "config.JSON"


def prompt_required(name, current, placeholder=None):
    value = current
    while not value or value == placeholder:
        value = input(f"{name}: ").strip()
    return value


def prompt_boolean(name, default):
    while True:
        answer = input(f"{name} [{ 'yes' if default else 'no' }]: ").strip().lower()
        if not answer:
            return default
        if answer in ("true", "yes", "y", "1"):
            return True
        if answer in ("false", "no", "n", "0"):
            return False
        print("Please enter yes or no.")


def load_config():
    config = {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    placeholders = ("Add your token here", "ADD_YOUR_SERVER_ID_HERE", "ADD_YOUR_CHANNEL_ID_HERE")
    required_values = {
        "TOKEN": config.get("TOKEN", ""),
        "GUILD_ID": config.get("GUILD_ID", ""),
        "CHANNEL_ID": config.get("CHANNEL_ID", ""),
    }

    missing_config = any(not value or value in placeholders for value in required_values.values())
    missing_config = missing_config or config.get("STATUS") not in ("online", "dnd", "idle")

    if missing_config or "SELF_MUTE" not in config or "SELF_DEAF" not in config:
        print("config.JSON was not found or is incomplete. Please enter the configuration values.")
        required_values["TOKEN"] = prompt_required("TOKEN", required_values["TOKEN"], "Add your token here")
        required_values["GUILD_ID"] = prompt_required("GUILD_ID", required_values["GUILD_ID"], "ADD_YOUR_SERVER_ID_HERE")
        required_values["CHANNEL_ID"] = prompt_required("CHANNEL_ID", required_values["CHANNEL_ID"], "ADD_YOUR_CHANNEL_ID_HERE")

        status = config.get("STATUS", "online")
        while status not in ("online", "dnd", "idle"):
            status = input("STATUS (online/dnd/idle) [online]: ").strip().lower() or "online"

        self_mute = prompt_boolean("SELF_MUTE", config.get("SELF_MUTE", True))
        self_deaf = prompt_boolean("SELF_DEAF", config.get("SELF_DEAF", False))

        config = {
            "TOKEN": required_values["TOKEN"],
            "GUILD_ID": required_values["GUILD_ID"],
            "CHANNEL_ID": required_values["CHANNEL_ID"],
            "STATUS": status,
            "SELF_MUTE": self_mute,
            "SELF_DEAF": self_deaf,
        }

        with open(CONFIG_PATH, "w", encoding="utf-8") as config_file:
            json.dump(config, config_file, indent=4)
            config_file.write("\n")
        print(f"Saved configuration to {CONFIG_PATH}")

    return config


def normalize_boolean(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "y", "1")
    return bool(value)


config = load_config()
TOKEN = config["TOKEN"]
GUILD_ID = config["GUILD_ID"]
CHANNEL_ID = config["CHANNEL_ID"]
STATUS = config["STATUS"]
SELF_MUTE = normalize_boolean(config["SELF_MUTE"])
SELF_DEAF = normalize_boolean(config["SELF_DEAF"])

API = "https://discord.com/api/v10"

try:
    res = requests.get(f"{API}/users/@me", headers={"Authorization": TOKEN}, timeout=15)
except requests.RequestException as exc:
    print(f"Could not reach Discord: {exc}")
    exit(1)

if res.status_code != 200:
    print(f"Invalid token or Discord returned HTTP {res.status_code}.")
    exit(1)

try:
    user = res.json()
except ValueError as exc:
    print(f"Discord returned an invalid response: {exc}")
    exit(1)

print(f"Logged in as {user['username']} ({user['id']})!")

async def heartbeat(ws, interval, stop_event, gateway_state):
    try:
        while not stop_event.is_set():
            await asyncio.sleep(interval / 1000)
            if stop_event.is_set():
                return

            await ws.send(json.dumps({
                "op": 1,
                "d": gateway_state["sequence"]
            }))
    except websockets.exceptions.ConnectionClosed:
        return
    except asyncio.CancelledError:
        return


async def send_voice_state(ws):
    await ws.send(json.dumps({
        "op": 4,
        "d": {
            "guild_id": GUILD_ID,
            "channel_id": CHANNEL_ID,
            "self_mute": SELF_MUTE,
            "self_deaf": SELF_DEAF
        }
    }))


async def main():
    uri = "wss://gateway.discord.gg/?v=10&encoding=json"
    gateway_state = {"sequence": None}
    stop_event = asyncio.Event()
    background_tasks = []

    try:
        async with websockets.connect(uri, max_size=10 * 1024 * 1024, ping_interval=20, ping_timeout=20) as ws:
            hello = json.loads(await asyncio.wait_for(ws.recv(), timeout=30))
            heartbeat_interval = hello["d"]["heartbeat_interval"]

            heartbeat_task = asyncio.create_task(heartbeat(ws, heartbeat_interval, stop_event, gateway_state))
            background_tasks.append(heartbeat_task)

            await ws.send(json.dumps({
                "op": 2,
                "d": {
                    "token": TOKEN,
                    "properties": {
                        "$os": "windows",
                        "$browser": "chrome",
                        "$device": "pc"
                    },
                    "presence": {
                        "status": STATUS,
                        "afk": False
                    }
                }
            }))

            while True:
                raw_event = await ws.recv()
                try:
                    event = json.loads(raw_event)
                except json.JSONDecodeError:
                    print("Received an invalid JSON event from Discord; ignoring it.")
                    continue

                if isinstance(event.get("s"), int):
                    gateway_state["sequence"] = event["s"]

                if event.get("t") == "READY":
                    break

            await send_voice_state(ws)
            print("Joined the voice channel!")

            while True:
                raw_event = await ws.recv()
                try:
                    event = json.loads(raw_event)
                except json.JSONDecodeError:
                    print("Received an invalid JSON event from Discord; ignoring it.")
                    continue

                if isinstance(event.get("s"), int):
                    gateway_state["sequence"] = event["s"]

                event_type = event.get("t")
                data = event.get("d") or {}


    except websockets.exceptions.ConnectionClosedOK as exc:
        print(f"Discord gateway closed normally (code {exc.code}). Reconnecting...")
    except websockets.exceptions.ConnectionClosedError as exc:
        print(f"Discord gateway connection closed unexpectedly (code {exc.code}). Reconnecting...")
    except websockets.exceptions.ConnectionClosed as exc:
        print(f"Discord gateway connection closed (code {exc.code}). Reconnecting...")
    except asyncio.TimeoutError:
        print("Timed out waiting for Discord; reconnecting...")
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        print(f"Invalid Discord gateway response: {exc}. Reconnecting...")
    except OSError as exc:
        print(f"Network error: {exc}. Reconnecting...")
    except Exception as exc:
        print(f"Unexpected gateway error ({type(exc).__name__}): {exc}. Reconnecting...")
    finally:
        stop_event.set()
        for task in background_tasks:
            if not task.done():
                task.cancel()
        if background_tasks:
            await asyncio.gather(*background_tasks, return_exceptions=True)


async def run():
    reconnect_delay = 5
    while True:
        await main()
        await asyncio.sleep(reconnect_delay)


if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\nStopped by user.")
