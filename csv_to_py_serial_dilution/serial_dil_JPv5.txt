from opentrons import protocol_api
import math 
from math import ceil, floor
from datetime import datetime
#JPV5 flow rate was improved

metadata= { 'ctxname':'serial_dilutions',
            'apiLevel':'2.8',
            'author':'Justin Pickard',
            'source':'Alturas_Analytics',
            'description':'Serial Dilution'
        }
def run (protocol: protocol_api.ProtocolContext):
#imported variables
    int1=['STD', 'INT1', '7', 'A1', '0', '0', '250', '0', 'example', '1']
    std8=['STD', 'STD8', '4', 'A3', '1', '0', '21', '2079', 'example', '1']
    std7=['STD', 'STD7', '4', 'A4', '2', '0', '21', '3479', 'example', '1']
    std6=['STD', 'STD6', '4', 'B1', '3', '2', '1470', '1470', 'example', '1']
    std5=['STD', 'STD5', '4', 'B2', '4', '3', '1470', '1470', 'example', '1']
    std4=['STD', 'STD4', '4', 'B4', '5', '4', '1050', '2887', 'example', '1']
    std3=['STD', 'STD3', '4', 'C1', '6', '5', '1050', '3150', 'example', '1']
    std2=['STD', 'STD2', '4', 'C3', '7', '6', '1050', '1575', 'example', '1']
    std1=['STD', 'STD1', '4', 'C4', '8', '7', '1050', '1050', 'example', '1']
    int2=['QC', 'INT2', '7', 'A2', '0', '0', '250', '0', 'example', '1']
    hqc=['QC', 'HQC', '4', 'A5', '2', '0', '21', '2604', 'example', '1']
    mqc=['QC', 'MQC', '4', 'B3', '3', '2', '315', '3284', 'example', '1']
    lqc=['QC', 'LQC', '4', 'C2', '4', '3', '315', '3360', 'example', '1']
