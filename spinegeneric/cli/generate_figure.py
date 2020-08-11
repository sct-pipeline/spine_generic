#!/usr/bin/env python
#
# Generate figures for the spine-generic project.
#
# Note: Matplotlib crashes when running debugger in Pycharm with python 3.7.3. To fix the problem, run this script
# using a virtual env python 3.7.0. More info at: https://github.com/MTG/sms-tools/issues/36
#
# Authors: Julien Cohen-Adad, Jan Valosek


import os
import argparse
import tqdm
import sys
import glob
import csv
import pandas as pd
import subprocess

import numpy as np
from scipy import ndimage
from collections import OrderedDict
from collections import defaultdict
import logging
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.patches as patches
from sklearn.linear_model import LinearRegression

import spinegeneric as sg


# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # default: logging.DEBUG, logging.INFO
hdlr = logging.StreamHandler(sys.stdout)
logging.root.addHandler(hdlr)

# List subject to remove, associated with contrast
SUBJECTS_TO_REMOVE = [
    # CSA
    {'subject': 'sub-oxfordFmrib04', 'metric': 'csa_t1'},  # T1w scan is not aligned with other contrasts (subject repositioning)
    {'subject': 'sub-oxfordFmrib04', 'metric': 'csa_t2'},  # T1w scan is not aligned with other contrasts (subject repositioning)
    {'subject': 'sub-mountSinai03', 'metric': 'csa_t1'},  # T2w was re-acquired (subject repositioning)
    {'subject': 'sub-mountSinai03', 'metric': 'csa_t2'},  # T2w was re-acquired (subject repositioning)
    # DTI
    {'subject': 'sub-beijingPrisma03', 'metric': 'dti_fa'},  # wrong FOV placement
    {'subject': 'sub-mountSinai03', 'metric': 'dti_fa'},  # T2w was re-acquired (hence wrong T2w -> DWI registration)
    {'subject': 'sub-oxfordFmrib04', 'metric': 'dti_fa'},  # T1w scan is not aligned with other contrasts (subject repositioning)
    {'subject': 'sub-oxfordFmrib01', 'metric': 'dti_fa'},  # registration issue (segmentation OK)
    # MTR
    {'subject': 'sub-beijingPrisma04', 'metric': 'mtr'},  # different coil, shim value and FOV placement between MTon and MToff
    {'subject': 'sub-geneva02', 'metric': 'mtr'},  # FOV positioning changed between MTon and MToff
    {'subject': 'sub-oxfordFmrib04', 'metric': 'mtr'},  # T1w scan is not aligned with other contrasts (subject repositioning)
    # MTsat
    {'subject': 'sub-geneva02', 'metric': 'mtsat'},  # TODO: check what's going on with this scan
    {'subject': 'sub-oxfordFmrib04', 'metric': 'mtsat'},  # T1w scan is not aligned with other contrasts (subject repositioning)
    {'subject': 'sub-tehranS04', 'metric': 'mtsat'},  # TODO: check what's going on with this scan
    # T1 map
    {'subject': 'sub-oxfordFmrib04', 'metric': 't1'},  # T1w scan is not aligned with other contrasts (subject repositioning)
    {'subject': 'sub-fslAchieva03', 'metric': 't1'},  # TODO: check what's going on with this scan
    {'subject': 'sub-fslAchieva04', 'metric': 't1'},  # TODO: check what's going on with this scan
    {'subject': 'sub-fslAchieva05', 'metric': 't1'},  # TODO: check what's going on with this scan
    {'subject': 'sub-fslAchieva06', 'metric': 't1'},  # TODO: check what's going on with this scan
    ]

# List of sites to exclude based on the metric
SITES_TO_EXCLUDE = {
    'mtr': ['stanford',  # Used different TR.
    ]
    #         'sapienza']  # TODO: check what's going on with this site
    }

