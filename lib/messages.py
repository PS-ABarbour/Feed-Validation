class msgColor:
    OKGREEN = '\33[32m'
    WARNINGYELLOW = '\033[93m'
    STOPRED = '\33[31m'
    HEADERWHITE = '\033[37m'
    CEND = '\033[0m'

def printOkay(message, data = ''):
    print(msgColor.OKGREEN, message, '\n', data, '\n', msgColor.CEND)

def printWarning(message, data = ''):
    print(msgColor.WARNINGYELLOW, message, '\n', data, '\n', msgColor.CEND)

def printStop(message, data = ''):
    print(msgColor.STOPRED, message, '\n', data, '\n', msgColor.CEND)

def printHeader(message, data = ''):
    print(msgColor.HEADERWHITE,'-'*int((30-len(message)/2)), message,'-'*int((30-len(message)/2)+(len(message) % 2)), '\n', msgColor.CEND)
