# Author: Alexandru Foias
# License MIT

import os
import nibabel as nib
import cv2
import numpy as np
from pathlib import Path

home = str(Path.home())
path_data = input ('Please specify the path for the defaced dataset: \n')
output_path = input ('Please specify the path for the qc report output folder: \n')

if not os.path.isdir(output_path):
    os.makedirs(output_path)

for dirName, subdirList, fileList in os.walk(path_data):
    for file in fileList:
        if file.endswith('T1w.nii.gz') or file.endswith('T2w.nii.gz'):
            originalFilePath = os.path.join(dirName,file)
            img = nib.load(originalFilePath)
            #Check and fix image orientation
            orientation = nib.aff2axcodes(img.affine)
            ideal_orientation = ('R', 'A', 'S')
            if ( orientation != ideal_orientation):
                img=nib.as_closest_canonical(img)
            img_np = img.get_data()
            x = np.rot90(img_np[int(img_np.shape[0]/2),:,:])
            # Adjust pixel intesity between 0 and 4095 for plotting
            x = np.interp(x, (x.min(), x.max()), (0, 4095))
            # Adjust contrast and brightness
            alpha = 0.1
            beta = 0
            x = cv2.convertScaleAbs(x, alpha=alpha, beta=beta)
            #Fix image size
            dim = (260, 320)
            x = cv2.resize(x,dim,interpolation = cv2.INTER_AREA)
            file.split('.')[0]
            cv2.imwrite(output_path + '/'+file.split('.')[0]+ '.png',x)

path_data = output_path

part1 = """
<table width="750" border="1" cellpadding="5">
<th>Subject</th>
<th>T1w</th>
<th>T2w</th> 

"""
part2 ="""
<tr>
<td align="center" valign="center" width="1000000">
"""

part3 = '''
<td align="center" valign="center">
<img src="'''

part4 = ''' alt="T1w defaced" />
<br />
</td>

<td align="center" valign="center">
<img src="'''

part5 = '''  alt="T2w defaced" />
<br />
</td>
</tr>

'''

final_qc = part1

list_images = os.listdir(path_data)
list_subjects = []
for item in list_images:
    subject = (item.split("_")[0])
    if subject not in list_subjects:
        list_subjects.append(subject)
        
list_subjects.sort()        
for subject in list_subjects:
    final_qc += part2+subject
    final_qc += part3+'./'+subject+'_T1w.png"'
    final_qc += part4+'./'+subject+'_T2w.png"'
    final_qc += part5
final_qc += "</table>"

if final_qc:
    path_qc_report = output_path+"/qc_report.html"
    html_file = open(output_path+"/qc_report.html", "w")
    html_file.write(final_qc)
    html_file.close()

command = """open -a "Google Chrome" """+ path_qc_report
os.system(command)