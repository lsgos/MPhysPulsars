# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
"""ID & extract all the confirmed MSPs (rotation period around 30ms or less)
 from the T"""
thornton_feat = 'HTRU_2_Thornton_Features (22).csv'
# ID all the confirmed MSPs (rotation period around 30ms or less)
with open(thornton_feat,'U') as fr:
        for i,row in enumerate(fr):
            l = row.split(',')
            psrconf = int(l[len(l)-1])
            periodms = float(l[11])
            
            if periodms < 31.0:
                
                if psrconf == 1:
                    
                    print i+1
                    #i+1 due to viewing .csv in LibreOffice (counts from 1)
                else:
                    continue
            else:
                continue