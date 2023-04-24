import argparse
import numpy as np
import cv2
import h5py
from tqdm import tqdm
import os 
def main():
    args = read_args()
    create_and_save_video(args)

def read_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-h5", "--hdf", required=True)
    arg_parser.add_argument("-o", "--out", required=False)
    args = arg_parser.parse_args()
    return args

def create_and_save_video(args):
    nbr_imgs_total = 0
    fps = 30 
    out_file = args.hdf.replace('.h5', '.avi')
    
    with h5py.File(args.hdf) as f:
        key_0 = list(f['data_raw'].keys())[0]
        _, h, w, c = f['data_raw'][key_0].shape
        writer = cv2.VideoWriter(out_file, cv2.VideoWriter_fourcc(*'PIM1'), 30, (w, h))
        for images in tqdm(f['data_raw'].values()):

            for idx, img in enumerate(tqdm(images)):
                idx_file = nbr_imgs_total + idx
                img_out_file = args.hdf.replace('.h5', f'{idx_file}_.png')
                writer.write(img)
                cv2.imwrite(img_out_file, img)
            nbr_imgs_total += images.shape[0]
        writer.release()

if __name__ == '__main__':
    main()

    