#dilution modules    
    class dilution:
        group=''
        parent=''
        parslot=''
        parwell=''
        seq=''
        parseq=''
        stdvol=''
        dilvol=''
        location=''
        

        def __init__(self,group,parent,parslot,parwell,seq,parseq,stdvol,dilvol):
            labware_names=['test','tuberack1','tuberack2','tuberack3','tuberack4','tuberack5','tuberack6','tuberack7','tuberack8','tuberack9']
            self.group=str(group)
            self.parent=parent
            self.parslot=parslot
            self.parwell=parwell
            self.seq=seq
            self.parseq=parseq
            self.stdvol=float(stdvol)
            self.dilvol=float(dilvol)
                     
            self.alivol=0.0
            self.labware=labware_names[int(self.parslot)]
            self.lab_dict='dict_'+self.labware
            self.location=f"{self.labware}[{self.parwell}]"
        

    INT1= (dilution(int1[0],int1[1],int1[2],int1[3],int1[4],int1[5],int1[6],int1[7]))
    STD8= (dilution(std8[0],std8[1],std8[2],std8[3],std8[4],std8[5],std8[6],std8[7]))
    STD7= (dilution(std7[0],std7[1],std7[2],std7[3],std7[4],std7[5],std7[6],std7[7]))
    STD6= (dilution(std6[0],std6[1],std6[2],std6[3],std6[4],std6[5],std6[6],std6[7]))
    STD5= (dilution(std5[0],std5[1],std5[2],std5[3],std5[4],std5[5],std5[6],std5[7]))
    STD4= (dilution(std4[0],std4[1],std4[2],std4[3],std4[4],std4[5],std4[6],std4[7]))
    STD3= (dilution(std3[0],std3[1],std3[2],std3[3],std3[4],std3[5],std3[6],std3[7]))
    STD2= (dilution(std2[0],std2[1],std2[2],std2[3],std2[4],std2[5],std2[6],std2[7]))
    STD1= (dilution(std1[0],std1[1],std1[2],std1[3],std1[4],std1[5],std1[6],std1[7]))
    INT2= (dilution(int2[0],int2[1],int2[2],int2[3],int2[4],int2[5],int2[6],int2[7]))
    HQC= (dilution(hqc[0],hqc[1],hqc[2],hqc[3],hqc[4],hqc[5],hqc[6],hqc[7]))
    MQC= (dilution(mqc[0],mqc[1],mqc[2],mqc[3],mqc[4],mqc[5],mqc[6],mqc[7]))
    LQC= (dilution(lqc[0],lqc[1],lqc[2],lqc[3],lqc[4],lqc[5],lqc[6],lqc[7]))

    stdlist=[]
    qclist=[]
    stdlist.append(INT1)
    stdlist.append(STD8)
    stdlist.append(STD7)
    stdlist.append(STD6)
    stdlist.append(STD5)
    stdlist.append(STD4)
    stdlist.append(STD3)
    stdlist.append(STD2)
    stdlist.append(STD1)
    qclist.append(INT2)
    qclist.append(HQC)
    qclist.append(MQC)
    qclist.append(LQC)

    std_seqdata=[]
    qc_seqdata=[]
    for ws in stdlist:
        data=((ws.seq,eval(ws.parent)))
        std_seqdata.append(data)
    for ws in qclist:
        data=((ws.seq,eval(ws.parent)))
        qc_seqdata.append(data)

    std_seqlocation=dict(std_seqdata)
    qc_seqlocation=dict(qc_seqdata)
    
    def parent(child_name):
        group=child_name.group
        if group == 'STD':
            mom=std_seqlocation.get(child_name.parseq)
        elif group == 'QC':
            mom=qc_seqlocation.get(child_name.parseq)
        return mom
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
    tuberack1 = protocol.load_labware('opentrons_10_tuberack_nest_4x50ml_6x15ml_conical','1', 'tuberack1')#dilutent and waste
    tuberack2 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap','2','tuberack2')#lower aliquots QC WS
    tuberack3 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap','3','tuberack3')#lower aliquots QC WS
    tuberack4 = protocol.load_labware('opentrons_15_tuberack_nest_15ml_conical','4','tuberack4')#dilution WS
    tuberack5 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap','5','tuberack5')#middle aliquots WS5-8
    tuberack6 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap','6','tuberack6')#middle aliquots WS5-8
    tuberack7 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap','7','tuberack7')#IS and misc WS
    tuberack8 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap','8','tuberack8')#top aliquots WS1-4
    tuberack9 = protocol.load_labware('opentrons_24_tuberack_nest_1.5ml_snapcap','9','tuberack9')#top aliquots WS1-4

    tiprack= protocol.load_labware('opentrons_96_tiprack_300ul','10')
    tiprack1000 = protocol.load_labware('opentrons_96_tiprack_1000ul', '11')

    p1000 = protocol.load_instrument('p1000_single_gen2','right', tip_racks=[tiprack1000])
    p300 = protocol.load_instrument('p300_single_gen2', 'left', tip_racks=[tiprack])
    

    trash = protocol.fixed_trash['A1']

