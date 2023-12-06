import common.consts as consts

def get_session_path(session_name):
    return consts.WORK_DIR + f'/sessions/{session_name}'

def format_number(number):
    return number.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')

def format_name(name):
    name = name.replace('_', ' ')
    name = " ".join(w.capitalize() for w in name.split())
    return name