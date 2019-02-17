# -*- coding: utf-8 -*-

import numpy as np
import glob
import nibabel as nib
import pandas as pd
import cv2
import matplotlib
import scipy.ndimage

cc_filename=glob.glob('/data/stalxy/CCseg_DATASETS/Corbetta/CC*.nii')
cc_filename.sort()
filesize=len(cc_filename)
CCarea=np.zeros(filesize)
cv_CCarea=np.zeros(filesize)
cv_CCper=np.zeros(filesize)
fid=np.zeros(filesize)
CCr5=np.zeros([filesize,8])

for j in range(filesize):

    filename=cc_filename[j]
    fff=filename.split('_')[3]
    ttt=filename.split('_')[4]
    fid[j]=fff
    
    tmpnii = nib.load(cc_filename[j])
    tmpa=tmpnii.get_data()
    CCarea[j] = np.reshape(tmpa,tmpa.size).sum()
    tmpb=np.where(tmpa==1);
    
    slcn=np.unique(tmpb[0])[0]
    CCslice=tmpa[slcn]
    slcn_ap=np.unique(tmpb[1]) 
    slcn_du=np.unique(tmpb[2]) 
    CCap=slcn_ap.min()
    CCpp=slcn_ap.max()+1
    CCdp=slcn_du.min()
    CCup=slcn_du.max()+1
    itv5=(CCpp - CCap)/5
    itv3=(CCpp - CCap)/3
    itv2=(CCpp - CCap)/2
    itvDUM=(CCup - CCdp)*2/3
    CCatlas=np.array(CCslice)
    for i in range(5):
        if i == 0:
            rap=int(CCap)
            rpp=int(CCap+np.round(itv5))
            print(rap)
            print(rpp)
            CCr5[j,i]=CCslice[rap:rpp,:].sum()
            CCatlas[rap:rpp,:]=CCatlas[rap:rpp,:]+i
        elif i == 1:
            rap=int(CCap+np.round(itv5))
            rpp=int(CCap+np.round(itv3))
            print(rap)
            print(rpp)
            CCr5[j,i]=CCslice[rap:rpp,:].sum()
            CCatlas[rap:rpp,:]=CCatlas[rap:rpp,:]+i

        elif i == 2:
            rap=int(CCap+np.round(itv3))
            rpp=int(CCap+np.round(itv2))
            print(rap)
            print(rpp)
            CCr5[j,i]=CCslice[rap:rpp,:].sum()
            CCatlas[rap:rpp,:]=CCatlas[rap:rpp,:]+i

        elif i == 3:
            rap=int(CCap+np.round(itv2))
            rpp=int(CCap+np.round(2*itv3))
            #rmp=int(CCup-np.round(itvDUM))
            print(rap)
            print(rpp)
            CCr5[j,i]=(CCslice[rap:rpp,:].sum())
            CCatlas[rap:rpp,:]=CCatlas[rap:rpp,:]+i     
            
        elif i == 4:
            rap=int(CCap+np.round(2*itv3))
            rpp=int(CCpp+1)
            print(rap)
            print(rpp)
            
            bflag=0
            for k in range(rpp-rap):
                tp5y=rpp-k-2
                lines=CCslice[tp5y,:]
                linesect=np.where(lines==1)
                linenosec=(x for x in range(linesect[0][0],linesect[0][-1]+1))
                for g in linenosec:    
                    if g not in linesect[0]:        
                        bflag=1;
                        break
                if bflag==1:
                    break
            rmap=tp5y
            rmdu=g
                
            print(rmap)
            print(rmdu)
            
            CCr5[j,i]=(CCslice[rap:rmap+1,rmdu:CCup].sum())
            CCr5[j,i+1]=(CCslice[rmap+1:rpp,:].sum())
            CCr5[j,i+2]=(CCslice[rap:rmap+1,CCdp:rmdu].sum())
  
            CCatlas[rap:rmap+1,rmdu:CCup]=CCatlas[rap:rmap+1,rmdu:CCup]+i
            CCatlas[rmap+1:rpp,:]=CCatlas[rmap+1:rpp,:]+i+1
            CCatlas[rap:rmap+1,CCdp:rmdu]=CCatlas[rap:rmap+1,CCdp:rmdu]+i+2
            
        
    CCr5[j,7]=CCr5[j,0:7].sum()
        
#    matplotlib.image.imsave('/data/stalxy/HCP_CC/Pics/'+fff+'_cc.png', CCslice, cmap='gray')
    matplotlib.image.imsave('/data/stalxy/CCseg_DATASETS/Corbetta_atlas/'+fff+ttt+'_cc_atlas.png', CCatlas)

#    cv2.imwrite('a.png',tmpa[slcn])
#    imsave('a.png',tmpa[slcn])
    im=cv2.imread('/data/stalxy/CCseg_DATASETS/Corbetta_atlas/'+fff+ttt+'_cc_atlas.png',0)

    scn=25;
    area=np.array(scn)
    perimeter=np.array(scn)

    im3=scipy.ndimage.zoom(im, scn, order=1)

    ret,binary = cv2.threshold(im3,127,255,cv2.THRESH_BINARY)
    imgorig,contours,hierarchy=cv2.findContours(binary,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)

    cnt=contours[0]
    cv_CCarea[j] = (cv2.contourArea(cnt)/np.square(scn))
    cv_CCper[j] = (cv2.arcLength(cnt,True)/scn)
#
##print(area)
##print(perimeter)
#
##ac=cv2.drawContours(im3, cnt, -1, (0,255,0), 3)
##matplotlib.pyplot.imshow(ac, cmap='hot', interpolation='nearest')
##matplotlib.pyplot.show()
##matplotlib.pyplot.imshow(im, cmap='hot', interpolation='nearest')
##matplotlib.pyplot.show()
#
writer = pd.ExcelWriter('/data/stalxy/CCseg_DATASETS/Corbetta_CCarea.xlsx')
df1 = pd.DataFrame({'IDs': cc_filename, 'AreaVoxel': CCarea})
df2 = pd.DataFrame({'IDs': cc_filename, 'AreaR1': CCr5[:,6],'AreaR2': CCr5[:,5],'AreaR3': CCr5[:,4],'AreaR4': CCr5[:,3],'AreaR5': CCr5[:,2],'AreaR6': CCr5[:,1],'AreaR7': CCr5[:,0],'AreaRSUM': CCr5[:,7]})
df3 = pd.DataFrame({'IDs': cc_filename, 'AreaCV2': cv_CCarea})
df4 = pd.DataFrame({'IDs': cc_filename, 'PerimeterCV2': cv_CCper})
df1.to_excel(writer,'Sheet1')
df2.to_excel(writer,'Sheet2')
df3.to_excel(writer,'Sheet3')
df4.to_excel(writer,'Sheet4')
writer.save()