<div id="Phantom" align="center">
    <h1>Voicecord</h1>
    <p>Make Your Discord Account 24/7 On Voice Channels!</p>
    <img src="https://i.imgur.com/Pzu4u0S.png" height="100">
</div>

<br>

<p align="center">
<b>⭐ Feel free to star the repository if this helped you!</b>
</p>

## Disclaimer
By using this code, you are automating your Discord Account. This is against Discord's Terms of Service and Community Guidelines. If not used properly, your account(s) might get suspended or terminated by Discord. I, the developer, is not responsible for any consequences that may arise from the use of this code. Use this software at your own risk and responsibility. Learn more about <a href="https://discord.com/terms">Discord's Terms of Service</a> and <a href="https://discord.com/guidelines">Community Guidelines</a> here.
#### This repository is in no way affiliated with, authorized, maintained, sponsored or endorsed by Discord Inc. (discord.com) or any of its affiliates or subsidiaries.

## Warning
**DO <ins>NOT</ins> GIVE YOUR DISCORD TOKENS TO ANYONE.**
#### Giving your token to someone else will give them the ability to log into your account without the password or 2FA.

---

## ✨ Features:
- Secure [🔒]
- Supports Stage Channels
- Account will stay 24/7 online
- Supports all three status modes (Online, Idle, Do Not Disturb)
- Can be used on any platform that supports [Python](https://python.org)

---

## 🔎 Obtaining Your Token
You will need an user token inorder to use this code. You can obtain it by doing the following:
1. Logging in to your discord account
2. Pressing `Ctrl+Shift+I` to open Chrome Developer Tools
3. Go to the `Network` Tab
4. Keep it open and refresh the page
5. Type `/api` in the filter search box
6. Click the entry that has `science` as the `Name`
7. On the sub-menu, go to `Headers`
8. Scroll down till you see an entry named `Authorization`. Copy the line next to it.
9. This is your token. <ins>**DO NOT GIVE IT TO ANYONE**</ins>.

---

## 🛠️ Local Installation

1. Install [Python](https://python.org/downloads) on your machine and make sure it is added to `PATH`.
2. Download or clone this repository and open a terminal in the project folder.
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the bot:
   ```bash
   python main.py
   ```
5. The first run asks for the Discord account token, guild/server ID, and channel ID. It also creates `config.JSON`.

On later runs, Voicecord asks whether you want to change the settings or continue with the old ones. If you choose to change them, you can update:

- `TOKEN` — Discord account token
- `GUILD_ID` — server/guild ID
- `CHANNEL_ID` — voice channel ID
- `STATUS` — `online`, `idle`, or `dnd`
- `SELF_MUTE` — `true` or `false`
- `SELF_DEAF` — `true` or `false`

Press Enter or type `skip` for any setting you want to keep unchanged. Skipped values remain the values saved in `config.JSON`.

### Environment variables

You can avoid interactive prompts on a server by setting these variables instead:

| Variable | Required | Example |
|---|---:|---|
| `TOKEN` | Yes | Your Discord user token |
| `GUILD_ID` | Yes | `123456789012345678` |
| `CHANNEL_ID` | Yes | `123456789012345678` |
| `STATUS` | No | `online` |
| `SELF_MUTE` | No | `true` |
| `SELF_DEAF` | No | `false` |

When all three required values are available through environment variables, environment values take priority over `config.JSON`. Keep your token private and never commit real credentials.

---

## 🌐 Deploying on Bot-Hosting.net

Bot-Hosting.net must provide a Python process and allow environment variables or persistent files.

1. Upload the repository files, or create the service from your GitHub fork of this repository.
2. Select **Python** as the language/runtime. Use a supported Python 3 version such as Python 3.10 or newer.
3. Set the startup command to:
   ```bash
   python main.py
   ```
4. Configure the dependencies as `requirements.txt`; if the panel does not detect it automatically, run:
   ```bash
   pip install -r requirements.txt
   ```
5. Add these values in the panel's environment-variable or secrets section:
   - `TOKEN`
   - `GUILD_ID`
   - `CHANNEL_ID`
   - Optional: `STATUS`, `SELF_MUTE`, and `SELF_DEAF`
6. Save and start the service.
7. Check the console for `Logged in as ...` and `Joined the voice channel!`.

The hosting environment is non-interactive, so do not leave required values missing. You must set all of `TOKEN`, `GUILD_ID`, and `CHANNEL_ID`; otherwise Voicecord exits with a configuration error. Restart or redeploy the service after changing environment variables.

---

<p align="center">Voicecord is licensed under <a href="https://github.com/SealedSaucer/Voicecord/blob/main/LICENSE">GNU General Public License</a> ❤️</p>
