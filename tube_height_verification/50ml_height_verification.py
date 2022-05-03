from opentrons import protocol_api
from math import floor,ceil
from datetime import datetime

metadata= { 'ctxname':'50ml_height_verification',
            'apiLevel':'2.8',
            'author':'JEP',
            'description':'verify height for 50mL starstedt tube',
        }

#module will be executed by OT2
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
    tuberack1 = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical','1', 'tuberack1')

#pipette tips
    tiprack= protocol.load_labware('opentrons_96_tiprack_300ul','4')
    tiprack1000 = protocol.load_labware('opentrons_96_tiprack_1000ul', '8')
#pipettes
    p1000 = protocol.load_instrument('p1000_single_gen2','right', tip_racks=[tiprack1000])
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack])
    p1000.home
#assign permanent deck slot to trash
    trash = protocol.fixed_trash['A1']
#setting initial pipette conditions    
    p1000.flow_rate.aspirate = 300
    p1000.flow_rate.dispense = 300 
   

#volume tracking
    dict_tuberack1={tuberack1['A1']:(0,104), tuberack1['A2']:(0,104), 
        tuberack1['A3']:(0,94),tuberack1['A4']:(0,94),
        tuberack1['B1']:(0,104), tuberack1['B2']:(0,104), 
        tuberack1['B3']:(50000,94),tuberack1['B4']:(0,94),
        tuberack1['C1']:(0,104), tuberack1['C2']:(0,104)}

#volume reference (passed verification with 50mL starstedt) use modules from \templates\volume_tracking.py
    vol_50= {50000: 99, 49500: 98, 49000: 97, 48500: 96, 48000: 95, 47500: 94, 47000: 93, 46500: 92, 46000: 91, 45500: 90, 
        45000: 89, 44500: 88, 44000: 87, 43500: 87, 43000: 86, 42500: 85, 42000: 84, 41500: 83, 41000: 82, 40500: 81, 40000: 80,  39500: 79,
        39000: 78, 38500: 77, 38000: 76, 37500: 76, 37000: 75, 36500: 74, 36000: 73, 35500: 72, 35000: 71, 34500: 70, 34000: 69, 33500: 68, 
        33000: 67, 32500: 66, 32000: 65, 31500: 64, 31000: 64, 30500: 63, 30000: 62, 29500: 61, 29000: 60, 28500: 59, 28000: 58,  27500: 57,
        27000: 56, 26500: 55, 26000: 54, 25500: 53, 25000: 53, 24500: 52, 24000: 51, 23500: 50, 23000: 49, 22500: 48, 22000: 47, 21500: 46,
        21000: 45, 20500: 44, 20000: 43, 19500: 42, 19000: 41, 18500: 41, 18000: 40, 17500: 39, 17000: 38, 16500: 37, 16000: 36, 15500: 35, 
        15000: 34, 14500: 33, 14000: 32, 13500: 31, 13000: 30, 12500: 30, 12000: 29, 11500: 28, 11000: 27, 10500: 26, 10000: 25, 
        9500: 24, 9000: 23, 8500: 22, 8000: 21, 7500: 20, 7000: 19, 6500: 18, 6000: 18, 5500: 17, 5000: 16, 4500: 15, 4000: 14, 
        3500: 14, 3000: 13, 2500: 11, 2000: 9, 1500: 8, 1000: 6, 900: 3, 800: 2, 700: 2, 600: 2, 
        500: 2, 400: 1, 300: 1, 200: 1, 100: 1}
#commands    
    p1000.pick_up_tip()
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    p1000.mix(3,1000,tuberack1['B3'].bottom(z=h1))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))    
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))

        
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
        
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))    
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')    
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))    
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')    
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))    
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')    
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))    
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')    
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))    
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')   
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))    
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')   
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))    
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')    
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))    
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')    
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))    
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))
    
    h1=get_height(dict_tuberack1, tuberack1,'B3')
    v1=get_volume(dict_tuberack1, tuberack1, 'B3')
    h2=get_height(dict_tuberack1, tuberack1,'B4')
    v2=get_volume(dict_tuberack1, tuberack1,'B4')
    asp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B3')
    p1000.aspirate(1000, tuberack1['B3'].bottom(z=h1))
    protocol.comment(str(h1))
    protocol.comment(str(v1))
    disp_master(1000, vol_50, dict_tuberack1, tuberack1, 'B4')
    p1000.dispense(1000, tuberack1['B4'].bottom(z=h2))
    protocol.comment(str(h2))
    protocol.comment(str(v2))

    protocol.comment('Odie seems delighted')
    