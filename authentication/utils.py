import re


def emailFormatIsGood(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def passwordFormatIsGood(password):
    lowercase, uppercase, digits = 0, 0, 0
    if len(password) >= 8:
        for i in password:
            if i.islower():
                lowercase += 1
            elif i.isupper():
                uppercase += 1
            elif i.isdigit():
                digits += 1

    return lowercase >= 1 and uppercase >= 1 and digits >= 1 and lowercase + uppercase + digits == len(password)
