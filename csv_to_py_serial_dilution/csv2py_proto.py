import csv

#specify file/location
tm_csv = open('py_import.csv','r', newline='')
#create list objects
fields=[]
rows=[]

#reading csv
with tm_csv as csvfile:
    csvreader=csv.reader(csvfile)
    #extract field name
    fields=next(csvreader)
    #extract data to row
    for row in csvreader:
        rows.append(row)

#assigning rows to parents
int1=rows[0]
std8=rows[1]
std7=rows[2]
std6=rows[3]
std5=rows[4]
std4=rows[5]
std3=rows[6]
std2=rows[7]
std1=rows[8]
int2=rows[9]
hqc=rows[10]
mqc=rows[11]
lqc=rows[12]

#INT volumes for dictionary
int1_volume=int1[6]
int2_volume=int2[6]

#name for test method
TMname=int1[8]

#assign each line of py script to a list
with open('serial_dil_JPv5.txt','r') as file:
    data=file.readlines()

#overwrite each line that will be replaced with string
data[14]=f'    int1={rows[0]}\n'
data[15]=f'    std8={rows[1]}\n'
data[16]=f'    std7={rows[2]}\n'
data[17]=f'    std6={rows[3]}\n'
data[18]=f'    std5={rows[4]}\n'
data[19]=f'    std4={rows[5]}\n'
data[20]=f'    std3={rows[6]}\n'
data[21]=f'    std2={rows[7]}\n'
data[22]=f'    std1={rows[8]}\n'
data[23]=f'    int2={rows[9]}\n'
data[24]=f'    hqc={rows[10]}\n'
data[25]=f'    mqc={rows[11]}\n'
data[26]=f'    lqc={rows[12]}\n'
data[295]=str("    dict_tuberack7={tuberack7['A1']:("+f"{int1_volume}"+",34), tuberack7['A2']:("+f"{int2_volume}"",34), tuberack7['A3']:(0.0,34),")

#begin writing list to new file
with open(f'{TMname}_serial_dil.py','w')as file:
    file.writelines(data)