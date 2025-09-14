import logging
import os
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import transforms

from deepfake.deepfakeai.utils import DeepfakeDataset
from deepfake.deepfakeai.models.base_model import CNN_ViT_LSTM

logger = logging.getLogger(__name__)    


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor()
])


def train_model(config: dict[str, dict]):
    """
    Main funtion to training the Model
    """
    image_dataset = config["imgdir"] / "train"
    
    models_dir = config["modelsdir"]
    model_name = f"{config['model_name']}.pth"
    model_path = os.path.join(str(models_dir), model_name)
    
    cnn_backbone = config.get("models", {}).get("cnn_backbone", "resnet18")
    vit_backbone = config.get("models", {}).get("vit_backbone", "vit_base_patch16_224")

    train_dataset = DeepfakeDataset(
        root_dir=str(image_dataset), 
        transform=transform
    )
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)

    model = CNN_ViT_LSTM(
        cnn_backbone=cnn_backbone,
        vit_backbone=vit_backbone,
        hidden_dim=256,
        num_classes=2
    ).to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-4)

    for epoch in range(5):
        model.train()
        total_loss = 0
        for imgs, labels in tqdm(train_loader):
            imgs, labels = imgs.to(device), labels.to(device)
            imgs = imgs.unsqueeze(1)   # [B, 1, C, H, W]
            outputs = model(imgs)      # Model should handle batch properly
            loss = criterion(outputs, labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        logger.info(f"Epoch {epoch+1}, Loss: {total_loss/len(train_loader)}")

    # Save the model weights
    torch.save(model.state_dict(), model_path)
