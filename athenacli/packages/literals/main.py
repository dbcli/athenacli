import os
import json

ROOT = os.path.dirname(__file__)
LITERAL_FILE = os.path.join(ROOT, 'literals.json')


with open(LITERAL_FILE) as f:
    LITERALS = json.load(f)


def get_literals(literal_type, type_=tuple):
    # Where `literal_type` is one of 'keywords', 'functions', 'datatypes',
    # returns a tuple of literal values of that type.
    return type_(LITERALS[literal_type])