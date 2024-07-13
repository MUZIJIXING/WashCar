import os
import torch
from torchvision.models import densenet121, DenseNet121_Weights
from torchvision import transforms
from PIL import Image

class DenseNetClassifier:
    def __init__(self, model_path, num_classes=10):
        self.model_path = model_path
        self.num_classes = num_classes
        self.CUDA = torch.cuda.is_available()

        self.net = densenet121(weights=DenseNet121_Weights.IMAGENET1K_V1)
        self.net.classifier = torch.nn.Linear(self.net.classifier.in_features, self.num_classes)
        if self.CUDA:
            self.net.cuda()

        if os.path.exists(self.model_path):
            if self.CUDA:
                self.net.load_state_dict(torch.load(self.model_path))
            else:
                self.net.load_state_dict(torch.load(self.model_path, map_location=torch.device('cpu')))
            print("模型加载成功")
        else:
            raise FileNotFoundError("模型文件未找到")

        self.net.eval()

        self.transform = transforms.Compose([
            transforms.Resize(224),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def predict(self, img):
        img = img.convert('RGB')
        img = self.transform(img)
        img = img.unsqueeze(0)  # 添加批次维度

        if self.CUDA:
            img = img.cuda()

        with torch.no_grad():
            outputs = self.net(img)
            _, preds = torch.max(outputs, 1)

        return preds.item()

def classify_image(image):
    image = Image.open(image)
    model_path = r"F:\technology\Summer_training\hw_project2_1\ai\total_modal\DenseNet_last_model.mod"  # 使用最佳模型文件
    predictor = DenseNetClassifier(model_path)
    return predictor.predict(image)

if __name__ == "__main__":
    test_img_path = '../data/train/bus/0aa8c6bece0ab6ceda43e920634e4fa2.jpg'  # 替换为实际的测试图像路径
    image = Image.open(test_img_path)
    prediction = classify_image(image)
    print(f"预测结果：{prediction}")
