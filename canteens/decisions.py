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
    r'tuňák|'
    r'losos|'
    r'kančí|'
    r'surimi|'
    r'uzenina|'
    r'kotlet|'
    r'krůtí|'
    r'vrabec|'
    r'masem|'  # uzeným masem
    r'uzen.{,4}mas|' # uzené maso
    r'mlet.{,4}mas|' # mletý masem
    r'jelen|'
    r'butterfish|'
    r'filet|'
    r'drůbe|'
    r'zvěřin|'
    r'krkov|' # definitely not
    r'vepř',
    re.IGNORECASE | re.VERBOSE
)

IS_PIZZA = re.compile(
    r'pizza',
    re.IGNORECASE | re.VERBOSE
)

IS_NOT_MAIN_MEAL = re.compile(
    r'bageta|'
    r'minutky',
    re.IGNORECASE | re.VERBOSE
)
