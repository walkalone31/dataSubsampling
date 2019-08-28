import cv2
import json
import numpy as np

####################################################
#Input : intrinsics, extrinsics, depth, color      #
#Output: The color map which align to depth space  #
#Desc  : The goal is to generate align's color map #
#        which is align to depth space.            #
####################################################


def imageRegistration( intr, extr, depth, color, is_holefilling_on = True ):
    r = extr['depth2color_extrinsics.rotation']
    t = extr['depth2color_extrinsics.translation']

    #depth
    cx2 = float(intr['depth_intrinsics.ppx'])
    cy2 = float(intr['depth_intrinsics.ppy'])
    fx2 = float(intr['depth_intrinsics.fx'])
    fy2 = float(intr['depth_intrinsics.fy'])
    #rgb
    cx1 = float(intr['color_intrinsics.ppx'])
    cy1 = float(intr['color_intrinsics.ppy'])
    fx1 = float(intr['color_intrinsics.fx'])
    fy1 = float(intr['color_intrinsics.fy'])
    #rotation
    R = [[float(r[0]), float(r[1]), float(r[2])],
         [float(r[3]), float(r[4]), float(r[5])],
         [float(r[6]), float(r[7]), float(r[8])]]
    #translation
    T = [float(t[0]),
         float(t[1]),
         float(t[2])]
    
    invfx2 = 1.0 / fx2
    invfy2 = 1.0 / fy2

    ( d_height, d_width ) = depth.shape[:2]
    ( c_height, c_width ) = color.shape[:2]
    
    Z2 = depth.copy()
    depth_scale = 0.001 #Realsense depth unit

    #do depth hole filling
    kernel = np.asarray( [[0, 1, 0], [1, 1, 1], [0, 1, 0]] ).astype(np.uint8)
    num_all_pixels = d_width * d_height
    while is_holefilling_on == True:
        mask = (Z2 == 0)
        Z2[mask] = cv2.dilate( Z2, kernel )[mask]
        num_invalid_pixels = num_all_pixels - cv2.countNonZero(Z2)
        if num_invalid_pixels == 0:
            break
    
    #get x and y map in depth space
    indexX = np.asarray( [list( range(d_width) ) for y in range(d_height)] ).astype( np.float32 )
    indexY = np.asarray( [[y] * d_width for y in range(d_height)] ).astype( np.float32 )

    Z2 = Z2.astype(np.float32) * depth_scale
    X2 = ( indexX - cx2 ) * Z2 * invfx2 
    Y2 = ( indexY - cy2 ) * Z2 * invfy2 

    R = np.asarray(R)
    R = R.ravel() #ravel to 1d array
    
    X1 = R[0] * X2 + R[3] * Y2 + R[6] * Z2 + T[0]
    Y1 = R[1] * X2 + R[4] * Y2 + R[7] * Z2 + T[1]
    Z1 = R[2] * X2 + R[5] * Y2 + R[8] * Z2 + T[2]
    
    matMap1 = cx1 + fx1 * X1 / Z1
    matMap2 = cy1 + fy1 * Y1 / Z1

    out_image = cv2.remap( color, matMap1, matMap2, cv2.INTER_LINEAR )

    return out_image





#with open('test/camera_extrinsics.json') as reader:
#    extrinsics = json.loads( reader.read() )
#    
#
#with open('test/camera_intrinsics.json', 'r') as camera_intrinsics:
#    intrinsics = json.loads( camera_intrinsics.read() )
#
#
#    depth = cv2.imread( 'test/nocutoff_depth_000002.pgm', -1 )
#    color = cv2.imread( 'test/rgb_000002.png', -1 )
#
#
#    out_image = imageRegistration( intrinsics, extrinsics, depth, color )
