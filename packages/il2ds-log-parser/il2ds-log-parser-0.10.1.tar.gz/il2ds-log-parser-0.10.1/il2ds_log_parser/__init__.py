# -*- coding: utf-8 -*-
from il2ds_log_parser.parser import default_evt_parser, parse_log_lines


__all__ =  [
    'parser', 'register', 'unregister', 'parse_evt', 'parse_log',
]

register = default_evt_parser.register
unregister = default_evt_parser.unregister
parse_evt = default_evt_parser
parse_log = parse_log_lines
