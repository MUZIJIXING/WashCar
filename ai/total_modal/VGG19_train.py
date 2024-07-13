import os.path
from torch.optim.lr_scheduler import StepLR
import torch
from torchvision.models import vgg19, VGG19_Weights
from loaddata import load_train_data, load_test_data

class TrainVGG19:
    def __init__(self, train_img_dir="data/data/train", test_img_dir="data/data/val", epoch=50, batch_size=64, learning_rate=0.001, step_size=100, gamma=0.1):
        super().__init__()
        print("准备训练....")
        # 模型保存的位置
        self.best_model_file="mode/VGG19_best_model.mod"
        self.last_model_file="mode/VGG19_last_model.mod"
        # 记录当前最高准确率
        self.best_accuracy = 0.0
        # GPU是否可用 True False
        self.CUDA = torch.cuda.is_available()
        # 数据集
        self.tr, self.cls_idx = load_train_data(train_img_dir, batch_size=batch_size)
        self.ts, self.cls_idx = load_test_data(test_img_dir, batch_size=batch_size)
        # 初始化模型结构
        self.net = vgg19(weights=VGG19_Weights.IMAGENET1K_V1)
        # 替换最后的全连接层
        self.net.classifier[6] = torch.nn.Linear(4096, 10)
        if self.CUDA:
            self.net.cuda()  # cpu==>gpu
        if os.path.exists(self.last_model_file):
            print("加载本地模型，继续训练")
            state_dict = torch.load(self.last_model_file)
            self.net.load_state_dict(state_dict)
        else:
            print("从头训练")

        self.lr = learning_rate
        self.epoch = epoch
        self.opt = torch.optim.Adam(self.net.parameters(), lr=self.lr)
        self.scheduler = StepLR(self.opt, step_size=step_size, gamma=gamma)
        self.loss_function = torch.nn.CrossEntropyLoss()
        if self.CUDA:
            self.loss_function = self.loss_function.cuda()

    def train(self):
        print("开始训练")
        for e in range(self.epoch):
            self.net.train()
            loss=0
            for samples, labels in self.tr:
                self.opt.zero_grad()
                if self.CUDA:
                    samples = samples.cuda()
                    labels = labels.cuda()
                y = self.net(samples.view(-1, 3, 224, 224))
                loss = self.loss_function(y, labels)
                loss.backward()
                self.opt.step()
            # 清空缓存
            torch.cuda.empty_cache()
            # 测试
            c_rate = self.validate()
            print(F"轮数：{e},准确率：{c_rate},损失率：{loss}")
            # 如果当前准确率高于之前的最高准确率，则保存模型
            if c_rate > self.best_accuracy:
                self.best_accuracy = c_rate
                # 保存模型
                torch.save(self.net.state_dict(), self.best_model_file)
                print(f'模型更新，当前准确率为{self.best_accuracy}')
            torch.save(self.net.state_dict(), self.last_model_file)
            # 更新学习率
            self.scheduler.step()

    @torch.no_grad()
    def validate(self):
        num_samples = 0
        num_correct = 0
        for samples, labels in self.ts:
            if self.CUDA:
                samples = samples.cuda()
                labels = labels.cuda()
            num_samples += len(samples)
            out = self.net(samples.view(-1, 3, 224, 224))
            out = torch.nn.functional.softmax(out, dim=1)
            y = torch.argmax(out, dim=1)
            num_correct += (y == labels).float().sum()
        return num_correct * 100 / num_samples

if __name__ == "__main__":
    t = TrainVGG19()  # 适当减小批次大小
    t.train()
