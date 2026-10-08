#!/usr/bin/env bash
# setup_proxy.sh — 一键部署 mihomo：下载内核 → 修正配置 → 后台启动
# 用法:
#   ./setup_proxy.sh                # 代理端口 6006，控制端口 6008
#   ./setup_proxy.sh 7890 9090      # 自定义端口
#
# 会按需修改同目录 config.yaml（原始配置只备份一次为 config.yaml.orig）：
#   1. mixed-port / external-controller 设为指定端口
#   2. allow-lan: false + bind-address: 127.0.0.1（避免公网暴露）
#   3. 禁用 MMDB：DNS fallback 的 geoip 置 false，并注释所有 GEOIP 规则
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"
CONF="$DIR/config.yaml"
BIN="$DIR/mihomo"
LOG="$DIR/mihomo.log"
PORT="${1:-6006}"
CTRL="${2:-6008}"
VER="v1.19.30"

[ -f "$CONF" ] || { echo "缺少 $CONF"; exit 1; }
log() { printf '[setup] %s\n' "$*"; }

# ── 1. 下载 mihomo ──────────────────────────────────────────
if [ ! -x "$BIN" ]; then
  case "$(uname -m)" in
    x86_64|amd64)  ARCH=amd64 ;;
    aarch64|arm64) ARCH=arm64 ;;
    *) echo "不支持的架构: $(uname -m)"; exit 1 ;;
  esac
  F="mihomo-linux-${ARCH}-${VER}"
  URL="https://github.com/MetaCubeX/mihomo/releases/download/${VER}/${F}.gz"
  for M in "$URL" "https://ghfast.top/${URL}" "https://gh-proxy.com/${URL}"; do
    log "下载 $M"
    if curl -fL --connect-timeout 8 --max-time 120 -o "${F}.gz" "$M" 2>/dev/null \
       && [ "$(stat -c%s "${F}.gz" 2>/dev/null || echo 0)" -gt 5000000 ]; then
      break
    fi
  done
  [ -f "${F}.gz" ] || { echo "下载失败"; exit 1; }
  gunzip -f "${F}.gz"
  mv -f "$F" mihomo                    # gunzip 产物是带版本号的名字，不是 mihomo
  chmod +x mihomo
  log "已安装 $(./mihomo -v 2>&1 | head -1)"
else
  log "mihomo 已存在，跳过下载"
fi

# ── 2. 按需修正配置 ─────────────────────────────────────────
[ -f config.yaml.orig ] || cp "$CONF" config.yaml.orig

# 存在则替换（含被注释的同名项），不存在则插到首行
set_kv() {
  if grep -qE "^#?[[:space:]]*$1:" "$CONF"; then
    sed -i -E "s|^#?[[:space:]]*$1:.*|$1: $2|" "$CONF"
  else
    sed -i "1i $1: $2" "$CONF"
  fi
}

set_kv mixed-port "$PORT"
set_kv external-controller "'127.0.0.1:${CTRL}'"
set_kv allow-lan false
set_kv bind-address "'127.0.0.1'"

# 禁用 MMDB：DNS fallback 不再按国家判定
sed -i 's/geoip: true/geoip: false/g' "$CONF"
# 注释所有 GEOIP 规则（已注释的不重复处理，保留原有引号风格）
sed -i -E "s|^([[:space:]]*)-[[:space:]]*('?)GEOIP,|# \1- \2GEOIP,|" "$CONF"

log "配置已就绪：代理 ${PORT} / 控制 ${CTRL} / 已禁用 MMDB"

# ── 3. 后台启动 ─────────────────────────────────────────────
pkill -x mihomo 2>/dev/null || true    # 没有旧进程时 pkill 返回 1，必须吞掉否则 set -e 直接终止脚本
sleep 2
./mihomo -d "$DIR" > "$LOG" 2>&1 < /dev/null &
MIHOMO_PID=$!
# 后台任务：脚本立即返回，终端/SSH 会话结束时随之退出；要常驻用 tmux / screen
for _ in $(seq 1 20); do
  sleep 1
  # 必须写成 if：set -e 下 "pgrep && break" 在首次失败时会静默终止整个脚本
  if pgrep -x mihomo >/dev/null; then break; fi
done
pgrep -x mihomo >/dev/null || { echo "启动失败，日志尾部："; tail -20 "$LOG"; exit 1; }

# ── 4. 结果 ─────────────────────────────────────────────────
PW=$(sed -n "s/.*'clash:\([^']*\)'.*/\1/p" "$CONF" | head -1)
PROXY="http://clash:${PW}@127.0.0.1:${PORT}"
echo
echo "mihomo 已启动 pid=$(pgrep -x mihomo)"
echo -n "连通性: "
curl -s -o /dev/null -m 12 -x "$PROXY" -w "google code=%{http_code} ttfb=%{time_starttransfer}s\n" https://www.google.com || echo "（本次探测失败，不影响已启动的服务）"
echo
echo "当前 shell 启用代理："
echo "    export http_proxy=$PROXY"
echo "    export https_proxy=$PROXY"
echo "脚本已返回，mihomo 在后台运行，关闭终端时随之退出。"
echo "停止代理: pkill -x mihomo"
[ -f "$DIR/geoip.metadb" ] && echo "注意：目录里仍生成了 geoip.metadb，说明还有规则在用 MMDB" || true