#dictionaries for volume tracking, put starting volumes in corresponding wells
    dict_tuberack1={tuberack1['A1']:(0.0,104), tuberack1['A2']:(0.0,104), 
        tuberack1['A3']:(50000.0,99),tuberack1['A4']:(0.0,94),
        tuberack1['B1']:(0.0,104), tuberack1['B2']:(0.0,104), 
        tuberack1['B3']:(0.0,94),tuberack1['B4']:(0.0,94),
        tuberack1['C1']:(0.0,104), tuberack1['C2']:(0.0,104), 
        }

    dict_tuberack2={tuberack2['A1']:(0.0,34), tuberack2['A2']:(0.0,34), tuberack2['A3']:(0.0,34), 
        tuberack2['A4']:(0.0,34), tuberack2['A5']:(0.0,34), tuberack2['A6']:(0.0,34), 
        tuberack2['B1']:(0.0,34), tuberack2['B2']:(0.0,34), tuberack2['B3']:(0.0,34), 
        tuberack2['B4']:(0.0,34), tuberack2['B5']:(0.0,34), tuberack2['B6']:(0.0,34), 
        tuberack2['C1']:(0.0,34), tuberack2['C2']:(0.0,34), tuberack2['C3']:(0.0,34), 
        tuberack2['C4']:(0.0,34), tuberack2['C5']:(0.0,34), tuberack2['C6']:(0.0,34),
        tuberack2['D1']:(0.0,34), tuberack2['D2']:(0.0,34), tuberack2['D3']:(0.0,34), 
        tuberack2['D4']:(0.0,34), tuberack2['D5']:(0.0,34), tuberack2['D6']:(0.0,34), 
        }

    dict_tuberack3={tuberack3['A1']:(0.0,34), tuberack3['A2']:(0.0,34), tuberack3['A3']:(0.0,34), 
        tuberack3['A4']:(0.0,34), tuberack3['A5']:(0.0,34), tuberack3['A6']:(0.0,34), 
        tuberack3['B1']:(0.0,34), tuberack3['B2']:(0.0,34), tuberack3['B3']:(0.0,34), 
        tuberack3['B4']:(0.0,34), tuberack3['B5']:(0.0,34), tuberack3['B6']:(0.0,34), 
        tuberack3['C1']:(0.0,34), tuberack3['C2']:(0.0,34), tuberack3['C3']:(0.0,34), 
        tuberack3['C4']:(0.0,34), tuberack3['C5']:(0.0,34), tuberack3['C6']:(0.0,34),
        tuberack3['D1']:(0.0,34), tuberack3['D2']:(0.0,34), tuberack3['D3']:(0.0,34), 
        tuberack3['D4']:(0.0,34), tuberack3['D5']:(0.0,34), tuberack3['D6']:(0.0,34), 
        }
    
    dict_tuberack4={tuberack4['A1']:(0.0,104), tuberack4['A2']:(0.0,104), 
        tuberack4['A3']:(0.0,104), tuberack4['A4']:(0.0,104), tuberack4['A5']:(0.0,104), 
        tuberack4['B1']:(0.0,104), tuberack4['B2']:(0.0,104), tuberack4['B3']:(0.0,104), 
        tuberack4['B4']:(0.0,104), tuberack4['B5']:(0.0,104), 
        tuberack4['C1']:(0.0,104), tuberack4['C2']:(0.0,104), tuberack4['C3']:(0.0,104), 
        tuberack4['C4']:(0.0,104), tuberack4['C5']:(0.0,104), 
        }

    dict_tuberack5={tuberack5['A1']:(0.0,34), tuberack5['A2']:(0.0,34), tuberack5['A3']:(0.0,34), 
        tuberack5['A4']:(0.0,34), tuberack5['A5']:(0.0,34), tuberack5['A6']:(0.0,34), 
        tuberack5['B1']:(0.0,34), tuberack5['B2']:(0.0,34), tuberack5['B3']:(0.0,34), 
        tuberack5['B4']:(0.0,34), tuberack5['B5']:(0.0,34), tuberack5['B6']:(0.0,34), 
        tuberack5['C1']:(0.0,34), tuberack5['C2']:(0.0,34), tuberack5['C3']:(0.0,34), 
        tuberack5['C4']:(0.0,34), tuberack5['C5']:(0.0,34), tuberack5['C6']:(0.0,34),
        tuberack5['D1']:(0.0,34), tuberack5['D2']:(0.0,34), tuberack5['D3']:(0.0,34), 
        tuberack5['D4']:(0.0,34), tuberack5['D5']:(0.0,34), tuberack5['D6']:(0.0,34), 
        }

    dict_tuberack6={tuberack6['A1']:(0.0,34), tuberack6['A2']:(0.0,34), tuberack6['A3']:(0.0,34), 
        tuberack6['A4']:(0.0,34), tuberack6['A5']:(0.0,34), tuberack6['A6']:(0.0,34), 
        tuberack6['B1']:(0.0,34), tuberack6['B2']:(0.0,34), tuberack6['B3']:(0.0,34), 
        tuberack6['B4']:(0.0,34), tuberack6['B5']:(0.0,34), tuberack6['B6']:(0.0,34), 
        tuberack6['C1']:(0.0,34), tuberack6['C2']:(0.0,34), tuberack6['C3']:(0.0,34), 
        tuberack6['C4']:(0.0,34), tuberack6['C5']:(0.0,34), tuberack6['C6']:(0.0,34),
        tuberack6['D1']:(0.0,34), tuberack6['D2']:(0.0,34), tuberack6['D3']:(0.0,34), 
        tuberack6['D4']:(0.0,34), tuberack6['D5']:(0.0,34), tuberack6['D6']:(0.0,34), 
        }

    dict_tuberack7={tuberack7['A1']:(500.0,34), tuberack7['A2']:(200.0,34), tuberack7['A3']:(0.0,34), 
        tuberack7['A4']:(0.0,34), tuberack7['A5']:(0.0,34), tuberack7['A6']:(0.0,34), 
        tuberack7['B1']:(0.0,34), tuberack7['B2']:(0.0,34), tuberack7['B3']:(0.0,34), 
        tuberack7['B4']:(0.0,34), tuberack7['B5']:(0.0,34), tuberack7['B6']:(0.0,34), 
        tuberack7['C1']:(0.0,34), tuberack7['C2']:(0.0,34), tuberack7['C3']:(0.0,34), 
        tuberack7['C4']:(0.0,34), tuberack7['C5']:(0.0,34), tuberack7['C6']:(0.0,34),
        tuberack7['D1']:(0.0,34), tuberack7['D2']:(0.0,34), tuberack7['D3']:(0.0,34), 
        tuberack7['D4']:(0.0,34), tuberack7['D5']:(0.0,34), tuberack7['D6']:(0.0,34), 
        }

    dict_tuberack8={tuberack8['A1']:(0.0,34), tuberack8['A2']:(0.0,34), tuberack8['A3']:(0.0,34), 
        tuberack8['A4']:(0.0,34), tuberack8['A5']:(0.0,34), tuberack8['A6']:(0.0,34), 
        tuberack8['B1']:(0.0,34), tuberack8['B2']:(0.0,34), tuberack8['B3']:(0.0,34), 
        tuberack8['B4']:(0.0,34), tuberack8['B5']:(0.0,34), tuberack8['B6']:(0.0,34), 
        tuberack8['C1']:(0.0,34), tuberack8['C2']:(0.0,34), tuberack8['C3']:(0.0,34), 
        tuberack8['C4']:(0.0,34), tuberack8['C5']:(0.0,34), tuberack8['C6']:(0.0,34),
        tuberack8['D1']:(0.0,34), tuberack8['D2']:(0.0,34), tuberack8['D3']:(0.0,34), 
        tuberack8['D4']:(0.0,34), tuberack8['D5']:(0.0,34), tuberack8['D6']:(0.0,34), 
        }

    dict_tuberack9={tuberack9['A1']:(0.0,34), tuberack9['A2']:(0.0,34), tuberack9['A3']:(0.0,34), 
        tuberack9['A4']:(0.0,34), tuberack9['A5']:(0.0,34), tuberack9['A6']:(0.0,34), 
        tuberack9['B1']:(0.0,34), tuberack9['B2']:(0.0,34), tuberack9['B3']:(0.0,34), 
        tuberack9['B4']:(0.0,34), tuberack9['B5']:(0.0,34), tuberack9['B6']:(0.0,34), 
        tuberack9['C1']:(0.0,34), tuberack9['C2']:(0.0,34), tuberack9['C3']:(0.0,34), 
        tuberack9['C4']:(0.0,34), tuberack9['C5']:(0.0,34), tuberack9['C6']:(0.0,34),
        tuberack9['D1']:(0.0,34), tuberack9['D2']:(0.0,34), tuberack9['D3']:(0.0,34), 
        tuberack9['D4']:(0.0,34), tuberack9['D5']:(0.0,34), tuberack9['D6']:(0.0,34), 
        }
