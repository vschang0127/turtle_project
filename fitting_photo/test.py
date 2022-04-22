import torch.nn as nn

from models.afwm import AFWM
from models.networks import ResUnetGenerator, load_checkpoint
from options.test_options import TestOptions
from run_model import run_model

opt = TestOptions().parse()
user='rolling'
img_url='dataset/test_img/000066_0.jpg'
cloth_url='dataset/test_clothes/003434_1.jpg'
edge_url='dataset/test_edge/003434_1.jpg'
result_path='results/'

opt.img_url=img_url
opt.cloth_url=cloth_url
opt.edge_url=edge_url
opt.result_path=result_path
opt.user=user

# 모델정의
warp_model = AFWM(opt, 3)
warp_model.eval()
warp_model.cuda()
load_checkpoint(warp_model, opt.warp_checkpoint)
gen_model = ResUnetGenerator(7, 4, 5, ngf=64, norm_layer=nn.BatchNorm2d)
gen_model.eval()
gen_model.cuda()
load_checkpoint(gen_model, opt.gen_checkpoint)

class Run_model():
    run_model(opt,warp_model,gen_model)
    






