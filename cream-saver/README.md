# Cream Saver — ComfyUI 커스텀 노드

캐릭터 감정 에셋 일괄 생성 툴킷의 ComfyUI용 컴포넌트입니다. 이미지를 WebP 형식으로 저장할 때 편집용 워크플로우를 파일의 메타데이터(EXIF)에 함께 보관합니다. 이렇게 저장된 이미지를 ComfyUI 캔버스로 드래그 앤 드롭하면, 해당 이미지를 바로 편집할 수 있도록 기존 워크플로우(`Sampler_workflow.json` 기반)가 자동으로 복원됩니다.

> 감정 에셋 일괄 생성 워크플로우를 생성하려면 같은 저장소의 [`emotion-workflow-builder`](../emotion-workflow-builder/) skill을 사용합니다.

## 구성 요소

| 노드 | 역할 |
|---|---|
| **Cream Image Save with Context** | 이미지를 무손실 WebP 형식으로 저장할 때, `Sampler_workflow.json` 기반의 편집 워크플로우를 메타데이터에 포함시켜 저장합니다. |
| **Context Cream** | `rgthree Context Big` 노드의 확장 버전입니다. `LORA_STACK` 필드를 추가하여 Cream Saver 노드의 입력을 더욱 간편하게 구성할 수 있습니다. |

## 설치

### 필요한 커스텀 노드

`cream-saver`는 ComfyUI Manager에 등록되어 있지 않아 GitHub에서 직접 받아 `custom_nodes` 폴더에 복사해야 합니다. 나머지는 Manager에서 검색해 설치해도 됩니다.

| 커스텀 노드 | 사용 노드 |
|---|---|
| [`cream-saver`](https://github.com/vanila-cream/emotion-asset-toolkit) | Cream Image Save with Context, Context Cream |
| [`efficiency-nodes-comfyui`](https://github.com/jags111/efficiency-nodes-comfyui) + [`efficiency-nodes-ED`](https://github.com/NyaamZ/efficiency-nodes-ED) | Efficient Loader, LoRA Stacker, Simple Text |
| [`rgthree-comfy`](https://github.com/rgthree/rgthree-comfy) | Fast Groups Bypasser |
| [`comfyui-impact-pack`](https://github.com/ltdrdata/ComfyUI-Impact-Pack) | ImpactStringSelector, ImpactInt, FaceDetailer |

### 필요한 모델

편집용 워크플로우에서 사용하는 모델 3개입니다. 아래 링크에서 받은 뒤 표시된 폴더에 직접 넣으셔도 됩니다.

| 모델 | 배치 폴더 | 용도 |
|---|---|---|
| [`2x-AnimeSharpV4_Fast_RCAN_PU.safetensors`](https://huggingface.co/Kim2091/2x-AnimeSharpV4) | `ComfyUI/models/upscale_models/` | 업스케일 |
| [`face_yolov8m.pt`](https://huggingface.co/datasets/Gourieff/ReActor/blob/main/models/detection/bbox/face_yolov8m.pt) | `ComfyUI/models/ultralytics/bbox/` | FaceDetailer 얼굴 검출 |
| [`sam_vit_b_01ec64.pth`](https://huggingface.co/datasets/Gourieff/ReActor/blob/main/models/sams/sam_vit_b_01ec64.pth) | `ComfyUI/models/sams/` | FaceDetailer SAM 마스크 |

### 일괄 설치 명령어

위 커스텀 노드와 모델을 한 번에 다운로드하는 명령어입니다. ComfyUI 루트 폴더에서 cmd 터미널을 열고 아래 명령어를 통째로 붙여넣어 실행하세요.

```cmd
if not exist custom_nodes\ (echo. & echo [ERROR] ComfyUI 루트 폴더에서 실행해야 합니다. 'custom_nodes' 폴더를 찾을 수 없습니다. & echo.) else (
cd custom_nodes
git clone https://github.com/vanila-cream/emotion-asset-toolkit
move emotion-asset-toolkit\cream-saver .\cream-saver
rmdir /s /q emotion-asset-toolkit
git clone https://github.com/jags111/efficiency-nodes-comfyui
git clone https://github.com/NyaamZ/efficiency-nodes-ED
git clone https://github.com/rgthree/rgthree-comfy
git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack
cd ..
mkdir models\upscale_models 2>nul
mkdir models\ultralytics\bbox 2>nul
mkdir models\sams 2>nul
curl -L -o models\upscale_models\2x-AnimeSharpV4_Fast_RCAN_PU.safetensors "https://huggingface.co/Kim2091/2x-AnimeSharpV4/resolve/main/2x-AnimeSharpV4_Fast_RCAN_PU.safetensors"
curl -L -o models\ultralytics\bbox\face_yolov8m.pt "https://huggingface.co/datasets/Gourieff/ReActor/resolve/main/models/detection/bbox/face_yolov8m.pt"
curl -L -o models\sams\sam_vit_b_01ec64.pth "https://huggingface.co/datasets/Gourieff/ReActor/resolve/main/models/sams/sam_vit_b_01ec64.pth"
echo.
echo [완료] 모든 커스텀 노드와 모델 설치가 끝났습니다. ComfyUI를 재시작해 주세요.
echo.
)
```

설치를 마친 후 ComfyUI를 재시작합니다. 노드 검색 창에 `Cream Image Save with Context` 및 `Context Cream` 노드가 나타나면 설치가 성공적으로 완료된 것입니다.

## 사용법

### 이미지 저장 + 드래그앤드랍 복원

1. ComfyUI에서 워크플로우를 실행합니다. (일괄 감정 그리드 워크플로우나 일반 워크플로우 모두 가능합니다.)
2. `Cream Image Save with Context` 노드에 출력된 결과물 중 마음에 드는 이미지를 우클릭하여 저장합니다.
3. 저장한 WebP 파일을 ComfyUI 화면으로 드래그 앤 드롭하면, 해당 이미지를 생성했던 편집용 워크플로우가 즉시 복원됩니다.

## 폴더 구조

```
cream-saver/
├── __init__.py              ComfyUI 노드 등록
├── nodes.py                 SaveImageWithContext, ContextCream 구현
├── Sampler_workflow.json    드래그앤드랍 시 복원되는 편집 템플릿
└── README.md
```

## 라이선스 / 크레딧

- `Context Cream` 노드는 [rgthree-comfy](https://github.com/rgthree/rgthree-comfy)의 `Context Big` 노드를 기반으로 기능을 확장하여 제작되었습니다.