#height reference 
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

#custom command def
    def wet_tip(pip,vol_dict,dict_labware,labware,well):
        asp_h1=get_height(dict_labware, labware, well)
        max_vol=pip.max_volume
            
        pip.flow_rate.aspirate = max_vol/2 if max_vol < 300 else 150
        pip.flow_rate.dispense = max_vol if max_vol<300 else 300
        disp_waste=101
        
        asp_master(max_vol,vol_dict,dict_labware,labware,well)
        pip.aspirate(max_vol,labware[well].bottom(z=asp_h1))
        pip.dispense(max_vol,tuberack1['A1'].bottom(z=disp_waste))
        pip.blow_out(tuberack1['A1'].bottom(z=disp_waste))
        protocol.comment(str(asp_h1))

        asp_h1=get_height(dict_labware, labware, well)
        asp_master(max_vol,vol_dict,dict_labware,labware,well)
        pip.aspirate(max_vol,labware[well].bottom(z=asp_h1))
        pip.dispense(max_vol,tuberack1['A1'].bottom(z=disp_waste))
        pip.blow_out(tuberack1['A1'].bottom(z=disp_waste))
        protocol.comment(str(asp_h1))

        asp_h1=get_height(dict_labware, labware, well)
        asp_master(max_vol,vol_dict,dict_labware,labware,well)
        pip.aspirate(max_vol,labware[well].bottom(z=asp_h1))
        pip.dispense(max_vol,tuberack1['A1'].bottom(z=disp_waste))
        pip.blow_out(tuberack1['A1'].bottom(z=disp_waste))
        protocol.comment(str(asp_h1))

    def wet_tip_mix(pip, dict_labware, labware, well):
        protocol.comment('tip conditioning')
        h1=get_height(dict_labware,labware,well)
        max_vol=pip.max_volume
        pip.flow_rate.aspirate = max_vol/2 if max_vol < 300 else 150
        pip.flow_rate.dispense = max_vol if max_vol<300 else 300
        
        pip.aspirate(max_vol, labware[well].bottom(z=h1))
        pip.dispense(max_vol, labware[well].bottom(z=h1))
        pip.aspirate(max_vol, labware[well].bottom(z=h1))
        pip.dispense(max_vol, labware[well].bottom(z=h1))
        pip.aspirate(max_vol, labware[well].bottom(z=h1))
        pip.dispense(max_vol, labware[well].bottom(z=h1))
        pip.aspirate(max_vol, labware[well].bottom(z=h1))
        pip.dispense(max_vol, labware[well].bottom(z=h1))
        pip.blow_out(labware[well].bottom(z=h1))
        pip.blow_out(labware[well].bottom(z=h1+5))
        
    def one_to_one(pip, volume, asp_vol_dict, asp_lab_dict, asp_labware, asp_well, dsp_vol_dict, dsp_lab_dict, dsp_labware, dsp_well):
        num_trans= math.ceil(volume/pip.max_volume)
        vol_per_trans=float(volume/num_trans)
        if asp_labware==tuberack7:
            asp_vol_dict=vol_1500
        elif asp_labware==tuberack4:
            asp_vol_dict=vol_15
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
            pip.blow_out(dsp_labware[dsp_well].bottom(z=h2))
            pip.blow_out(dsp_labware[dsp_well].bottom(z=h2+5))

    def mix_mix(pip, lab_dict,labware, well):
        pip.flow_rate.aspirate=150
        pip.flow_rate.dispense=300
        h1=5
        volume=pip.max_volume
        vol1=get_volume(lab_dict,labware,well)
        if vol1 >= 6000:
            h1=get_height(lab_dict,labware,well)-10
        else:
            h1=5
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
    
    def ali_transfer(pip,vol,asp_vol_dict,asp_lab_dict,asp_labware,asp_well,dsp_labware,dsp_well):
        asp_master(vol, asp_vol_dict, asp_lab_dict, asp_labware, asp_well)
        tup1=asp_lab_dict.get(asp_labware[asp_well])
        h1=tup1[1]
        h2=30
        pip.aspirate(vol, asp_labware[asp_well].bottom(z=h1))
        pip.dispense(vol, dsp_labware[dsp_well].bottom(z=h2))
        pip.blow_out(dsp_labware[dsp_well].bottom(z=h2))
        pip.blow_out(dsp_labware[dsp_well].bottom(z=h2+5))
    
    def full_mix_300(lab_dict,labware,well):
        p300.flow_rate.aspirate=150
        p300.flow_rate.dispense=300
        h1=5
        volume=p300.max_volume
        vol1=get_volume(lab_dict,labware,well)
        if vol1 >= 6000:
            h1=get_height(lab_dict,labware,well)-10
        else:
            h1=5
        num_mix= math.ceil(vol1/p300.max_volume)
        for n in range(num_mix):
            p300.aspirate(volume, labware[well].bottom(z=h1))
            p300.dispense(volume, labware[well].bottom(z=h1))
        
        p300.blow_out(labware[well].bottom(z=h1))
        p300.blow_out(labware[well].bottom(z=h1+5))

    def low_vol_mix(pip,volume,lab_dict,labware,well):
        pip.flow_rate.aspirate = volume/2 if volume < 300 else 150
        pip.flow_rate.dispense = volume if volume<300 else 300
        num_mix=3
        h1=(get_height(lab_dict,labware,well))
        for n in range(num_mix):
            p300.aspirate(volume, labware[well].bottom(z=h1))
            p300.dispense(volume, labware[well].bottom(z=h1))
            
        p300.blow_out(labware[well].bottom(z=h1))
        p300.blow_out(labware[well].bottom(z=h1+5))

    def int_transfer(pip, volume, asp_vol_dict, asp_lab_dict, asp_labware, asp_well, dsp_vol_dict, dsp_lab_dict, dsp_labware, dsp_well):
        num_trans= math.ceil(volume/pip.max_volume)
        vol_per_trans=float(volume/num_trans)
        if asp_labware==tuberack7:
            asp_vol_dict=vol_1500
        elif asp_labware==tuberack4:
            asp_vol_dict=vol_15
        else:
            pass 
        for n in range(num_trans):
            asp_master(vol_per_trans, asp_vol_dict, asp_lab_dict, asp_labware, asp_well)
            disp_master(vol_per_trans, dsp_vol_dict, dsp_lab_dict, dsp_labware, dsp_well)    
            tup1=asp_lab_dict.get(asp_labware[asp_well])
            tup2=dsp_lab_dict.get(dsp_labware[dsp_well])
            h1=tup1[1]
            h2=tup2[1]

            pip.pick_up_tip()           
            low_vol_mix(pip,vol_per_trans,asp_lab_dict,asp_labware,asp_well)
            pip.aspirate(vol_per_trans, asp_labware[asp_well].bottom(z=h1))
            pip.dispense(vol_per_trans, dsp_labware[dsp_well].bottom(z=h2))
            pip.blow_out(dsp_labware[dsp_well].bottom(z=h2))
            pip.blow_out(dsp_labware[dsp_well].bottom(z=h2+5))
            pip.drop_tip()
    


