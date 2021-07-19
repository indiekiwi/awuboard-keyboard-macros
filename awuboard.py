import os
import re
import subprocess

import keyboard
import json
import pyperclip
import base64
from getpass import getpass

# Init variables
profileJson = None
charDictionaryFile = 'CharacterShiftMapping.json'
charJson = []
decryptKey = ''
defaultAction = True

#Init custom variables from config.json
with open('config.json') as jsonConfig:
    config = json.load(jsonConfig)
keyboardName = config['KEYBOARD_NAME']
print('-------------------- AWUBOARD CONFIG --------------------')
print('- KEYBOARD_NAME:                 ' + keyboardName)
keyLog = config['ENABLE_KEY_LOGGING']
print('- ENABLE_KEY_LOGGING:            ' + str(keyLog))
actionLog = config['ENABLE_ACTION_LOGGING']
print('- ENABLE_ACTION_LOGGING:            ' + str(keyLog))
profileName = config['DEFAULT_PROFILE']
print('- DEFAULT_PROFILE:               ' + profileName)
useToggles = config['ENABLE_TOGGLE_MODE']
inputMode = not useToggles;
keyToToggle = config['KEY_TO_TOGGLE']
print('- ENABLE_TOGGLE_MODE:            ' + str(useToggles))
if useToggles:
    print('-- KEY_TO_TOGGLE:            ' + keyToToggle)
keyToTerminate = config['KEY_TO_TERMINATE']
print('- KEY_TO_TERMINATE:              ' + keyToTerminate)
allowAuthMacros = config['ALLOW_AUTH_MACROS']
decryptCheckString = config['DECRYPT_VISUAL_CHECK']

# Fake key stroke used to start listening
keyboard.press('shift')
keyboard.release('shift')

# Load Profile
with open(profileName) as jsonContents:
    profileJson = json.load(jsonContents)
    print('- Loaded key mappings:           ' + str(len(profileJson)) + '\n')

# Load Keyboard "Shift" combo simulation map
with open(charDictionaryFile) as jsonContents:
    charJson = json.load(jsonContents)

def main(inputMode):
    global decryptKey;
    eventDeviceId = ''
    with open('/proc/bus/input/devices', 'r') as file:
        data = file.read().split('\n\n')
        for part in data:
            if keyboardName in part:
                matches = re.search('sysrq .*? (event\d+) leds', part)
                if matches is not None:
                    eventDeviceId = matches.group(1)

    if eventDeviceId == '':
        raise Exception('Keyboard: (' + keyboardName + ') event device id not found')

    from evdev import InputDevice, categorize, ecodes
    dev = InputDevice('/dev/input/' + eventDeviceId)
    if not useToggles:
        dev.grab()

    if allowAuthMacros:
        decryptKey = getpass('[ALLOW_AUTH_MACROS is True] Secret:')
        if decryptCheckString != '':
            print('Decryption: ' + decode(decryptKey, decryptCheckString))

    for event in dev.read_loop():
        if event.type == ecodes.EV_KEY:
            key = categorize(event)
            if key.keystate == key.key_down:
                keyPressed = key.keycode
                if keyLog:
                    os.system('echo ' + str(keyPressed))
                if  keyPressed == keyToTerminate:
                    quit()
                elif keyPressed == keyToToggle:
                    inputMode ^= True
                    if (inputMode):
                        dev.grab()
                    else:
                        dev.ungrab()
                elif inputMode == True:
                    runAction(keyPressed)

def runAction(keyPressed):
    for row in profileJson:
        if row['key'] == keyPressed:
            for event in row['events']:
                data = getDataOrAlt(event)
                if event['action'] == 'keyboard':
                    keyboardAction(data)
                elif event['action'] == 'keyboardsys':
                    keyboardSysAction(data)
                elif event['action'] == 'cmd':
                    cmdAction(data)
                elif event['action'] == 'sub':
                    subAction(data)
                elif event['action'] == 'replace':
                    replaceAction(event['pattern'], event['replace'])
                elif event['action'] == 'password':
                    passwordAction(data)
                elif event['action'] == '2fa':
                    twoFactorAuthAction(data)
                elif event['action'] == 'combo':
                    comboKeyAction(event['down'], event['char'])
                elif event['action'] == 'action':
                    alternateAction(data)

def getDataOrAlt(event):
    global defaultAction
    if 'dataAlt' in event and defaultAction == False:
        return event['dataAlt']
    elif 'data' in event:
        return event['data']
    else:
        return None

def keyboardAction(data):
    if actionLog:
        print("Action: keyboard")
    for nextChar in data:
        if nextChar in charJson:
            keyboard.press('shift')
            keyboard.press(charJson[nextChar])
            keyboard.release(charJson[nextChar])
            keyboard.release('shift')
        else:
            # todo, exclude non valid input
            keyboard.write(nextChar)

def comboKeyAction(down, char):
    if actionLog:
        print("Action: combo")
    for downKey in down:
        keyboard.press(downKey)
    keyboard.press_and_release(char)
    for downKey in down:
        keyboard.release(downKey)

def keyboardSysAction(data):
    if actionLog:
        print("Action: keyboardsys")
    # Hit keyboard button such as Enter
    keyboard.press_and_release(data)
    print('System Key: ' + data)

def cmdAction(data):
    if actionLog:
        print("Action: cmd")
    os.system('gnome-terminal -e \"bash -c \'' + data + '\'\" &')
    print('Cmd: ' + data)

def subAction(data):
    if actionLog:
        print("Action: sub")
    subprocess.call(data)

def replaceAction(pattern, replace):
    if actionLog:
        print("Action: replace")
    keyboard.press('ctrl')
    keyboard.press_and_release('c')
    keyboard.release('ctrl')
    data = pyperclip.paste()
    result = re.sub(r'' + pattern, replace, data)
    pyperclip.copy(result)
    print(data + ' > ' + result)
    keyboard.press('ctrl')
    keyboard.press_and_release('v')
    keyboard.release('ctrl')

def passwordAction(data):
    if actionLog:
        print("Action: password")
    if allowAuthMacros:
        keyboardAction(decode(decryptKey, data))
    else:
        print('ALLOW_AUTH_MACROS = false, password macro skipped')

def twoFactorAuthAction(data):
    if actionLog:
        print("Action: 2fa")
    if allowAuthMacros:
        secret = decode(decryptKey, data)
        os.system('oathtool --base32 --totp "' + secret + '" > /tmp/2fa.tmp')
        code = open('/tmp/2fa.tmp', 'r').read()
        os.remove('/tmp/2fa.tmp')
        keyboardAction(code)
    else:
        print('ALLOW_AUTH_MACROS = false, 2fa macro skipped')

def alternateAction(data):
    if actionLog:
        print("Action: action")
    global defaultAction
    defaultAction = data == 'default'

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return ''.join(dec)

if __name__ == '__main__':
    main(inputMode)
