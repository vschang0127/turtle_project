import os.path
from .base_dataset import BaseDataset, get_params, get_transform
from PIL import Image
import linecache

class AlignedDataset(BaseDataset):
    def initialize(self, opt):
        self.opt = opt
        self.root = opt.dataroot

        self.fine_height=256
        self.fine_width=192

        self.img_people = Image.open(opt.img_url).convert('RGB')
        self.img_cloth = Image.open(opt.cloth_url).convert('RGB')
        self.img_edge = Image.open(opt.edge_url).convert('L')

    def __getitem__(self, index):        

        #file_path ='demo.txt'
        #im_name, c_name = linecache.getline(file_path, index+1).strip().split()

        #I_path = os.path.join(self.dir_I,im_name)
        I =self.img_people

        params = get_params(self.opt, I.size)
        transform = get_transform(self.opt, params)
        transform_E = get_transform(self.opt, params, method=Image.NEAREST, normalize=False)

        I_tensor = transform(I)

        #C_path = os.path.join(self.dir_C,c_name)
        C = self.img_cloth
        C_tensor = transform(C)

        #E_path = os.path.join(self.dir_E,c_name)
        E = self.img_edge
        E_tensor = transform_E(E)

        input_dict = { 'image': I_tensor,'clothes': C_tensor, 'edge': E_tensor}
        return input_dict

    def __len__(self):
        return 1

    def name(self):
        return 'AlignedDataset'
