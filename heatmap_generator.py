"""
Heatmap Generator for YoloE
Generates GradCAM heatmaps to visualize what the model "looks at" when making detections.
"""

import warnings
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')

import torch
import cv2
import os
import traceback
import numpy as np
from PIL import Image
from tqdm import trange
from ultralytics import YOLO
from pytorch_grad_cam import GradCAMPlusPlus, GradCAM, XGradCAM, EigenCAM, HiResCAM, LayerCAM, RandomCAM, EigenGradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image, scale_cam_image
from pytorch_grad_cam.activations_and_gradients import ActivationsAndGradients


def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    """Resize and pad image while meeting stride-multiple constraints"""
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return im, ratio, (dw, dh)


class YoloTarget(torch.nn.Module):
    """Target layer for GradCAM computation
    
    This target function focuses GradCAM on areas with high detection confidence,
    producing "hot" (red/yellow) areas where objects are detected, rather than
    weak, diffuse gradients that appear as "cold" (blue) areas everywhere.
    """
    
    def __init__(self, output_type, conf, ratio):
        super().__init__()
        self.output_type = output_type
        self.conf = conf
        self.ratio = ratio

    def forward(self, data):
        """
        Compute target for gradient backpropagation.
        
        For YOLO models, we want to focus on high-confidence detections, not all outputs.
        This is achieved by using top-k values instead of sum(), which creates
        stronger, more focused gradients that produce visible "hot" areas in the heatmap.
        
        Args:
            data: Model output tensor(s)
            
        Returns:
            Scalar tensor for gradient computation
        """
        if isinstance(data, (list, tuple)):
            data = data[0] if len(data) > 0 else data
        
        if torch.is_tensor(data):
            # Use top-k sum to focus on strong detections
            # Take top 1% of activations or at least 50 values
            k = max(50, int(data.numel() * 0.01))
            k = min(k, data.numel())
            
            if data.numel() > 0:
                top_values = torch.topk(data.flatten(), k=k).values
                return top_values.sum()
            else:
                return torch.tensor(0.0, device=data.device)
        
        return torch.tensor(0.0)


