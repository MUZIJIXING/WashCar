import os
from torch.optim.lr_scheduler import StepLR
import torch
from torchvision.models import squeezenet1_0, SqueezeNet1_0_Weights
from loaddata import load_train_data, load_test_data
from torch.utils.tensorboard import SummaryWriter

class TrainSqueezeNet:
    def __init__(self, train_img_dir="data/data/train", test_img_dir="data/data/val", epoch=50, batch_size=64, learning_rate=0.001, step_size=100, gamma=0.1):
        super().__init__()
        print("准备训练....")
        self.best_model_file = "mode/SqueezeNet_best_model.mod"
        self.last_model_file = "mode/SqueezeNet_last_model.mod"
        self.best_accuracy = 0.0
        self.CUDA = torch.cuda.is_available()
        self.tr, self.cls_idx = load_train_data(train_img_dir, batch_size=batch_size)
        self.ts, self.cls_idx = load_test_data(test_img_dir, batch_size=batch_size)
        self.net = squeezenet1_0(weights=SqueezeNet1_0_Weights.IMAGENET1K_V1)
        self.net.classifier[1] = torch.nn.Conv2d(512, 10, kernel_size=(1, 1), stride=(1, 1))
        self.net.num_classes = 10
        
        if self.CUDA:
            self.net.cuda()
        
        if os.path.exists(self.last_model_file):
            try:
                print("加载本地模型，继续训练")
                state_dict = torch.load(self.last_model_file)
                self.net.load_state_dict(state_dict)
            except Exception as e:
                print(f"加载模型失败：{e}")
                print("从头开始训练")
        else:
            print("从头开始训练")

        self.lr = learning_rate
        self.epoch = epoch
        self.opt = torch.optim.Adam(self.net.parameters(), lr=self.lr)
        self.scheduler = StepLR(self.opt, step_size=step_size, gamma=gamma)
        self.loss_function = torch.nn.CrossEntropyLoss()
        
        if self.CUDA:
            self.loss_function = self.loss_function.cuda()

        self.writer = SummaryWriter(log_dir='logs')

    def train(self):
        print("开始训练")
        for e in range(self.epoch):
            self.net.train()
            epoch_loss = 0
            for samples, labels in self.tr:
                self.opt.zero_grad()
                if self.CUDA:
                    samples = samples.cuda()
                    labels = labels.cuda()
                outputs = self.net(samples)
                loss = self.loss_function(outputs, labels)
                loss.backward()
                self.opt.step()
                epoch_loss += loss.item()
            
            torch.cuda.empty_cache()
            c_rate = self.validate()
            print(f"轮数：{e}, 准确率：{c_rate:.2f}%, 损失：{epoch_loss:.4f}")
            self.writer.add_scalar('Loss/train', epoch_loss, e)
            self.writer.add_scalar('Accuracy/train', c_rate, e)
            
            if c_rate > self.best_accuracy:
                self.best_accuracy = c_rate
                torch.save(self.net.state_dict(), self.best_model_file)
                print(f'模型更新，当前准确率为 {self.best_accuracy:.2f}%')
            torch.save(self.net.state_dict(), self.last_model_file)
            self.scheduler.step()
        
        self.writer.close()

    @torch.no_grad()
    def validate(self):
        self.net.eval()
        num_samples = 0
        num_correct = 0
        for samples, labels in self.ts:
            if self.CUDA:
                samples = samples.cuda()
                labels = labels.cuda()
            outputs = self.net(samples)
            _, preds = torch.max(outputs, 1)
            num_correct += (preds == labels).sum().item()
            num_samples += labels.size(0)
        
        accuracy = 100.0 * num_correct / num_samples
        return accuracy

if __name__ == "__main__":
    t = TrainSqueezeNet()  # 适当减小批次大小
    t.train()
