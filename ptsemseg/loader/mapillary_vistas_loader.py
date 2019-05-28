import os
import json
import torch
import numpy as np
import scipy.misc as m

from torch.utils import data

from ptsemseg.utils import recursive_glob
from ptsemseg.augmentations import *

class mapillaryVistasLoader(data.Dataset):
    def __init__(self, root, split="training", img_size=(640, 1280), 
                 is_transform=True, augmentations=None):
        self.root = root     
        self.split = split
        self.is_transform = is_transform
        self.augmentations = augmentations
        self.n_classes = 66

        self.img_size = img_size if isinstance(img_size, tuple) else (img_size, img_size)
        self.mean = np.array([80.5423, 91.3162, 81.4312])
        self.files = {}

        self.images_base = os.path.join(self.root, self.split, 'images')
        self.annotations_base = os.path.join(self.root, self.split, 'labels')

        self.files[split] = recursive_glob(rootdir=self.images_base, suffix='.jpg')
        self.number_of_images = len(self.files[split])

        self.class_ids, self.class_names, self.class_colors = self.parse_config()

        self.ignore_id = 250

        if not self.files[split]:
            raise Exception("No files for split=[%s] found in %s" % (split, self.images_base))

        print("Found %d %s images" % (len(self.files[split]), split))

    def parse_config(self):
        with open(os.path.join(self.root, 'config.json')) as config_file:
            config = json.load(config_file)

        labels = config['labels']

        class_names = []
        class_ids = []
        class_colors = []
        print("There are {} labels in the config file".format(len(labels)))
        for label_id, label in enumerate(labels):
            class_names.append(label["readable"])
            class_ids.append(label_id)
            class_colors.append(label["color"])

        return class_names, class_ids, class_colors

    def __len__(self):
        """__len__"""
        return len(self.files[self.split])

    def __getitem__(self, index):
        """__getitem__
        :param index:
        """
        img_path = self.files[self.split][index].rstrip()
        lbl_path = os.path.join(self.annotations_base, os.path.basename(img_path).replace(".jpg", ".png"))

        img = Image.open(img_path)
        lbl = Image.open(lbl_path)
        
        if self.augmentations is not None:
            img, lbl = self.augmentations(img, lbl)

        if self.is_transform:
            img, lbl = self.transform(img, lbl)


        

        return img, lbl
        #return lbl
    
    def getLabel(self, index):
        img_path = self.files[self.split][index].rstrip()
        lbl_path = os.path.join(self.annotations_base, os.path.basename(img_path).replace(".jpg", ".png"))
        lbl = Image.open(lbl_path)
        lbl = torch.from_numpy(np.array(lbl)).long()
        
        return lbl
        




    def transform(self, img, lbl):
        #if self.img_size == ('same', 'same'):
        #    pass
        #else: 
        #    img = img.resize((self.img_size[0], self.img_size[1]), 
        #                      resample=Image.LANCZOS)  # uint8 with RGB mode
        #    lbl = lbl.resize((self.img_size[0], self.img_size[1]))
                
        img = img.resize((self.img_size[0], self.img_size[1]), 
                              resample=Image.LANCZOS)  # uint8 with RGB mode
        lbl = lbl.resize((self.img_size[0], self.img_size[1]))
        
        img = np.array(img).astype(np.float64) / 255.0                                      # IS THIS NORMALISATION OK?
        img = torch.from_numpy(img.transpose(2, 0, 1)).float()  # From HWC to CHW
        lbl = torch.from_numpy(np.array(lbl)).long()
        #lbl[lbl == 65] = self.ignore_id
        
        #lbl[lbl>=4] = self.ignore_id
        return img, lbl
 

    def decode_segmap(self, temp):   # temp is HW np slice
        r = temp.copy() 
        g = temp.copy()
        b = temp.copy()
        for l in range(0, self.n_classes):
            r[temp == l] = self.class_colors[l][0]
            g[temp == l] = self.class_colors[l][1]
            b[temp == l] = self.class_colors[l][2]

        rgb = np.zeros((temp.shape[0], temp.shape[1], 3))   # dummy tensor in np order HWC
        rgb[:, :, 0] = r / 255.0
        rgb[:, :, 1] = g / 255.0
        rgb[:, :, 2] = b / 255.0
        return rgb

if __name__ == '__main__':
    augment = Compose([RandomHorizontallyFlip(), 
                       RandomRotate(6)])

    local_path = '/private/home/meetshah/datasets/seg/vistas/'
    dst = mapillaryVistasLoader(local_path, img_size=(512, 1024), is_transform=True, augmentations=augment)
    bs = 8
    trainloader = data.DataLoader(dst, batch_size=bs, num_workers=4, shuffle=True)
    for i, data in enumerate(trainloader):
        x = dst.decode_segmap(data[1][0].numpy())   # 1 isolates the second element of the tuple (label) and 0 isolates the first batch.
        print("batch :", i)
