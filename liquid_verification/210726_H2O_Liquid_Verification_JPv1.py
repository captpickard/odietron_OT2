from opentrons import protocol_api
from math import floor,ceil
from datetime import datetime

metadata= { 'ctxname':'H2O_Liquid_Verification_JPv1',
            'apiLevel':'2.8',
            'author':'Justin Pickard',
            'source':'Alturas_Analytics',
            'description':'Liquid Verification'
        }


def run (protocol: protocol_api.ProtocolContext):
#Change these values according to OT2 protocol writing tool
#save as new file with liquid in title

    vol_p300_low  = 20.6    #default 21.0
    vol_p300_high = 299.4   #default 300.0
    vol_p1000_low = 101.2   #default 100.0
    vol_p1000_high= 996.5 #default 1000.0

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
        if  x-y < 0.0:
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
        divisor=1.0

        if volume >=1000.0:
            vol_even=(volume//500.0)*500.0

        elif 100.0 <= volume <1000.0:
            divisor=100.0
            vol_even=round_down(volume,divisor)
        else:
            divisor=10.0
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
        if volume >=1000.0:
            vol_even=-(-volume//500.0)*500.0
        elif 100.0 <= volume <1000.0:
            divisor=100.0
        else:
            divisor = 10.0

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
    tuberack2 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap','2','tuberack2')
    

    tiprack= protocol.load_labware('opentrons_96_tiprack_300ul','4')
    tiprack1000 = protocol.load_labware('opentrons_96_tiprack_1000ul', '5')

    p1000 = protocol.load_instrument('p1000_single_gen2','right', tip_racks=[tiprack1000])
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack])
    

    trash = protocol.fixed_trash['A1']

#dictionary for volume tracking, put starting volumes in corresponding wells
    dict_tuberack1={tuberack1['A1']:(0.0,104.0), tuberack1['A2']:(0.0,104.0), 
                tuberack1['A3']:(50000.0,99.0),tuberack1['A4']:(0.0,94.0),
                tuberack1['B1']:(0.0,104.0), tuberack1['B2']:(0.0,104.0), 
                tuberack1['B3']:(0.0,94.0),tuberack1['B4']:(0.0,94.0),
                tuberack1['C1']:(0.0,104.0), tuberack1['C2']:(0.0,104.0), 
                }
    dict_tuberack2={tuberack2['A1']:(0.0,34.0), tuberack2['A2']:(0.0,34.0), tuberack2['A3']:(0.0,34.0),
            tuberack2['A4']:(0.0,34.0), tuberack2['A5']:(0.0,34.0), tuberack2['A6']:(0.0,34.0),
            tuberack2['B1']:(0.0,34.0), tuberack2['B2']:(0.0,34.0), tuberack2['B3']:(0.0,34.0),
            tuberack2['B4']:(0.0,34.0), tuberack2['B5']:(0.0,34.0), tuberack2['B6']:(0.0,34.0),
            tuberack2['C1']:(0.0,34.0), tuberack2['C2']:(0.0,34.0), tuberack2['C3']:(0.0,34.0),
            tuberack2['C4']:(0.0,34.0), tuberack2['C5']:(0.0,34.0), tuberack2['C6']:(0.0,34.0),
            tuberack2['D1']:(0.0,34.0), tuberack2['D2']:(0.0,34.0), tuberack2['D3']:(0.0,34.0),
            tuberack2['D4']:(0.0,34.0), tuberack2['D5']:(0.0,34.0), tuberack2['D6']:(0.0,34.0),}
