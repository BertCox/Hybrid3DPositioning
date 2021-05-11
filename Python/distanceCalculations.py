#  ____  ____      _    __  __  ____ ___
# |  _ \|  _ \    / \  |  \/  |/ ___/ _ \
# | | | | |_) |  / _ \ | |\/| | |  | | | |
# | |_| |  _ <  / ___ \| |  | | |__| |_| |
# |____/|_| \_\/_/   \_\_|  |_|\____\___/
#                           research group
#                             dramco.be/
#
#  KU Leuven - Technology Campus Gent,
#  Gebroeders De Smetstraat 1,
#  B-9000 Gent, Belgium
#
#         File: simple_mlat_3D.py
#      Created: 2021-02-23
#       Author: Bert Cox
#      Version: 0.2
#
#  Description: 3D positioning of acoustic data based on trilateration algorithms
#  Uses the CSV data of three distances
#
#  License L (optionally)
#

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

# Libraries -----------------------------------

import numpy as np
from locfunc import *
from plotting import *
print("hello")

from numpy import genfromtxt
print("hello")

from multiprocessing import Pool

# variables ---------------------------------
# datafiles
path = 'C:\\Users\\coxbe\\Box\\KU Leuven\\PhD\\Papers\\IPIN2021\\Code\\Python\\Data2\\'
positions_CSV = path + 'Positions.csv'
# speaker0_CSV_file = path + 'Speaker 3PositionTest3.csv'
# speaker1_CSV_file = path + 'Speaker 0PositionTest3.csv'
# speaker2_CSV_file = path + 'Speaker 1PositionTest3.csv'
# speaker3_CSV_file = path + 'Speaker 2PositionTest3.csv'
#
positions = genfromtxt(positions_CSV, delimiter=',', skip_header=1)
# speaker0_data = genfromtxt(speaker0_CSV_file, delimiter=',', skip_header=1)
# speaker1_data = genfromtxt(speaker1_CSV_file, delimiter=',', skip_header=1)
# speaker2_data = genfromtxt(speaker2_CSV_file, delimiter=',', skip_header=1)
# speaker3_data = genfromtxt(speaker3_CSV_file, delimiter=',', skip_header=1)
#
# start_index = 0
# stop_index = min(len(speaker0_data), len(speaker1_data), len(speaker2_data), len(speaker3_data))
# speaker_all = np.stack((speaker0_data[start_index:stop_index],speaker1_data[start_index:stop_index],speaker2_data[start_index:stop_index],speaker3_data[start_index:stop_index]))

num_speakers = 4
h = 3

# set the speaker coordinates
speaker_x_coords = np.array([0.5, 1.015, 5.183, 6.901])
speaker_y_coords = np.array([0.05, 3.950, 0.067, 3.948])
speaker_z_coords = np.array([0.146, 2.215, 0.744, 1.322])



speaker_total = np.transpose(np.vstack((speaker_x_coords, speaker_y_coords, speaker_z_coords)))
print(speaker_total)
# # Absolute measured coordinates with laser measurer

x_coord = np.array(positions)[:,1]
y_coord = np.array(positions)[:,2]
z_coord = np.array(positions)[:,3]

speaker0_reference_distances = [calc_distance_3D(x_coord[i], y_coord[i], z_coord[i], speaker_x_coords[0], speaker_y_coords[0], speaker_z_coords[0]) for i in range(len(x_coord))]
speaker1_reference_distances = [calc_distance_3D(x_coord[i], y_coord[i], z_coord[i], speaker_x_coords[1], speaker_y_coords[1], speaker_z_coords[1]) for i in range(len(x_coord))]
speaker2_reference_distances = [calc_distance_3D(x_coord[i], y_coord[i], z_coord[i], speaker_x_coords[2], speaker_y_coords[2], speaker_z_coords[2]) for i in range(len(x_coord))]
speaker3_reference_distances = [calc_distance_3D(x_coord[i], y_coord[i], z_coord[i], speaker_x_coords[3], speaker_y_coords[3], speaker_z_coords[3]) for i in range(len(x_coord))]
distances_to_speakers = np.transpose(np.vstack((speaker0_reference_distances, speaker1_reference_distances, speaker2_reference_distances, speaker3_reference_distances)))

