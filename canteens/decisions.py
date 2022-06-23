import re

IS_MEAT = re.compile(
    r'kuře|'
    r'slan|'
    r'klobá|'
    r'salám|'
    r'gothaj|'
    r'guláš|'  # probably questionable
    r'hově|'
    r'říz|'
    r'kachn|'
    r'steak|'
    r'šunk|'
    r'ryb[aí]|'
    r'losos|'
    r'masem|'  # uzeným masem
    r'vepř',
    re.IGNORECASE | re.VERBOSE
)

IS_PIZZA = re.compile(
    r'pizza',
    re.IGNORECASE | re.VERBOSE
)

IS_NOT_MAIN_MEAL = re.compile(
    r'bageta',
    re.IGNORECASE | re.VERBOSE
)