#volume table
    vol_1500= {1500.0: 32.0, 1400.0: 30.0, 1300.0: 28.0, 1200: 28.0,
    1100.0: 22.0, 1000.0: 22.0, 900.0: 18.0, 800.0: 18.0,
    700.0: 16.0, 600.0: 12.0, 500.0: 12.0, 400.0: 11.0,
    300.0: 10.0, 200.0:5.0, 100.0: 3.0, 90.0: 1.0, 80.0: 1.0, 70.0: 1.0,
    60.0: 1.0, 50.0: 1.0, 40.0: 1.0, 30.0: 1.0, 20.0: 1.0, 10.0: 1.0}

    vol_50= {50000.0: 99.0, 49500.0: 98.0, 49000.0: 97.0, 48500.0: 96.0, 48000.0: 95.0, 47500.0: 94.0, 47000.0: 93.0, 46500.0: 92.0, 46000.0: 91.0, 45500.0: 90.0, 
        45000.0: 89.0, 44500.0: 88.0, 44000.0: 87.0, 43500.0: 87.0, 43000.0: 86.0, 42500.0: 85.0, 42000.0: 84.0, 41500.0: 83.0, 41000.0: 82.0, 40500.0: 81.0, 40000.0: 80.0,  39500.0: 79.0,
        39000.0: 78.0, 38500.0: 77.0, 38000.0: 76.0, 37500.0: 76.0, 37000.0: 75.0, 36500.0: 74.0, 36000.0: 73.0, 35500.0: 72.0, 35000.0: 71.0, 34500.0: 70.0, 34000.0: 69.0, 33500.0: 68.0, 
        33000.0: 67.0, 32500.0: 66.0, 32000.0: 65.0, 31500.0: 64.0, 31000.0: 64.0, 30500.0: 63.0, 30000.0: 62.0, 29500.0: 61.0, 29000.0: 60.0, 28500.0: 59.0, 28000.0: 58.0,  27500.0: 57.0,
        27000.0: 56.0, 26500.0: 55.0, 26000.0: 54.0, 25500.0: 53.0, 25000.0: 53.0, 24500.0: 52.0, 24000.0: 51.0, 23500.0: 50.0, 23000.0: 49.0, 22500.0: 48.0, 22000.0: 47.0, 21500.0: 46.0,
        21000.0: 45.0, 20500.0: 44.0, 20000.0: 43.0, 19500.0: 42.0, 19000.0: 41.0, 18500.0: 41.0, 18000.0: 40.0, 17500.0: 39.0, 17000.0: 38.0, 16500.0: 37.0, 16000.0: 36.0, 15500.0: 35.0, 
        15000.0: 34.0, 14500.0: 33.0, 14000.0: 32.0, 13500.0: 31.0, 13000.0: 30.0, 12500.0: 30.0, 12000.0: 29.0, 11500.0: 28.0, 11000.0: 27.0, 10500.0: 26.0, 10000.0: 25.0, 9500.0: 24.0,
        9000.0: 23.0, 8500.0: 22.0, 8000.0: 21.0, 7500.0: 20.0, 7000.0: 19.0, 6500.0: 18.0, 6000.0: 18.0, 5500.0: 17.0, 5000.0: 16.0, 4500: 15.0, 4000: 14.0, 3500.0: 14.0, 3000.0: 13.0,
        2500.0: 11.0, 2000.0: 9.0, 1500.0: 8.0, 1000.0: 6.0, 900.0: 3.0, 800.0: 2.0, 700.0: 2.0, 600.0: 2.0, 500.0: 2.0, 400.0: 1.0, 300.0: 1.0, 200.0: 1.0, 100.0: 1.0}