speaker0_mean_measured_distances = [np.mean(genfromtxt(path + 'PositionAllData\\Speaker0Position' + str((i+1)) + '.csv', delimiter=',', skip_header=1)) for i in range(len(x_coord))]
speaker1_mean_measured_distances = [np.mean(genfromtxt(path + 'PositionAllData\\Speaker1Position' + str((i+1)) + '.csv', delimiter=',', skip_header=1)) for i in range(len(x_coord))]
speaker2_mean_measured_distances = [np.mean(genfromtxt(path + 'PositionAllData\\Speaker2Position' + str((i+1)) + '.csv', delimiter=',', skip_header=1)) for i in range(len(x_coord))]
speaker3_mean_measured_distances = [np.mean(genfromtxt(path + 'PositionAllData\\Speaker3Position' + str((i+1)) + '.csv', delimiter=',', skip_header=1)) for i in range(len(x_coord))]
mean_measured_distances = np.transpose(np.vstack((speaker0_mean_measured_distances, speaker1_mean_measured_distances, speaker2_mean_measured_distances, speaker3_mean_measured_distances)))

error_on_distances = mean_measured_distances - distances_to_speakers

# create heatmaps for different speakers on different Z
# plot_heatmap(abs(error_on_distances[0:50,:]), 'Heatmap Z = 0.751', 'HeatmapZ1')
# plot_heatmap(abs(error_on_distances[50:100,:]), 'Heatmap Z = 1.881', 'HeatmapZ2')
plot_heatmap(abs(error_on_distances[100:150,:]), 'Heatmap Z = 1.406', 'HeatmapZ3')

# plot the error of each speaker in a heatmap
# plot_error_speaker(speaker_x_coords, speaker_y_coords, speaker_z_coords, x_coord, y_coord, z_coord, abs(error_on_distances), 'Mean distance error to', '3DplotMeanDistanceError')


euclidian_dist_mean = np.ones(150)
euclidian_dist_mean_NLSE = np.ones(150)
euclidian_dist_mean_RangeBancroft = np.ones(150)
euclidian_dist_mean_Beck = np.ones(150)
euclidian_dist_mean_Chueng = np.ones(150)
euclidian_dist_mean_GaussNewton = np.ones(150)
minimumvalue= np.ones(150)