#begin commands
    p1000.pick_up_tip()
    wet_tip(p1000,vol_50,dict_tuberack1, tuberack1,'A3')
    
#adding dilutent
    for std in std_seqdata[1:]:
        child=std[1]
        one_to_one(p1000, child.dilvol, vol_50, dict_tuberack1,tuberack1,'A3',vol_15,eval(child.lab_dict),eval(child.labware),child.parwell)
    for qc in qc_seqdata[1:]:
        child=qc[1]
        one_to_one(p1000, child.dilvol, vol_50, dict_tuberack1,tuberack1,'A3',vol_15,eval(child.lab_dict),eval(child.labware),child.parwell)
    p1000.drop_tip()
    
#adding INT1
    for std in std_seqdata[1:]:
        child=std[1]                   
        int_transfer(p300, child.stdvol, vol_15, eval(parent(child).lab_dict),eval(parent(child).labware),parent(child).parwell,vol_15,eval(child.lab_dict),eval(child.labware),child.parwell)
        p300.pick_up_tip()
        full_mix_300(eval(child.lab_dict),eval(child.labware),child.parwell)
        protocol.comment('Transferred '+str(child.stdvol)+' of WS into '+str(child.dilvol)+' of dilutent')
        p300.drop_tip()
#adding INT2
    for qc in qc_seqdata[1:]:
        child=qc[1]
                
        int_transfer(p300, child.stdvol, vol_15, eval(parent(child).lab_dict),eval(parent(child).labware),parent(child).parwell,vol_15,eval(child.lab_dict),eval(child.labware),child.parwell)
        p300.pick_up_tip()
        full_mix_300(eval(child.lab_dict),eval(child.labware),child.parwell)
        protocol.comment('Transferred '+str(child.stdvol)+' of WS into '+str(child.dilvol)+' of dilutent')
        p300.drop_tip()
     
