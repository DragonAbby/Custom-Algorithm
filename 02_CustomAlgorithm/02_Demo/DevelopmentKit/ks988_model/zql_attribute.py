from logger import LOGGER
from model import OnnxModel


class Model(OnnxModel):
    default_args = {
        'img_size': (256, 192)
    }

    def __init__(self, acc_id, name, conf):
        super().__init__(acc_id, name, conf, ['model'])
        self.mean = [123.675, 116.28, 103.53]
        self.std = [58.395, 57.12, 57.375]

    def _load_args(self, args):
        try:
            self.img_size = args.get('img_size', self.default_args['img_size'])
        except:
            LOGGER.exception('_load_args')
            return False
        return True

    def infer(self, data, **kwargs):
        """
        属性识别
        Args:
            data: 图像数据，ndarray类型，RGB格式（BGR格式需转换）
        Returns: infer_result
        """
        infer_result = None
        if self.status:
            try:
                # Do image preprocess
                image = data
                image, _, _ = self._letterbox(image, self.img_size, mean=self.mean, std=self.std, stretch=True)
                outputs = self._onnx_infer('model', image)
                output = outputs[0].reshape(-1)
                obj = {
                    'output': output.tolist()
                }
                infer_result = obj
            except:
                LOGGER.exception('infer')
        return infer_result
