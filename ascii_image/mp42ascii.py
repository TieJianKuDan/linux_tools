import cv2
import os
import time
import argparse

def get_simple_color_frame(frame, width=120):
    """将彩色视频帧转换为带颜色的'0'字符表示"""
    height, width_original, _ = frame.shape
    # 调整尺寸以适应终端（字符高度约为宽度的2倍）
    height_ratio = height / width_original
    new_height = int(width * height_ratio / 2)
    frame_resized = cv2.resize(frame, (width, new_height))
    
    ascii_frame = []
    for y in range(new_height):
        ascii_row = []
        for x in range(width):
            # 获取像素BGR值并转为RGB
            b, g, r = frame_resized[y, x]
            
            # 生成ANSI颜色代码（前景色）
            color_code = f"\033[38;2;{r};{g};{b}m"
            reset_code = "\033[0m"
            
            # 统一使用'0'字符并应用颜色
            ascii_row.append(f"{color_code}0{reset_code}")
        ascii_frame.append(''.join(ascii_row))
    
    return '\n'.join(ascii_frame)

def simple_color_video_play(video_path, target_fps=None, output_width=120):
    """播放彩色0字符视频"""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频文件: {video_path}")
        return
    
    # 获取视频属性
    fps = cap.get(cv2.CAP_PROP_FPS)
    if target_fps:
        fps = target_fps
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"视频帧率: {fps} FPS, 总帧数: {frame_count}")
    frame_interval = 1.0 / fps
    
    print("开始播放... (按Ctrl+C退出)")
    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # 转换为彩色0字符帧
            ascii_frame = get_simple_color_frame(frame, output_width)
            
            # 清空终端并显示
            os.system('cls' if os.name == 'nt' else 'clear')
            print(ascii_frame)
            
            # 控制帧率
            start_time = time.time()
            if frame_interval > 0:
                time.sleep(max(0, frame_interval - (time.time() - start_time)))
                
    except KeyboardInterrupt:
        print("\n用户中断播放")
    finally:
        cap.release()
        print("播放结束")

def main():
    parser = argparse.ArgumentParser(description='极简彩色0字符视频播放器')
    parser.add_argument('video_path', help='输入视频文件路径')
    parser.add_argument('--fps', type=float, help='目标播放帧率，默认使用原始帧率')
    parser.add_argument('--width', type=int, default=120, help='终端显示宽度，默认120字符')
    args = parser.parse_args()
    
    simple_color_video_play(args.video_path, target_fps=args.fps, output_width=args.width)

if __name__ == "__main__":
    main()
