Data collection and organization
================================

The "Spine Generic" MRI acquisition protocol is available at `this
link <http://www.spinalcordmri.org/protocols>`__. Each site scanned six healthy subjects
(3 men, 3 women), aged between 20 and 40 y.o. Note: there is a
flexibility here, and if you wish to scan more than 6 subjects, you are
welcome to. If your site is interested in participating in this
publicly-available database, please contact Julien Cohen-Adad for
details.

Data conversion: DICOM to BIDS
------------------------------

To facilitate the collection, sharing and processing of data, we use the
`BIDS standard <http://bids.neuroimaging.io/>`__. An example of the data
structure for one center is shown below:

::

    spineGeneric_multiSubjects
    ├── dataset_description.json
    ├── participants.json
    ├── participants.tsv
    ├── sub-ucl01
    ├── sub-ucl02
    ├── sub-ucl03
    ├── sub-ucl04
    ├── sub-ucl05
    └── sub-ucl06
        ├── anat
        │   ├── sub-ucl06_T1w.json
        │   ├── sub-ucl06_T1w.nii.gz
        │   ├── sub-ucl06_T2star.json
        │   ├── sub-ucl06_T2star.nii.gz
        │   ├── sub-ucl06_T2w.json
        │   ├── sub-ucl06_T2w.nii.gz
        │   ├── sub-ucl06_acq-MToff_MTS.json
        │   ├── sub-ucl06_acq-MToff_MTS.nii.gz
        │   ├── sub-ucl06_acq-MTon_MTS.json
        │   ├── sub-ucl06_acq-MTon_MTS.nii.gz
        │   ├── sub-ucl06_acq-T1w_MTS.json
        │   └── sub-ucl06_acq-T1w_MTS.nii.gz
        └── dwi
            ├── sub-ucl06_dwi.bval
            ├── sub-ucl06_dwi.bvec
            ├── sub-ucl06_dwi.json
            └── sub-ucl06_dwi.nii.gz

To convert your DICOM data folder to the compatible BIDS structure, we
ask you to install
`dcm2bids <https://github.com/cbedetti/Dcm2Bids#install>`__. Once
installed, `download this config
file <https://raw.githubusercontent.com/sct-pipeline/spine-generic/master/config_spine.txt>`__
(click File>Save to save the file), then convert your Dicom folder using
the following command (replace xx with your center and subject number):

.. code-block:: bash

  dcm2bids -d -p sub-xx -c config_spine.txt -o CENTER_spineGeneric

For example:

.. code-block:: bash

  dcm2bids -d /Users/julien/Desktop/DICOM_subj3 -p sub-milan03 -c ~/Desktop/config_spine.txt -o milan_spineGeneric


A log file is generated under ``tmp_dcm2bids/log/``. If you encounter
any problem while running the script, please `open an
issue <https://github.com/sct-pipeline/spine-generic/issues>`__ and
upload the log file. We will offer support.

Once you've converted all subjects for the study, create the following
files and add them to the data structure:

**dataset\_description.json** (Pick the correct values depending on your
system and environment)

::

    {
        "Name": "Spinal Cord MRI Public Database",
        "BIDSVersion": "1.2.0",
        "InstitutionName": "Name of the institution",
        "Manufacturer": "YOUR_VENDOR",
        "ManufacturersModelName": "YOUR_MODEL",
        "ReceiveCoilName": "YOUR_COIL",
        "SoftwareVersion": "YOUR_SOFTWARE",
        "Researcher": "J. Doe, S. Wonder, J. Pass",
        "Notes": "Particular notes you might have. E.g.: We don't have the ZOOMit license, unf-prisma/sub-01 and unf-skyra/sub-03 is the same subject.
    }

Example of possible values:

- **Manufacturer**: "Siemens", "GE", "Philips"
- **ManufacturersModelName**: "Prisma", "Prisma-fit", "Skyra", "750w", "Achieva"
- **ReceiveCoilName**: "64ch+spine", "12ch+4ch neck", "neurovascular"
- **SoftwareVersion**: "VE11C", "DV26.0", "R5.3", ...

**participants.json** (This file is generic, you don't need to change
anything there. Just create a new file with this content)

.. code:: json

    {
        "participant_id": {
            "LongName": "Participant ID",
            "Description": "Unique ID"
        },
        "sex": {
            "LongName": "Participant gender",
            "Description": "M or F"
        },
        "age": {
            "LongName": "Participant age",
            "Description": "yy"
        },
        "date_of_scan": {
            "LongName": "Date of scan",
            "Description": "yyyy-mm-dd"
        }
    }

