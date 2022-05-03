from opentrons import protocol_api
from math import floor,ceil
from datetime import datetime

metadata= { 'ctxname':'Liquid_verification_JPv3',
            'apiLevel':'2.11',
            'author':'Justin Pickard',
            'source':'Alturas_Analytics',
            'description':'Liquid verification using data from liquid characterization'
        }
#updated flow_rate and mix_mix procedure

def run (protocol: protocol_api.ProtocolContext):
#Change these values according to OT2 protocol writing tool
#save as new file with liquid in title

    vol_p300_low  = 21.0    #default 21.0
    vol_p300_high = 300.0   #default 300.0
    vol_p1000_low = 101.0   #default 101.0
    vol_p1000_high= 1000.0  #default 1000.0

#volume tracking modules
    def pip_flow_rate(volume):
            new_asp_flow=volume
            new_dsp_flow=volume*2        
            if volume <=37:
                new_dsp_flow=150
                p300.flow_rate.aspirate=new_asp_flow
                p300.flow_rate.dispense=new_dsp_flow
            else:
                if new_asp_flow <= 150:
                    p300.flow_rate.aspirate=new_asp_flow
                    p1000.flow_rate.aspirate=new_asp_flow
                    p300.flow_rate.dispense=new_dsp_flow
                    p1000.flow_rate.dispense=new_dsp_flow

                else:
                    p300.flow_rate.aspirate=150
                    p1000.flow_rate.aspirate=150
                    p300.flow_rate.dispense=300
                    p1000.flow_rate.dispense=300
        

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
        
        tup = dict_labware.get(labware[well])
        volume1 = tup[0]
        volume2 = volume
        adj_volume = volume1-volume2
        adj_list=list(tup)
        adj_list[0]=(adj_volume)
        tup=tuple(adj_list)
        return tup[0]

    def get_volume(dict_labware,labware,well):
        tup = dict_labware.get(labware[well])
        return tup[0]
    def get_height(dict_labware,labware,well):
        tup = dict_labware.get(labware[well])
        return tup[1]
    def round_up(volume,divisor):
        vol=ceil(volume/divisor)*divisor
        return vol
    def round_d_500(volume):
        x=volume-(volume%500)
        return (x)
    def tup_update_add(volume,dict_vol,dict_labware,labware,well):


        tup = dict_labware[labware[well]]
        adj_list=list(tup)
        adj_list[0]=volume
        divisor=1
        if volume >=2000.0:
            vol_even=round_d_500(volume)
        elif 100.0 <= volume <2000.0:
            divisor=100.0
            vol_even=round_up(volume,divisor)
        else:
            divisor = 10.0
            vol_even=round_up(volume,divisor)

        new_height=dict_vol.get(vol_even)
        adj_list[1]=new_height

        new_tup=tuple(adj_list)
        dict_labware[labware[well]]= new_tup

    def round_down(volume,divisor):
        vol_even=floor(volume/divisor)*divisor
        return vol_even

    def tup_update_sub(volume,dict_vol,dict_labware,labware,well):

        tup = dict_labware.get(labware[well])
        adj_list=list(tup)
        adj_list[0]=volume
        divisor=1.0

        if volume >=2000.0:
            vol_even=round_d_500(volume)

        elif 100.0 <= volume <2000.0:
            divisor=100.0
            vol_even=round_down(volume,divisor)
        else:
            divisor=10.0
            vol_even=round_down(volume,divisor)

        new_height=dict_vol.get(vol_even)
        adj_list[1]=new_height

        new_tup=tuple(adj_list)
        dict_labware[labware[well]]= new_tup

    def disp_master(volume,dict_vol,dict_labware,labware,well):
            new_vol=volume_add(volume,dict_labware,labware,well)
            tup_update_add(new_vol,dict_vol,dict_labware,labware,well)

    def asp_master(volume,dict_vol,dict_labware,labware,well):
        
        new_vol=volume_sub(volume,dict_labware,labware,well)
        tup_update_sub(new_vol,dict_vol,dict_labware,labware,well)

#load labware
    tuberack1 = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical','1', 'tuberack1')
    tuberack2 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap','2','tuberack2')
    

    tiprack= protocol.load_labware('opentrons_96_tiprack_300ul','4')
    tiprack1000 = protocol.load_labware('opentrons_96_tiprack_1000ul', '5')

    p1000 = protocol.load_instrument('p1000_single_gen2','right', tip_racks=[tiprack1000])
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack])
    
    trash = protocol.fixed_trash['A1']

