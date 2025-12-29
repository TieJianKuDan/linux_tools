# 下载V2Ray
wget https://github.com/v2fly/v2ray-core/releases/download/v4.45.2/v2ray-linux-64.zip

# 解压文件
mkdir -p v2ray
unzip v2ray-linux-64.zip -d v2ray

# 移动到系统目录
sudo mv v2ray /usr/local/

# 创建软链接
sudo ln -s /usr/local/v2ray/v2ray /usr/local/bin/v2ray
sudo ln -s /usr/local/v2ray/v2ctl /usr/local/bin/v2ctl

# 创建配置目录
sudo mkdir -p /usr/local/etc/v2ray