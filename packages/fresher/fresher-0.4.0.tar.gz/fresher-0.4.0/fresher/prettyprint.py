#-*- coding: utf-8 -*-

try:
    import curses
    curses.setupterm()
    COLOR_SUPPORT = (curses.tigetnum('colors') > 0)
except Exception:
    COLOR_SUPPORT = False


COLORS = {
    'bold': '1',
    'grey': '2',
    'underline': '4',
    'normal': '0',
    'red': '31',
    'green': '32',
    'yellow': '33',
    'blue': '34',
    'magenta': '35',
    'cyan': '36',
    'white': '37'
}

UNDEFINED = 'yellow'
AMBIGUOUS = 'cyan'
FAILED = 'red'
ERROR = 'red,bold'
PASSED = 'green'
TAG = 'cyan'
COMMENT = 'grey'
NOTRUN = 'normal'

def colored(text, colorspec):
    if not COLOR_SUPPORT:
        return text
    colors = [c.strip() for c in colorspec.split(',')]
    result = ""
    for c in colors:
        result += "\033[%sm" % COLORS[c]
    result += text + "\033[0m"
    return result

class FresherPrettyPrint(object):
    @classmethod
    def feature(cls, feature):
        ret = []
        if feature.tags:
            ret.append(colored(" ".join(("@" + t) for t in feature.tags), TAG))
        ret.append("Feature: " + feature.name)
        if feature.description != ['']:
            ret.extend('    ' + l for l in feature.description)
        return "\n".join(ret)
    
    @classmethod
    def scenario(cls, scenario):
        ret = []
        if scenario.tags:
            ret.append("    " + colored(" ".join(('@' + t) for t in scenario.tags), TAG))
        ret.append("    Scenario: "+scenario.name)
        return "\n".join(ret)
    
    @classmethod
    def _step(cls, step, color):
        return "        " + colored('%-40s' % (step.step_type + " " + step.match), color) \
                            + " " +\
                            colored("# " + step.source_location(), COMMENT)
    
    @classmethod
    def step_failed(cls, step):
        return cls._step(step, FAILED)
    
    @classmethod
    def step_ambiguous(cls, step):
        return cls._step(step, AMBIGUOUS)
    
    @classmethod
    def step_undefined(cls, step):
        return cls._step(step, UNDEFINED)
    
    @classmethod
    def step_exception(cls, step):
        return cls._step(step, ERROR)
    
    @classmethod
    def step_passed(cls, step):
        return cls._step(step, PASSED)
    
    @classmethod
    def step_notrun(cls, step):
        return cls._step(step, NOTRUN)
