
# 사진 정리 및 통계 대시보드

이 프로젝트는 이미지와 동영상 파일의 EXIF 데이터를 기반으로 파일들을 날짜별로 정리하고, 다양한 통계 정보를 시각화하는 [Streamlit](https://streamlit.io/) 대시보드를 제공합니다. 

## 기능

- **파일 정리:**  
  입력된 폴더 내 이미지(`.jpg`, `.jpeg`, `.png`, `.heic`, `.cr2`, `.nef`, `.arw`, `.raf`, `.dng`)와 동영상(`.mp4`, `.mov`, `.avi`) 파일들을 날짜별/비디오 폴더로 이동 또는 복사합니다.

- **EXIF 데이터 수집:**  
  EXIF 데이터를 활용하여 카메라 모델, 초점거리, ISO, 셔터 스피드, 조리개 등 다양한 정보를 추출합니다.

- **통계 및 차트 시각화:**  
  [Plotly](https://plotly.com/python/)를 사용하여 카메라별 사진 수, 35mm 환산 초점거리, 조리개, 노출 시간, ISO 등 다양한 차트를 생성합니다.

- **사용자 인터페이스:**  
  [Streamlit](https://streamlit.io/) 인터페이스를 통해 입력 경로, 목적지, 작업 모드(복사/이동, 통계만 보기) 등을 설정할 수 있습니다.

## 설치 및 실행

1. **Python 3.7 이상**이 설치되어 있어야 합니다.

2. 필요한 패키지들을 설치합니다. (예시)
    ```sh
    pip install streamlit plotly exifread numpy
    ```

3. 대시보드를 실행합니다.
    ```sh
    streamlit run photo_organizer.py
    ```

## 프로젝트 구조

- `photo_organizer.py`  
  메인 스크립트 파일로, 파일 정리 작업 및 Streamlit 기반 대시보드 UI를 구현합니다.

- `test_exif.py`  
  EXIF 데이터와 관련된 테스트 코드를 포함할 수 있습니다.

## 주의 사항

- 정리 작업 시 원본 파일의 이동 또는 복사가 이루어지므로, 작업 전에 백업을 권장합니다.
- EXIF 데이터가 없는 파일은 파일의 수정일자를 기준으로 정리됩니다.
- **주의:** 본 프로그램은 파일 손실에 대해 책임지지 않습니다.

실행 streamlit run photo_organizer.py

## 개발자

개발자: [github.com/ColdTbrew](https://github.com/ColdTbrew)