import os
import time

import boto3
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from turtle_app.settings import *

from fitting_photo.data.data_loader_test import CreateDataLoader


def run_model(opt, warp_model, gen_model):
    data_loader = CreateDataLoader(opt)
    dataset = data_loader.load_data()

    dataset_size = 1
    start_epoch, epoch_iter = 1, 0
    total_steps = (start_epoch-1) * dataset_size + epoch_iter
    step = 0
    step_per_batch = dataset_size / opt.batchSize
    for epoch in range(1, 2):

        for i, data in enumerate(dataset, start=epoch_iter):
            iter_start_time = time.time()

            real_image = data['image']
            clothes = data['clothes']
            ##edge is extracted from the clothes image with the built-in function in python
            edge = data['edge']
            edge = torch.FloatTensor(
                (edge.detach().numpy() > 0.5).astype(np.int))
            clothes = clothes * edge

            flow_out = warp_model(real_image.cuda(), clothes.cuda())
            warped_cloth, last_flow, = flow_out
            warped_edge = F.grid_sample(edge.cuda(), last_flow.permute(0, 2, 3, 1), align_corners=True,
                                        mode='bilinear', padding_mode='zeros')

            gen_inputs = torch.cat(
                [real_image.cuda(), warped_cloth, warped_edge], 1)
            gen_outputs = gen_model(gen_inputs)
            p_rendered, m_composite = torch.split(gen_outputs, [3, 1], 1)
            p_rendered = torch.tanh(p_rendered)
            m_composite = torch.sigmoid(m_composite)
            m_composite = m_composite * warped_edge
            p_tryon = warped_cloth * m_composite + \
                p_rendered * (1 - m_composite)

            #저장할 위치 + user_id
            s3 = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )

            path = opt.result_path
            photo_name = str(opt.img_url).split('/')[-1].split('.')[0]
            cloth_name = str(opt.cloth_url).split('/')[-1]
            file_name = f'/{photo_name}_{cloth_name}'
            os.makedirs(path, exist_ok=True)
            #sub_path = path + '/PFAFN'
            #os.makedirs(sub_path,exist_ok=True)

            if step % 1 == 0:
                a = real_image.float().cuda()
                b = clothes.cuda()
                c = p_tryon
                combine = torch.cat([a[0], b[0], c[0]], 2).squeeze()

                # cat a + b+c =abc 이렇게 보여줌
                cv_img = (combine.permute(
                    1, 2, 0).detach().cpu().numpy()+1)/2
                # 차원이(3,4,5) 가 주어졌다고 하자 permute(1,2,0)하면 (4,5,3) 이렇게 변한다. 즉 permute뒤에 있는 것은 첫번쨰 텐서 사이즈의 index이다,.
                rgb = (cv_img*255).astype(np.uint8)
                bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

                cv_img_p = (c[0].permute(
                    1, 2, 0).detach().cpu().numpy()+1)/2
                rgb_p = (cv_img_p*255).astype(np.uint8)
                bgr_p = cv2.cvtColor(rgb_p, cv2.COLOR_RGB2BGR)

                cv2.imwrite(path + file_name, bgr_p)
                s3.upload_file(
                    path + file_name, AWS_STORAGE_BUCKET_NAME, 'media/' + path + file_name)

    # path 를 리턴하고 장고 html 에서 src에 그 값을 주면 볼 수 있다.
            step += 1
            if epoch_iter >= dataset_size:
                break