for j in range(1, len(x_coord)+1):
    speaker0_data = genfromtxt(path + 'PositionAllData\\Speaker0Position' + str(j) + '.csv', delimiter=',', skip_header=1)
    speaker1_data = genfromtxt(path + 'PositionAllData\\Speaker1Position' + str(j) + '.csv', delimiter=',', skip_header=1)
    speaker2_data = genfromtxt(path + 'PositionAllData\\Speaker2Position' + str(j) + '.csv', delimiter=',', skip_header=1)
    speaker3_data = genfromtxt(path + 'PositionAllData\\Speaker3Position' + str(j) + '.csv', delimiter=',', skip_header=1)

    start_index = 0
    stop_index = min(len(speaker0_data), len(speaker1_data), len(speaker2_data), len(speaker3_data))
    speaker_all = np.stack((speaker0_data[start_index:stop_index], speaker1_data[start_index:stop_index],
                            speaker2_data[start_index:stop_index], speaker3_data[start_index:stop_index]))

    calculated_positions = [estimate_xyz(speaker_x_coords, speaker_y_coords, speaker_z_coords, speaker_all[:, i]) for i
                            in range(len(speaker_all[0]))]
    # calculated_positions_NLSE = [
    #     estimate_xyz_NLSE(speaker_x_coords, speaker_y_coords, speaker_z_coords, speaker_all[:, i], [3.6, 2.0, 1.2]).x
    #     for i in range(len(speaker_all[0]))]
    calculated_positions_RangeBancroft = [estimate_xyz_RangeBancroft(speaker_total, num_speakers, speaker_all[:, i]) for i in range(len(speaker_all[0]))]
    calculated_positions_Beck = [estimate_xyz_Beck(speaker_total, num_speakers, speaker_all[:, i]) for i in range(len(speaker_all[0]))]
    calculated_positions_Chueng = [estimate_xyz_Chueng2(speaker_total,num_speakers, speaker_all[:,i]) for i in range(len(speaker_all[0]))]
    calculated_positions_GaussNewton = [estimate_xyz_GaussNewton(speaker_total,num_speakers, speaker_all[:,i]) for i in range(len(speaker_all[0]))]

    if j == 20:
        # plot = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j-1, 1:4] , calculated_positions, 'Position 8 Simple Intersection', 'Position8SimpleIntersection')
        # plot = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j-1, 1:4] , calculated_positions_NLSE, 'Position 1 NLSE', 'Position1NLSE')
        # plot = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j-1, 1:4] , calculated_positions_RangeBancroft, 'Position 8 RangeBancroft', 'Position8RangeBancroft')
        # plot = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j-1, 1:4] , calculated_positions_Beck, 'Position 8 Beck', 'Position8Beck')
        # plot = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j-1, 1:4] , calculated_positions_Chueng, 'Position 8 Chueng', 'Position8Chueng')
        # plot = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j-1, 1:4] , calculated_positions_GaussNewton, 'Position 8 Gauss Newton', 'Position8BancroftChueng')
        plot = plot_room_plotly_two_methods(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j - 1, 1:4],
                            calculated_positions_RangeBancroft, calculated_positions_Chueng, 'Position 20', 'Position20GaussNewton')

    #
    if j == 34:
    #     plot = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j - 1, 1:4], calculated_positions, 'Position 34 Simple Intersection', 'Position34SimpleIntersection')
    #     # plot = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j - 1, 1:4], calculated_positions_NLSE, 'Position 34 NLSE', 'Position34NLSE')
    #     plot = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j - 1, 1:4], calculated_positions_RangeBancroft, 'Position 34 RangeBancroft', 'Position34RangeBancroft')
    #     plot = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j - 1, 1:4], calculated_positions_Beck, 'Position 34 Beck', 'Position34Beck')
    #     plot = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j-1, 1:4] , calculated_positions_Chueng, 'Position 34 Chueng', 'Position34Chueng')
    #     plot = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j - 1, 1:4], calculated_positions_GaussNewton, 'Position 34 Gauss Newton', 'Position34GaussNewton')
          plot = plot_room_plotly_two_methods(speaker_x_coords, speaker_y_coords, speaker_z_coords, positions[j - 1, 1:4], calculated_positions_RangeBancroft, calculated_positions_Chueng,'Position 34', 'Position34BancroftChueng')

    euclidian_dist = [np.linalg.norm(positions[j-1, 1:4] - calculated_positions[i]) for i in range(len(speaker_all[0]))]
    # euclidian_dist_NLSE = [np.linalg.norm(positions[j - 1, 1:4] - calculated_positions_NLSE[i]) for i in range(len(speaker_all[0]))]
    euclidian_dist_RangeBancroft = [np.linalg.norm(positions[j-1, 1:4] - calculated_positions_RangeBancroft[i]) for i in range(len(speaker_all[0]))]
    euclidian_dist_Beck = [np.linalg.norm(positions[j-1, 1:4] - calculated_positions_Beck[i]) for i in range(len(speaker_all[0]))]
    euclidian_dist_Chueng = [np.linalg.norm(positions[j-1, 1:4] - calculated_positions_Chueng[i]) for i in range(len(speaker_all[0]))]
    euclidian_dist_GaussNewton = [np.linalg.norm(positions[j-1, 1:4] - calculated_positions_GaussNewton[i]) for i in range(len(speaker_all[0]))]

    euclidian_dist_total = np.concatenate((euclidian_dist,euclidian_dist_RangeBancroft, euclidian_dist_Beck, euclidian_dist_Chueng, euclidian_dist_GaussNewton))

    minimumvalue[j-1] = np.amin(euclidian_dist_total)
    euclidian_dist_mean[j-1] = np.mean(euclidian_dist)
    # euclidian_dist_mean_NLSE[j - 1] = np.mean(euclidian_dist_NLSE)
    euclidian_dist_mean_RangeBancroft[j-1] = np.mean(euclidian_dist_RangeBancroft)
    euclidian_dist_mean_Beck[j-1] = np.mean(euclidian_dist_Beck)
    euclidian_dist_mean_Chueng[j-1] = np.mean(euclidian_dist_Chueng)
    euclidian_dist_mean_GaussNewton[j-1] = np.mean(euclidian_dist_GaussNewton)
    print(j)