class YoloEHeatmapGenerator:
    """Generates GradCAM heatmaps for YoloE models"""
    
    def __init__(self, weight, device='cpu', method='HiResCAM', layer=None, 
                 backward_type='class', conf_threshold=0.2, ratio=0.02, 
                 show_box=False, renormalize=True):
        """
        Initialize the heatmap generator.
        
        Args:
            weight: Path to model weights (.pt file)
            device: Device to run on ('cpu' or 'cuda:0')
            method: GradCAM method to use (HiResCAM, GradCAM, etc.)
            layer: List of layer indices to target (default: [10, 12, 14, 16, 18])
            backward_type: Type of backward pass ('class', 'box', or 'all')
            conf_threshold: Confidence threshold for detections
            ratio: Ratio for processing detections
            show_box: Whether to draw bounding boxes on heatmap
            renormalize: Whether to renormalize CAM in bounding boxes
        """
        if layer is None:
            layer = [10, 12, 14, 16, 18]
            
        self.device = torch.device(device)
        self.conf_threshold = conf_threshold
        self.show_box = show_box
        self.renormalize = renormalize
        
        # Load model using YOLO API
        print(f"[INFO] Loading model from {weight}")
        self.yolo_model = YOLO(weight)
        
        # Access the underlying PyTorch model
        self.model = self.yolo_model.model
        self.model = self.model.to(self.device)
        
        # Enable gradients
        for p in self.model.parameters():
            p.requires_grad_(True)
        self.model.eval()
        
        # Get model names
        self.model_names = self.yolo_model.names
        
        # Setup GradCAM
        self.target = YoloTarget(backward_type, conf_threshold, ratio)
        
        # Get target layers - handle different model structures
        try:
            target_layers = [self.model.model[l] for l in layer]
        except (AttributeError, IndexError, TypeError):
            # Fallback to using the model directly if layer access fails
            print(f"[WARN] Could not access layers {layer}, using model output layers")
            target_layers = [self.model]
        
        # Initialize GradCAM method
        self.method = eval(method)(self.model, target_layers)
        self.method.activations_and_grads = ActivationsAndGradients(self.model, target_layers, None)
        
        # Random colors for boxes
        self.colors = np.random.uniform(0, 255, size=(len(self.model_names), 3)).astype(int)
        
        print(f"[INFO] Heatmap generator initialized")

    def draw_detections(self, box, color, name, img):
        """Draw detection boxes on image"""
        xmin, ymin, xmax, ymax = list(map(int, list(box)))
        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), tuple(int(x) for x in color), 2)
        cv2.putText(img, str(name), (xmin, ymin - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, 
                    tuple(int(x) for x in color), 2, lineType=cv2.LINE_AA)
        return img

    def renormalize_cam_in_bounding_boxes(self, boxes, image_float_np, grayscale_cam):
        """Normalize the CAM to be in the range [0, 1] inside every bounding boxes, 
        and zero outside of the bounding boxes."""
        renormalized_cam = np.zeros(grayscale_cam.shape, dtype=np.float32)
        for x1, y1, x2, y2 in boxes:
            x1, y1 = max(x1, 0), max(y1, 0)
            x2, y2 = min(grayscale_cam.shape[1] - 1, x2), min(grayscale_cam.shape[0] - 1, y2)
            renormalized_cam[y1:y2, x1:x2] = scale_cam_image(grayscale_cam[y1:y2, x1:x2].copy())
        renormalized_cam = scale_cam_image(renormalized_cam)
        eigencam_image_renormalized = show_cam_on_image(image_float_np, renormalized_cam, use_rgb=True)
        return eigencam_image_renormalized

    def generate(self, img_array, save_path):
        """
        Generate heatmap from an image array.
        
        Args:
            img_array: Input image as numpy array (BGR format from cv2)
            save_path: Path to save the heatmap image
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Process image
            img = letterbox(img_array)[0]
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_float = np.float32(img) / 255.0
            tensor = torch.from_numpy(np.transpose(img_float, axes=[2, 0, 1])).unsqueeze(0).to(self.device)
            tensor.requires_grad_(True)

            # Generate GradCAM
            try:
                grayscale_cam = self.method(tensor, [self.target])
                grayscale_cam = grayscale_cam[0, :]
            except Exception as e:
                print(f"[WARN] GradCAM generation failed: {e}, using simple approach")
                traceback.print_exc()
                # Fallback: create a uniform heatmap that will be filled by detections
                # Using zeros so that renormalization will highlight detected regions
                grayscale_cam = np.zeros(img_float.shape[:2], dtype=np.float32)
            
            cam_image = show_cam_on_image(img_float, grayscale_cam, use_rgb=True)

            # Get predictions using YOLO predict
            results = self.yolo_model.predict(
                source=img_array,
                conf=self.conf_threshold,
                verbose=False,
                show=False
            )
            
            # Process results
            if results and len(results) > 0:
                result = results[0]
                boxes = result.boxes
                
                if boxes is not None and len(boxes) > 0:
                    boxes_xyxy = boxes.xyxy.cpu().numpy().astype(np.int32)
                    
                    # Renormalize if requested
                    if self.renormalize and len(boxes_xyxy) > 0:
                        cam_image = self.renormalize_cam_in_bounding_boxes(
                            boxes_xyxy, 
                            img_float, 
                            grayscale_cam
                        )
                    
                    # Draw boxes if requested
                    if self.show_box:
                        for i, box_xyxy in enumerate(boxes_xyxy):
                            cls_id = int(boxes.cls[i])
                            conf = float(boxes.conf[i])
                            label = f'{self.model_names[cls_id]} {conf:.2f}'
                            color = self.colors[cls_id % len(self.colors)]
                            cam_image = self.draw_detections(box_xyxy, color, label, cam_image)

            # Save image
            cam_image = Image.fromarray(cam_image)
            cam_image.save(save_path)
            print(f"[INFO] Heatmap saved to {save_path}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to generate heatmap: {e}")
            import traceback
            traceback.print_exc()
            return False


def get_default_params():
    """Get default parameters for heatmap generation"""
    return {
        'device': 'cpu',
        'method': 'HiResCAM',
        'layer': [10, 12, 14, 16, 18],
        'backward_type': 'class',
        'conf_threshold': 0.2,
        'ratio': 0.02,
        'show_box': False,
        'renormalize': True
    }