#row by row
    rowa=['A1','A2','A3','A4','A5']
    rowb=['B1','B2','B3','B4','B5']
    rowc=['C1','C2','C3','C4','C5']
    rowd=['D1','D2','D3','D4','D5']
  
#add aliqout volumes to class
    for std in stdlist[1:]:
        x=get_volume(eval(std.lab_dict),eval(std.labware),std.parwell)
        y=x-130
        new_vol=round(y/10,1)
        std.alivol=new_vol
    
    for qc in qclist[1:]:
        x=get_volume(eval(qc.lab_dict),eval(qc.labware),qc.parwell)
        y=x-130
        new_vol=round(y/10,1)
        qc.alivol=new_vol    
    
    p1000.pick_up_tip()
    mix_mix(p1000,dict_tuberack4,tuberack4,STD1.parwell)
#WS1 aliquots
    protocol.comment('Preparing 10 '+str(STD1.alivol)+' ul aliquots of STD1 ')
    for well in rowa:
        ali_transfer(p1000,STD1.alivol,vol_15,eval(STD1.lab_dict),eval(STD1.labware),STD1.parwell,tuberack8,well)
    for well in rowa:
        ali_transfer(p1000,STD1.alivol,vol_15,eval(STD1.lab_dict),eval(STD1.labware),STD1.parwell,tuberack9,well)
