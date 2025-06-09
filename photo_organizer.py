import os, shutil, json
from datetime import datetime
import exifread
from collections import defaultdict
import streamlit as st
import plotly.graph_objs as go
import plotly.express as px
import numpy as np

SUPPORTED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.heic', '.cr2', '.nef', '.arw', '.raf', '.dng'}
SUPPORTED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.avi'}

def get_file_date(file_path):
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f)
            date_str = tags.get('EXIF DateTimeOriginal')
            if date_str:
                return datetime.strptime(str(date_str), '%Y:%m:%d %H:%M:%S').strftime('%Y-%m-%d')
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d')

def get_file_hour(file_path):
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f)
            date_str = tags.get('EXIF DateTimeOriginal')
            if date_str:
                dt = datetime.strptime(str(date_str), '%Y:%m:%d %H:%M:%S')
                return dt.strftime('%Y-%m-%d %H:00')
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:00')

def fraction_to_float(fraction_str):
    if '/' in fraction_str:
        num, denom = map(int, fraction_str.split('/'))
        return num / denom if denom else 0
    return float(fraction_str) if fraction_str.isdigit() else 0

def organize_files(input_path, dest_root="", copy_mode=True, stats_only=False):
    if not os.path.exists(input_path):
        return ["유효하지 않은 경로입니다."], {}
    organized_dir = dest_root if dest_root else os.path.join(os.path.dirname(input_path), "Organized_Photos")
    os.makedirs(organized_dir, exist_ok=True)
    
    # 통계 변수 초기화
    stats = defaultdict(lambda: defaultdict(int))
    iso_stats = defaultdict(int)
    shutter_stats = defaultdict(int)
    aperture_stats = defaultdict(int)
    date_stats = defaultdict(int)
    hour_stats = defaultdict(int)
    exposure_program_stats = defaultdict(int)
    fnumber_stats = defaultdict(int)
    exposure_time_stats = defaultdict(int)
    focal35_stats = defaultdict(int)
    lens_model_stats = defaultdict(int)
    make_stats = defaultdict(int)
    orientation_stats = defaultdict(int)
    
    total_files = video_files = error_count = 0
    log = []
    for root, _, files in os.walk(input_path):
        for file in files:
            file_path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            is_image = ext in SUPPORTED_IMAGE_EXTENSIONS
            is_video = ext in SUPPORTED_VIDEO_EXTENSIONS
            if not (is_image or is_video):
                continue
            if is_video:
                video_files += 1
            date = get_file_date(file_path)
            date_stats[date] += 1
            hour_stats[get_file_hour(file_path)] += 1
            
            # EXIF 통계 (이미지에 한함)
            if is_image:
                try:
                    with open(file_path, 'rb') as f:
                        tags = exifread.process_file(f)
                        camera = str(tags.get('Image Model', 'Unknown'))
                        focal_length = fraction_to_float(str(tags.get('EXIF FocalLength', 'Unknown')))
                        iso = str(tags.get('EXIF ISOSpeedRatings', 'Unknown'))
                        exposure_time = tags.get('EXIF ExposureTime')
                        shutter_speed = str(exposure_time) if exposure_time else str(tags.get('EXIF ShutterSpeedValue', 'Unknown'))
                        aperture = str(tags.get('EXIF FNumber', 'Unknown'))
                        stats[camera][focal_length] += 1
                        iso_stats[iso] += 1
                        shutter_stats[shutter_speed] += 1
                        aperture_stats[aperture] += 1
                        
                        # 추가 EXIF 정보
                        exposure_program = str(tags.get('EXIF ExposureProgram', 'Unknown'))
                        fnum = str(tags.get('EXIF FNumber', 'Unknown'))
                        exposure_time_val = str(tags.get('EXIF ExposureTime', 'Unknown'))
                        focal35 = str(tags.get('EXIF FocalLengthIn35mmFilm', 'Unknown'))
                        lens_model = str(tags.get('EXIF LensModel', 'Unknown'))
                        make = str(tags.get('Image Make', 'Unknown'))
                        orientation = str(tags.get('Image Orientation', 'Unknown'))
                        
                        exposure_program_stats[exposure_program] += 1
                        fnumber_stats[fnum] += 1
                        exposure_time_stats[exposure_time_val] += 1
                        focal35_stats[focal35] += 1
                        lens_model_stats[lens_model] += 1
                        make_stats[make] += 1
                        orientation_stats[orientation] += 1
                        
                        log.append(f"EXIF read for {file}: Camera={camera}, FocalLength={focal_length}, ISO={iso}, Shutter={shutter_speed}, Aperture={aperture}")
                except Exception as e:
                    log.append(f"Error reading EXIF for {file}: {e}")
                    error_count += 1
            # 파일 이동/복사 (통계만 모드가 아닐 때)
            if not stats_only:
                dest_dir = os.path.join(organized_dir, date) if is_image else os.path.join(organized_dir, 'Videos', date)
                os.makedirs(dest_dir, exist_ok=True)
                dest_path = os.path.join(dest_dir, file)
                if os.path.exists(dest_path):
                    base, extn = os.path.splitext(file)
                    dest_path = os.path.join(dest_dir, f"{base}_copy{extn}")
                try:
                    (shutil.copy if copy_mode else shutil.move)(file_path, dest_path)
                    log.append(f"{'Copied' if copy_mode else 'Moved'} {file} to {dest_path}")
                    total_files += 1
                except Exception as e:
                    log.append(f"Error moving/copying '{file_path}' to '{dest_path}': {e}")
    start_date = min(date_stats.keys()) if date_stats else "N/A"
    end_date = max(date_stats.keys()) if date_stats else "N/A"
    log.extend([f"Total files: {total_files}",
                f"Date range: {start_date} to {end_date}",
                "Stats collected.",
                f"File read failures: {error_count}"])
    
    return log, {
        "camera_stats": dict(stats),
        "iso_stats": dict(iso_stats),
        "shutter_stats": dict(shutter_stats),
        "aperture_stats": dict(aperture_stats),
        "date_stats": dict(date_stats),
        "hour_stats": dict(hour_stats),
        "exposure_program_stats": dict(exposure_program_stats),
        "fnumber_stats": dict(fnumber_stats),
        "exposure_time_stats": dict(exposure_time_stats),
        "focal35_stats": dict(focal35_stats),
        "lens_model_stats": dict(lens_model_stats),
        "make_stats": dict(make_stats),
        "orientation_stats": dict(orientation_stats),
        "total_files": total_files,
        "video_files": video_files,
        "date_range": (start_date, end_date),
        "error_count": error_count
    }