# country dictionary: key: site, value: country name
# Flags are downloaded from: https://emojipedia.org/
flags = {
    'amu': 'france',
    'balgrist': 'ch',
    'barcelona': 'spain',
    'beijing750': 'china',
    'beijingPrisma': 'china',
    'beijingVerio': 'china',
    'brno': 'cz',
    'brnoCeitec': 'cz',
    'brnoPrisma': 'cz',
    'brnoUhb': 'cz',
    'cardiff': 'uk',
    'chiba': 'japan',
    'chiba750': 'japan',
    'chibaIngenia': 'japan',
    'cmrra': 'us',
    'cmrrb': 'us',
    'douglas': 'canada',
    'dresden': 'germany',
    'juntendo750w': 'japan',
    'juntendoAchieva': 'japan',
    'juntendoPrisma': 'japan',
    'juntendoSkyra': 'japan',
    'geneva': 'ch',
    'glen': 'canada',
    'hamburg': 'germany',
    'mgh': 'us',
    'milan': 'italy',
    'mni': 'canada',
    'mountSinai': 'us',
    'mpicbs': 'germany',
    'nottwil': 'ch',
    'nwu': 'us',
    'oxfordFmrib': 'uk',
    'oxfordOhba': 'uk',
    'pavia': 'italy',
    'perform': 'canada',
    'poly': 'canada',
    'queensland': 'australia',
    'fslAchieva': 'italy',
    'fslPrisma': 'italy',
    'sherbrooke': 'canada',
    'stanford': 'us',
    'strasbourg': 'france',
    'tehran': 'iran',
    'tokyo': 'japan',
    'tokyo750w': 'japan',
    'tokyoSigna1': 'japan',
    'tokyoSigna2': 'japan',
    'tokyoSkyra': 'japan',
    'tokyoIngenia': 'japan',
    'ubc': 'canada',
    'ucl': 'uk',
    'unf': 'canada',
    'vallHebron': 'spain',
    'vuiisAchieva': 'us',
    'vuiisIngenia': 'us',
    }

# color to assign to each MRI model for the figure
vendor_to_color = {
    'GE': 'black',
    'Philips': 'dodgerblue',
    'Siemens': 'limegreen',
    }

# fetch contrast based on csv file
file_to_metric = {
    'csa-SC_T1w.csv': 'csa_t1',
    'csa-SC_T2w.csv': 'csa_t2',
    'csa-GM_T2s.csv': 'csa_gm',
    'DWI_FA.csv': 'dti_fa',
    'DWI_MD.csv': 'dti_md',
    'DWI_RD.csv': 'dti_rd',
    'MTR.csv': 'mtr',
    'MTsat.csv': 'mtsat',
    'T1.csv': 't1',
    }

# fetch metric field
metric_to_field = {
    'csa_t1': 'MEAN(area)',
    'csa_t2': 'MEAN(area)',
    'csa_gm': 'MEAN(area)',
    'dti_fa': 'WA()',
    'dti_md': 'WA()',
    'dti_rd': 'WA()',
    'mtr': 'WA()',
    'mtsat': 'WA()',
    't1': 'WA()',
    }

# fetch metric field
metric_to_label = {
    'csa_t1': 'Cord CSA from T1w [$mm^2$]',
    'csa_t2': 'Cord CSA from T2w [$mm^2$]',
    'csa_gm': 'Gray Matter CSA [$mm^2$]',
    'dti_fa': 'Fractional anisotropy',
    'dti_md': 'Mean diffusivity [$mm^2.s^{-1}$]',
    'dti_rd': 'Radial diffusivity [$mm^2.s^{-1}$]',
    'mtr': 'Magnetization transfer ratio [%]',
    'mtsat': 'Magnetization transfer saturation [%]',
    't1': 'T1 [ms]',
    }

# scaling factor (for display)
scaling_factor = {
    'csa_t1': 1,
    'csa_t2': 1,
    'csa_gm': 1,
    'dti_fa': 1,
    'dti_md': 1000,
    'dti_rd': 1000,
    'mtr': 1,
    'mtsat': 1,
    't1': 1000,
    }

# FIGURE PARAMETERS
FONTSIZE = 15
TICKSIZE = 10
LABELSIZE = 15


