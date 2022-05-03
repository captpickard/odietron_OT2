from opentrons import protocol_api
from math import floor,ceil
from datetime import datetime

metadata= { 'ctxname':'Aliquot_1x10_1500ul',
            'apiLevel':'2.8',
            'author':'JEP',
            'source':'used to verify that volume table is accurate',
        }


def run (protocol: protocol_api.ProtocolContext):

#volume tracking modules
    def volume_add(volume,dict_labware,labware,well):
        tup = dict_labware.get(labware[well])
        volume1 = tup[0]
        volume2 = volume
        adj_volume = volume1+volume2
        adj_list=list(tup)
        adj_list[0]=(adj_volume)
        tup=tuple(adj_list)
        return tup[0]

    def volume_sub(volume,dict_labware,labware,well):
        if low_vol_check(volume,dict_labware,labware,well)==True:
            tup = dict_labware.get(labware[well])
            volume1 = tup[0]
            volume2 = volume
            adj_volume = volume1-volume2
            adj_list=list(tup)
            adj_list[0]=(adj_volume)
            tup=tuple(adj_list)
            return tup[0]
        else:
            print("Aspiration denied!\nEnter a lower amount")

    def get_volume(dict_labware,labware,well):
        tup = dict_labware[labware[well]]
        return tup[0]

    def get_height(dict_labware,labware,well):
        tup = dict_labware[labware[well]]
        return tup[1]

    def low_vol_check(volume,dict_labware,labware,well):
        x=get_volume(dict_labware,labware,well)
        y=volume
        if  x-y < 0:
            return False
        else:
            return True

    def round_down(volume,divisor):
        vol_even=floor(volume/divisor)*divisor
        return vol_even

    def tup_update_sub(volume,dict_vol,dict_labware,labware,well):

        tup = dict_labware.get(labware[well])
        adj_list=list(tup)
        adj_list[0]=volume
        divisor=1

        if volume >=1600:
            divisor=1000
            vol_even=round_down(volume, divisor)
        elif 100 <= volume <1000:
            divisor=100
            vol_even=round_down(volume,divisor)
        else:
            divisor=10
            vol_even=round_down(volume,divisor)

        new_height=dict_vol.get(vol_even)
        adj_list[1]=new_height

        new_tup=tuple(adj_list)
        dict_labware[labware[well]]= new_tup

    def tup_update_add(volume,dict_vol,dict_labware,labware,well):

        tup = dict_labware[labware[well]]
        adj_list=list(tup)
        adj_list[0]=volume
        divisor=1
        if volume >=1600:
            divisor=1000
        elif 100 <= volume <1000:
            divisor=100
        else:
            divisor = 10

        def round_up(volume,divisor):
            vol_even=ceil(volume/divisor)*divisor
            return vol_even

        vol_even=round_up(volume,divisor)
        new_height=dict_vol.get(vol_even)
        adj_list[1]=new_height

        new_tup=tuple(adj_list)
        dict_labware[labware[well]]= new_tup

    def disp_master(volume,dict_vol,dict_labware,labware,well):
        new_vol=volume_add(volume,dict_labware,labware,well)
        tup_update_add(new_vol,dict_vol,dict_labware,labware,well)
        

    def asp_master(volume,dict_vol,dict_labware,labware,well):
        if low_vol_check(volume,dict_labware,labware,well)==True:
            new_vol=volume_sub(volume,dict_labware,labware,well)
            tup_update_sub(new_vol,dict_vol,dict_labware,labware,well)

        else:
            print('Cannot aspirate')

#load labware
    tuberack1 = protocol.load_labware('opentrons_15_tuberack_nest_15ml_conical','1','tuberack1')
#pipette tips
    tiprack= protocol.load_labware('opentrons_96_tiprack_300ul','7')
    tiprack1000 = protocol.load_labware('opentrons_96_tiprack_1000ul', '8')
#pipettes
    p1000 = protocol.load_instrument('p1000_single_gen2','right', tip_racks=[tiprack1000])
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack])
    p300.home
#assign permanent deck slot to trash
    trash = protocol.fixed_trash['A1']

