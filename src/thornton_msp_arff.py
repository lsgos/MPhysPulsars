# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
"""ID & extract all the confirmed MSPs (rotation period around 30ms or less)
 from the Thornton file"""
 

 
thornton_feat = 'HTRU_2_Thornton_Features (22).csv'
msp = 'thorton_msp_datalines.arff'
# ID all the confirmed MSPs (rotation period around 30ms or less)
with open(thornton_feat,'U') as fr:
    with open(msp, 'wb') as fw:
        count = 0
        for i,row in enumerate(fr):
            l = row.split(',')
            psrconf = int(l[len(l)-1])
            periodms = float(l[11])
            
            if periodms < 31.0:
                
                if psrconf == 1:
                    print i
                    count = count + 1
                    print count
                    
                else:
                    continue
                
            else:
                continue
            swrt=str(i)
            fw.write(swrt + ", ")
        fw.write(str(count)+" millisecond pulsars in HTRU2")
                        
                
                
            