import argparse
import logging
import os

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

from utils.data_loading import BasicDataset
from unet import UNet
from utils.utils import plot_img_and_mask

def predict_img(net,
                full_img,
                device,
                scale_factor=1,
                out_threshold=0.5):
    net.eval()
    img = torch.from_numpy(BasicDataset.preprocess(full_img, scale_factor, is_mask=False))
    img = img.unsqueeze(0)
    img = img.to(device=device, dtype=torch.float32)

    with torch.no_grad():
        output = net(img)

        if net.n_classes > 1:
            probs = F.softmax(output, dim=1)[0]
        else:
            probs = torch.sigmoid(output)[0]

        tf = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((full_img.size[1], full_img.size[0])),
            transforms.ToTensor()
        ])

    #     full_mask = tf(probs.cpu()).squeeze()
    #
    # if net.n_classes == 1:
    #     return (full_mask > out_threshold).numpy()
    # else:
    #     return F.one_hot(full_mask.argmax(dim=0), net.n_classes).permute(2, 0, 1).numpy()

        mask = probs.argmax(0).cpu().numpy()  # 假设`probs`是模型的原始输出
        colored_image = mask_to_image(mask, colors)

    return colored_image

def get_args():
    parser = argparse.ArgumentParser(description='Predict masks from input images')
    parser.add_argument('--model', '-m', default='MODEL.pth', metavar='FILE',
                        help='Specify the file in which the model is stored')
    parser.add_argument('--input', '-i', metavar='INPUT', nargs='+', help='Filenames of input images', required=True)
    parser.add_argument('--output', '-o', metavar='INPUT', nargs='+', help='Filenames of output images')
    parser.add_argument('--viz', '-v', action='store_true',
                        help='Visualize the images as they are processed')
    parser.add_argument('--no-save', '-n', action='store_true', help='Do not save the output masks')
    parser.add_argument('--mask-threshold', '-t', type=float, default=0.5,
                        help='Minimum probability value to consider a mask pixel white')
    parser.add_argument('--scale', '-s', type=float, default=0.5,
                        help='Scale factor for the input images')
    parser.add_argument('--bilinear', action='store_true', default=False, help='Use bilinear upsampling')

    return parser.parse_args()


def get_output_filenames(args):
    def _generate_name(fn):
        split = os.path.splitext(fn)
        return f'{split[0]}_OUT{split[1]}'

    return args.output or list(map(_generate_name, args.input))

def mask_to_image(mask: np.ndarray, colors: list):
    """
    Convert a mask (H x W numpy array) to an RGB image.

    Args:
    - mask (np.ndarray): Array of shape (H, W) where each element is a class index.
    - colors (list): List of colors where each color is a tuple of (R, G, B).

    Returns:
    - Image: An RGB image where each class is mapped to a specific color.
    """
    # 创建一个空的RGB图像，初始颜色为黑色。
    # mask.shape[:2] 仅获取高度和宽度，忽略可能的通道维度
    colored_mask = np.zeros((*mask.shape[:2], 3), dtype=np.uint8)

    for idx, color in enumerate(colors):
        # 为每个类别应用颜色
        colored_mask[mask == idx] = color

    return Image.fromarray(colored_mask)

# 定义颜色映射
colors = [
    (0, 0, 0),       # 背景
    (255, 128, 255),     # background
    (128, 128, 128),     # building
    (255, 255, 0),     # road
    (0, 0, 255),   # water
    (255, 0, 0),   # barren
    (0, 128, 0),   # forest
    (0, 255, 0)  # agriculture
]

# 假设`mask`是模型预测结果，是一个形状为(H, W)的numpy数组，
# 其中每个元素的值是对应像素点的类别索引。
# 使用mask_to_image函数将其转换为彩色图像
# colored_image = mask_to_image(mask, colors)

# 如果从多通道掩码（每个类别一个通道）开始，
# 首先使用argmax获取每个位置的类别索引：
# mask = probs.argmax(0).cpu().numpy()  # 假设`probs`是模型的原始输出
# colored_image = mask_to_image(mask, colors)


if __name__ == '__main__':
    args = get_args()
    in_files = args.input
    out_files = get_output_filenames(args)

    net = UNet(n_channels=3, n_classes=8, bilinear=args.bilinear)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    logging.info(f'Loading model {args.model}')
    logging.info(f'Using device {device}')

    net.to(device=device)
    net.load_state_dict(torch.load(args.model, map_location=device))

    logging.info('Model loaded!')

    for i, filename in enumerate(in_files):
        logging.info(f'\nPredicting image {filename} ...')
        img = Image.open(filename)

        mask = predict_img(net=net,
                           full_img=img,
                           scale_factor=args.scale,
                           out_threshold=args.mask_threshold,
                           device=device)

        if not args.no_save:
            out_filename = out_files[i]
            # result = mask_to_image(mask, colors)
            # result.save(out_filename)
            mask.save(out_filename)
            logging.info(f'Mask saved to {out_filename}')

        if args.viz:
            logging.info(f'Visualizing results for image {filename}, close to continue...')
            plot_img_and_mask(img, mask)