#custom command
    def wet_tip(pip,vol_dict,dict_labware,labware,well):
        if pip==p300:
            asp_h1=get_height(dict_labware, labware, well)
            p300.flow_rate.aspirate = 100
            p300.flow_rate.dispense = 200
            disp_waste=101.0
            
            asp_master(300.0,vol_dict,dict_labware,labware,well)
            pip.aspirate(300.0,labware[well].bottom(z=asp_h1))
            pip.dispense(300.0,tuberack1['A1'].bottom(z=disp_waste))
            pip.blow_out(tuberack1['A1'].bottom(z=disp_waste))
            protocol.comment(str(asp_h1))

            asp_h1=get_height(dict_labware, labware, well)
            asp_master(300.0,vol_dict,dict_labware,labware,well)
            pip.aspirate(300.0,labware[well].bottom(z=asp_h1))
            pip.dispense(300.0,tuberack1['A1'].bottom(z=disp_waste))
            pip.blow_out(tuberack1['A1'].bottom(z=disp_waste))
            protocol.comment(str(asp_h1))

            asp_h1=get_height(dict_labware, labware, well)
            asp_master(300.0,vol_dict,dict_labware,labware,well)
            pip.aspirate(300.0,labware[well].bottom(z=asp_h1))
            pip.dispense(300.0,tuberack1['A1'].bottom(z=disp_waste))
            pip.blow_out(tuberack1['A1'].bottom(z=disp_waste))
            protocol.comment(str(asp_h1))

        elif pip==p1000:
            asp_h1=get_height(dict_labware, labware, well)
            p300.flow_rate.aspirate = 150
            p300.flow_rate.dispense = 300
            disp_waste=101
            
            asp_master(1000,vol_dict,dict_labware,labware,well)
            pip.aspirate(1000,labware[well].bottom(z=asp_h1))
            pip.dispense(1000,tuberack1['A1'].bottom(z=disp_waste))
            pip.blow_out(tuberack1['A1'].bottom(z=disp_waste))
            protocol.comment(str(asp_h1))

            asp_h1=get_height(dict_labware, labware, well)
            asp_master(1000,vol_dict,dict_labware,labware,well)
            pip.aspirate(1000,labware[well].bottom(z=asp_h1))
            pip.dispense(1000,tuberack1['A1'].bottom(z=disp_waste))
            pip.blow_out(tuberack1['A1'].bottom(z=disp_waste))
            protocol.comment(str(asp_h1))

            asp_h1=get_height(dict_labware, labware, well)
            asp_master(1000,vol_dict,dict_labware,labware,well)
            pip.aspirate(1000,labware[well].bottom(z=asp_h1))
            pip.dispense(1000,tuberack1['A1'].bottom(z=disp_waste))
            pip.blow_out(tuberack1['A1'].bottom(z=disp_waste))
            protocol.comment(str(asp_h1))

#set a general dispense distance for aliquots into 1000ul tube
    disp1=2
