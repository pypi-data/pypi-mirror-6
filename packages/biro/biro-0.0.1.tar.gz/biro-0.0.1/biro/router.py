import re
from collections import defaultdict


class Router:

    param_macher = re.compile(r"\(\?P<([^>]+)>[^)]*\)")

    def __init__(self):
        self.__idx__ = defaultdict(list)
        self.__reversedidx__ = {}

    def append(self, method, pattern, handler):
        if type(pattern) is str:
            pattern = self.parse_pattern(pattern)
        self.__idx__[self.index(pattern)].append((method, pattern, handler))
        name = handler if type(handler) is str else handler.__qualname__
        self.__reversedidx__[name] = pattern
        return handler

    def extend(self, rules):
        for rule in rules:
            self.append(*rule)

    def index(self, pattern):
        pattern = pattern.pattern.lstrip('^').rstrip('$')
        pos = pattern.find('(')
        if pos != -1:
            pattern = pattern[:pos]
        segments = pattern.split('/')
        segments.pop()
        return '/'.join(segments)

    def parse_pattern(self, pattern):
        pattern = re.compile('^%s$' %
                             re.sub(r'<([^>]+)>', r'(?P<\1>[^/]+)', pattern))
        return pattern

    def match(self, method, path):
        """find handler from registered rules

        Example:

            handler, params = match('GET', '/path')

        """
        segments = path.split('/')
        while len(segments):
            index = '/'.join(segments)
            if index in self.__idx__:
                return self.match_rule(method, path, self.__idx__[index])
            segments.pop()
        return None, None

    def match_rule(self, method, path, rules):
        for _method, pattern, handler in rules:
            if _method != method:
                continue
            result = pattern.match(path)
            if result:
                return handler, result.groupdict()
        return None, None

    def path_for(self, handler, **kwargs):
        """construct path for a given handler

        Example:

            path = path_for(show_user, user_id=109)
        """
        if type(handler) is not str:
            handler = handler.__qualname__
        if handler not in self.__reversedidx__:
            return None
        pattern = self.__reversedidx__[handler].pattern.lstrip('^').rstrip('$')
        return self.param_macher.sub(lambda m: str(kwargs[m.group(1)]),
                                     pattern)

    def __repr__(self):
        return "\n".join(["%s %s -> %s" %
                          (method, pattern.pattern, handler.__qualname__)
                          for rules in self.__idx__.values()
                          for (method, pattern, handler) in rules])
