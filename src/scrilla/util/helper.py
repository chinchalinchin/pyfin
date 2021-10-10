import argparse
from math import trunc
from typing import List, Tuple

from scrilla.static import definitions

def truncate(number: float, digits: int) -> float:
    stepper = 10.0 ** digits
    return trunc(stepper * number) / stepper

def strip_string_array(array: List[str]) -> List[str]:
    new_array = []
    for string in array:
        new_array.append(string.strip())
    return new_array

def split_and_strip(string: str, upper: bool = True, delimiter=",")-> List[str]:
    if upper:
        return strip_string_array(string.upper().split(delimiter))
    return strip_string_array(string.lower().split(delimiter))

def round_array(array: List[float], decimals: int) -> List[float]:
    cutoff = (1/10**decimals)
    return [0 if element < cutoff else truncate(element, decimals) for element in array]

def intersect_dict_keys(dict1: dict, dict2: dict) -> Tuple[dict, dict]:
    intersection = [x for x in dict1.keys() if x in dict2.keys()]

    new_dict1, new_dict2 = {}, {}
    for key, value in dict1.items():
        if key in intersection:
            new_dict1[key] = value
    for key, value in dict2.items():
        if key in intersection:
            new_dict2[key] = value
    
    return new_dict1, new_dict2

################################################
##### PARSING FUNCTIONS

### CLI PARSING
def format_args(args, default_estimation_method) -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    choices = []
    for func in definitions.FUNC_DICT:
        choices.append(definitions.FUNC_DICT[func]['values'][0])
        choices.append(definitions.FUNC_DICT[func]['values'][1])

    parser.add_argument('function_arg', choices=choices)

    groups = [parser.add_mutually_exclusive_group() for arg_group in definitions.ARG_META['groups'] ]

    for arg in definitions.ARG_DICT:
        if definitions.ARG_DICT[arg]['format'] not in ('group', bool):
            parser.add_argument(definitions.ARG_DICT[arg]['values'][0], 
                                definitions.ARG_DICT[arg]['values'][1], 
                                definitions.ARG_DICT[arg]['values'][2], 
                                definitions.ARG_DICT[arg]['values'][3],
                                default=None, 
                                type=definitions.ARG_DICT[arg]['format'],
                                dest=arg)
        elif definitions.ARG_DICT[arg]['format'] == 'group':
            group_index = definitions.ARG_META['groups'].index(definitions.ARG_DICT[arg]['group'])
            groups[group_index].add_argument(definitions.ARG_DICT[arg]['values'][0],
                                            definitions.ARG_DICT[arg]['values'][1],
                                            definitions.ARG_DICT[arg]['values'][2],
                                            definitions.ARG_DICT[arg]['values'][3],
                                            action='store_const',
                                            dest=definitions.ARG_DICT[arg]['group'],
                                            const=arg)
        # NOTE: 'format' == group AND 'format' == bool => Empty Set, so only other alternative is
        # 'format' == bool
        else:
            parser.add_argument(definitions.ARG_DICT[arg]['values'][0], 
                                definitions.ARG_DICT[arg]['values'][1], 
                                definitions.ARG_DICT[arg]['values'][2], 
                                definitions.ARG_DICT[arg]['values'][3],
                                action='store_true',
                                dest=arg)

    parser.set_defaults(estimation_method=default_estimation_method)
    parser.add_argument('tickers', nargs='*', type=str)
    return vars(parser.parse_args(args))

def get_first_json_key(this_json: dict) -> str:
    return list(this_json.keys())[0]

def replace_troublesome_chars(msg: str) -> str:
    return msg.replace('\u2265','').replace('\u0142', '')