def round_aperture(aperture):
    try:
        val = float(aperture)
        stops = [1.0, 1.4, 2.0, 2.8, 4.0, 5.6, 8.0, 11.0, 16.0, 22.0, 32.0]
        return str(stops[np.abs(np.array(stops) - val).argmin()])
    except:
        return "Unknown"

def create_charts(stats):
    # 카메라 통계
    camera_stats = stats.get("camera_stats", {})
    cam_labels = list(camera_stats.keys()) or ["No Data"]
    cam_values = [sum(focal.values()) for focal in camera_stats.values()] or [0]
    # 35mm 환산 초점거리 (합산)
    focal_data = defaultdict(int)
    for focal_dict in camera_stats.values():
        for f, count in focal_dict.items():
            focal_data[f] += count
    focal_labels = list(focal_data.keys()) or ["No Data"]
    focal_values = list(focal_data.values()) or [0]
    # 나머지 통계
    iso = (list(stats.get("iso_stats", {}).keys()) or ["No Data"],
           list(stats.get("iso_stats", {}).values()) or [0])
    shutter = (list(stats.get("shutter_stats", {}).keys()) or ["No Data"],
               list(stats.get("shutter_stats", {}).values()) or [0])
    # Aperture: round 후 합산
    apt_raw = list(stats.get("aperture_stats", {}).keys())
    apt_vals = list(stats.get("aperture_stats", {}).values()) or [0]
    apt_bins = defaultdict(int)
    for a, v in zip(apt_raw, apt_vals):
        apt_bins[round_aperture(a)] += v
    aperture = (list(apt_bins.keys()) or ["No Data"], list(apt_bins.values()) or [0])
    # Exposure, Date, Hour (기본)
    exposure = (list(stats.get("exposure_stats", {}).keys()) or ["No Data"],
                list(stats.get("exposure_stats", {}).values()) or [0])
    date = (list(stats.get("date_stats", {}).keys()) or ["No Data"],
            list(stats.get("date_stats", {}).values()) or [0])
    hour = (list(stats.get("hour_stats", {}).keys()) or ["No Data"],
            list(stats.get("hour_stats", {}).values()) or [0])
    
    return {
        "camera": (cam_labels, cam_values),
        "focal": (focal_labels, focal_values),
        "iso": iso,
        "shutter": shutter,
        "aperture": aperture,
        "exposure": exposure,
        "date": date,
        "hour": hour
    }

