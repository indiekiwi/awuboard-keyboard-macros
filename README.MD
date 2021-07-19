# About awuboard

This python script listens to your keyboard to perform macros; with a **single keystroke** you'll be able to perform one of 9 actions, some of which are:

 1. Typing a phrase
 2. Opening and running a command on the terminal
 3. Outputting a password
 4. Generating and entering a 2fa token
	
**Use Case 1:**	You have a single keyboard, when you tap the "PAUSE|Break" key, it switches to macro mode, and every key is disabled from the default behaviour and can be assigned macros instead. Tapping the "Pause|Break" key again will toggle-switch back to normal keyboard functionality.
	
**Use Case 2:** If you do not wish to use your primary keyboard, you can plug in a secondary keyboard (either another full sized keyboard or a number-pad keyboard), this secondary keyboard will have it's default behaviour disabled and can be dedicated to macros only.
	
This is my first python project, originally created about a year ago. I've been using it regularly. I've finally gotten around to cleaning it up and preparing it for github, although there's a few bugs/things I still need to work on (listed at the end).

## Preresequits

- Runs on Debian (I've only tested on Ubuntu) using python3

    pip3 install keyboard
	pip3 install pyperclip
	pip3 install evdev
	apt install oathtool
	apt install xsel

## Hooking the keyboard
The script will use the keyboard's name to retrieve it's id. Use `cat /proc/bus/input/devices` to list the connected devices to identify the keyboard. Finding the diff between it plugged & unplugged may help in this process.

Also see https://www.reddit.com/r/linux/comments/8geyru/diy_linux_macro_board/

## Usage
- configure `config.json` for settings
- configure `profile.json` for macros
-- Hint: Enable `ENABLE_KEY_LOGGING` to test the name of the keystrokes
- (optional, see Adding Passwords section below) run `python3 pass.py` to generate encrypted passwords
- run `sudo python3 awuboard.py` to start the main script

## Adding Passwords
Generate passwords and 2fa using `pass.py`, save it into profile.json as action: 'password' or '2fa'.

This project uses the 2fa "string secret code" and encrypts it using `pass.py` in the same way password encryption is done. The "string secret codes" are usually found alongside or extracted from the QR code during new 2fa setup.

**WARNING !!!**
**Use this feature at your Own Risk**. Due to the risky nature of storing and entering passwords/2fa, you may wish to review the code first in `pass.py` to see if the encryption is satisfactory, then to **ENABLE** this feature, set `ALLOW_AUTH_MACROS` to `true` in `config.json`

#### Password generating demo
		$ python3 pass.py
			[Secret]: test
			[Password / 2fa] to encrypt:password
			w6TDhsOmw6fDq8OUw6XDmA==

##### Installation
In the `profile.json` sample, the action = "2fa" and "password" fields can now be used to set the generated encrypted key: `w6TDhsOmw6fDq8OUw6XDmA==`
	
##### Usage

 - In `config.json`, set `ALLOW_AUTH_MACROS = true`
 - `DECRYPT_VISUAL_CHECK` can  also take a encrypted string which can help you visually validate  that you entered your secret correctly (leave blank to skip this   step)
 - When starting `awuboard.py`, you'll be prompted for your secret

## SETUP
- See `config.json` and `profile.json`
- Template of adding a new macro to `profile.json`:

		{
			"desc": "",
			"key": "",
			"events": [
				{
					"action": "",
					"data": ""
				}
			]
		},
		
### config.js

- `KEYBOARD_NAME` - The name of the keyboard to hook
- `ENABLE_KEY_LOGGING` - Logs the key strokes from the macro keyboard which will help during setup (disabled by default)
- `ENABLE_ACTION_LOGGING` - Logs the actions to the console which will help during setup
- `ALLOW_AUTH_MACROS` - Whether actions for 2fa and password are enabled (disabled by default)
- `ENABLE_TOGGLE_MODE` - Whether the hooked keyboard can be switched between default and macro modes
- `KEY_TO_TOGGLE` - If `ENABLE_TOGGLE_MODE` is enabled, this key will switch between the default and macro keyboard behaviours
- `KEY_TO_TERMINATE` - Press this key to kill the script
- `DEFAULT_PROFILE` - In case you're working with multiple profile files
- `DECRYPT_VISUAL_CHECK` - After entering your secret, it'll use the secret to decrypt this reference string, if it looks different from what you expected, you may have entered your secret incorrectly.

## Actions:
9 actions were originally implemented, which a single keystroke can perform, see the `profile.json` for more details on what each action does and how they can be configured:
- keyboard
- keyboardsys
- cmd
- sub
- replace
- password
- 2fa
- combo
- action

### Todo
 - [known bug] 3 - regex replace not working
 - [known bug] 6 - copy function not working (paste is though)
- Make a setup script to install prerequisites and configure the config.json