#pipette setting for 21ul transfer
    p300.pick_up_tip()
    wet_tip(p300, vol_50, dict_tuberack1, tuberack1, 'A3')
       
    p300.flow_rate.aspirate = 21
    p300.flow_rate.dispense = 42
        
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p300_low, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p300.aspirate(vol_p300_low, tuberack1['A3'].bottom(z=hA1))
    p300.dispense(vol_p300_low, tuberack2['A1'].bottom(z=disp1))
    p300.blow_out(tuberack2['A1'].bottom(z=disp1))
    p300.blow_out(tuberack2['A1'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p300_low, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p300.aspirate(vol_p300_low, tuberack1['A3'].bottom(z=hA1))
    p300.dispense(vol_p300_low, tuberack2['A2'].bottom(z=disp1))
    p300.blow_out(tuberack2['A2'].bottom(z=disp1))
    p300.blow_out(tuberack2['A2'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p300_low, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p300.aspirate(vol_p300_low, tuberack1['A3'].bottom(z=hA1))
    p300.dispense(vol_p300_low, tuberack2['A3'].bottom(z=disp1))
    p300.blow_out(tuberack2['A3'].bottom(z=disp1))
    p300.blow_out(tuberack2['A3'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p300_low, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p300.aspirate(vol_p300_low, tuberack1['A3'].bottom(z=hA1))
    p300.dispense(vol_p300_low, tuberack2['A4'].bottom(z=disp1))
    p300.blow_out(tuberack2['A4'].bottom(z=disp1))
    p300.blow_out(tuberack2['A4'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p300_low, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p300.aspirate(vol_p300_low, tuberack1['A3'].bottom(z=hA1))
    p300.dispense(vol_p300_low, tuberack2['A5'].bottom(z=disp1))
    p300.blow_out(tuberack2['A5'].bottom(z=disp1))
    p300.blow_out(tuberack2['A5'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p300_low, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p300.aspirate(vol_p300_low, tuberack1['A3'].bottom(z=hA1))
    p300.dispense(vol_p300_low, tuberack2['A6'].bottom(z=disp1))
    p300.blow_out(tuberack2['A6'].bottom(z=disp1))
    p300.blow_out(tuberack2['A6'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    p300.drop_tip()

#set a general dispense distance for aliquots into 1000ul tube
    disp1=10
#pipette setting for 21ul transfer
    p300.pick_up_tip()
    wet_tip(p300, vol_50, dict_tuberack1, tuberack1, 'A3')
       
    p300.flow_rate.aspirate = 150
    p300.flow_rate.dispense = 300
        
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p300_high, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p300.aspirate(vol_p300_high, tuberack1['A3'].bottom(z=hA1))
    p300.dispense(vol_p300_high, tuberack2['B1'].bottom(z=disp1))
    p300.blow_out(tuberack2['B1'].bottom(z=disp1))
    p300.blow_out(tuberack2['B1'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p300_high, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p300.aspirate(vol_p300_high, tuberack1['A3'].bottom(z=hA1))
    p300.dispense(vol_p300_high, tuberack2['B2'].bottom(z=disp1))
    p300.blow_out(tuberack2['B2'].bottom(z=disp1))
    p300.blow_out(tuberack2['B2'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p300_high, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p300.aspirate(vol_p300_high, tuberack1['A3'].bottom(z=hA1))
    p300.dispense(vol_p300_high, tuberack2['B3'].bottom(z=disp1))
    p300.blow_out(tuberack2['B3'].bottom(z=disp1))
    p300.blow_out(tuberack2['B3'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p300_high, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p300.aspirate(vol_p300_high, tuberack1['A3'].bottom(z=hA1))
    p300.dispense(vol_p300_high, tuberack2['B4'].bottom(z=disp1))
    p300.blow_out(tuberack2['B4'].bottom(z=disp1))
    p300.blow_out(tuberack2['B4'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p300_high, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p300.aspirate(vol_p300_high, tuberack1['A3'].bottom(z=hA1))
    p300.dispense(vol_p300_high, tuberack2['B5'].bottom(z=disp1))
    p300.blow_out(tuberack2['B5'].bottom(z=disp1))
    p300.blow_out(tuberack2['B5'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p300_high, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p300.aspirate(vol_p300_high, tuberack1['A3'].bottom(z=hA1))
    p300.dispense(vol_p300_high, tuberack2['B6'].bottom(z=disp1))
    p300.blow_out(tuberack2['B6'].bottom(z=disp1))
    p300.blow_out(tuberack2['B6'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    p300.drop_tip()

#set a general dispense distance for aliquots into 1500ul tube
    disp1=10

#pipette setting for 100ul transfer
    p1000.flow_rate.aspirate = 100 
    p1000.flow_rate.dispense = 200
    p1000.pick_up_tip()

#tip condition    
    wet_tip(p1000, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p1000_low, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p1000.aspirate(vol_p1000_low, tuberack1['A3'].bottom(z=hA1))
    p1000.dispense(vol_p1000_low, tuberack2['C1'].bottom(z=disp1))
    p1000.blow_out(tuberack2['C1'].bottom(z=disp1+5))
    p1000.blow_out(tuberack2['C1'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p1000_low, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p1000.aspirate(vol_p1000_low, tuberack1['A3'].bottom(z=hA1))
    p1000.dispense(vol_p1000_low, tuberack2['C2'].bottom(z=disp1))
    p1000.blow_out(tuberack2['C2'].bottom(z=disp1+5))
    p1000.blow_out(tuberack2['C2'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p1000_low, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p1000.aspirate(vol_p1000_low, tuberack1['A3'].bottom(z=hA1))
    p1000.dispense(vol_p1000_low, tuberack2['C3'].bottom(z=disp1))
    p1000.blow_out(tuberack2['C3'].bottom(z=disp1+5))
    p1000.blow_out(tuberack2['C3'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p1000_low, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p1000.aspirate(vol_p1000_low, tuberack1['A3'].bottom(z=hA1))
    p1000.dispense(vol_p1000_low, tuberack2['C4'].bottom(z=disp1))
    p1000.blow_out(tuberack2['C4'].bottom(z=disp1+5))
    p1000.blow_out(tuberack2['C4'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p1000_low, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p1000.aspirate(vol_p1000_low, tuberack1['A3'].bottom(z=hA1))
    p1000.dispense(vol_p1000_low, tuberack2['C5'].bottom(z=disp1))
    p1000.blow_out(tuberack2['C5'].bottom(z=disp1+5))
    p1000.blow_out(tuberack2['C5'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p1000_low, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p1000.aspirate(vol_p1000_low, tuberack1['A3'].bottom(z=hA1))
    p1000.dispense(vol_p1000_low, tuberack2['C6'].bottom(z=disp1))
    p1000.blow_out(tuberack2['C6'].bottom(z=disp1+5))
    p1000.blow_out(tuberack2['C6'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))    

    p1000.drop_tip()
    #set a general dispense distance for aliquots into 1500ul tube
    disp1=30

#pipette setting for 100ul transfer
    p1000.flow_rate.aspirate = 150 
    p1000.flow_rate.dispense = 300
    p1000.pick_up_tip()

#tip condition    
    wet_tip(p1000, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p1000_high, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p1000.aspirate(vol_p1000_high, tuberack1['A3'].bottom(z=hA1))
    p1000.dispense(vol_p1000_high, tuberack2['D1'].bottom(z=disp1))
    p1000.blow_out(tuberack2['D1'].bottom(z=disp1+5))
    p1000.blow_out(tuberack2['D1'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p1000_high, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p1000.aspirate(vol_p1000_high, tuberack1['A3'].bottom(z=hA1))
    p1000.dispense(vol_p1000_high, tuberack2['D2'].bottom(z=disp1))
    p1000.blow_out(tuberack2['D2'].bottom(z=disp1+5))
    p1000.blow_out(tuberack2['D2'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p1000_high, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p1000.aspirate(vol_p1000_high, tuberack1['A3'].bottom(z=hA1))
    p1000.dispense(vol_p1000_high, tuberack2['D3'].bottom(z=disp1))
    p1000.blow_out(tuberack2['D3'].bottom(z=disp1+5))
    p1000.blow_out(tuberack2['D3'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p1000_high, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p1000.aspirate(vol_p1000_high, tuberack1['A3'].bottom(z=hA1))
    p1000.dispense(vol_p1000_high, tuberack2['D4'].bottom(z=disp1))
    p1000.blow_out(tuberack2['D4'].bottom(z=disp1+5))
    p1000.blow_out(tuberack2['D4'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p1000_high, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p1000.aspirate(vol_p1000_high, tuberack1['A3'].bottom(z=hA1))
    p1000.dispense(vol_p1000_high, tuberack2['D5'].bottom(z=disp1))
    p1000.blow_out(tuberack2['D5'].bottom(z=disp1+5))
    p1000.blow_out(tuberack2['D5'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))

    asp_master(vol_p1000_high, vol_50, dict_tuberack1, tuberack1, 'A3')
    hA1=get_height(dict_tuberack1, tuberack1,'A3')
    hA2=get_volume(dict_tuberack1, tuberack1, 'A3')
    p1000.aspirate(vol_p1000_high, tuberack1['A3'].bottom(z=hA1))
    p1000.dispense(vol_p1000_high, tuberack2['D6'].bottom(z=disp1))
    p1000.blow_out(tuberack2['D6'].bottom(z=disp1+5))
    p1000.blow_out(tuberack2['D6'].bottom(z=disp1+5))
    protocol.comment(str(hA1))
    protocol.comment(str(hA2))
    
    p1000.drop_tip()

    protocol.comment("Odie seems satisfied")