def sort_labels_and_values(labels, values, key_func=float, round_digits=None):
    items = []
    for l, v in zip(labels, values):
        try:
            k = key_func(l)
            if round_digits is not None:
                k = round(k, round_digits)
            items.append((k, v))
        except Exception:
            items.append((l, v))
    items.sort(key=lambda x: (isinstance(x[0], str), x[0]))
    return [str(x[0]) for x in items], [x[1] for x in items]

# ---------- Streamlit UI ----------
custom_css = """
<style>
body { background-color: #f0f2f6; font-family: 'Segoe UI', sans-serif; }
h1 { text-align: center; font-size: 3em; margin-bottom: 0.2em; }
.markdown-text { font-size: 1.1em; color: #e76f51; text-align: center; }
.stButton>button { background-color: #264653; color: white; font-weight: bold; border-radius: 5px; border: none; margin-bottom: 0.5em; }
.sidebar-content { font-size: 1em; margin-top: 2em; text-align: center; }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)
st.title("사진 정리 및 통계 대시보드")
st.markdown("<p class='markdown-text'>파일 손실에 대해 책임지지 않습니다.</p>", unsafe_allow_html=True)

input_path = st.text_input("정리할 폴더 경로", placeholder="예: /Users/username/Photos")
dest_path = st.text_input("목적지 경로 (옵션)", placeholder="비워두면 기본 경로 사용")
copy_mode = st.checkbox("복사 모드(체크: 복사, 해제: 이동)", value=True)
stats_only = st.checkbox("정리하지 않고 통계만 보기", value=False)

start_pressed = st.button("정리 시작")
stop_pressed = st.button("중지")
if stop_pressed:
    st.warning("프로세스가 중지되었습니다.")
    st.stop()

if start_pressed and input_path:
    log, stats = organize_files(input_path, dest_root=dest_path, copy_mode=copy_mode, stats_only=stats_only)
    charts = create_charts(stats)
    total_files = stats.get("total_files", 0)
    video_files = stats.get("video_files", 0)
    error_count = stats.get("error_count", 0)
    date_range = stats.get("date_range", ("N/A", "N/A"))
    
    st.subheader("정리 결과 로그")
    st.text_area("Log", "\n".join(log), height=200)
    
    st.subheader("통계 요약")
    st.markdown(f"""
    - **총 파일 수:** {total_files}개  
    - **동영상 파일 수:** {video_files}개  
    - **파일 읽기 실패:** {error_count}건  
    - **날짜 범위:** {date_range[0]} ~ {date_range[1]}  
    - **사용된 카메라:** {', '.join(stats.get('camera_stats', {}).keys()) or 'N/A'}
    """)
    
    # 카메라별 파이 차트
    st.subheader("카메라별 사진 수")
    cam_labels, cam_values = charts["camera"]
    fig = go.Figure(data=[go.Pie(labels=cam_labels, values=cam_values, hole=0.3)])
    st.plotly_chart(fig, use_container_width=True)
    
    # 35mm 환산 초점거리 (정수 정렬)
    st.subheader("35mm 환산 초점거리")
    if stats.get("focal35_stats"):
        labels = list(stats["focal35_stats"].keys())
        values = list(stats["focal35_stats"].values())
        items = []
        for l, v in zip(labels, values):
            try:
                items.append((int(float(l)), v))
            except Exception:
                items.append((l, v))
        items.sort(key=lambda x: (isinstance(x[0], str), x[0]))
        sorted_labels = [str(x[0]) for x in items]
        sorted_values = [x[1] for x in items]
        st.plotly_chart(go.Figure(data=[go.Bar(x=sorted_labels, y=sorted_values)]), use_container_width=True)
    
    # 조리개(FNumber)
    st.subheader("조리개(FNumber)")
    if stats.get("fnumber_stats"):
        labels = list(stats["fnumber_stats"].keys())
        values = list(stats["fnumber_stats"].values())
        items = []
        for l, v in zip(labels, values):
            try:
                k = round(float(l.split('/')[0]) / float(l.split('/')[1]), 1) if '/' in l else round(float(l), 1)
                items.append((k, v))
            except Exception:
                items.append((l, v))
        items.sort(key=lambda x: (isinstance(x[0], str), float(x[0]) if not isinstance(x[0], str) else x[0]))
        sorted_labels = [str(x[0]) for x in items]
        sorted_values = [x[1] for x in items]
        st.plotly_chart(go.Figure(data=[go.Bar(x=sorted_labels, y=sorted_values)]), use_container_width=True)
    
    # Shutter Speed (분수 원본 유지, 정렬은 실수 기준)
    st.subheader("Shutter Speed")
    if stats.get("exposure_time_stats"):
        labels = list(stats["exposure_time_stats"].keys())
        values = list(stats["exposure_time_stats"].values())
        items = []
        for l, v in zip(labels, values):
            try:
                k = float(l.split('/')[0]) / float(l.split('/')[1]) if '/' in l else float(l)
                items.append((k, l, v))
            except Exception:
                items.append((float('inf'), l, v))
        items.sort(key=lambda x: x[0])
        sorted_labels = [x[1] for x in items]
        sorted_values = [x[2] for x in items]
        st.plotly_chart(go.Figure(data=[go.Bar(x=sorted_labels, y=sorted_values)]), use_container_width=True)
    
    # ISO (소수점 버림)
    st.subheader("ISO")
    iso_labels, iso_values = charts["iso"]
    items = []
    for l, v in zip(iso_labels, iso_values):
        try:
            items.append((int(float(l)), v))
        except Exception:
            items.append((l, v))
    items.sort(key=lambda x: (isinstance(x[0], str), x[0]))
    sorted_iso_labels = [str(x[0]) for x in items]
    sorted_iso_values = [x[1] for x in items]
    st.plotly_chart(go.Figure(data=[go.Bar(x=sorted_iso_labels, y=sorted_iso_values)]), use_container_width=True)
    
    # 추가 EXIF 차트들 (카테고리컬 색상 적용)
    for title, key in [("노출 프로그램별 파일 수", "exposure_program_stats"),
                       ("카메라 제조사별 파일 수", "make_stats"),
                       ("사진 방향(Orientation)별 파일 수", "orientation_stats")]:
        data = stats.get(key, {})
        if data:
            labels = list(data.keys())
            values = list(data.values())
            colors = [px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)] for i in range(len(labels))]
            st.subheader(title)
            st.plotly_chart(go.Figure(data=[go.Bar(x=labels, y=values, marker=dict(color=colors))]), use_container_width=True)

st.caption("개발자 : github.com/ColdTbrew")
