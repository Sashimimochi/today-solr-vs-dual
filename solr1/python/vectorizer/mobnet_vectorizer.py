import timm
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
import torch

class Vectorizer:
    def __init__(self) -> None:
        self.model = timm.create_model('mobilenetv3_large_100', pretrained=True)
        self.model.eval()
        config = resolve_data_config({}, model=self.model)
        self.transform = create_transform(**config)

    def img_vectorize(self, img):
        tensor = self.transform(img.convert('RGB')).unsqueeze(0) # transform and add batch dimension
        with torch.no_grad():
            out = self.model(tensor)
        return out