#dictionary for volume tracking, put starting volumes in corresponding wells
    dict_tuberack1={tuberack1['A1']:(0,104), tuberack1['A2']:(0,104), 
        tuberack1['A3']:(50000,94),tuberack1['A4']:(0,94),
        tuberack1['B1']:(0,104), tuberack1['B2']:(0,104), 
        tuberack1['B3']:(0,94),tuberack1['B4']:(0,94),
        tuberack1['C1']:(0,104), tuberack1['C2']:(0,104), 
        }
    dict_tuberack2={tuberack2['A1']:(0,34), tuberack2['A2']:(0,34), tuberack2['A3']:(0,34),
        tuberack2['A4']:(0,34), tuberack2['A5']:(0,34), tuberack2['A6']:(0,34),
        tuberack2['B1']:(0,34), tuberack2['B2']:(0,34), tuberack2['B3']:(0,34),
        tuberack2['B4']:(0,34), tuberack2['B5']:(0,34), tuberack2['B6']:(0,34),
        tuberack2['C1']:(0,34), tuberack2['C2']:(0,34), tuberack2['C3']:(0,34),
        tuberack2['C4']:(0,34), tuberack2['C5']:(0,34), tuberack2['C6']:(0,34),
        tuberack2['D1']:(0,34), tuberack2['D2']:(0,34), tuberack2['D3']:(0,34),
        tuberack2['D4']:(0,34), tuberack2['D5']:(0,34), tuberack2['D6']:(0,34)
        }        

#volume table
    vol_50= {50000.0: 99, 49500.0: 98, 49000.0: 97, 48500.0: 96, 48000.0: 95, 47500.0: 94, 47000.0: 93, 46500.0: 92, 46000.0: 91, 45500.0: 90, 
        45000.0: 89, 44500.0: 88, 44000.0: 87, 43500.0: 87, 43000.0: 86, 42500.0: 85, 42000: 84, 41500.0: 83, 41000.0: 82, 40500.0: 81, 40000.0: 80,  39500.0: 79,
        39000.0: 78, 38500.0: 77, 38000.0: 76, 37500.0: 76, 37000.0: 75, 36500.0: 74, 36000: 73, 35500.0: 72, 35000.0: 71, 34500.0: 70, 34000.0: 69, 33500.0: 68, 
        33000.0: 67, 32500.0: 66, 32000.0: 65, 31500.0: 64, 31000.0: 64, 30500.0: 63, 30000: 62, 29500.0: 61, 29000.0: 60, 28500.0: 59, 28000.0: 58,  27500.0: 57,
        27000.0: 56, 26500.0: 55, 26000.0: 54, 25500.0: 53, 25000.0: 53, 24500.0: 52, 24000: 51, 23500.0: 50, 23000.0: 49, 22500.0: 48, 22000.0: 47, 21500.0: 46,
        21000.0: 45, 20500.0: 44, 20000.0: 43, 19500.0: 42, 19000.0: 41, 18500.0: 41, 18000: 40, 17500.0: 39, 17000.0: 38, 16500.0: 37, 16000.0: 36, 15500.0: 35, 
        15000.0: 34, 14500.0: 33, 14000.0: 32, 13500: 31, 13000.0: 30, 12500.0: 30, 12000.0: 29, 11500.0: 28, 11000.0: 27, 10500.0: 26, 10000.0: 25, 9500.0: 24,
        9000.0: 23, 8500.0: 22, 8000.0: 21, 7500: 20, 7000.0: 19, 6500.0: 18, 6000.0: 18, 5500: 17, 5000.0: 16, 4500: 15, 4000: 14, 3500.0: 14, 3000.0: 13,
        2500.0: 11, 2000.0: 9, 1900.0:8, 1800.0:8, 1700.0:8, 1600.0:8, 1500.0: 8, 1400.0:6, 1300.0:6, 1200.0:6, 1100.0:6, 1000.0: 6, 900.0: 3, 800.0: 2, 700.0: 2, 
        600.0: 2, 500.0: 2, 400.0: 1, 300.0: 1, 200.0: 1, 100.0: 1 
        }

    vol_15={14000.0: 104, 13500.0: 101, 13000.0: 98, 12500.0: 94, 
        12000.0: 91, 11500.0: 88, 11000.0: 85, 10500.0: 81, 
        10000.0: 78, 9500.0: 75, 9000.0: 72, 8500.0: 68, 
        8000.0: 65, 7500.0: 62, 7000.0: 59, 6500.0: 55, 
        6000.0: 52, 5500.0: 49, 5000.0: 46, 4500.0: 42, 
        4000.0: 39, 3500.0: 36, 3000.0: 33, 2500.0: 29, 
        2000.0: 26, 1900.0:22, 1800.0:22, 1700.0:22, 1600.0:22,
        1500.0:20, 1400.0:19, 1300.0:19, 1200.0:19, 1100.0:19, 1000.0: 19, 900.0: 15, 800.0: 15, 
        700.0: 15, 600.0: 15, 500.0: 15, 400.0: 13, 
        300.0: 11, 200.0: 9, 100.0: 6, 90.0: 2, 80.0: 2,
        70.0: 2, 60.0: 2, 50.0: 1, 40.0: 1, 30.0: 1,
        20.0: 1, 10.0: 1
        }
    
    vol_1500={1500.0: 32, 1400.0: 28, 1300.0: 26, 1200.0: 24,
        1100.0: 22, 1000.0: 20, 900.0: 18, 800.0: 18, 
        700.0: 18, 600.0: 16, 500.0: 16, 400.0: 12, 
        300.0: 12, 200.0:5, 100.0: 5, 90.0: 1, 80.0: 1, 70.0: 1, 
        60.0: 1, 50.0: 1, 40.0: 1, 30.0: 1, 20.0: 1, 10.0: 1
        }


