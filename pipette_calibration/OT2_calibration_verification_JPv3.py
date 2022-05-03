from opentrons import protocol_api
from math import floor,ceil
from datetime import datetime
import math

metadata= { 'ctxname':'pipette_calibration_verification_JPv3',
            'apiLevel':'2.8',
            'author':'Justin Pickard',
            'source':'Alturas_Analytics',
            'description':'Verification using single dye for GEN2 P300 and P1000'
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


#load labware
    tuberack1 = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical','1', 'tuberack1')
    tuberack2 = protocol.load_labware('nest_96_wellplate_2ml_deep','2','tuberack2')
    tuberack3 = protocol.load_labware('nest_96_wellplate_200ul_flat','3','tuberack3')

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

    dict_tuberack2={tuberack2['A1']:(0.0,37), tuberack2['A2']:(0.0,37), tuberack2['A3']:(0.0,37), tuberack2['A4']:(0.0,37), 
            tuberack2['A5']:(0.0,37), tuberack2['A6']:(0.0,37), tuberack2['A7']:(0.0,37), tuberack2['A8']:(0.0,37), 
            tuberack2['A9']:(0.0,37), tuberack2['A10']:(0.0,37), tuberack2['A11']:(0.0,37), tuberack2['A12']:(0.0,37), 
            tuberack2['B1']:(0.0,37), tuberack2['B2']:(0.0,37), tuberack2['B3']:(0.0,37), tuberack2['B4']:(0.0,37), 
            tuberack2['B5']:(0.0,37), tuberack2['B6']:(0.0,37), tuberack2['B7']:(0.0,37), tuberack2['B8']:(0.0,37), 
            tuberack2['B9']:(0.0,37), tuberack2['B10']:(0.0,37), tuberack2['B11']:(0.0,37), tuberack2['B12']:(0.0,37), 
            tuberack2['C1']:(0.0,37), tuberack2['C2']:(0.0,37), tuberack2['C3']:(0.0,37), tuberack2['C4']:(0.0,37), 
            tuberack2['C5']:(0.0,37), tuberack2['C6']:(0.0,37), tuberack2['C7']:(0.0,37), tuberack2['C8']:(0.0,37), 
            tuberack2['C9']:(0.0,37), tuberack2['C10']:(0.0,37), tuberack2['C11']:(0.0,37), tuberack2['C12']:(0.0,37), 
            tuberack2['D1']:(0.0,37), tuberack2['D2']:(0.0,37), tuberack2['D3']:(0.0,37), tuberack2['D4']:(0.0,37), 
            tuberack2['D5']:(0.0,37), tuberack2['D6']:(0.0,37), tuberack2['D7']:(0.0,37), tuberack2['D8']:(0.0,37), 
            tuberack2['D9']:(0.0,37), tuberack2['D10']:(0.0,37), tuberack2['D11']:(0.0,37), tuberack2['D12']:(0.0,37), 
            tuberack2['E1']:(300.0,37), tuberack2['E2']:(300.0,37), tuberack2['E3']:(300.0,37), tuberack2['E4']:(300.0,37), 
            tuberack2['E5']:(300.0,37), tuberack2['E6']:(300.0,37), tuberack2['E7']:(300.0,37), tuberack2['E8']:(300.0,37), 
            tuberack2['E9']:(300.0,37), tuberack2['E10']:(300.0,37), tuberack2['E11']:(300.0,37), tuberack2['E12']:(300.0,37), 
            tuberack2['F1']:(500.0,37), tuberack2['F2']:(500.0,37), tuberack2['F3']:(500.0,37), tuberack2['F4']:(500.0,37), 
            tuberack2['F5']:(500.0,37), tuberack2['F6']:(500.0,37), tuberack2['F7']:(500.0,37), tuberack2['F8']:(500.0,37), 
            tuberack2['F9']:(500.0,37), tuberack2['F10']:(500.0,37), tuberack2['F11']:(500.0,37), tuberack2['F12']:(500.0,37), 
            tuberack2['G1']:(0.0,37), tuberack2['G2']:(0.0,37), tuberack2['G3']:(0.0,37), tuberack2['G4']:(0.0,37), 
            tuberack2['G5']:(0.0,37), tuberack2['G6']:(0.0,37), tuberack2['G7']:(0.0,37), tuberack2['G8']:(0.0,37), 
            tuberack2['G9']:(0.0,37), tuberack2['G10']:(0.0,37), tuberack2['G11']:(0.0,37), tuberack2['G12']:(0.0,37), 
            tuberack2['H1']:(0.0,37), tuberack2['H2']:(0.0,37), tuberack2['H3']:(0.0,37), tuberack2['H4']:(0.0,37), 
            tuberack2['H5']:(0.0,37), tuberack2['H6']:(0.0,37), tuberack2['H7']:(0.0,37), tuberack2['H8']:(0.0,37), 
            tuberack2['H9']:(0.0,37), tuberack2['H10']:(0.0,37), tuberack2['H11']:(0.0,37), tuberack2['H12']:(0.0,37), 
            }
    
    dict_tuberack3={tuberack3['A1']:(200.0,6), tuberack3['A2']:(200.0,6), tuberack3['A3']:(200.0,6), tuberack3['A4']:(200.0,6), 
            tuberack3['A5']:(200.0,6), tuberack3['A6']:(200.0,6), tuberack3['A7']:(200.0,6), tuberack3['A8']:(200.0,6), 
            tuberack3['A9']:(200.0,6), tuberack3['A10']:(200.0,6), tuberack3['A11']:(200.0,6), tuberack3['A12']:(200.0,6), 
            tuberack3['B1']:(200.0,6), tuberack3['B2']:(200.0,6), tuberack3['B3']:(200.0,6), tuberack3['B4']:(200.0,6), 
            tuberack3['B5']:(200.0,6), tuberack3['B6']:(200.0,6), tuberack3['B7']:(200.0,6), tuberack3['B8']:(200.0,6), 
            tuberack3['B9']:(200.0,6), tuberack3['B10']:(200.0,6), tuberack3['B11']:(200.0,6), tuberack3['B12']:(200.0,6), 
            tuberack3['C1']:(180.0,6), tuberack3['C2']:(180.0,6), tuberack3['C3']:(180.0,6), tuberack3['C4']:(180.0,6), 
            tuberack3['C5']:(180.0,6), tuberack3['C6']:(180.0,6), tuberack3['C7']:(180.0,6), tuberack3['C8']:(180.0,6), 
            tuberack3['C9']:(180.0,6), tuberack3['C10']:(180.0,6), tuberack3['C11']:(180.0,6), tuberack3['C12']:(180.0,6), 
            tuberack3['D1']:(100.0,6), tuberack3['D2']:(100.0,6), tuberack3['D3']:(100.0,6), tuberack3['D4']:(100.0,6), 
            tuberack3['D5']:(100.0,6), tuberack3['D6']:(100.0,6), tuberack3['D7']:(100.0,6), tuberack3['D8']:(100.0,6), 
            tuberack3['D9']:(100.0,6), tuberack3['D10']:(100.0,6), tuberack3['D11']:(100.0,6), tuberack3['D12']:(100.0,6), 
            tuberack3['E1']:(0.0,6), tuberack3['E2']:(0.0,6), tuberack3['E3']:(0.0,6), tuberack3['E4']:(0.0,6), 
            tuberack3['E5']:(0.0,6), tuberack3['E6']:(0.0,6), tuberack3['E7']:(0.0,6), tuberack3['E8']:(0.0,6), 
            tuberack3['E9']:(0.0,6), tuberack3['E10']:(0.0,6), tuberack3['E11']:(0.0,6), tuberack3['E12']:(0.0,6), 
            tuberack3['F1']:(0.0,6), tuberack3['F2']:(0.0,6), tuberack3['F3']:(0.0,6), tuberack3['F4']:(0.0,6), 
            tuberack3['F5']:(0.0,6), tuberack3['F6']:(0.0,6), tuberack3['F7']:(0.0,6), tuberack3['F8']:(0.0,6), 
            tuberack3['F9']:(0.0,6), tuberack3['F10']:(0.0,6), tuberack3['F11']:(0.0,6), tuberack3['F12']:(0.0,6), 
            tuberack3['G1']:(0.0,6), tuberack3['G2']:(0.0,6), tuberack3['G3']:(0.0,6), tuberack3['G4']:(0.0,6), 
            tuberack3['G5']:(0.0,6), tuberack3['G6']:(0.0,6), tuberack3['G7']:(0.0,6), tuberack3['G8']:(0.0,6), 
            tuberack3['G9']:(0.0,6), tuberack3['G10']:(0.0,6), tuberack3['G11']:(0.0,6), tuberack3['G12']:(0.0,6), 
            tuberack3['H1']:(0.0,6), tuberack3['H2']:(0.0,6), tuberack3['H3']:(0.0,6), tuberack3['H4']:(0.0,6), 
            tuberack3['H5']:(0.0,6), tuberack3['H6']:(0.0,6), tuberack3['H7']:(0.0,6), tuberack3['H8']:(0.0,6), 
            tuberack3['H9']:(0.0,6), tuberack3['H10']:(0.0,6), tuberack3['H11']:(0.0,6), tuberack3['H12']:(0.0,6), 
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
        2500.0: 11, 2000.0: 9, 1500.0: 8, 1000.0: 6, 900.0: 3, 800.0: 2, 700.0: 2, 600.0: 2, 500.0: 2, 400.0: 1, 300.0: 1, 200.0: 1, 100.0: 1 
        }
    
    
    vol_2000={2000.0: 37, 1900.0: 33, 1800.0: 33, 1700.0: 25, 1600.0: 25,
        1500.0: 25, 1400.0: 25, 1300.0: 25, 1200.0: 22, 1100.0: 22, 
        1000.0: 15, 900.0: 15, 800.0: 10, 700.0: 10, 600.0: 10, 
        500.0: 7, 400.0: 7, 300.0: 5, 200.0: 5, 100.0: 4, 
        90.0: 2, 80.0: 2, 70.0: 2, 60.0: 1, 50.0: 1, 40.0: 1, 
        30.0: 1, 20.0: 1, 10.0: 1}

    vol_200={200.0: 6, 100.0: 4, 90.0: 1, 80.0: 1, 
        70.0: 1, 60.0: 1, 50.0: 1, 40.0: 1, 
        30.0: 1, 20.0: 1, 10.0: 1}

#custom command
    def wet_tip(pip,vol_dict,dict_labware,labware,well):
            asp_h1=get_height(dict_labware, labware, well)
            max_vol=pip.max_volume
                
            pip.flow_rate.aspirate = max_vol/2 if max_vol < 300 else 150
            pip.flow_rate.dispense = max_vol if max_vol<300 else 300
            disp_waste=101
            
            asp_master(max_vol,vol_dict,dict_labware,labware,well)
            pip.aspirate(max_vol,labware[well].bottom(z=asp_h1))
            disp_master(max_vol, vol_dict, dict_labware, labware, well)
            pip.dispense(max_vol,tuberack1[well].bottom(z=disp_waste))
            pip.blow_out(tuberack1[well].bottom(z=disp_waste))
            protocol.comment(str(asp_h1))

            asp_h1=get_height(dict_labware, labware, well)
            asp_master(max_vol,vol_dict,dict_labware,labware,well)
            pip.aspirate(max_vol,labware[well].bottom(z=asp_h1))
            disp_master(max_vol, vol_dict, dict_labware, labware, well)
            pip.dispense(max_vol,tuberack1[well].bottom(z=disp_waste))
            pip.blow_out(tuberack1[well].bottom(z=disp_waste))
            protocol.comment(str(asp_h1))

            asp_h1=get_height(dict_labware, labware, well)
            asp_master(max_vol,vol_dict,dict_labware,labware,well)
            pip.aspirate(max_vol,labware[well].bottom(z=asp_h1))
            disp_master(max_vol, vol_dict, dict_labware, labware, well)
            pip.dispense(max_vol,tuberack1[well].bottom(z=disp_waste))
            pip.blow_out(tuberack1[well].bottom(z=disp_waste))
            protocol.comment(str(asp_h1))

    def one_to_one(pip, volume, asp_vol_dict, asp_lab_dict, asp_labware, asp_well, dsp_vol_dict, dsp_lab_dict, dsp_labware, dsp_well):
        num_trans= math.ceil(volume/pip.max_volume)
        vol_per_trans=float(volume/num_trans)
        pip_flow_rate(volume)
        if asp_labware==tuberack2:
            asp_vol_dict=vol_2000
        elif asp_labware==tuberack3:
            asp_vol_dict=vol_200
        else:
            pass 
        for n in range(num_trans):
            asp_master(vol_per_trans, asp_vol_dict, asp_lab_dict, asp_labware, asp_well)
            disp_master(vol_per_trans, dsp_vol_dict, dsp_lab_dict, dsp_labware, dsp_well)    
            tup1=asp_lab_dict.get(asp_labware[asp_well])
            tup2=dsp_lab_dict.get(dsp_labware[dsp_well])
            h1=tup1[1]
            v1=tup1[0]
            h2=tup2[1]
            v2=tup2[0]
            
            pip.aspirate(vol_per_trans, asp_labware[asp_well].bottom(z=h1))
            pip.dispense(vol_per_trans, dsp_labware[dsp_well].bottom(z=h2))
            if pip==p300:
                pip.blow_out(dsp_labware[dsp_well].bottom(z=h2))
                pip.blow_out(dsp_labware[dsp_well].bottom(z=h2+5))
            elif pip==p1000:
                pip.blow_out(dsp_labware[dsp_well].bottom(z=h2+5))

    def mix_mix(pip, lab_dict,labware, well):
        pip.flow_rate.aspirate=150
        pip.flow_rate.dispense=300
        h1=2
        volume=pip.max_volume
        vol1=get_volume(lab_dict,labware,well)
        if vol1 >= 6000:
            h1=get_height(lab_dict,labware,well)-10
        else:
            h1=2
        pip.aspirate(volume, labware[well].bottom(z=h1))
        pip.dispense(volume, labware[well].bottom(z=h1))
        pip.aspirate(volume, labware[well].bottom(z=h1))
        pip.dispense(volume, labware[well].bottom(z=h1))
        pip.aspirate(volume, labware[well].bottom(z=h1))
        pip.dispense(volume, labware[well].bottom(z=h1))
        pip.aspirate(volume, labware[well].bottom(z=h1))
        pip.dispense(volume, labware[well].bottom(z=h1))
        pip.blow_out(labware[well].bottom(z=h1))
        pip.blow_out(labware[well].bottom(z=h1+5))
    
    def small_mix(pip,lab_dict,labware, well):
        pip.flow_rate.aspirate=150
        pip.flow_rate.dispense=300
        h1=2
        volume=100
        pip.aspirate(volume, labware[well].bottom(z=h1))
        pip.dispense(volume, labware[well].bottom(z=h1))
        pip.aspirate(volume, labware[well].bottom(z=h1))
        pip.dispense(volume, labware[well].bottom(z=h1))
        pip.aspirate(volume, labware[well].bottom(z=h1))
        pip.dispense(volume, labware[well].bottom(z=h1))
        pip.aspirate(volume, labware[well].bottom(z=h1))
        pip.dispense(volume, labware[well].bottom(z=h1))
        pip.blow_out(labware[well].bottom(z=h1))
        pip.blow_out(labware[well].bottom(z=h1+5))
    

    row_C=['C1','C2','C3','C4','C5','C6','C7','C8','C9','C10','C11','C12']
    row_D=['D1','D2','D3','D4','D5','D6','D7','D8','D9','D10','D11','D12']
    row_E=['E1','E2','E3','E4','E5','E6','E7','E8','E9','E10','E11','E12']
    row_F=['F1','F2','F3','F4','F5','F6','F7','F8','F9','F10','F11','F12']
#pip condition
    p300.pick_up_tip()
    wet_tip(p300, vol_50, dict_tuberack1, tuberack1, 'A3')


#transfer to 2000uL plate
    for well in row_E:
        one_to_one(p300,300,vol_50,dict_tuberack1,tuberack1,'A3',vol_2000,dict_tuberack2,tuberack2,well)

#condition 
    p300.drop_tip()
    p300.pick_up_tip()
    wet_tip(p300, vol_50, dict_tuberack1, tuberack1, 'A3')

#transfer to 200ul plate
    for well in row_C:
        one_to_one(p300,20,vol_50,dict_tuberack1,tuberack1,'A3',vol_200,dict_tuberack3,tuberack3,well)

#condition 
    p300.drop_tip()
    p300.home()
    p1000.home()
    p1000.pick_up_tip()
    wet_tip(p1000, vol_50, dict_tuberack1, tuberack1, 'A3')


#transfer to 2000ul plate
    for well in row_F:
        one_to_one(p1000,1000,vol_50,dict_tuberack1,tuberack1,'A3',vol_2000,dict_tuberack2,tuberack2,well)

#condition
    p1000.drop_tip()
    p1000.pick_up_tip()
    wet_tip(p1000, vol_50, dict_tuberack1, tuberack1, 'A3')


#transfer to 200ul
    for well in row_D:
        one_to_one(p1000,100,vol_50,dict_tuberack1,tuberack1,'A3',vol_200,dict_tuberack3,tuberack3,well)


#condition
    p1000.drop_tip()
    p1000.home()
    p300.pick_up_tip()
    

#mix row E in 2000ul
    for well in row_E:
        mix_mix(p300,dict_tuberack2, tuberack2, well)


#transfer row E 2000ul to 200ul
    for well in row_E:
        one_to_one(p300,200,vol_2000,dict_tuberack2,tuberack2,well,vol_200,dict_tuberack3,tuberack3,well)

#condition
    p300.drop_tip()
    p300.pick_up_tip()


#mix row F in 2000ul
    for well in row_F:
        mix_mix(p300, dict_tuberack2, tuberack2, well)


#transfer row F 2000ul to 200ul
    for well in row_F:
        one_to_one(p300,200,vol_2000,dict_tuberack2,tuberack2,well,vol_200,dict_tuberack3,tuberack3,well)

#condition
    p300.drop_tip()
    p300.pick_up_tip()
    
    
#mix row C in 200ul
    for well in row_C:
        small_mix(p300, dict_tuberack3, tuberack3, well)

#condition
    p300.drop_tip()
    p300.pick_up_tip()
    
#mix row D in 200ul
    for well in row_D:
        small_mix(p300, dict_tuberack3, tuberack3, well)
    p300.drop_tip()
#END
    protocol.comment("Odie seems satisfied")