#dictionary for volume tracking, put starting volumes in corresponding wells
    dict_15ml={tuberack1['A1']:(0,104), tuberack1['A2']:(0,104), tuberack1['A3']:(0,104), 
            tuberack1['A4']:(0,104), tuberack1['A5']:(0,104), 
            tuberack1['B1']:(0,104), tuberack1['B2']:(0,104), tuberack1['B3']:(0,104), 
            tuberack1['B4']:(0,104), tuberack1['B5']:(0,104), 
            tuberack1['C1']:(14000,104), tuberack1['C2']:(0,104), tuberack1['C3']:(0,104), 
            tuberack1['C4']:(0,104), tuberack1['C5']:(0,104), 
    }

#volume table, add dictionary for each type of labware
    vol_15ml= {14000: 104, 13500: 101, 13000: 98, 12500: 94, 
					12000: 91, 11500: 88, 11000: 85, 10500: 81, 
					10000: 78, 9500: 75, 9000: 72, 8500: 68, 
					8000: 65, 7500: 62, 7000: 59, 6500: 55, 
					6000: 52, 5500: 49, 5000: 46, 4500: 42, 
					4000: 39, 3500: 36, 3000: 33, 2500: 29, 
					2000: 26, 1500:23, 1000: 20, 900: 15, 800: 15, 
					700: 15, 600: 15, 500: 15, 400: 13, 
					300: 11, 200: 9, 100: 6, 90: 2, 80: 2,
					70: 2, 60: 2, 50: 1, 40: 1, 30: 1,
					20: 1, 10: 1}
#custom command
    def wet_tip(pip,vol_dict,dict_labware,labware,well):
        asp_master(200,vol_dict,dict_labware,labware,well)
        asp_h1=get_height(dict_labware, labware, well)
        pip.aspirate(200,labware[well].bottom(z=asp_h1))
        disp_master(200, vol_dict, dict_labware, labware, well)
        pip.dispense(200,labware[well].bottom(z=asp_h1+7))
        asp_master(200,vol_dict,dict_labware,labware,well)
        pip.aspirate(200, labware[well].bottom(z=asp_h1))
        disp_master(200, vol_dict, dict_labware, labware, well)
        pip.dispense(300,labware[well].bottom(z=asp_h1+7))

#setting initial pipette conditions    
    p300.flow_rate.aspirate = 100
    p300.flow_rate.dispense = 200 
    p1000.flow_rate.aspirate = 200
    p1000.flow_rate.dispense = 300

#actions below
    
    p1000.pick_up_tip()
    wet_tip(p1000, vol_15ml, dict_15ml, tuberack1, 'C1')
    
