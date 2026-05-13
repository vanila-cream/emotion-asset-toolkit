@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM  emotion-asset-toolkit 일괄 설치 스크립트
REM  ComfyUI 루트 폴더에 이 파일을 넣고 더블클릭하세요.
REM ============================================================

if not exist "custom_nodes\" (
    echo.
    echo [ERROR] ComfyUI 루트 폴더에서 실행해야 합니다.
    echo         'custom_nodes' 폴더를 찾을 수 없습니다.
    echo.
    echo 이 install.bat 파일을 ComfyUI 루트 폴더
    echo ^(예: ComfyUI_windows_portable\ComfyUI\^) 안에 넣고
    echo 다시 더블클릭해 주세요.
    echo.
    pause
    exit /b 1
)

echo.
echo [1/2] 커스텀 노드 설치 중...
echo.

cd custom_nodes

if not exist "cream-saver\" (
    git clone https://github.com/vanila-cream/emotion-asset-toolkit
    move emotion-asset-toolkit\cream-saver .\cream-saver >nul
    rmdir /s /q emotion-asset-toolkit
) else (
    echo [SKIP] cream-saver 이미 설치됨
)

if not exist "efficiency-nodes-comfyui\" (
    git clone https://github.com/jags111/efficiency-nodes-comfyui
) else (
    echo [SKIP] efficiency-nodes-comfyui 이미 설치됨
)

if not exist "efficiency-nodes-ED\" (
    git clone https://github.com/NyaamZ/efficiency-nodes-ED
) else (
    echo [SKIP] efficiency-nodes-ED 이미 설치됨
)

if not exist "rgthree-comfy\" (
    git clone https://github.com/rgthree/rgthree-comfy
) else (
    echo [SKIP] rgthree-comfy 이미 설치됨
)

if not exist "ComfyUI-Impact-Pack\" (
    git clone https://github.com/ltdrdata/ComfyUI-Impact-Pack
) else (
    echo [SKIP] ComfyUI-Impact-Pack 이미 설치됨
)

cd ..

echo.
echo [2/2] 모델 다운로드 중...
echo.

mkdir models\upscale_models 2>nul
mkdir models\ultralytics\bbox 2>nul
mkdir models\sams 2>nul

if not exist "models\upscale_models\2x-AnimeSharpV4_Fast_RCAN_PU.safetensors" (
    curl -L -o models\upscale_models\2x-AnimeSharpV4_Fast_RCAN_PU.safetensors "https://huggingface.co/Kim2091/2x-AnimeSharpV4/resolve/main/2x-AnimeSharpV4_Fast_RCAN_PU.safetensors"
) else (
    echo [SKIP] 2x-AnimeSharpV4_Fast_RCAN_PU.safetensors 이미 존재
)

if not exist "models\ultralytics\bbox\face_yolov8m.pt" (
    curl -L -o models\ultralytics\bbox\face_yolov8m.pt "https://huggingface.co/datasets/Gourieff/ReActor/resolve/main/models/detection/bbox/face_yolov8m.pt"
) else (
    echo [SKIP] face_yolov8m.pt 이미 존재
)

if not exist "models\sams\sam_vit_b_01ec64.pth" (
    curl -L -o models\sams\sam_vit_b_01ec64.pth "https://huggingface.co/datasets/Gourieff/ReActor/resolve/main/models/sams/sam_vit_b_01ec64.pth"
) else (
    echo [SKIP] sam_vit_b_01ec64.pth 이미 존재
)

echo.
echo ============================================================
echo  [완료] 모든 커스텀 노드와 모델 설치가 끝났습니다.
echo         ComfyUI를 재시작해 주세요.
echo ============================================================
echo.
pause
endlocal
