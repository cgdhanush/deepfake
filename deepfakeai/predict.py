import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import cv2
import os
from deepfake.deepfakeai.models.base_model import CNN_ViT_LSTM

class Predictor:
    def __init__(self, config: dict):
        self.device = ("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load model
        models_dir = config["modelsdir"]
        model_name = f"{config['model_name']}.pth"
        model_path = os.path.join(str(models_dir), model_name)
        
        self.model = CNN_ViT_LSTM().to(self.device)
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        
        # Preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((224,224)),
            transforms.ToTensor()
        ])

    def predict_image(self, image_path):
        """ 
        Predict single image (Real / Fake)
        """
        img = Image.open(image_path).convert("RGB")
        img = self.transform(img).unsqueeze(0).unsqueeze(1).to(self.device)  # [B, Seq, C, H, W]

        with torch.no_grad():
            output = self.model(img)
            probs = F.softmax(output, dim=1)
            pred = torch.argmax(probs, dim=1).item()

        return {"label": "Real" if pred == 0 else "Fake", "confidence": probs[0][pred].item()}

    def predict_video(self, video_path, frame_skip=10, max_frames=20):
        """ 
        Predict video by sampling frames
        """
        cap = cv2.VideoCapture(video_path)
        frames = []
        count = 0
        while cap.isOpened() and len(frames) < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
            if count % frame_skip == 0:
                img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                img = self.transform(img).unsqueeze(0).to(self.device)
                frames.append(img)
            count += 1
        cap.release()

        if not frames:
            return {"label": "Error", "confidence": 0.0}

        frames = torch.cat(frames, dim=0).unsqueeze(0)  # [1, Seq, C, H, W]

        with torch.no_grad():
            output = self.model(frames)
            probs = F.softmax(output, dim=1)
            pred = torch.argmax(probs, dim=1).item()

        return {"label": "Real" if pred == 0 else "Fake", "confidence": probs[0][pred].item()}