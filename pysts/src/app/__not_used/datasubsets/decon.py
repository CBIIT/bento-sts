import re

def get_model_and_tag(input):
    mdl = None
    tg = None

    p = re.compile('(.+)----(.+)')
    m = p.match(input)
    if m:
        mdl = m.group(1)
        tg = m.group(2)

    print('DECON {} {}'.format(mdl, tg))

    return (mdl, tg)