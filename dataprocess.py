from PIL import Image
import os
from pathlib import Path

def crop_to_patches(imgs_dir, masks_dir, output_img_dir, output_mask_dir, patch_size=(500, 500), img_format='tif', mask_format='tif', mask_suffix='_mask'):
    imgs_dir = Path(imgs_dir)
    masks_dir = Path(masks_dir)
    output_img_dir = Path(output_img_dir)
    output_mask_dir = Path(output_mask_dir)
    output_img_dir.mkdir(parents=True, exist_ok=True)
    output_mask_dir.mkdir(parents=True, exist_ok=True)

    for img_path in imgs_dir.glob(f'*.{img_format}'):
        mask_path = masks_dir / f'{img_path.stem}{mask_suffix}.{mask_format}'

        if not mask_path.exists():
            print(f"Warning: Mask not found for image {img_path.stem}{mask_suffix}.{mask_format}")
            continue

        img = Image.open(img_path)
        mask = Image.open(mask_path)

        for i in range(0, img.height, patch_size[1]):
            for j in range(0, img.width, patch_size[0]):
                box = (j, i, j + patch_size[0], i + patch_size[1])
                img_patch = img.crop(box)
                mask_patch = mask.crop(box)

                patch_name = f'{img_path.stem}_{i}_{j}'
                img_patch.save(output_img_dir / f'{patch_name}.{img_format}')
                mask_patch.save(output_mask_dir / f'{patch_name}{mask_suffix}.{mask_format}')


"""
参数:
- imgs_dir: 原始大图像的目录路径。
- masks_dir: 对应掩码的目录路径。
- output_img_dir: 保存小图像块的目录路径。
- output_mask_dir: 保存小掩码块的目录路径。
- patch_size: 裁剪出的小图像块的尺寸，格式为(width, height)。
- img_format: 图像文件的格式。
- mask_format: 掩码文件的格式。
- mask_suffix: 掩码文件名后缀，用于从图像文件名推导掩码文件名。
"""
imgs_dir = './data/imgs'  # 原始图像所在目录
masks_dir = './data/masks'  # 对应掩码所在目录
output_img_dir = './data2/imgs'  # 保存裁剪后图像的目录
output_mask_dir = './data2/masks'  # 保存裁剪后掩码的目录
crop_to_patches(imgs_dir, masks_dir, output_img_dir, output_mask_dir, patch_size=(500, 500), img_format='tif', mask_format='tif', mask_suffix='_mask')
