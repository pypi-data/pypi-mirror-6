def has_double_percent(text):
    return text.startswith('%%') or '\n%%' in text

def reader(loads, fp):
    chunk = ''
    for line in fp:
        if line.startswith('%%'):
            yield loads(chunk)
            chunk = ''
        else:
            chunk += line

def writer(dumps, obj, fp):
    new = True
    for item in obj:
        if not new:
            fp.write('\n%%\n')
        dumped = dumps(obj)
        if has_double_percent(dumped):
            raise ValueError('The (dumped) object must not contain "\n%%".')
        fp.write(dumped)
        new = False
