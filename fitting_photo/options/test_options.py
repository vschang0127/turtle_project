from .base_options import BaseOptions

class TestOptions(BaseOptions):
    def initialize(self):
        BaseOptions.initialize(self)

        self.parser.add_argument('--warp_checkpoint', type=str, default='checkpoints/PFAFN/warp_model_final.pth', help='load the pretrained model from the specified location')
        self.parser.add_argument('--gen_checkpoint', type=str, default='checkpoints/PFAFN/gen_model_final.pth', help='load the pretrained model from the specified location')
        self.parser.add_argument('--phase', type=str, default='test', help='train, val, test, etc')
        self.parser.add_argument('--img_url',type=str,default='')
        self.parser.add_argument('--cloth_url',type=str,default='')
        self.parser.add_argument('--edge_url',type=str,default='')
        self.parser.add_argument('--result_path',type=str,default='')
        self.parser.add_argument('--user',type=str,default='')

        self.isTrain = False