# ----------------------------------plot the error in color-------------------------------------------------------------
# plot_error = plot_error_color_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, x_coord, y_coord, z_coord,euclidian_dist_mean, 'Mean Error Euclidian Distance', 'EuclidianErrorFullColor')
# plot_error_NLSE = plot_error_color_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, x_coord, y_coord, z_coord,euclidian_dist_mean_NLSE, 'Mean Error Euclidian Distance NLSE', 'EuclidianErrorNLSEFullColor')
# plot_error_RangeBancroft = plot_error_color_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, x_coord, y_coord, z_coord,euclidian_dist_mean_RangeBancroft, 'Mean Error Euclidian Distance Range Bancroft', 'EuclidianErrorRangeBancroftFullColor')
# plot_error_Beck = plot_error_color_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, x_coord, y_coord, z_coord,euclidian_dist_mean_Beck, 'Mean Error Euclidian Distance Beck', 'EuclidianErrorBeckFullColor')
# plot_error_Chueng = plot_error_color_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, x_coord, y_coord, z_coord,euclidian_dist_mean_Chueng, 'Mean Error Euclidian Distance Chueng', 'EuclidianErrorChueng')
# plot_error_GaussNewton = plot_error_color_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, x_coord, y_coord, z_coord,euclidian_dist_mean_GaussNewton, 'Mean Error Euclidian Distance Gauss Newton', 'EuclidianErrorGaussNewtonFullColor')

# ----------------------------------plot the CDF -------------------------------------------------------------


euclidian_dist_mean = genfromtxt(path + 'euclidian_dist_mean.csv', delimiter= ',', skip_header=0)
euclidian_dist_mean_RangeBancroft = genfromtxt(path + 'euclidian_dist_mean_RangeBancroft.csv', delimiter= ',', skip_header=0)
euclidian_dist_mean_Beck = genfromtxt(path + 'euclidian_dist_mean_Beck.csv', delimiter= ',', skip_header=0)
euclidian_dist_mean_Chueng = genfromtxt(path + 'euclidian_dist_mean_Chueng.csv', delimiter= ',', skip_header=0)
euclidian_dist_mean_GaussNewton = genfromtxt(path + 'euclidian_dist_mean_GaussNewton.csv', delimiter= ',', skip_header=0)

sorted_simpleIntersection = np.sort(euclidian_dist_mean)
sorted_RangeBancroft = np.sort(euclidian_dist_mean_RangeBancroft)
sorted_Beck = np.sort(euclidian_dist_mean_Beck)
sorted_Chueng = np.sort(euclidian_dist_mean_Chueng)
sorted_GaussNewton = np.sort(euclidian_dist_mean_GaussNewton)
plot_cumdensityfunc = plot_CDF(sorted_simpleIntersection, sorted_RangeBancroft, sorted_Beck, sorted_Chueng, sorted_GaussNewton, 'Cumulative Density function of mean euclidian distances', 'CDF plot', )


plot = plot_references_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, x_coord, y_coord, z_coord, 'Room Positions', 'RoomPositions')

# Calculations

