import os
import sys
import cv2
import numpy as np
import shutil
import functools
import json
import xlwt
from rgb2depth import imageRegistration
#from functools import partial
Save_folder = "hand_dataset_sampling_ir"
MyPath  = sys.argv[1]
sampling_gap = int( sys.argv[2] )
START = True
STOP = False

def addIndex( index, end_index ):
    if index < end_index:
        return index + 1
    else:
        return index

def minusIndex( index, start_index ):
    if index > start_index:
        return index - 1
    else:
        return index

def changeStatus( stream_status ):
    if stream_status == START:
        return STOP
    else:
        return START

def pp( string ):
    print( string )

################################################################
# Name   : fileCounter()                                       #
# Input  : Folder's dir                                        #
# Output : Number of files in the folder's dir                 #
# Desc   : We list all files in folder's dir and use           #
#          os.path.isfile to check if is file and calculate    #
#          total number                                        #
################################################################
def fileCounter( dir_str ):
    return len([f for f in os.listdir( dir_str ) if os.path.isfile( os.path.join( dir_str, f ) )])


#################################################################
# Name   : getBaseDirList()                                     #
# Input  : top folder's dir                                     #
# Output : Dir list about which folder have files in it         #
# Desc   : Use os.walk to check all folder in top folder's and  #
#          list all the dir which we find                       #
#################################################################
def getBaseDirList( dir_str ):
    base_list = []

    if os.path.isdir( dir_str ):
        for root, dirs, files in os.walk( dir_str ):
            dirs.sort()
            num_files = fileCounter( root )
            if num_files != 0:
                base_list.append( root )
    return base_list

#################################################################
# Name   : getSerialNumberFromMaskIR()                          #
# Input  : files's name string                                  #
# Output : int(serial_number)                                   #
# Desc   : This func is to get the serial_number from file's    #
#          name.                                                #
#################################################################
def getSerialNumberFromMaskIR( string ):
    back_number = string.replace("mask_ir_", "")
    serial_number = int(back_number.replace(".png", ""))
    return serial_number

#################################################################
# Name   : showSequenceUseList()                                #
# Input  : folder's path                                        #
# Output : None                                                 #
# Desc   : This func is just show image.                        #
#                                                               #
#################################################################
def showSequenceUseList( sequence_list ):
    print( sequence_list )
    for files_name in sorted( os.listdir( sequence_list )):
        if files_name.startswith( "mask_ir_" ):
            mask_ir_path = os.path.join( sequence_list, files_name )
            img = cv2.imread( mask_ir_path )
            cv2.imshow( "mask_ir", img )
            cv2.waitKey(10)
            
#################################################################
# Name   : removeFilesFromFolder()                              #
# Input  : folder's path                                        #
# Output : None                                                 #
# Desc   : This func is check if folder has file or not, if     #
#          file exist then remove it.                           #
#################################################################
def removeFilesFromFolder( dir_str ):
    for the_file in os.listdir( dir_str ):
        file_path = os.path.join( dir_str , the_file )
        try:
            if os.path.isfile( file_path ):
                os.unlink( file_path )
        except Exception as e:
            print(e)

#################################################################
# Name   : samplingAndSaveFile()                                #
# Input  : folder's path                                        #
# Output : None                                                 #
# Desc   : This func will check the dst folder first and        #
#          copy the sampling data from src folder to dst folder.#
#################################################################
def samplingAndSaveFile( src_dirs, index, sheet1 ):
    count = 0
    
    dst_dirs = src_dirs.replace( MyPath, '')
    dst_dirs = dst_dirs.split('/')

    print( dst_dirs)
    time_str = dst_dirs[ 0 ]
    name_str = dst_dirs[ 1 ]
    scene_str = dst_dirs[ 2 ]
    gesture_str = dst_dirs[ 3 ]
    folder_name = 'hand_' + time_str + '_' + name_str + '_' + scene_str + '_' + gesture_str

    dst_dirs = os.path.join( Save_folder, folder_name )
    if not os.path.exists( dst_dirs ):
        os.makedirs( dst_dirs )
    


    print( 'sampling...' )
