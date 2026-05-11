# Emotion Asset Toolkit

ComfyUI에서 캐릭터 감정 에셋을 일괄 생성하기 위한 도구 모음입니다. 두 개의 독립적인 컴포넌트로 구성되며, 각각 독립적인 환경에 설치하여 사용합니다.

## 컴포넌트

| 폴더 | 역할 | 설치 위치 |
|---|---|---|
| [`cream-saver/`](./cream-saver/) | ComfyUI 커스텀 노드. WebP EXIF에 편집 워크플로우 임베드 + 드래그앤드랍 복원 | `ComfyUI/custom_nodes/` |
| [`emotion-workflow-builder/`](./emotion-workflow-builder/) | Claude Code skill. NAI/SD 프리셋 → ComfyUI 일괄 감정 그리드 워크플로우 JSON 생성 | `~/.claude/skills/` |

두 컴포넌트는 독립적으로 동작하므로 개별적으로 사용할 수도 있지만, 함께 연계해서 사용하면 다음과 같은 작업 흐름을 구성할 수 있습니다.

## 작업 흐름

1. **워크플로우 빌드** — `emotion-workflow-builder` 스킬에 프리셋 소스(NAI HTML, JSON, dict 등)를 제공하면, 표준 preset JSON과 ComfyUI 일괄 감정 그리드 워크플로우 JSON이 생성됩니다.
2. **그리드 생성** — 생성된 워크플로우를 ComfyUI에 로드하고, 캐릭터 설정을 조정한 뒤 전체 감정 그리드 워크플로우를 실행합니다.
3. **저장** — 결과물 중 마음에 드는 이미지를 `Cream Image Save with Context` 노드를 통해 WebP 형식으로 저장합니다.
4. **편집** — 저장된 WebP 파일을 ComfyUI 화면에 드래그 앤 드롭하면 해당 이미지를 생성했던 편집 워크플로우가 자동으로 복원됩니다. 이후 세부 설정을 미세 조정하여 이미지를 다시 생성할 수 있습니다.

## 설치

세부 사항은 각 컴포넌트의 README/SKILL 문서를 참고하세요:

- [`cream-saver/README.md`](./cream-saver/README.md) — ComfyUI 노드 + 의존 노드 설치
- [`emotion-workflow-builder/SKILL.md`](./emotion-workflow-builder/SKILL.md) — skill 발동 조건 및 변환 절차