#WS2 aliquots
    p1000.drop_tip()
    p1000.pick_up_tip()
    mix_mix(p1000,dict_tuberack4,tuberack4,STD2.parwell)
    protocol.comment('Preparing 10 '+str(STD2.alivol)+' ul aliquots of STD2 ')
    for well in rowb:
        ali_transfer(p1000, STD2.alivol, vol_15, eval(STD2.lab_dict),eval(STD2.labware),STD2.parwell,tuberack8,well)
    for well in rowb:
        ali_transfer(p1000, STD2.alivol, vol_15, eval(STD2.lab_dict),eval(STD2.labware),STD2.parwell,tuberack9,well)    
#WS3 aliquots
    p1000.drop_tip()
    p1000.pick_up_tip()
    mix_mix(p1000,dict_tuberack4,tuberack4,STD3.parwell)
    protocol.comment('Preparing 10 '+str(STD3.alivol)+' ul aliquots of STD3 ')
    for well in rowc:
        ali_transfer(p1000, STD3.alivol, vol_15, eval(STD3.lab_dict),eval(STD3.labware),STD3.parwell,tuberack8,well)
    for well in rowc:
        ali_transfer(p1000, STD3.alivol, vol_15, eval(STD3.lab_dict),eval(STD3.labware),STD3.parwell,tuberack9,well)
#WS4 aliquots
    p1000.drop_tip()
    p1000.pick_up_tip()
    mix_mix(p1000,dict_tuberack4,tuberack4,STD4.parwell) 
    protocol.comment('Preparing 10 '+str(STD4.alivol)+' ul aliquots of STD4 ')
    for well in rowd:
        ali_transfer(p1000, STD4.alivol, vol_15, eval(STD4.lab_dict),eval(STD4.labware),STD4.parwell,tuberack8,well)
    for well in rowd:
        ali_transfer(p1000, STD4.alivol, vol_15, eval(STD4.lab_dict),eval(STD4.labware),STD4.parwell,tuberack9,well)
#WS5 aliquots
    p1000.drop_tip()
    p1000.pick_up_tip()
    mix_mix(p1000,dict_tuberack4,tuberack4,STD5.parwell)
    protocol.comment('Preparing 10 '+str(STD5.alivol)+' ul aliquots of STD5 ')
    for well in rowa:
        ali_transfer(p1000, STD5.alivol, vol_15, eval(STD5.lab_dict),eval(STD5.labware),STD5.parwell,tuberack5,well)
    for well in rowa:
        ali_transfer(p1000, STD5.alivol, vol_15, eval(STD5.lab_dict),eval(STD5.labware),STD5.parwell,tuberack6,well)