#custom command
    def mix_mix(pip,lab_dict,labware, well):
        pip.flow_rate.aspirate=150
        pip.flow_rate.dispense=300
        volume=pip.max_volume
        
        asp_master(volume,vol_50,lab_dict,labware,well)
        h1=get_height(lab_dict,labware,well)
        
        pip.aspirate(volume, labware[well].bottom(z=h1))
        pip.dispense(volume, labware[well].bottom(z=h1))
        pip.aspirate(volume, labware[well].bottom(z=h1))
        pip.dispense(volume, labware[well].bottom(z=h1))
        pip.aspirate(volume, labware[well].bottom(z=h1))
        pip.dispense(volume, labware[well].bottom(z=h1))
        pip.aspirate(volume, labware[well].bottom(z=h1))
        pip.dispense(volume, labware[well].bottom(z=h1+5))
        disp_master(volume,vol_50,lab_dict,labware,well)
        pip.blow_out(labware[well].bottom(z=h1+5))
        pip.blow_out(labware[well].bottom(z=h1+5))
    
    
    def one_to_one(pip, volume, asp_vol_dict, asp_lab_dict, asp_labware, asp_well, dsp_vol_dict, dsp_lab_dict, dsp_labware, dsp_well):
        pip_flow_rate(volume)
        asp_master(volume, asp_vol_dict, asp_lab_dict, asp_labware, asp_well)
        disp_master(volume, dsp_vol_dict, dsp_lab_dict, dsp_labware, dsp_well)    
        tup1=asp_lab_dict.get(asp_labware[asp_well])
        tup2=dsp_lab_dict.get(dsp_labware[dsp_well])
        h1=tup1[1]
        h2=tup2[1]
               
        pip.aspirate(volume, asp_labware[asp_well].bottom(z=h1))
        pip.dispense(volume, dsp_labware[dsp_well].bottom(z=h2))
        pip.blow_out(dsp_labware[dsp_well].bottom(z=h2))
        pip.blow_out(dsp_labware[dsp_well].bottom(z=h2+5))

    
    rowa=['A1','A2','A3','A4','A5','A6']
    rowb=['B1','B2','B3','B4','B5','B6']
    rowc=['C1','C2','C3','C4','C5','C6']
    rowd=['D1','D2','D3','D4','D5','D6']
    
    p300.pick_up_tip()
    mix_mix(p300,dict_tuberack1,tuberack1,'A3')
    for well in rowa:
        one_to_one(p300,vol_p300_low,vol_50,dict_tuberack1,tuberack1,'A3',vol_1500,dict_tuberack2,tuberack2,well)
    for well in rowb:
        one_to_one(p300,vol_p300_high,vol_50,dict_tuberack1,tuberack1,'A3',vol_1500,dict_tuberack2,tuberack2,well)
    p300.drop_tip()
    
    p1000.pick_up_tip()
    mix_mix(p1000,dict_tuberack1,tuberack1,'A3')
    for well in rowc:
        one_to_one(p1000,vol_p1000_low,vol_50,dict_tuberack1,tuberack1,'A3',vol_1500,dict_tuberack2,tuberack2,well)
    for well in rowd:
        one_to_one(p1000,vol_p1000_high,vol_50,dict_tuberack1,tuberack1,'A3',vol_1500,dict_tuberack2,tuberack2,well)
    
    p1000.drop_tip()
    protocol.comment('Deniro seems satisfied')