#    dst_dirs = src_dirs.replace( "hand_dataset", Save_folder )
#    # we have 1 camera intrinsics file and many set of pitcure ( a set with 4 pic)
#    file_num = (fileCounter( dst_dirs ) - 1) / 4
#    if file_num != 0:
#        removeFilesFromFolder( dst_dirs )

    cam_intrinsics_src = os.path.join( src_dirs, "camera_intrinsics.json" )
    cam_intrinsics_dst = os.path.join( dst_dirs, "camera_intrinsics.json" )
    cam_extrinsics_src = os.path.join( src_dirs, "camera_extrinsics.json" )
    cam_extrinsics_dst = os.path.join( dst_dirs, "camera_extrinsics.json" )
    shutil.copy( cam_intrinsics_src, cam_intrinsics_dst )
    shutil.copy( cam_extrinsics_src, cam_extrinsics_dst )

    with open(cam_extrinsics_src) as camera_extrinsics:
        extrinsics = json.loads( camera_extrinsics.read() )
    with open(cam_intrinsics_src, 'r') as camera_intrinsics:
        intrinsics = json.loads( camera_intrinsics.read() )

    for files_name in sorted( os.listdir( src_dirs )):
        if files_name.startswith( "mask_ir_" ):

            serial_number = getSerialNumberFromMaskIR( files_name )

            if serial_number % sampling_gap == 0:

                count = count+1
                serial_number_pad0 = str(serial_number).zfill(6)

                depth_name        = "depth_" + serial_number_pad0 + ".pgm"
                nocutoff_depth_name = "nocutoff_depth_" + serial_number_pad0 + ".pgm"
                ir_name           = "ir_" + serial_number_pad0 + ".png"
                mask_ir_name      = "mask_ir_" + serial_number_pad0 + ".png"
                rgb_name          = "rgb_" + serial_number_pad0 + ".png"
                nofill_rgb_name          = "nofill_rgb_" + serial_number_pad0 + ".png"

                mask_ir_src        = os.path.join( src_dirs, mask_ir_name )
                mask_ir_dst        = os.path.join( dst_dirs, mask_ir_name )  # join( dst_dir, mask_ir_name )
                ir_src             = os.path.join( src_dirs, ir_name )
                ir_dst             = os.path.join( dst_dirs, ir_name )
                depth_src          = os.path.join( src_dirs, depth_name )
                depth_dst          = os.path.join( dst_dirs, depth_name )
                nocutoff_depth_src = os.path.join( src_dirs, nocutoff_depth_name )
                nocutoff_depth_dst = os.path.join( dst_dirs, nocutoff_depth_name )
                rgb_src            = os.path.join( src_dirs, rgb_name)
                rgb_dst            = os.path.join( dst_dirs, rgb_name)
                nofill_rgb_dst     = os.path.join( dst_dirs, nofill_rgb_name)

                #generate align rgb
                depth = cv2.imread( depth_src, -1 )
                color = cv2.imread( rgb_src, -1 )
                ir = cv2.imread( ir_src, -1 )
                print( depth_src )
		
                depth_3c = np.zeros_like(color)
                depth_3c[:,:,0] = depth.copy()/900 * 255
                depth_3c[:,:,1] = depth.copy()/900 * 255
                depth_3c[:,:,2] = depth.copy()/900 * 255
                ir_3c = np.zeros_like(color)
                ir_3c[:,:,0] = ir.copy()
                ir_3c[:,:,1] = ir.copy()
                ir_3c[:,:,2] = ir.copy()
                backtorgb = cv2.applyColorMap(ir_3c, cv2.COLORMAP_HSV)

                rgb_align = imageRegistration( intrinsics, extrinsics, depth, color, True )
                nofill_rgb_align = imageRegistration( intrinsics, extrinsics, depth, color, False )

                show_image = cv2.addWeighted( rgb_align, 0.5, backtorgb, 0.5, 0 )
                #cv2.imshow( "backtorgb", backtorgb )
                #cv2.imshow( "depth", depth_3c )
                #cv2.imshow( "show_image", show_image )
                #cv2.imshow( "rgb_align", rgb_align )
                #cv2.waitKey(0)
                
                cv2.imwrite( rgb_dst, rgb_align )
                cv2.imwrite( nofill_rgb_dst, nofill_rgb_align )

                shutil.copy( mask_ir_src, mask_ir_dst )
                shutil.copy( ir_src, ir_dst )
                shutil.copy( depth_src, depth_dst )
                shutil.copy( nocutoff_depth_src, nocutoff_depth_dst )
    print( count ) 
    out_name = 'hand_' + time_str + "_" + name_str + "_" + scene_str + "_" + gesture_str
    sheet1.write(index + 1,0,out_name)
    sheet1.write(index + 1,1,count)
    #sheet1.write(index + 1,0,scene_str)
    #sheet1.write(index + 1,1,gesture_str)
    #sheet1.write(index + 1,2,count)
    #sheet1.write(index + 1,3,name_str)
    

def main():

    base_dir_list = []
    print( MyPath )
    print( "Sampling_gap = ", sampling_gap )

    base_dir_list = getBaseDirList( MyPath )
    print( "There are ", len( base_dir_list ), " folders" )

    # New folder
    #for src_dirs in sorted( base_dir_list ):
    #    dst_dirs = src_dirs.replace("hand_dataset", Save_folder)

    #    if not os.path.exists( dst_dirs ):
    #        os.makedirs( dst_dirs )

    # Search files and sampling file then save to dst_dir
    index = 0
    start_index = 0
    end_index = len( base_dir_list ) - 1
    stream_status = STOP 
    if len( base_dir_list ) > 0:
        stream_status = START

    # write to excel
    book = xlwt.Workbook(encoding="utf-8")
    sheet1 = book.add_sheet("LIPS.P1.IR")

    while( stream_status == START ):
        if index > end_index :
            break
        #if index == 0:
        src_dirs = base_dir_list[ index ]


        samplingAndSaveFile( src_dirs, index, sheet1 )
        index = index + 1 #jump to next folder
	
        #if index > end_index :
        #    break

        #if index != 0:
        #    src_dirs = base_dir_list[ index ]
    book.save('data_record.xls')



if __name__ == "__main__":
    main()