def get_parameters():
    parser = argparse.ArgumentParser(
        description="Generate figures for the spine-generic project.")
    parser.add_argument(
        '-indiv-subj',
        type=int,
        choices=(0, 1),
        required=False,
        help="Display the value of each individual subject as a red dot.",
        default=1)
    parser.add_argument(
        '-path-results',
        required=False,
        metavar='<dir_path>',
        help="Folder that includes all the output csv files (generated by process_data.sh).")
    args = parser.parse_args()
    return args


def aggregate_per_site(dict_results, metric):
    """
    Aggregate metrics per site. This function assumes that the file participants.tsv is present in the -path-results
    folder.
    :param dict_results:
    :param metric: Metric type
    :return:
    """
    # Build Panda DF of participants based on participants.tsv file
    participants = pd.read_csv(os.path.join('participants.tsv'), sep="\t")

    # Fetch specific field for the selected metric
    metric_field = metric_to_field[metric]
    # Build a dictionary that aggregates values per site
    results_agg = {}
    # Loop across lines and fill dict of aggregated results
    subjects_removed = []
    for i in tqdm.tqdm(range(len(dict_results)), unit='iter', unit_scale=False, desc="Loop across subjects",
                       ascii=False,
                       ncols=80):
        filename = dict_results[i]['Filename']
        logger.debug('Filename: ' + filename)
        # Fetch metadata for the site
        # dataset_description = read_dataset_description(filename, path_data)
        # cluster values per site
        subject = fetch_subject(filename)
        # check if subject needs to be discarded
        if not remove_subject(subject, metric):
            # Fetch index of row corresponding to subject
            rowIndex = participants[participants['participant_id'] == subject].index
            # Add column "val" with metric value
            participants.loc[rowIndex, 'val'] = dict_results[i][metric_field]
            site = participants['institution_id'][rowIndex].array[0]
            if not site in results_agg.keys():
                # if this is a new site, initialize sub-dict
                results_agg[site] = {}
                results_agg[site][
                    'site'] = site  # need to duplicate in order to be able to sort using vendor AND site with Pandas
                results_agg[site]['vendor'] = participants['manufacturer'][rowIndex].array[0]
                results_agg[site]['model'] = participants['manufacturers_model_name'][rowIndex].array[0]
                results_agg[site]['val'] = []
            # add val for site (ignore None)
            val = dict_results[i][metric_field]
            if not val == 'None':
                results_agg[site]['val'].append(float(val))
        else:
            subjects_removed.append(subject)
    logger.info("Subjects removed: {}".format(subjects_removed))
    return results_agg


def add_flag(coord, name, ax):
    """
    Add flag images to the plot.
    :param coord Coordinate of the xtick
    :param name Name of the country
    :param ax Matplotlib ax
    """

    def _get_flag(name):
        """
        Get the flag of a country from the folder flags.
        :param name Name of the country
        """
        path_flag = os.path.join(sg.__path__[0], 'flags', '{}.png'.format(name))
        return plt.imread(path_flag)

    img = _get_flag(name)
    img_rot = ndimage.rotate(img, 45)
    im = OffsetImage(img_rot.clip(0, 1), zoom=0.18)
    im.image.axes = ax

    ab = AnnotationBbox(im, (coord, 0), frameon=False, pad=0, xycoords='data')

    ax.add_artist(ab)
    return ax


def add_stats_per_vendor(ax, x_i, x_j, y_max, mean, std, cov_intra, cov_inter, f, color):
    """"
    Add stats per vendor to the plot.
    :param ax
    :param x_i coordinate where current vendor is starting
    :param x_j coordinate where current vendor is ending
    :param y_max top of the higher bar of the current vendor
    :param mean
    :param std
    :param cov_intra
    :param cov_inter
    :param f scaling factor
    :param color
    """
    # add stats as strings
    txt = "{0:.2f} $\pm$ {1:.2f}\nCOV intra:{2:.2f}%, inter:{3:.2f}%". \
        format(mean * f, std * f, cov_intra * 100., cov_inter * 100.)
    ax.annotate(txt, xy=(np.mean([x_i, x_j]), y_max), va='center', ha='center',
                bbox=dict(edgecolor='none', fc=color, alpha=0.3))
    # add rectangle for variance
    rect = patches.Rectangle((x_i, (mean - std) * f), x_j - x_i, 2 * std * f,
                             edgecolor=None, facecolor=color, alpha=0.3)
    ax.add_patch(rect)
    # add dashed line for mean value
    ax.plot([x_i, x_j], [mean * f, mean * f], "k--", alpha=0.5)
    return ax


