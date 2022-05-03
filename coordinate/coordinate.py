from opentrons import protocol_api, types
import math 
from math import ceil, floor
from datetime import datetime

metadata= { 'ctxname':'coordinate_dev',
            'apiLevel':'2.8',
            'author':'Justin Pickard',
            'source':'Alturas_Analytics',
            'description':'using coordinates instead of deck slot'
        }
def run (protocol: protocol_api.ProtocolContext):
    
    rack = protocol.load_labware('opentrons_96_tiprack_300ul','10')
    pip = protocol.load_instrument('p300_single_gen2','left')
    pip2 = protocol.load_instrument('p300_single_gen2','right')
    trash = protocol.fixed_trash['A1']

    pip.move_to(protocol.deck.position_for('5').move(types.Point(x=50,y=50,z=50)))