**participants.tsv** (Tab-separated values)

::

    participant_id  sex age date_of_scan    institution_id  institution manufacturer    manufacturers_model_name    receive_coil_name   software_versions   researcher
    sub-unf01   F   24  2018-12-07  unf Neuroimaging Functional Unit (UNF), CRIUGM, Polytechnique Montreal  Siemens Prisma-fit  HeadNeck_64 syngo_MR_E11    J. Cohen-Adad, A. Foias
    sub-unf02   M   29  2018-12-07  unf Neuroimaging Functional Unit (UNF), CRIUGM, Polytechnique Montreal  Siemens Prisma-fit  HeadNeck_64 syngo_MR_E11    J. Cohen-Adad, A. Foias
    sub-unf03   M   22  2018-12-07  unf Neuroimaging Functional Unit (UNF), CRIUGM, Polytechnique Montreal  Siemens Prisma-fit  HeadNeck_64 syngo_MR_E11    J. Cohen-Adad, A. Foias
    sub-unf04   M   31  2018-12-07  unf Neuroimaging Functional Unit (UNF), CRIUGM, Polytechnique Montreal  Siemens Prisma-fit  HeadNeck_64 syngo_MR_E11    J. Cohen-Adad, A. Foias
    sub-unf05   F   23  2019-01-11  unf Neuroimaging Functional Unit (UNF), CRIUGM, Polytechnique Montreal  Siemens Prisma-fit  HeadNeck_64 syngo_MR_E11    J. Cohen-Adad, A. Foias
    sub-unf06   F   27  2019-01-11  unf Neuroimaging Functional Unit (UNF), CRIUGM, Polytechnique Montreal  Siemens Prisma-fit  HeadNeck_64 syngo_MR_E11    J. Cohen-Adad, A. Foias

Once you've created the BIDS dataset, remove any temp folders (e.g.,
``tmp_dcm2bids/``) and zip the entire folder. It is now ready for
sharing! You could send it to Julien Cohen-Adad via any cloud-based
method (Gdrive, Dropbox, etc.).

Ethics and anonymization
------------------------

Each subject consented to be scanned and to have their anonymized data
put in a publicly-available repository. To prove it, an email from each
participant should be sent to the manager of the database (Julien
Cohen-Adad). The email should state the following: "I am the subject who
volunteered and I give you permission to release the scan freely to the
public domain."

Anatomical scans where facial features are visible (T1w) could be
"defaced" before being collected (at the discretion of the subject).
Because FreeSurfer's ``mri_deface`` does not work well on those data
(which include a big portion of the spine), we recommend to do the
defacing manually. It is a very easy procedure that takes less than a
minute. To do so, open Fsleyes (as an example, but you could use another
MRI editor) and open the T1w scan. Go to **Tools > Edit mode**, Select
the pencil with size 100, deface, then save. Below is an example of a
defaced subject:

.. figure:: _static/example_defacing.png
   :alt: example\_defacing
   :align: center
   :scale: 70%

   Example of manual defacing.

Defacing using R
------------------------

1. Install R and the following depdendencies:

.. code-block:: R
  install.packages("sessioninfo")
  install.packages("remotes")
  remotes::install_github("muschellij2/oro.nifti")
  install.packages("fslr")
  install.packages("argparser")
  install.packages("devtools")
  remotes::install_github("muschellij2/extrantsr")


2. Call `deface_spineGeneric_usingR -i PATH_TO_DATASET_TO_DEFACE -o PATH_TO_OUTPUT_DATASET_DEFACED`. If you use the command for the first time and you want to populate the `_defaced` folder add the `-f` flag at the end. 

3. For qc report, call `qc_bids_deface.py`

Analysis pipeline
=================

The analysis pipeline available in this repository enables to output the
following metrics (organized per contrast):

-  **T1**: Spinal cord CSA averaged between C2 and C3.
-  **T2**: Spinal cord CSA averaged between C2 and C3.
-  **T2s**: Gray matter CSA averaged between C3 and C4.
-  **DWI**: FA in WM averaged between C2 and C5.
-  **MTS**: MTR in WM averaged between C2 and C5. Uses MTon\_MTS and
   MToff\_MTS.
