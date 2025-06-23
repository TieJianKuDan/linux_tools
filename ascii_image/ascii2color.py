import argparse
import sys

# ANSI 颜色代码
COLORS = {
    'black': 30, 'red': 31, 'green': 32, 'yellow': 33,
    'blue': 34, 'purple': 35, 'cyan': 36, 'white': 37,
    'bright_black': 90, 'bright_red': 91, 'bright_green': 92,
    'bright_yellow': 93, 'bright_blue': 94, 'bright_purple': 95,
    'bright_cyan': 96, 'bright_white': 97
}

def colorize_text(text, color_code):
    """将文本转换为指定颜色的 ANSI 转义序列"""
    return f"\033[{color_code}m{text}\033[0m"

def main():
    parser = argparse.ArgumentParser(description='将文本以指定颜色输出')
    parser.add_argument('-c', '--color', choices=list(COLORS.keys()), default='white',
                        help='指定输出颜色')
    parser.add_argument('-f', '--file', help='从文件读取文本')
    parser.add_argument('-i', '--input', help='直接输入文本')
    parser.add_argument('--rgb', nargs=3, type=int, metavar=('R', 'G', 'B'),
                        help='使用 RGB 颜色 (0-255)')
    parser.add_argument('-o', '--output', help='保存着色后的文本到文件')
    
    args = parser.parse_args()
    
    # 确保中文显示正常
    sys.stdout.reconfigure(encoding='utf-8')
    
    # 获取颜色代码
    if args.rgb:
        r, g, b = args.rgb
        # 验证 RGB 值范围
        for val in (r, g, b):
            if val < 0 or val > 255:
                print("错误: RGB 值必须在 0-255 之间")
                sys.exit(1)
        color_code = f"38;2;{r};{g};{b}"
    else:
        color_code = COLORS[args.color]
    
    # 获取文本内容
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except FileNotFoundError:
            print(f"错误: 文件 '{args.file}' 不存在")
            sys.exit(1)
        except Exception as e:
            print(f"读取文件时出错: {e}")
            sys.exit(1)
    elif args.input:
        text = args.input
    else:
        # 从标准输入读取（例如通过管道）
        text = sys.stdin.read()
    
    # 生成彩色文本
    colored_text = colorize_text(text, color_code)
    
    # 输出或保存
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(colored_text)
            print(f"已将着色文本保存到: {args.output}")
        except Exception as e:
            print(f"保存文件时出错: {e}")
            sys.exit(1)
    else:
        print(colored_text)

if __name__ == "__main__":
    main()    