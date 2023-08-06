import re


class RogotoParser(object):
    """Parse Rogoto Commands"""
    def __init__(self):
        self.code_to_execute = []
        self.pen_state = 'up'

    def parse(self, commands):
        cmdRegex = r'pendown|pd|penup|pu|forward \d+|fd \d+|backward \d+|bk \d+|left \d+|lt \d+|right \d+|rt \d+'
        cmd = commands.split('\n')
        for x in range(len(cmd)):
            matches = re.search(cmdRegex, cmd[x])
            if matches is None:
                raise RogotoParserException('Invalid Syntax was found')
            else:
                if 'fd' in matches.group(0):
                    self.code_to_execute.append(matches.group(0).replace('fd', 'forward'))
                elif 'bk' in matches.group(0):
                    self.code_to_execute.append(matches.group(0).replace('bk', 'backward'))
                elif 'lt' in matches.group(0):
                    self.code_to_execute.append(matches.group(0).replace('lt', 'left'))
                elif 'rt' in matches.group(0):
                    self.code_to_execute.append(matches.group(0).replace('rt', 'right'))
                elif 'pd' in matches.group(0):
                    self.code_to_execute.append('pendown')
                    self.pen_state = 'down'
                elif 'pu' in matches.group(0):
                    self.code_to_execute.append('penup')
                    self.pen_state = 'up'
                else:
                    self.code_to_execute.append(matches.group(0))
                    if matches.group(0) == 'penup':
                        self.pen_state = 'up'
                    elif matches.group(0) == 'pendown':
                        self.pen_state = 'pendown'

        return self.code_to_execute

    def clear(self):
        self.code_to_execute = []


class RogotoParserException(Exception):
    """Exception object when there is invalid items in the code """
    def __init__(self, message):
        self.message = message
