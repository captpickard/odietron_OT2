from opentrons import protocol_api
from math import floor,ceil
from datetime import datetime
import math

metadata= { 'ctxname':'dot',
            'apiLevel':'2.8',
            'author':'Justin Pickard',
            'source':'Alturas_Analytics',
            'description':'for making dots on paper'
        }


def run (protocol: protocol_api.ProtocolContext):

#volume tracking modules
    def pip_flow_rate(volume):
        new_asp_flow=volume
        new_dsp_flow=volume*2
        if new_asp_flow <= 150:
            p300.flow_rate.aspirate=new_asp_flow
            p1000.flow_rate.aspirate=new_asp_flow
        else:
            p300.flow_rate.aspirate=150
            p1000.flow_rate.aspirate=150
        
        if new_dsp_flow <= 300:
            p300.flow_rate.dispense=new_dsp_flow
            p1000.flow_rate.dispense=new_dsp_flow
        else:
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
        if volume >=1000.0:
            vol_even=round_d_500(volume)
        elif 100.0 <= volume <1000.0:
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

        if volume >=1000.0:
            vol_even=round_d_500(volume)

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

    def disp_master(volume,dict_vol,dict_labware,labware,well):
            new_vol=volume_add(volume,dict_labware,labware,well)
            tup_update_add(new_vol,dict_vol,dict_labware,labware,well)

    def asp_master(volume,dict_vol,dict_labware,labware,well):
        
        new_vol=volume_sub(volume,dict_labware,labware,well)
        tup_update_sub(new_vol,dict_vol,dict_labware,labware,well)

    tuberack1 = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical','1', 'tuberack1')
    tuberack2 = protocol.load_labware('corning_384_wellplate_112ul_flat','2','tuberack2')
    

    tiprack= protocol.load_labware('opentrons_96_tiprack_300ul','4')
    tiprack1000 = protocol.load_labware('opentrons_96_tiprack_1000ul', '5')

    p1000 = protocol.load_instrument('p1000_single_gen2','right', tip_racks=[tiprack1000])
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack])
    

    trash = protocol.fixed_trash['A1']

    dict_tuberack1={tuberack1['A1']:(5000.0,104.0), tuberack1['A2']:(0.0,104.0), 
        tuberack1['A3']:(0.0,99.0),tuberack1['A4']:(0.0,94.0),
        tuberack1['B1']:(0.0,104.0), tuberack1['B2']:(0.0,104.0), 
        tuberack1['B3']:(0.0,94.0),tuberack1['B4']:(0.0,94.0),
        tuberack1['C1']:(0.0,104.0), tuberack1['C2']:(0.0,104.0), 
        }
    vol_15= {14000: 104, 13500: 101, 13000: 98, 12500: 94, 
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

    def dot(pip,vol,vol_dict,lab_dict,asp_lab,dsp_lab, well):
        asp_master(vol,vol_dict,lab_dict,asp_lab,'A1')

        h1=get_height(dict_tuberack1,tuberack1,'A1')
        pip.aspirate(vol,asp_lab['A1'].bottom(z=h1))
        pip.dispense(vol,dsp_lab[well].bottom(z=4))
    
    def slicer(well_list,n):
        p=len(well_list) // n
        if len(well_list)-p >0:
            return [well_list[:p]] + slicer(well_list[p:], n-1)
        else:
            return [well_list]

    def dot_dot(vol,vol_dict,lab_dict,asp_lab,dsp_lab,well_list):
        
        #slicer interval is 13 for 384 wells at 10ul       
        trans_list=slicer(well_list,13)
                
        for lst in trans_list:
            max_v=len(lst)*vol
            asp_master(max_v,vol_dict,lab_dict,asp_lab,'A1')
            h1=get_height(dict_tuberack1,tuberack1,'A1')
            p300.aspirate(max_v,asp_lab['A1'].bottom(z=h1))
            for well in lst:
                p300.dispense(vol,dsp_lab[well].bottom(z=4))

            


    p300.flow_rate.aspirate=300
    p300.flow_rate.dispense=100
   #compile a list of wells for dot_dot
    letter=['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']
    number=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
    every_well=[]
    
    for let in letter:
        for num in number:
            new_well=str(let+str(num))
            every_well.append(new_well)
            
    p300.pick_up_tip()
    dot_dot(10,vol_15,dict_tuberack1,tuberack1,tuberack2,every_well)
    p300.drop_tip()

    protocol.comment('Deniro seems satisfied')