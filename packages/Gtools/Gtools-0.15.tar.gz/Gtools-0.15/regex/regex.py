import re

def checktags(text):
    match = re.findall('##[A-Z]+##',text)
    text = re.sub('##[A-Z]+##', '', text)
    return not "#" in text