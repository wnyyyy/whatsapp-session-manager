from enum import Enum


class WhatsAppContext(Enum):
    NONE = 0
    LANDING_PAGE = 1
    HOME = 2
    GROUP_MEMBERS_SELECT = 3
    GROUP_OPTIONS = 4
    
class CommandType(Enum):
    QUIT = 0
    LOGIN = 1
    CONTACT_CHECK = 2
    BEGIN_GROUP_CREATION = 3
    ADD_GROUP_MEMBER = 4
    SETUP_GROUP = 5
    
class Error(Enum):
    DRIVER_ERROR = "Erro no driver"
    UNEXPECTED_CONTEXT = "Contexto inesperado"
    CONTACT_NOT_FOUND = "Contato não encontrado"
    MORE_THAN_ONE_CONTACT_FOUND = "Mais de um contato encontrado (erro???)"
    
class EmojiGroup(Enum):
    SUCCESS = '💫🔨🔛🆗✅🌞🌈🥇👌👍💪👀🦉🐒'
    FAILURE = '⁉️🆘🛑❌💥🪠🩼🙊🧐🫣🫢😨🤔'
    PROGRESS = '🔝💯🏴‍☠️✈️🍆🩻🎃🙅‍♂️🙅🥷💀😈👿😱🤡😜😝'