#14000
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#13500
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#13000
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#12500
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1') 
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#12000
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#11500
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#11000
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#10500
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#10000
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#9500
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#9000
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#8500
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#8000
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#7500
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#7000
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#6500
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#6000
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#5500
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#5000
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#4500
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#4000
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#3500
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#3000
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#2500
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#2000
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#1500
    asp_master(500,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p1000.aspirate(500, tuberack1['C1'].bottom(z=h1))
    disp_master(500, vol_15ml, dict_15ml,tuberack1,'C5')
    p1000.dispense(500, tuberack1['C5'].bottom(z=h2+7))
#1000
    p300.pick_up_tip()
    wet_tip(p300, vol_15ml, dict_15ml, tuberack1, 'C1')
    asp_master(100,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p300.aspirate(100, tuberack1['C1'].bottom(z=h1))
    disp_master(100, vol_15ml, dict_15ml,tuberack1,'C5')
    p300.dispense(100, tuberack1['C5'].bottom(z=h2+7))
#900
    asp_master(100,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p300.aspirate(100, tuberack1['C1'].bottom(z=h1))
    disp_master(100, vol_15ml, dict_15ml,tuberack1,'C5')
    p300.dispense(100, tuberack1['C5'].bottom(z=h2+7))
#800
    asp_master(100,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p300.aspirate(100, tuberack1['C1'].bottom(z=h1))
    disp_master(100, vol_15ml, dict_15ml,tuberack1,'C5')
    p300.dispense(100, tuberack1['C5'].bottom(z=h2+7))
#700
    asp_master(100,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p300.aspirate(100, tuberack1['C1'].bottom(z=h1))
    disp_master(100, vol_15ml, dict_15ml,tuberack1,'C5')
    p300.dispense(100, tuberack1['C5'].bottom(z=h2+7))
#600
    asp_master(100,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p300.aspirate(100, tuberack1['C1'].bottom(z=h1))
    disp_master(100, vol_15ml, dict_15ml,tuberack1,'C5')
    p300.dispense(100, tuberack1['C5'].bottom(z=h2+7))
#500
    asp_master(100,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p300.aspirate(100, tuberack1['C1'].bottom(z=h1))
    disp_master(100, vol_15ml, dict_15ml,tuberack1,'C5')
    p300.dispense(100, tuberack1['C5'].bottom(z=h2+7))
#400
    asp_master(100,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p300.aspirate(100, tuberack1['C1'].bottom(z=h1))
    disp_master(100, vol_15ml, dict_15ml,tuberack1,'C5')
    p300.dispense(100, tuberack1['C5'].bottom(z=h2+7))
#300
    asp_master(100,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p300.aspirate(100, tuberack1['C1'].bottom(z=h1))
    disp_master(100, vol_15ml, dict_15ml,tuberack1,'C5')
    p300.dispense(100, tuberack1['C5'].bottom(z=h2+7))
#200
    asp_master(100,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p300.aspirate(100, tuberack1['C1'].bottom(z=h1))
    disp_master(100, vol_15ml, dict_15ml,tuberack1,'C5')
    p300.dispense(100, tuberack1['C5'].bottom(z=h2+7))
#100
    asp_master(21,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p300.aspirate(21, tuberack1['C1'].bottom(z=h1))
    disp_master(21, vol_15ml, dict_15ml,tuberack1,'C5')
    p300.dispense(21, tuberack1['C5'].bottom(z=h2+7))
#80
    asp_master(21,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p300.aspirate(21, tuberack1['C1'].bottom(z=h1))
    disp_master(21, vol_15ml, dict_15ml,tuberack1,'C5')
    p300.dispense(21, tuberack1['C5'].bottom(z=h2+7))
#60
    asp_master(21,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p300.aspirate(21, tuberack1['C1'].bottom(z=h1))
    disp_master(21, vol_15ml, dict_15ml,tuberack1,'C5')
    p300.dispense(21, tuberack1['C5'].bottom(z=h2+7))
#40
    asp_master(21,vol_15ml, dict_15ml, tuberack1, 'C1')
    h1=get_height(dict_15ml, tuberack1, 'C1')
    h2=get_height(dict_15ml, tuberack1, 'C5')
    p300.aspirate(21, tuberack1['C1'].bottom(z=h1))
    disp_master(21, vol_15ml, dict_15ml,tuberack1,'C5')
    p300.dispense(21, tuberack1['C5'].bottom(z=h2+7))
#20
    p300.drop_tip()
    p1000.drop_tip()

    protocol.comment('Odie seems satisfied')
    protocol.set_rail_lights(True)
    protocol.delay(seconds=0.1)
    protocol.set_rail_lights(False)
    protocol.delay(seconds=0.1)
    protocol.set_rail_lights(True)
    protocol.delay(seconds=0.1)
    protocol.set_rail_lights(False)
    protocol.delay(seconds=0.1)
    protocol.set_rail_lights(True)
    protocol.delay(seconds=0.1)
    protocol.set_rail_lights(False)
    protocol.delay(seconds=0.1)
    protocol.set_rail_lights(True)
    protocol.delay(seconds=0.3)
    protocol.set_rail_lights(False)
    protocol.delay(seconds=0.3)
    protocol.set_rail_lights(True)
    protocol.delay(seconds=0.3)
    protocol.set_rail_lights(False)
    protocol.delay(seconds=0.1)
    protocol.set_rail_lights(True)
    protocol.delay(seconds=0.1)
    protocol.set_rail_lights(False)
    protocol.delay(seconds=0.1)
    protocol.set_rail_lights(True)
    protocol.delay(seconds=0.2)
    protocol.set_rail_lights(False)
    protocol.delay(seconds=0.2)
    protocol.set_rail_lights(True)
    protocol.delay(seconds=0.1)
    protocol.set_rail_lights(False)

    protocol.comment('Odie flashes in delight')