def compute_statistics(df, sites_to_exclude=[]):
    """
    Compute statistics such as mean, std, COV, etc.
    :param df Pandas structure
    :param sites_to_exclude: list: sites to exclude from the statistics
    """
    vendors = ['GE', 'Philips', 'Siemens']
    mean_per_row = []
    std_per_row = []
    stats = {}
    # Compute statistics within site
    for site in df.index:
        mean_per_row.append(np.mean(df['val'][site]))
        std_per_row.append(np.std(df['val'][site]))
    # Update Dataframe
    df['mean'] = mean_per_row  # mean within each site (e.g., if there are 35 sites, this will be a vector of length 35)
    df['std'] = std_per_row
    df['cov'] = np.array(std_per_row) / np.array(mean_per_row)
    # Compute intra-vendor COV
    for vendor in vendors:
        # init dict
        if not 'cov_inter' in stats.keys():
            stats['cov_inter'] = {}
        if not 'cov_intra' in stats.keys():
            stats['cov_intra'] = {}
        if not 'mean' in stats.keys():
            stats['mean'] = {}
        if not 'std' in stats.keys():
            stats['std'] = {}
        # fetch within-site mean values for a specific vendor
        val_per_vendor = df['mean'][(df['vendor'] == vendor) & (~df['site'].isin(sites_to_exclude))]
        # compute mean across vendors (of the mean within site)
        stats['mean'][vendor] = np.mean(val_per_vendor)
        # compute the std across vendors (of the mean within site)
        stats['std'][vendor] = np.std(val_per_vendor)
        # compute inter-site COV, within vendor (based on the mean within site)
        stats['cov_inter'][vendor] = np.std(val_per_vendor) / np.mean(val_per_vendor)
        # compute intra-site COV, and average it across all the sites within the same vendor
        # TODO: exclude sites to exclude
        stats['cov_intra'][vendor] = \
            np.mean(df['std'][df['vendor'] == vendor].values / df['mean'][df['vendor'] == vendor].values)
    return df, stats


def fetch_subject(filename):
    """
    Get subject from filename
    :param filename:
    :return: subject
    """
    path, file = os.path.split(filename)
    subject = path.split(os.sep)[-2]
    return subject