-  **MTS**: MTSat & T1 map in WM averaged between C2 and C5. Uses
   MTon\_MTS, MToff\_MTS and T1w\_MTS.



Dependencies
------------

MANDATORY:

- For processing: `SCT 4.1.0 <https://github.com/neuropoly/spinalcordtoolbox/releases/tag/4.1.0>`__.
- For generating figures: Python >= 3.6

OPTIONAL:

- `FSLeyes <https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FSLeyes>`__ for correcting segmentations.
- `GNU parallel <https://www.gnu.org/software/parallel/>`__ for processing multiple subjects in parallel.


Example datasets
----------------

As a starting point, you could use either of these example datasets:

- `Multi-center, single-subject <https://openneuro.org/datasets/ds002393>`__
- `Multi-center, multi-subject <https://openneuro.org/datasets/ds001919>`__



How to run
----------

Download (or ``git clone``) this repository:

.. code-block:: bash

  git clone https://github.com/sct-pipeline/spine-generic.git

Install Python dependencies:

.. code-block:: bash

  cd spine-generic
  pip install -e .

Go outside of this git repos and create a folder where outputs will be created

.. code-block:: bash

  mkdir ~/spineGeneric_results
  cp processing/parameters_template.sh ~/spineGeneric_results/parameters.sh
  cd ~/spineGeneric_results

Edit the parameter file and modify the variables according to your needs:

.. code-block:: bash

  edit parameters.sh

Launch processing:

.. code-block:: bash

  sct_run_batch parameters.sh process_data.sh



Quality Control
---------------

After the processing is run, check your Quality Control (QC) report, by
opening double clicking on the file ``qc/index.html``. Use the "Search"
feature of the QC report to quickly jump to segmentations or labeling
results.

Segmentation
^^^^^^^^^^^^

If you spot segmentation issues, manually fix them using the procedure described
below. Also see the video tutorial after the procedure.

- Create a file and copy/past the script below:

.. code-block:: bash

  #!/bin/bash
  # Local folder to output the manual labels (you need to create it before running this script). Do not add "/" at the end.
  PATH_SEGMANUAL="/Users/bob/seg_manual"
  # List of files to correct segmentation on
  FILES=(
  sub-amu02_acq-T1w_MTS.nii.gz
  sub-beijingGE04_T2w_RPI_r.nii.gz
  sub-brnoPrisma01_T2star_rms.nii.gz
  sub-geneva04_dwi_crop_moco_dwi_mean.nii.gz
  )
  # Loop across files
  for file in ${FILES[@]}; do
    # extract subject using first delimiter '_'
    subject=${file%%_*}
    # check if file is under dwi/ or anat/ folder and get fname_data
    if [[ $file == *"dwi"* ]]; then
      fname_data=$subject/dwi/$file
    else
      fname_data=$subject/anat/$file
    fi
    # get fname_seg depending if it is cord or GM seg
    if [[ $file == *"T2star"* ]]; then
      fname_seg=${fname_data%%".nii.gz"*}_gmseg.nii.gz${fname_data##*".nii.gz"}
      fname_seg_dest=${PATH_SEGMANUAL}/${file%%".nii.gz"*}_gmseg-manual.nii.gz${file##*".nii.gz"}
    else
      fname_seg=${fname_data%%".nii.gz"*}_seg.nii.gz${fname_data##*".nii.gz"}
      fname_seg_dest=${PATH_SEGMANUAL}/${file%%".nii.gz"*}_seg-manual.nii.gz${file##*".nii.gz"}
    fi
    # Copy file to PATH_SEGMANUAL
    cp $fname_seg $fname_seg_dest
    # Launch FSLeyes
    echo "In FSLeyes, click on 'Edit mode', correct the segmentation, then save it with the same name (overwrite)."
    fsleyes -yh $fname_data $fname_seg_dest -cm red
  done

- In the QC report, enter the string "deepseg" to only display segmentation results.
- Review all segmentations. Use the keyboard shortcuts up/down arrow to switch between
  subjects and the left arrow to toggle overlay.
- If you spot *major* issues with the segmentation (e.g. noticeable leaking or under-segmentation that extends over several slices),
  add the image name in the variable array ``FILES`` in the script.
- If the data quality is too low to be interpreted (too blurry, large artifacts),
  add the image file name to the variable ``TO_EXCLUDE`` in the file ```parameters.sh``,
  which will be used in the next processing iteration.

.. Hint::
   For the interest of time, you don't need to fix *all* slices of the segmentation
   but only the ones listed in the "Relevant levels" column of the table below.

+-------------------------------------------------------+---------------------------------------------------+-----------------+-----------------------+
| Segmentation                                          | Associated image                                  | Relevant levels | Used for              |
+=======================================================+===================================================+=================+=======================+
| sub-XX\_T1w\_RPI\_r\_seg.nii.gz                       | sub-XX\_T1w\_RPI\_r.nii.gz                        | C2-C3           | CSA                   |
+-------------------------------------------------------+---------------------------------------------------+-----------------+-----------------------+
| sub-XX\_T2w\_RPI\_r\_seg.nii.gz                       | sub-XX\_T2w\_RPI\_r.nii.gz                        | C2-C3           | CSA                   |
+-------------------------------------------------------+---------------------------------------------------+-----------------+-----------------------+
| sub-XX\_T2star\_rms\_gmseg.nii.gz                     | sub-XX\_T2star\_rms.nii.gz                        | C3-C4           | CSA                   |
+-------------------------------------------------------+---------------------------------------------------+-----------------+-----------------------+
| sub-XX\_acq-T1w\_MTS\_seg.nii.gz                      | sub-XX\_acq-T1w\_MTS.nii.gz                       | C2-C5           | Template registration |
+-------------------------------------------------------+---------------------------------------------------+-----------------+-----------------------+
| sub-XX\_dwi\_concat\_crop\_moco\_dwi\_mean_seg.nii.gz | sub-XX\_dwi\_concat\_crop\_moco\_dwi\_mean.nii.gz | C2-C5           | Template registration |
+-------------------------------------------------------+---------------------------------------------------+-----------------+-----------------------+

.. raw:: html

   <div style="position: relative; padding-bottom: 5%; height: 0; overflow: hidden; max-width: 100%; height: auto;">
     <iframe width="700" height="394" src="https://www.youtube.com/embed/lB-F8WOHGeg" frameborder="0" allowfullscreen></iframe>

Vertebral labeling
^^^^^^^^^^^^^^^^^^

If you spot issues (wrong labeling), manually create labels in the cord
at C3 and C5 mid-vertebral levels. The bash script below loops across all
subjects that require manual labeling. Below is the procedure, followed by a video tutorial.

- Create a folder where you will save the manual labels
- Create the bash script below and edit the environment variables (see next point).
- Go through the QC, and when you identify a problematic subject, add it in the
  variable array ``SUBJECTS``. Once you've gone through all the QC, go to the
  folder ``results/data`` and run the script: ``sh manual_correction.sh``:

.. code-block:: bash

   #!/bin/bash
   # Local folder to output the manual labels (you need to create it before running this script)
   PATH_SEGMANUAL="/Users/bob/seg_manual"
   # List of subjects to create manual labels
   SUBJECTS=(
     "sub-amu01"
     "sub-beijingGE01"
     "sub-ucl01"
   )
   # Loop across subjects
   for subject in ${SUBJECTS[@]}; do
     sct_label_utils -i $subject/anat/${subject}_T1w_RPI_r.nii.gz -create-viewer 3,5 -o ${PATH_SEGMANUAL}/${subject}_T1w_RPI_r_labels-manual.nii.gz
   done

.. raw:: html

   <div style="position: relative; padding-bottom: 5%; height: 0; overflow: hidden; max-width: 100%; height: auto;">
     <iframe width="700" height="394" src="https://www.youtube.com/embed/bX9yWYTipO8" frameborder="0" allowfullscreen></iframe>

Once all labels are created, move the content of seg_manual to the up-to-date
`seg_manual` folder (that contains other manual corrections, and that will be
used for the next processing iteration).

Once you've corrected all the necessary files, re-run the whole process.
If the manual file exists, the script will use it in the processing.


Generate figures
----------------

Generate figures based on the output csv files. Figures will be created in the
folder `results/`:

.. code-block:: bash

  generate_figures parameters.sh



Contributors
------------

`List of contributors for the analysis
pipeline. <https://github.com/sct-pipeline/spine-generic/graphs/contributors>`__

`How to contribute? <https://github.com/sct-pipeline/spine-generic/blob/master/CONTRIBUTING.md>`_


License
-------

See the file `LICENSE <https://github.com/sct-pipeline/spine-generic/blob/master/LICENSE>`_.