# calculate the positions for each speaker set
# calculated_positions = [estimate_xyz(speaker_x_coords, speaker_y_coords, speaker_z_coords, speaker_all[:,i]) for i in range(len(speaker_all[0]))]
# calculated_positions_NLSE = [estimate_xyz_NLSE(speaker_x_coords, speaker_y_coords, speaker_z_coords, speaker_all[:,i], [3.6, 2.0, 1.2]).x for i in range(len(speaker_all[0]))]
#
# calculated_positions_SimpleIntersections = [estimate_xyz_SimpleIntersection(speaker_total,num_speakers, speaker_all[:,i]) for i in range(len(speaker_all[0]))]
# calculated_positions_RangeBancroft = [estimate_xyz_RangeBancroft(speaker_total,num_speakers, speaker_all[:,i]) for i in range(len(speaker_all[0]))]
# calculated_positions_Beck = [estimate_xyz_Beck(speaker_total,num_speakers, speaker_all[:,i]) for i in range(len(speaker_all[0]))]
# calculated_positions_Chueng = [estimate_xyz_Chueng(speaker_total,num_speakers, speaker_all[:,i]) for i in range(len(speaker_all[0]))]
# calculated_positions_GaussNewton = [estimate_xyz_GaussNewton(speaker_total,num_speakers, speaker_all[:,i]) for i in range(len(speaker_all[0]))]
# calculated_positions_GaussNewtonReg = [estimate_xyz_GaussNewton_reg(speaker_total,num_speakers, speaker_all[:,i]) for i in range(len(speaker_all[0]))]


# euclidian_dist = [np.linalg.norm(point_laser - calculated_positions[i]) for i in range(len(speaker_all[0]))]
# print(euclidian_dist)
#
# euclidian_dist_NLSE = [np.linalg.norm(point_laser - calculated_positions_NLSE[i]) for i in range(len(speaker_all[0]))]
# print(euclidian_dist_NLSE)
#
# euclidian_dist_NLSE = [np.linalg.norm(point_laser - calculated_positions_NLSE[i]) for i in range(len(speaker_all[0]))]
# print(euclidian_dist_NLSE)



# intersection_position = estimate_xyz_SimpleIntersection(speaker_total, num_speakers, speaker_all[:,0])
# print(intersection_position)


# MATPLOTLIB
# plot = plot_room(speaker_x_coords, speaker_y_coords, speaker_z_coords, point_laser, calculated_positions, 'Least Squares')
# plot_NLSE = plot_room(speaker_x_coords, speaker_y_coords, speaker_z_coords, point_laser, calculated_positions_NLSE, 'Non-linear Least Squares')

# PLOTLY
# plot = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, point_laser, calculated_positions, 'Least Squares', 'LeastSquaresTest3')
# plot_NLSE = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, point_laser, calculated_positions_NLSE, 'Non-Linear Least Squares', 'Non-LinearLeastSquaresTest3')
# plot_intersection = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, point_laser, calculated_positions_SimpleIntersections, 'Simple Intersection', 'SimpleIntersectionTest3')
# plot_RangeBancroft = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, point_laser, calculated_positions_RangeBancroft, 'RangeBancroft', 'RangeBancroftTest3')
# plot_Beck = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, point_laser, calculated_positions_Beck, 'Beck', 'BeckTest3')
# plot_Chueng = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, point_laser, calculated_positions_Chueng, 'Chueng', 'CheungTest3')
# plot_GaussNewton = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, point_laser, calculated_positions_GaussNewton, 'Gauss Newton', 'GaussNewtonTest3')
# plot_GaussNewtonReg = plot_room_plotly(speaker_x_coords, speaker_y_coords, speaker_z_coords, point_laser, calculated_positions_GaussNewtonReg, 'Regularised Gauss Newton', 'GaussNewtonRegTest3')


#
# est = estimate_xyz(speaker_x_coords, speaker_y_coords, speaker_z_coords, distances)

#
# Speaker0_mean = Speaker0_data["Speaker0"].mean()
# print(Speaker0_mean)
# x_coord = 0.5
# y_coord = 0.8
# z_coord = 1.0
#
# x_coord = 3.385
# y_coord = 2.603
# z_coord = 1.110
#
# point = np.array([x_coord, y_coord, z_coord])
# distances = [4.008984, 3.00124, 3.058188, 3.684506]
#
# distances = np.array(distances) # + 0.01 * np.random.randn(4)
#
# est = estimate_xyz(speaker_x_coords, speaker_y_coords, speaker_z_coords, distances)
#
# print(est)
# # error_processing_3D(est, point, False)
#
# est_nlse = estimate_xyz_NLSE(speaker_x_coords, speaker_y_coords, speaker_z_coords, distances, [0., 0., 0.])
# print(est_nlse)
# # error_processing_3D(est_nlse.x, point, False)
#