#WS6 aliquots
    p1000.drop_tip()
    p1000.pick_up_tip()
    mix_mix(p1000,dict_tuberack4,tuberack4,STD6.parwell)
    protocol.comment('Preparing 10 '+str(STD6.alivol)+' ul aliquots of STD6 ')
    for well in rowb:
        ali_transfer(p1000, STD6.alivol, vol_15, eval(STD6.lab_dict),eval(STD6.labware),STD6.parwell,tuberack5,well)
    for well in rowb:
        ali_transfer(p1000, STD6.alivol, vol_15, eval(STD6.lab_dict),eval(STD6.labware),STD6.parwell,tuberack6,well)
#WS7 aliquots
    p1000.drop_tip()
    p1000.pick_up_tip()
    mix_mix(p1000,dict_tuberack4,tuberack4,STD7.parwell)
    protocol.comment('Preparing 10 '+str(STD7.alivol)+' ul aliquots of STD7 ')
    for well in rowc:
        ali_transfer(p1000, STD7.alivol, vol_15, eval(STD7.lab_dict),eval(STD7.labware),STD7.parwell,tuberack5,well)
    for well in rowc:
        ali_transfer(p1000, STD7.alivol, vol_15, eval(STD7.lab_dict),eval(STD7.labware),STD7.parwell,tuberack6,well)
#WS8 aliquots
    p1000.drop_tip()
    p1000.pick_up_tip()
    mix_mix(p1000,dict_tuberack4,tuberack4,STD8.parwell)
    protocol.comment('Preparing 10 '+str(STD8.alivol)+' ul aliquots of STD8 ')
    for well in rowd:
        ali_transfer(p1000, STD8.alivol, vol_15, eval(STD8.lab_dict),eval(STD8.labware),STD8.parwell,tuberack5,well)
    for well in rowd:
        ali_transfer(p1000, STD8.alivol, vol_15, eval(STD8.lab_dict),eval(STD8.labware),STD8.parwell,tuberack6,well)
    p1000.drop_tip()

#LQC aliquots
    p1000.pick_up_tip()
    mix_mix(p1000,dict_tuberack4,tuberack4,LQC.parwell)
    protocol.comment('Preparing 10 '+str(LQC.alivol)+' ul aliquots of LQC ')
    for well in rowa:
        ali_transfer(p1000, LQC.alivol, vol_15, eval(LQC.lab_dict),eval(LQC.labware),LQC.parwell,tuberack2,well)
    for well in rowa:
        ali_transfer(p1000, LQC.alivol, vol_15, eval(LQC.lab_dict),eval(LQC.labware),LQC.parwell,tuberack3,well)   
#MQC aliquots
    p1000.drop_tip()
    p1000.pick_up_tip()
    mix_mix(p1000,dict_tuberack4,tuberack4,MQC.parwell)
    protocol.comment('Preparing 10 '+str(MQC.alivol)+' ul aliquots of MQC ')
    for well in rowb:
        ali_transfer(p1000, MQC.alivol, vol_15, eval(MQC.lab_dict),eval(MQC.labware),MQC.parwell,tuberack2,well)
    for well in rowb:
        ali_transfer(p1000, MQC.alivol, vol_15, eval(MQC.lab_dict),eval(MQC.labware),MQC.parwell,tuberack3,well)
#HQC aliquots
    p1000.drop_tip()
    p1000.pick_up_tip()
    mix_mix(p1000,dict_tuberack4,tuberack4,HQC.parwell)
    protocol.comment('Preparing 10 '+str(HQC.alivol)+' ul aliquots of HQC ')
    for well in rowc:
        ali_transfer(p1000, HQC.alivol, vol_15, eval(HQC.lab_dict),eval(HQC.labware),HQC.parwell,tuberack2,well)
    for well in rowc:
        ali_transfer(p1000, HQC.alivol, vol_15, eval(HQC.lab_dict),eval(HQC.labware),HQC.parwell,tuberack3,well)
    p1000.drop_tip()
    protocol.comment('Deniro seems satisfied')