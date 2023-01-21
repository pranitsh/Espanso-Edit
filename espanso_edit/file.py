from easygui import *
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError as e:
    print(e, print(
        e, "[ESPANSO-EDIT] Using pure python instead of libyaml (no significant difference expected)"))
    from yaml import Loader, Dumper
import os
import pprint
import logging
import subprocess


home_directory = os.path.expanduser('~')

default = os.path.join(home_directory, '.config/espanso/config/default.yml')
base = os.path.join(home_directory, '.config/espanso/match/base.yml')
log = os.path.join(home_directory, '.config/espanso/match/Espanso-Edit.log')
assert (os.path.exists(default))
assert (os.path.exists(base))

new = os.path.join(home_directory, '.config/espanso/match/new.yml')


# Logging
logging.basicConfig(filename=log,
                    format='%(name)s - %(levelname)s - %(message)s - %(asctime)s', level=logging.INFO)

starter = '''
matches:
  - trigger: ":espanso"
    replace: "{{vscode}}"
    vars:
      - name: "form1"
        type: form
        params:
          layout: "Edit: [[files]] \nEdit Input: [[name]]"
          fields:
            name:
              multiline: true
            files:
              type: list # or `choice`
              values:
                - /home/pranit/.config/espanso/config/default.yml
                - /home/pranit/.config/espanso/match/base.yml
                - /home/pranit/.config/espanso/match/new.yml
                - /home/pranit/Documents/GitHub/Espanso-Edit/espanso_edit/file.py
      - name: vscode
        type: shell
        params:
          cmd: "code -r {{form1.files}} {{form1.name}}"
          
  - trigger: ":addEspanso"
    replace: "{{vscode}}"
    vars:
      - name: vscode
        type: shell
        params:
          cmd: "poetry -C /home/pranit/Documents/GitHub/Espanso-Edit run python3 espanso_edit/file.py"'''
try:
    logging.info("[ESPANSO-EDIT] Opening file [new.yml]")
    with open(new, 'r') as stream:
        data = load(stream, Loader=Loader)
except FileNotFoundError as e:
    logging.info(e, "\n[ESPANSO-EDIT] Creating new file [new.yml]")
    with open(new, 'x') as f:
        f.write(starter)
    data = load(starter, Loader=Loader)

logging.info("[ESPANSO-EDIT] Successfully loaded file [new.yml]")
pp = pprint.PrettyPrinter(indent=1)
logging.info(f"[ESPANSO-EDIT] Data:\n {pp.pformat(data)}")

choices = data["matches"][0]["vars"][0]["params"]["fields"]["files"]["values"] + ["New File"]
text = "Select any one item"
title = "Espanso Edit"
userChoice = choicebox(text, title, choices)

if userChoice == "New File":
    logging.info("[ESPANSO-EDIT] Selected option is to add new file")
    message = "Below is the text to edit to a path"
    title = "Espanso Edit"
    text = [home_directory]
    userFile = textbox(message, title, text)
    logging.info(f"[ESPANSO-EDIT] Selected file to add: {userFile}")
    data["matches"][0]["vars"][0]["params"]["fields"]["files"]["values"].append(
        userFile)
    with open(new, 'w') as f:
        f.truncate(0)
        f.write(dump(data, Dumper=Dumper))
    logging.info("[ESPANSO-EDIT] Successfully added file to [new.yml]")
elif userChoice != None:
    logging.info(f"[ESPANSO-EDIT] Selected file is to remove: {userChoice}")
    data["matches"][0]["vars"][0]["params"]["fields"]["files"]["values"].remove(
        userChoice)
    with open(new, 'w') as f:
        f.truncate(0)
        f.write(dump(data, Dumper=Dumper))
    logging.info("[ESPANSO-EDIT] Successfully removed file from [new.yml]")
elif userChoice == None:
    logging.info("[ESPANSO-EDIT] No changes made")


openOrNot = ["Open", "Don't Open"]
text = " Open or don't open the files"
title = "Espanso Edit"
userChoice = choicebox(text, title, openOrNot)
if userChoice == "Open":
    subprocess.Popen(["code", log, new, default, base])
