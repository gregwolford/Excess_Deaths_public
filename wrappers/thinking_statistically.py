# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import chart_studio
import chart_studio.plotly as py

def ecdf(data):
    """Compute ECDF for a one-dimensional array of measurements."""
    # Number of data points: n
    n = len(data)

    # x-data for the ECDF: x
    x = np.sort(data)

    # y-data for the ECDF: y
    y = np.arange(1, n+1) / n

    return x, y

def pearson_r(x, y):
    """Compute Pearson correlation coefficient between two arrays."""
    # Compute correlation matrix: corr_mat
    corr_mat=np.corrcoef(x,y)

    # Return entry [0,1]
    return corr_mat[0,1]

def bootstrap_replicate_1d(data, func):
    """Generate bootstrap replicate of 1D data."""
    bs_sample = np.random.choice(data, len(data))
    return func(bs_sample)

def draw_bs_reps(data, func, size=1):
    """Draw bootstrap replicates."""

    # Initialize array of replicates: bs_replicates
    bs_replicates = np.empty(size)

    # Generate replicates
    for i in range(size):
        bs_replicates[i] = bootstrap_replicate_1d(data,func)

    return bs_replicates

def draw_bs_pairs_linreg(x, y, size=1):
    """Perform pairs bootstrap for linear regression."""

    # Set up array of indices to sample from: inds
    inds = np.arange(0, len(x))

    # Initialize replicates: bs_slope_reps, bs_intercept_reps
    bs_slope_reps = np.empty(size)
    
    bs_intercept_reps = np.empty(size)

    # Generate replicates
    for i in range(size):
        bs_inds = np.random.choice(inds, size=len(inds))
        bs_x, bs_y = x[bs_inds], y[bs_inds]
        bs_slope_reps[i], bs_intercept_reps[i] = np.polyfit(bs_x, bs_y, 1)

    return bs_slope_reps, bs_intercept_reps

def permutation_sample(data1, data2):
    """Generate a permutation sample from two data sets."""

    # Concatenate the data sets: data
    data = np.concatenate((data1, data2))

    # Permute the concatenated array: permuted_data
    permuted_data = np.random.permutation(data)

    # Split the permuted array into two: perm_sample_1, perm_sample_2
    perm_sample_1 = permuted_data[:len(data1)]
    perm_sample_2 = permuted_data[len(data1):]

    return perm_sample_1, perm_sample_2

def draw_perm_reps(data_1, data_2, func, size=1):
    """Generate multiple permutation replicates."""

    # Initialize array of replicates: perm_replicates
    perm_replicates = np.empty(size)

    for i in range(size):
        # Generate permutation sample
        perm_sample_1, perm_sample_2 = permutation_sample(data_1, data_2)

        # Compute the test statistic
        perm_replicates[i] = func(perm_sample_1, perm_sample_2)

    return perm_replicates

def diff_of_means(data_1, data_2):
    """Difference in means of two arrays."""

    # The difference of means of data_1, data_2: diff
    diff = np.mean(data_1)-np.mean(data_2)

    return diff

def is_it_normally_distributed(_series):
    # Is it normally distributed?
    _std = np.std(_series)
    _mean = np.mean(_series)
    samples = np.random.normal(_mean, _std, 1000000)
    x_theor, y_theor = ecdf(samples)
    x,y = ecdf(_series)
    
    _ = plt.plot(x_theor, y_theor)
    _ = plt.plot(x, y, marker='.', linestyle='none')
    #_ = plt.xlabel('Percent cases')
    #_ = plt.ylabel('CDF')
    plt.show()


def permutation_test(sample1, sample2, title, assessment, name1, name2):
    print(title)
    data = []
    for _ in range(50):
        perm_sample1, perm_sample2 = permutation_sample(sample1, sample2)

        x1, y1 = ecdf(perm_sample1)
        x2, y2 = ecdf(perm_sample2)
        
        trace1 = go.Scatter(x=x1, y=y1,
                    mode='markers', 
                    marker_color='rgba(0,0,255, 0.2)',
                    name = name1,
                    showlegend=False)
        data.append(trace1)
        
        trace2 = go.Scatter(x=x2, y=y2,
                    mode='markers', 
                    marker_color='rgba(255, 0, 0, 0.2)',
                    name = name2,
                    showlegend=False)
        
        data.append(trace2)

        #_ = plt.plot(x1, y1, marker='.', linestyle='none', color='blue', alpha=0.02)
        #_ = plt.plot(x2, y2, marker='.', linestyle='none', color='red', alpha=0.02)

    # Plot original data
    x1, y1 = ecdf(sample1)
    x2, y2 = ecdf(sample2)
    trace1 = go.Scatter(x=x1, y=y1,
                    mode='markers', 
                    marker_color='rgb(0,0,255)',
                    name=name1,
                    showlegend=False)
    data.append(trace1)
        
    trace2 = go.Scatter(x=x2, y=y2,
                    mode='markers', 
                    marker_color='rgb(255, 0, 0)',
                    name=name2,
                    showlegend=False)
        
    data.append(trace2)
    py.plot(data, filename = 'Excess-deaths-permuation-test', auto_open = True)
    
    #_ = plt.plot(x1, y1, marker='.', linestyle='none', color='blue')
    #_ = plt.plot(x2, y2, marker='.', linestyle='none', color='red')
    #plt.margins(0.02)
    #plt.show()
    #plt.close()

    empirical_diff_means = diff_of_means(sample1, sample2)
    perm_replicates = draw_perm_reps(sample1, sample2, diff_of_means, size=10000)
    # Compute p-value: p
    p = np.sum(perm_replicates >= empirical_diff_means) / len(perm_replicates)

    # Print the result
    print(assessment.format(name1, name2, p))


def shifted_means_test(sample_all, sample1, sample2, name1, name2, sample_size=10000):
    # Get the mean of all cases
    mean_all = np.mean(sample_all)
    mean1 = np.mean(sample1)
    mean2 = np.mean(sample2)

    mean1_shifted = sample1 - mean1 + mean_all
    mean2_shifted = sample2 - mean2 + mean_all

    # Compute 10,000 bootstrap replicates from the shifted arrays
    bs_replicates_1 = draw_bs_reps(mean1_shifted, np.mean, sample_size)
    bs_replicates_2 = draw_bs_reps(mean2_shifted, np.mean, sample_size)

    bs_replicates = bs_replicates_1 - bs_replicates_2

    # Compute and print p-Value
    empirical_diff_means = diff_of_means(sample1, sample2)
    p = np.sum(bs_replicates >= empirical_diff_means) / sample_size
    print('P Value for difference of means comparison between {} and {}: {:.3f}\n'.format(name1, name2, p))