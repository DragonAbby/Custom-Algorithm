import os
import sys

import cv2
import numpy as np
import onnxruntime as ort

from logger import LOGGER
from utils.file_utils import abspath

CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(CURRENT_PATH)


class OnnxModel:
    def __init__(self, acc_id, name, conf, sub_model_names):
        self.acc_id = acc_id
        self.name = name
        self.sub_model_names = sub_model_names
        self.sub_models = {}
        self.status = False
        self.__init(conf)

    def __init(self, conf):
        """
        初始化，无需重写
        Args:
            conf: 模型配置
        Returns: True or False
        """
        try:
            if self._load_model(conf['path']):
                if self._load_args(conf.get('args')):
                    self.status = True
                else:
                    LOGGER.error('Load args failed')
            else:
                LOGGER.error('Load model failed')
        except:
            LOGGER.exception('__init')
            self.release()
        finally:
            LOGGER.info('Model({}) inited'.format(self.name))
        return self.status

    def release(self):
        """
        释放模型，无需重写
        Returns: True or False
        """
        try:
            self.status = False
            self.sub_models.clear()
            LOGGER.info('Model({}) released'.format(self.name))
            return True
        except:
            LOGGER.exception('release')
            return False

    def _onnx_infer(self, sub_model_name, data):
        """
        onnx推理，无需重写
        Args:
            sub_model_name: 模型
            data: 推理数据
        Returns: infer_result
        """
        sub_model = self.sub_models.get(sub_model_name)
        if sub_model is not None:
            input_name = sub_model['input_names'][0]
            output_names = sub_model['output_names']
            output = sub_model['session'].run(output_names, {input_name: data})
            return output
        return None

    def _load_model(self, path):
        """
        加载模型，按需重写
        Args:
            path: 模型路径
        Returns: True or False
        """
        try:
            for sub_model_name in self.sub_model_names:
                sub_model_path = abspath(path, sub_model_name)
                session = ort.InferenceSession(
                    sub_model_path,
                    providers=[("CUDAExecutionProvider", {"device_id": self.acc_id})]
                )
                input_names = [input.name for input in session.get_inputs()]
                output_names = [output.name for output in session.get_outputs()]
                self.sub_models[sub_model_name] = {
                    # Store
                    'session': session,
                    'input_names': input_names,
                    'output_names': output_names
                }
        except:
            LOGGER.exception('_load_model')
            return False
        return True

    def _load_args(self, args):
        """
        加载参数，按需重写
        Args:
            args: 模型参数
        Returns: True or False
        """
        return True

    def infer(self, data, **kwargs):
        """
        推理，需要重写
        Args:
            data: 推理数据
        Returns: infer_result
        """
        return None

    ######################################################工具函数######################################################
    @staticmethod
    def _xywh2xyxy(x):
        """
        xywh转xyxy，按需重写
        Args:
            x: xywh
        Returns: xyxy
        """
        y = np.copy(x)
        # top left x
        y[:, 0] = x[:, 0] - x[:, 2] / 2
        # top left y
        y[:, 1] = x[:, 1] - x[:, 3] / 2
        # bottom right x
        y[:, 2] = x[:, 0] + x[:, 2] / 2
        # bottom right y
        y[:, 3] = x[:, 1] + x[:, 3] / 2
        return y

    @staticmethod
    def _letterbox(image, size=(640, 640), color=(114, 114, 114), mean=[0, 0, 0], std=[255, 255, 255], stretch=False):
        """
        生成letterbox，按需重写
        Args:
            image: 图像数据
            size: letterbox尺寸
            color: letterbox颜色
            stretch: 是否拉伸
        Returns: image, dw, dh
        """
        shape = image.shape[:2]
        if stretch:
            dw, dh = 0.0, 0.0
            pad_size = (size[1], size[0])
            if shape[::-1] != pad_size:
                image = cv2.resize(image, pad_size, interpolation=cv2.INTER_LINEAR)
        else:
            ratio = min(size[0] / shape[1], size[1] / shape[0])
            pad_size = int(round(shape[1] * ratio)), int(round(shape[0] * ratio))
            if shape[::-1] != pad_size:
                image = cv2.resize(image, pad_size, interpolation=cv2.INTER_LINEAR)
            dw, dh = (size[0] - pad_size[0]) / 2, (size[1] - pad_size[1]) / 2
            top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
            left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
            image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
        image = image.astype(np.float32)
        # Normalize to [0,1]
        image -= mean
        image /= std
        # HWC to CHW format:
        image = np.transpose(image, [2, 0, 1])
        # CHW to NCHW format
        image = np.expand_dims(image, axis=0)
        # Convert the image to row-major order, also known as "C order":
        image = np.ascontiguousarray(image).astype(np.float32)
        return image, dw, dh

    def _nms_boxes(self, boxes, scores):
        """
        Suppress non-maximal boxes.
        按需重写
        # Args:
            boxes: ndarray, boxes of objects.
            scores: ndarray, scores of objects.
        # Returns:
            keep: ndarray, index of effective boxes.
        """
        x = boxes[:, 0]
        y = boxes[:, 1]
        w = boxes[:, 2] - boxes[:, 0]
        h = boxes[:, 3] - boxes[:, 1]
        areas = w * h
        order = scores.argsort()[::-1]
        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)
            xx1 = np.maximum(x[i], x[order[1:]])
            yy1 = np.maximum(y[i], y[order[1:]])
            xx2 = np.minimum(x[i] + w[i], x[order[1:]] + w[order[1:]])
            yy2 = np.minimum(y[i] + h[i], y[order[1:]] + h[order[1:]])
            w1 = np.maximum(0.0, xx2 - xx1 + 0.00001)
            h1 = np.maximum(0.0, yy2 - yy1 + 0.00001)
            inter = w1 * h1
            ovr = inter / (areas[i] + areas[order[1:]] - inter)
            inds = np.where(ovr <= self.nms_thres)[0]
            order = order[inds + 1]
        return np.array(keep)
