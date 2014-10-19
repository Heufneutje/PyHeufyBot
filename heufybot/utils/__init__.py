# Taken from txircd:
# https://github.com/ElementalAlchemist/txircd/blob/8832098149b7c5f9b0708efe5c836c8160b0c7e6/txircd/utils.py#L9
def _enum(**enums):
    return type('Enum', (), enums)

ModeType = _enum(LIST=0, PARAM_SET=1, PARAM_UNSET=2, NO_PARAM=3)

def isNumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
