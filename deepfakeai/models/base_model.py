import torch
import torch.nn as nn

from .classifier_model import ClassifierHead
from .cnn_model import CNNExtractor
from .lstm_model import TemporalLSTM
from .vit_model import ViTExtractor


class CNN_ViT_LSTM(nn.Module):
    """
    A hybrid deep learning model combining CNN, Vision Transformer (ViT), and LSTM modules.

    - CNN: Extracts local spatial features.
    - ViT: Captures global spatial relationships.
    - LSTM: Models temporal dynamics across frame sequences.
    - Classifier: Outputs final class predictions.

    Args:
        cnn_backbone (str): Name of the CNN backbone (default: 'resnet18').
        vit_backbone (str): Name of the ViT backbone (default: 'vit_base_patch16_224').
        hidden_dim (int): Hidden dimension size for LSTM (default: 256).
        num_classes (int): Number of output classes (default: 2).

    Input:
        Tensor of shape (batch_size, seq_len, channels, height, width)

    Output:
        Tensor of shape (batch_size, num_classes)
    """
    def __init__(
        self, 
        cnn_backbone='resnet18', 
        vit_backbone='vit_base_patch16_224', 
        hidden_dim=256, 
        num_classes=2
    ):
        super().__init__()
        self.cnn = CNNExtractor(cnn_backbone, out_dim=512)
        self.vit = ViTExtractor(vit_backbone, out_dim=768)

        self.temporal = TemporalLSTM(
            input_dim=512+768, 
            hidden_dim=hidden_dim
        )
        self.classifier = ClassifierHead(
            input_dim=hidden_dim, 
            num_classes=num_classes
        )

    def forward(self, x_seq):
        """
        x_seq: [B, Seq, C, H, W]
        """
        B, S, C, H, W = x_seq.shape
        features = []
        for i in range(S):
            x = x_seq[:, i]          # [B, C, H, W]
            cnn_feat = self.cnn(x)   # [B, 512]
            vit_feat = self.vit(x)   # [B, 768]
            feat = torch.cat((cnn_feat, vit_feat), dim=1)  # [B, 1280]
            features.append(feat.unsqueeze(1))

        features = torch.cat(features, dim=1)  # [B, Seq, 1280]
        temporal_out = self.temporal(features) # [B, hidden_dim]
        return self.classifier(temporal_out)   # [B, num_classes]