def get_env(file_param):
    """
    Get shell environment variables from a shell script.
    Source: https://stackoverflow.com/a/19431112
    :param file_param:
    :return: env: dictionary of all environment variables declared in the shell script
    """
    logger.debug("\nFetch environment variables from file: {}".format(file_param))
    env = {}
    p = subprocess.Popen('env', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    oldEnv = p.communicate()[0].decode('utf-8')
    p = subprocess.Popen('source {} ; env'.format(file_param), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         shell=True)
    newEnv = p.communicate()[0].decode('utf-8')
    for newStr in newEnv.split('\n'):
        flag = True
        for oldStr in oldEnv.split('\n'):
            if newStr == oldStr:
                # not exported by setenv.sh
                flag = False
                break
        if flag:
            # exported by setenv.sh
            logger.debug("  {}".format(newStr))
            # add to dictionary
            env[newStr.split('=')[0]] = newStr.split('=')[1]
    return env


def label_bar_model(ax, bar_plot, model_lst):
    """
    Add ManufacturersModelName embedded in each bar.
    :param ax Matplotlib axes
    :param bar_plot Matplotlib object
    :param model_lst sorted list of model names
    """
    height = bar_plot[0].get_height()  # in order to align all the labels along y-axis
    for idx, rect in enumerate(bar_plot):
        ax.text(rect.get_x() + rect.get_width() / 2., 0.1 * height,
                model_lst[idx], color='white', weight='bold',
                ha='center', va='bottom', rotation=90)
    return ax


def remove_subject(subject, metric):
    """
    Check if subject should be removed
    :param subject:
    :param metric:
    :return: Bool
    """
    for subject_to_remove in SUBJECTS_TO_REMOVE:
        if subject_to_remove['subject'] == subject and subject_to_remove['metric'] == metric:
            return True
    return False


def compute_regression(CSA_dict, vendor):
    """
    Compute linear regression for T1w and T2 CSA agreement
    :param CSA_dict: dict with T1w and T2w CSA values
    :param vendor: vendor name
    :return: results of linear regression
    """
    # Y = Slope*X + Intercept

    # create object for the class
    linear_regression = LinearRegression()
    # perform linear regression (compute slope and intercept)
    linear_regression.fit(np.concatenate(CSA_dict[vendor + '_t2'], axis=0).reshape(-1, 1),
                          np.concatenate(CSA_dict[vendor + '_t1'], axis=0).reshape(-1, 1))
    intercept = linear_regression.intercept_
    slope = linear_regression.coef_

    # compute prediction
    reg_predictor = linear_regression.predict(
        np.concatenate(CSA_dict[vendor + '_t2'], axis=0).reshape(-1, 1))
    # compute coefficient of determination R^2 of the prediction
    r2_sc = linear_regression.score(np.concatenate(CSA_dict[vendor + '_t2'], axis=0).reshape(-1, 1),
                          np.concatenate(CSA_dict[vendor + '_t1'], axis=0).reshape(-1, 1))

    return intercept, slope, reg_predictor, r2_sc


def main():

    args = get_parameters()
    display_individual_subjects = args.indiv_subj

    if args.path_results is not None:
        if os.path.isdir(args.path_results):
            # Go to results directory defined by user
            os.chdir(args.path_results)
        else:
            raise FileNotFoundError("Directory '{}' was not found.".format(args.path_results))
    else:
        # Stay in current directory (assume it is results directory)
        os.chdir(os.getcwd())

    # fetch all .csv result files, assuming they are located in the current folder.
    csv_files = glob.glob('*.csv')

    if not csv_files:
        raise RuntimeError("Variable 'csv_files' is empty, i.e. no *.csv files were found in current directory.")

    # loop across results and generate figure
    for csv_file in csv_files:

        # Open CSV file and create dict
        logger.info('\nProcessing: ' + csv_file)
        dict_results = []
        with open(csv_file, newline='') as f_csv:
            reader = csv.DictReader(f_csv)
            for row in reader:
                dict_results.append(row)

        # Fetch metric name
        _, csv_file_small = os.path.split(csv_file)
        metric = file_to_metric[csv_file_small]

        # Fetch mean, std, etc. per site
        results_dict = aggregate_per_site(dict_results, metric)

        # Make it a pandas structure (easier for manipulations)
        df = pd.DataFrame.from_dict(results_dict, orient='index')

        # Compute statistics
        if metric not in SITES_TO_EXCLUDE.keys():
            sites_to_exclude = []
        else:
            sites_to_exclude = SITES_TO_EXCLUDE[metric]
        df, stats = compute_statistics(df, sites_to_exclude)

        # sites = list(results_agg.keys())
        # val_mean = [np.mean(values_per_site) for values_per_site in list(results_agg.values())]
        # val_std = [np.std(values_per_site) for values_per_site in list(results_agg.values())]

        if logger.level == 10:
            import matplotlib
            matplotlib.use('TkAgg')
            plt.ion()

        # Sort values per vendor
        # TODO: sort per model
        site_sorted = df.sort_values(by=['vendor', 'model', 'site']).index.values
        vendor_sorted = df['vendor'][site_sorted].values
        mean_sorted = df['mean'][site_sorted].values
        std_sorted = df['std'][site_sorted].values
        model_sorted = df['model'][site_sorted].values

        # Scale values (for display)
        mean_sorted = mean_sorted * scaling_factor[metric]
        std_sorted = std_sorted * scaling_factor[metric]

        # Get color based on vendor
        list_colors = [vendor_to_color[i] for i in vendor_sorted]

        # Create figure and plot bar graph
        fig, ax = plt.subplots(figsize=(15, 8))
        # TODO: show only superior part of STD
        plt.grid(axis='y')
        ax.set_axisbelow(True)
        bar_plot = plt.bar(range(len(site_sorted)), height=mean_sorted, width=0.5,
                           tick_label=site_sorted, yerr=[[0 for v in std_sorted], std_sorted], color=list_colors)

        # Display individual subjects
        if display_individual_subjects:
            for site in site_sorted:
                index = list(site_sorted).index(site)
                val = df['val'][site]
                # Set scaling
                val = [value * scaling_factor.get(metric) for value in val]
                plt.plot([index] * len(val), val, 'r.')
        ax = label_bar_model(ax, bar_plot, model_sorted)  # add ManufacturersModelName embedded in each bar
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")  # rotate xticklabels at 45deg, align at end
        plt.xlim([-1, len(site_sorted)])
        ax.set_xticklabels([s for s in site_sorted])  # add space after the site name to allow space for flag
        # ax.get_xaxis().set_visible(True)
        ax.tick_params(labelsize=15)
        # plt.ylim(ylim[contrast])
        # plt.yticks(np.arange(ylim[contrast][0], ylim[contrast][1], step=ystep[contrast]))
        plt.ylabel(metric_to_label[metric], fontsize=15)

        # add country flag of each site
        for i, c in enumerate(site_sorted):
            try:
                ax = add_flag(i, flags[c], ax)
            except KeyError:
                logger.error('ERROR: Flag {} is not defined in dict flags'.format(c))
                sys.exit(1)

        # add stats per vendor
        x_init_vendor = 0
        # height_bar = [rect.get_height() for idx,rect in enumerate(bar_plot)]
        # y_max = height_bar[i_max]+std_sorted[i_max]  # used to display stats
        y_max = ax.get_ylim()[1] * 95 / 100  # stat will be located at the top 95% of the graph
        for vendor in list(OrderedDict.fromkeys(vendor_sorted)):
            n_site = list(vendor_sorted).count(vendor)
            ax = add_stats_per_vendor(ax=ax,
                                      x_i=x_init_vendor - 0.5,
                                      x_j=x_init_vendor + n_site - 1 + 0.5,
                                      y_max=y_max,
                                      mean=stats['mean'][vendor],
                                      std=stats['std'][vendor],
                                      cov_intra=stats['cov_intra'][vendor],
                                      cov_inter=stats['cov_inter'][vendor],
                                      f=scaling_factor[metric],
                                      color=list_colors[x_init_vendor])
            x_init_vendor += n_site

        plt.tight_layout()  # make sure everything fits
        fname_fig = os.path.join('fig_' + metric + '.png')
        plt.savefig(fname_fig)
        logger.info('Created: ' + fname_fig)

        # Get T1w and T2w CSA from pandas df structure
        if metric == "csa_t1":
            CSA_t1 = df.sort_values('site').values
        elif metric == "csa_t2":
            CSA_t2 = df.sort_values('site').values

    # Create dictionary with CSA for T1w and T2w per vendors
    CSA_dict = defaultdict(list)
    for index, line in enumerate(CSA_t1):       # loop through individual sites
        CSA_dict[line[1] + '_t1'].append(np.asarray(CSA_t1[index, 3]))      # line[1] denotes vendor
        CSA_dict[line[1] + '_t2'].append(np.asarray(CSA_t2[index, 3]))      # line[1] denotes vendor

    # Generate figure for T1w and T2w agreement for all vendors together
    fig, ax = plt.subplots(figsize=(7, 7))
    # Loop across vendors
    for vendor in list(OrderedDict.fromkeys(vendor_sorted)):
        plt.scatter(np.concatenate(CSA_dict[vendor + '_t2'], axis=0),
                    np.concatenate(CSA_dict[vendor + '_t1'], axis=0),
                    s=50,
                    linewidths=2,
                    facecolors='none',
                    edgecolors=vendor_to_color[vendor],
                    label=vendor)
    ax.tick_params(labelsize=LABELSIZE)
    plt.plot([50, 100], [50, 100], ls="--", c=".3")  # add diagonal line
    plt.title("CSA agreement between T1w and T2w data")
    plt.xlim(50, 100)
    plt.ylim(50, 100)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlabel("T2w CSA", fontsize=FONTSIZE)
    plt.ylabel("T1w CSA", fontsize=FONTSIZE)
    plt.grid(True)
    plt.legend(fontsize=FONTSIZE)
    plt.tight_layout()
    fname_fig = 'fig_t1_t2_agreement.png'
    plt.savefig(fname_fig, dpi=200)
    logger.info('Created: ' + fname_fig)

    # Generate figure for T1w and T2w agreement per vendor
    plt.subplots(figsize=(15, 5))
    # Loop across vendors (create subplot for each vendor)
    for index, vendor in enumerate(list(OrderedDict.fromkeys(vendor_sorted))):
        ax = plt.subplot(1, 3, index + 1)
        x = np.concatenate(CSA_dict[vendor + '_t2'], axis=0)
        y = np.concatenate(CSA_dict[vendor + '_t1'], axis=0)
        plt.scatter(x,
                    y,
                    s=50,
                    linewidths=2,
                    facecolors='none',
                    edgecolors=vendor_to_color[vendor],
                    label=vendor)
        ax.tick_params(labelsize=TICKSIZE)
        # Define vendor name position
        legend = ax.legend(loc='lower right', handletextpad=0, fontsize=FONTSIZE)
        # Change box's frame color to black (to be same as box around linear fit equation)
        frame = legend.get_frame()
        frame.set_edgecolor('black')
        ax.add_artist(legend)
        # Dynamic scaling of individual subplots based on data
        offset = 2
        lim_min = min(min(x), min(y))
        lim_max = max(max(x), max(y))
        plt.xlim(lim_min - offset, lim_max + offset)
        plt.ylim(lim_min - offset, lim_max + offset)
        # Add bisection (diagonal) line
        plt.plot([lim_min - offset , lim_max + offset],
                 [lim_min - offset, lim_max + offset],
                 ls="--", c=".3")
        plt.xlabel("T2w CSA", fontsize=FONTSIZE)
        plt.ylabel("T1w CSA", fontsize=FONTSIZE)
        # Move grid to background (i.e. behind other elements)
        ax.set_axisbelow(True)
        plt.grid(True)
        # Enforce square grid
        plt.gca().set_aspect('equal', adjustable='box')
        # Compute linear fit
        intercept, slope, reg_predictor, r2_sc = compute_regression(CSA_dict, vendor)
        # Place regression equation to upper-left corner
        plt.text(0.1, 0.9,
                 "y = {0:.4}x + {1:.4}\nR\u00b2 = {2:.4}".format(float(slope), float(intercept), float(r2_sc)),
                 ha='left', va='center', transform = ax.transAxes, fontsize=TICKSIZE, color='red',
                 bbox=dict(boxstyle='round', facecolor='white', alpha=1))   # box around equation
        # Plot linear fit
        axes = plt.gca()
        x_vals = np.array(axes.get_xlim())
        y_vals = intercept + slope * x_vals
        y_vals = np.squeeze(y_vals)     # change shape from (1,N) to (N,)
        plt.plot(x_vals, y_vals, color='red')
        # Add title above middle subplot
        if index == 1:
            plt.title("CSA agreement between T1w and T2w data per vendors", fontsize=FONTSIZE, pad=20)
    # Move subplots closer to each other
    plt.subplots_adjust(wspace=-0.5)
    plt.tight_layout()
    fname_fig = 'fig_t1_t2_agreement_per_vendor.png'
    plt.savefig(fname_fig, dpi=200)
    logger.info('Created: ' + fname_fig)


if __name__ == "__main__":
    main()
