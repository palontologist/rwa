from hyperon.ext import register_atoms
from hyperon.atoms import OperationAtom
import time
import math
import random

def updateSeed():
    random.seed(int(time.time_ns() // 1_000_000))

def timems():
    return int(time.time_ns() // 1_000_000)

def quotient(x, y):
    return x // y

@register_atoms
def reg_atoms():
    return {
        'timems!': OperationAtom("timems!", timems),
        '//': OperationAtom("//", quotient),
    }