import cv2
import numpy as np
from torchvision.datasets import ImageFolder
from torchvision import transforms
from torch.utils.data import DataLoader
from PIL import Image


class ConvertToRGB(object):
    def __call__(self, img):
        if img.mode != "RGB":
            img = img.convert("RGB")
        return img


def opencv_loader(path):
    try:
        # print(f"正在加载图像: {path}")
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"无法加载图像: {path}")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
    except Exception as e:
        # print(f"错误加载图像 {path}: {e}")
        # 返回一个空白图像（或其他合适的默认值）以跳过此图像
        return np.zeros((224, 224, 3), dtype=np.uint8)


def load_train_data(train_img_dir, batch_size=128):
    transform_train = transforms.Compose([
        transforms.ToPILImage(),  # 转换为PIL图像以便使用torchvision的变换
        ConvertToRGB(),
        transforms.RandomResizedCrop((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.56719673, 0.5293289, 0.48351972], std=[0.20874391, 0.21455203, 0.22451781])
    ])

    # 创建ImageFolder数据集，使用自定义加载器
    train_datasets = ImageFolder(train_img_dir, transform=transform_train, loader=opencv_loader)
    # 创建DataLoader
    train_loader = DataLoader(dataset=train_datasets, shuffle=True, batch_size=batch_size)
    return train_loader, train_datasets.classes


def load_test_data(test_img_dir, batch_size=128):
    transform_test = transforms.Compose([
        transforms.ToPILImage(),  # 转换为PIL图像以便使用torchvision的变换
        ConvertToRGB(),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.56719673, 0.5293289, 0.48351972], std=[0.20874391, 0.21455203, 0.22451781])
    ])

    # 加载图像数据集，使用自定义加载器
    test_datasets = ImageFolder(test_img_dir, transform=transform_test, loader=opencv_loader)
    # 创建DataLoader
    test_loader = DataLoader(dataset=test_datasets, shuffle=False, batch_size=batch_size)
    return test_loader, test_datasets.classes
