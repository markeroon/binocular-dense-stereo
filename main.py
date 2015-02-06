import sys
import numpy as np

import cv2

from utils import get_rot_trans_matrix_img2_wrt_img1, get_disparity


def main():
    # Choose images
    left_img_number = "01"
    right_img_number = "02"

    # Load images
    img_left = cv2.imread('dataset_templeRing/templeR00%s.png' % left_img_number)
    img_right = cv2.imread('dataset_templeRing/templeR00%s.png' % right_img_number)

    height, width, depth = img_left.shape
    img_shape = (width, height)

    ##############################################################################################
    # Load Calibration Information
    ##############################################################################################
    # Calibration Matrix - same for each image
    K = np.array([[1520.4, 0., 302.32],
                  [0, 1525.9, 246.87],
                  [0, 0, 1]])

    # images are distorsion free
    d = np.zeros((5, 1))

    ##############################################################################################
    # Load Images Calibration from file
    ##############################################################################################
    calibration_file = open('dataset_templeRing/templeR_par.txt', 'r')
    all_images_parameters = []
    for line in calibration_file:
        row = [float(j) for j in line[107:378].split()]
        all_images_parameters.append(row)
    calibration_file.close()
    all_images_parameters = np.array(all_images_parameters[1:])  # remove useless header
    ##############################################################################################

    ##############################################################################################
    # Rectify images
    ##############################################################################################
    # Get Rotation Matrix and T of right images from the left one
    # r_left and r_right are the original rotation matrix
    R, T = get_rot_trans_matrix_img2_wrt_img1(all_images_parameters, int(left_img_number), int(right_img_number))
    img_shape_rectified = (width, height)
    # Compute stereo Rectification
    R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(K, d, K, d, img_shape_rectified, R, T, alpha=0)

    # Get map rectification
    map_left1, map_left2 = cv2.initUndistortRectifyMap(K, d, R1, P1, img_shape_rectified, cv2.CV_32FC1)
    map_right1, map_right2 = cv2.initUndistortRectifyMap(K, d, R2, P2, img_shape_rectified, cv2.CV_32FC1)

    # Apply Rectification
    left_rectified = cv2.remap(img_left, map_left1, map_left2, cv2.INTER_NEAREST)
    right_rectified = cv2.remap(img_right, map_right1, map_right2, cv2.INTER_NEAREST)
    ##############################################################################################

    ##############################################################################################
    # Compute disparity images
    ##############################################################################################
    # Compute disparity on rectified images
    disparity_method = "SGBM"
    disparity = get_disparity(left_rectified, right_rectified, disparity_method)
    ##############################################################################################


    pre_rectify = np.hstack((img_left, img_right))
    after_rectify = np.hstack((left_rectified, right_rectified))
    # total = np.vstack((pre_rectify, after_rectify))
    cv2.imshow("PreRectify", pre_rectify)
    cv2.imshow("AfterRectify", after_rectify)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    #
    # # Show images
    # cv2.imshow("disparity", disparity)
    # cv2.imshow("left1", img_left)
    # cv2.imshow("right2", img_right)
    # cv2.imshow("rectified_left", left_rectified)
    # cv2.imshow("rectified_right", right_rectified)

    # cv2.reprojectImageTo3D()


if __name__ == "__main__":
    main()









# #templeR0002.png 1520.400000 0.000000 302.320000 0.000000 1525.900000 246.870000 0.000000 0.000000 1.000000 0.00272557078828676410 0.98353557606148900000 -0.18069405603193772000 0.99651741905514424000 -0.01773058775937118300 -0.08147797111723514800 -0.08334029507718225500 -0.17984270037758626000 -0.98015865977776562000 -0.0288222339759 -0.0306361018019 0.525505113107
# #"imgname.png k11 k12 k13 k21 k22 k23 k31 k32 k33 r11 r12 r13 r21 r22 r23 r31 r32 r33 t1 t2 t3"
# #The projection matrix for that image is given by K*[R t]
#
# (CM1, CM2, D1, D2, R, T, E, F) = loadCalibration(calibdir)
# # CM 3x3 -> K
# # D 1x5  ->
# # R 3x3
# # T 3x1
# # E 3x3
# # F 3x3
#
# R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(CM1, D1, CM2, D2, image_size, R, T, alpha=0)


