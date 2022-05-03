import math

metadata = {
    'protocolName': 'Jupyter calibration example',
    'author': 'Nick <ndiehl@opentrons.com>',
    'apiLevel': '2.11'
}

 
def run(ctx):

    labware1 = ctx.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical','1', 'tuberack1')
    labware2 = ctx.load_labware('nest_96_wellplate_2ml_deep','2','tuberack2')
    tiprack = [ctx.load_labware('opentrons_96_tiprack_300ul','10')]
    pip = ctx.load_instrument('p300_single_gen2', 'left', tip_racks=tiprack)

    # ensure tipracks are accessed and calibrated
    for p in ctx.loaded_instruments.values():
        p.pick_up_tip()

    # ensure other labware is accessed and calibrated
    for lw in ctx.loaded_labwares.values():
        if not lw.is_tiprack:
            pip.aspirate(pip.min_volume, lw.wells()[0].top())
            pip.dispense(pip.min_volume, lw.wells()[0].top())
    for p in ctx.loaded_instruments.values():
        p.return_tip()
