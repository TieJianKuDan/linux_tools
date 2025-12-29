# 手动复制到终端运行

nohup v2ray -c config.json > /dev/null 2>&1 &

export http_proxy=http://127.0.0.1:6006
export https_proxy=http://127.0.0.1:6006

curl -v https://www.google.com