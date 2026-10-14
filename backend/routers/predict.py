# routers/predict.py
# FastAPI prediction routes for ESP32-CAM -> EfficientNet-B0 (4 classes).
# - POST /predict/bytes?device_id=coop1[&ts=ISO8601]   Content-Type: image/jpeg
# - POST /predict/image   (multipart form upload "file")
# - GET  /predict/last
# - GET  /predict/history?device_id=...&n=...
# - GET  /predict/labels
# - GET  /predict/health

# # routers/predict.py
# # FastAPI router for poultry disease prediction (4 classes) with ESP32-CAM support.
# # Endpoints:
# #   - POST /predict/bytes   (raw JPEG bytes; Content-Type: image/jpeg)
# #   - POST /predict/image   (multipart form upload "file")
# #
# # Assumes the .pth checkpoint is in the SAME folder as this file.

# from fastapi import APIRouter, UploadFile, File, HTTPException, Request
# from pydantic import BaseModel
# from typing import List
# import io

# import torch
# import torch.nn as nn
# from PIL import Image
# from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

# route = APIRouter(prefix="/predict", tags=["prediction"])

# # ====== Config: filenames live next to your backend files ======
# CKPT_PATH = "poultry_efficientnet_b0_best_30ep.pth"

# # Hardcoded 4 labels (ORDER must match your training)
# CLASS_NAMES = ["COCCI", "HEALTHY", "NEWCASTLE", "SALMO"]

# # ====== Device ======
# device = torch.device(
#     "xpu" if hasattr(torch, "xpu") and torch.xpu.is_available()
#     else "cuda" if torch.cuda.is_available()
#     else "cpu"
# )

# # ====== Preprocess (RGB, same as your training/eval) ======
# weights = EfficientNet_B0_Weights.DEFAULT
# preprocess = weights.transforms(antialias=True)

# # ====== Build & load model (strict 4-class head) ======
# def build_model() -> nn.Module:
#     model = efficientnet_b0(weights=None)
#     in_features = model.classifier[-1].in_features
#     model.classifier[-1] = nn.Linear(in_features, len(CLASS_NAMES), bias=True)

#     raw = torch.load(CKPT_PATH, map_location="cpu")
#     state_dict = raw.get("state_dict", raw) if isinstance(raw, dict) else raw
#     # Remove DataParallel "module." if present
#     if any(k.startswith("module.") for k in state_dict.keys()):
#         state_dict = {k.replace("module.", "", 1): v for k, v in state_dict.items()}

#     # Strict ensures your checkpoint is truly 4-class
#     model.load_state_dict(state_dict, strict=True)
#     model.to(device).eval()
#     torch.set_grad_enabled(False)
#     return model

# MODEL = build_model()

# # ====== Schema ======
# class PredictResponse(BaseModel):
#     label: str
#     index: int
#     probs: List[float]  # length 4

# # ====== Core prediction ======
# def _predict_pil(img: Image.Image) -> PredictResponse:
#     if img.mode != "RGB":
#         img = img.convert("RGB")
#     x = preprocess(img).unsqueeze(0).to(device)
#     with torch.no_grad():
#         logits = MODEL(x)
#         probs = torch.softmax(logits, dim=1).squeeze(0)  # [4]
#     idx = int(torch.argmax(probs).item())
#     return PredictResponse(label=CLASS_NAMES[idx], index=idx, probs=probs.tolist())

# # ====== Endpoints ======

# @route.post("/bytes", response_model=PredictResponse)
# async def predict_bytes(request: Request):
#     """
#     ESP32-CAM friendly route.
#     Send raw JPEG bytes in the body with header: Content-Type: image/jpeg
#     """
#     try:
#         data = await request.body()
#         img = Image.open(io.BytesIO(data))
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid image bytes.")
#     try:
#         return _predict_pil(img)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Inference failed: {e}")

# @route.post("/image", response_model=PredictResponse)
# async def predict_image(file: UploadFile = File(...)):
#     """
#     Multipart upload: form field 'file' = image.
#     """
#     try:
#         data = await file.read()
#         img = Image.open(io.BytesIO(data))
#     except Exception:
#         raise HTTPException(status_code=400, detail="Invalid image file.")
#     try:
#         return _predict_pil(img)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Inference failed: {e}")

