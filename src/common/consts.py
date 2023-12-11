import os

WORK_DIR = f'{os.getenv('LOCALAPPDATA')}/WhatsApp Session Manager'
PAGE_LOAD_TIMEOUT_SECONDS = 20
DEFAULT_TIMEOUT_SECONDS = 5
COMMAND_READ_DELAY = 0.05
UI_INTERACTION_DELAY = 0.3
KEY_PRESS_DELAY = 0.05

UI_REFRESH_RATE = 500
SESSION_CREATE_GROUP_DESYNC = 1

CSV_HEADER = 'Name,Given Name,Additional Name,Family Name,Yomi Name,Given Name Yomi,Additional Name Yomi,Family Name Yomi,Name Prefix,Name Suffix,Initials,Nickname,Short Name,Maiden Name,Birthday,Gender,Location,Billing Information,Directory Server,Mileage,Occupation,Hobby,Sensitivity,Priority,Subject,Notes,Language,Photo,Group Membership,Phone 1 - Type,Phone 1 - Value\n'