from enum import Enum


class WhatsAppContext(Enum):
    NONE = 0
    LANDING_PAGE = 1
    HOME = 2
    GROUP_MEMBERS_SELECT = 3
    
class CommandType(Enum):
    QUIT = 0
    LOGIN = 1
    CONTACT_CHECK = 2
    