# @route.get("/labels")
# def labels():
#     return CLASS_NAMES

# @route.get("/ping")
# def ping():
#     return {"status": "ok", "device": str(device), "classes": CLASS_NAMES}



# routers/predict.py
# ESP32-CAM friendly prediction routes + "last prediction" memory.

from fastapi import APIRouter, UploadFile, File, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import io

import torch
import torch.nn as nn
from PIL import Image
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights

route = APIRouter(prefix="/predict", tags=["prediction"])

# ====== Config: files live next to backend code ======
CKPT_PATH = "poultry_efficientnet_b0_best_30ep.pth"

# Hardcoded 4 labels (ORDER must match your training)
CLASS_NAMES = ["COCCI", "HEALTHY", "NEWCASTLE", "SALMO"]

# ====== Device ======
device = torch.device(
    "xpu" if hasattr(torch, "xpu") and torch.xpu.is_available()
    else "cuda" if torch.cuda.is_available()
    else "cpu"
)

# ====== Preprocess (RGB) ======
weights = EfficientNet_B0_Weights.DEFAULT
preprocess = weights.transforms(antialias=True)

# ====== Build & load model (strict 4-class head) ======
def build_model() -> nn.Module:
    model = efficientnet_b0(weights=None)
    in_features = model.classifier[-1].in_features
    model.classifier[-1] = nn.Linear(in_features, len(CLASS_NAMES), bias=True)

    raw = torch.load(CKPT_PATH, map_location="cpu")
    state_dict = raw.get("state_dict", raw) if isinstance(raw, dict) else raw
    if any(k.startswith("module.") for k in state_dict.keys()):
        state_dict = {k.replace("module.", "", 1): v for k, v in state_dict.items()}

    model.load_state_dict(state_dict, strict=True)
    model.to(device).eval()
    torch.set_grad_enabled(False)
    return model

MODEL = build_model()

# ====== Schemas ======
class PredictResponse(BaseModel):
    label: str
    index: int
    probs: List[float]  # length 4

class PredictStamped(PredictResponse):
    at: str  # ISO time in UTC

# ====== In-memory "last prediction" store ======
_LAST_PRED: Optional[PredictStamped] = None

# ====== Core prediction ======
def _predict_pil(img: Image.Image) -> PredictResponse:
    if img.mode != "RGB":
        img = img.convert("RGB")
    x = preprocess(img).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = MODEL(x)
        probs = torch.softmax(logits, dim=1).squeeze(0)  # [4]
    idx = int(torch.argmax(probs).item())
    return PredictResponse(label=CLASS_NAMES[idx], index=idx, probs=probs.tolist())

def _stamp(pred: PredictResponse) -> PredictStamped:
    return PredictStamped(**pred.dict(), at=datetime.now(timezone.utc).isoformat())

# ====== Endpoints ======

@route.post("/bytes", response_model=PredictResponse)
async def predict_bytes(request: Request):
    """
    ESP32-CAM friendly: send raw JPEG bytes (Content-Type: image/jpeg)
    """
    global _LAST_PRED
    try:
        data = await request.body()
        img = Image.open(io.BytesIO(data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image bytes.")
    try:
        pred = _predict_pil(img)
        _LAST_PRED = _stamp(pred)  # store last result
        return pred
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")

@route.post("/image", response_model=PredictResponse)
async def predict_image(file: UploadFile = File(...)):
    """
    Multipart upload alternative (for browsers/Postman)
    """
    global _LAST_PRED
    try:
        data = await file.read()
        img = Image.open(io.BytesIO(data))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid image file.")
    try:
        pred = _predict_pil(img)
        _LAST_PRED = _stamp(pred)
        return pred
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")

@route.get("/last", response_model=Optional[PredictStamped])
def get_last_prediction():
    """
    Return the most recent prediction received (or null if none yet).
    """
    return _LAST_PRED

@route.get("/labels")
def labels():
    return CLASS_NAMES

@route.get("/ping")
def ping():
    return {"status": "ok", "device": str(device), "classes": CLASS_NAMES}
