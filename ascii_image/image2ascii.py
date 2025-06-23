import argparse
from PIL import Image
import os

# 确保中文显示正常
os.environ['PYTHONIOENCODING'] = 'utf-8'

def get_color_escape(r, g, b, background=False):
    """生成ANSI转义序列以显示指定RGB颜色"""
    return '\033[{};2;{};{};{}m'.format(48 if background else 38, r, g, b)

def image_to_ascii(image_path, width=100, height=None):
    """将图像转换为彩色ASCII艺术"""
    try:
        # 打开图像并调整大小
        with Image.open(image_path) as img:
            # 如果未指定高度，根据原图比例计算
            if height is None:
                aspect_ratio = img.height / img.width
                height = int(width * aspect_ratio * 0.5)  # 0.5 是为了补偿字符的高宽比
            
            img = img.resize((width, height), Image.LANCZOS)
            pixels = img.load()
            
            # 构建彩色ASCII艺术
            ascii_art = []
            for y in range(height):
                row = []
                for x in range(width):
                    try:
                        r, g, b = pixels[x, y][:3]  # 忽略可能的alpha通道
                    except TypeError:
                        # 处理灰度图像
                        r = g = b = pixels[x, y]
                    
                    color_code = get_color_escape(r, g, b)
                    row.append(f"{color_code}0\033[0m")  # 使用"0"作为字符，并重置颜色
                ascii_art.append(''.join(row))
            
            return '\n'.join(ascii_art) + "\n"
    
    except Exception as e:
        print(f"处理图像时出错: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='将图像转换为彩色字符画')
    parser.add_argument('image_path', help='输入图像的路径')
    parser.add_argument('-w', '--width', type=int, default=100, help='字符画的宽度（默认: 100）')
    parser.add_argument('-o', '--output', help='输出文本文件的路径（可选）')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.image_path):
        print(f"错误: 文件 '{args.image_path}' 不存在")
        return
    
    # 生成彩色字符画
    ascii_art = image_to_ascii(args.image_path, width=args.width)
    
    if ascii_art:
        # 输出到控制台
        print(ascii_art)
        
        # 如果指定了输出文件，则保存
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(ascii_art)
                print(f"已保存到文件: {args.output}")
            except Exception as e:
                print(f"保存文件时出错: {e}")

if __name__ == "__main__":
    main()    