#!/bin/bash
# 军师的"一键打包"脚本 - pack_project.sh

echo "🔍 军师正在扫描核心资产..."

# 1. 创建临时整理目录
PROJECT_NAME="tiangong-video-factory"
TEMP_DIR="/tmp/$PROJECT_NAME"
rm -rf "$TEMP_DIR"
mkdir -p "$TEMP_DIR"

# 2. 复制核心代码 (假设主要在 /root 下)
# 如果您的代码在其他地方，请修改下面的路径
cp -r /root/*.sh "$TEMP_DIR/" 2>/dev/null
cp -r /root/*.py "$TEMP_DIR/" 2>/dev/null
cp -r /root/requirements.txt "$TEMP_DIR/" 2>/dev/null
cp -r /root/config* "$TEMP_DIR/" 2>/dev/null

# 如果之前有创建过专门的目录，也复制进去
if [ -d "/root/tiangong" ]; then
    cp -r /root/tiangong/* "$TEMP_DIR/"
fi

# 3. 创建一个 README 说明文件 (方便军师看)
cat > "$TEMP_DIR/README.md" <<EOF
# 天工视频工厂 (Tiangong Video Factory)
- 更新时间: $(date)
- 包含内容: 自动化脚本, Python应用, 配置文件
EOF

# 4. 打包
cd /tmp
tar -czf "${PROJECT_NAME}.tar.gz" "$PROJECT_NAME"

echo "✅ 打包完成！文件位于: /tmp/${PROJECT_NAME}.tar.gz"
echo "👉 请主公把这个文件下载到本地，然后拖拽上传到 GitHub 仓库即可。"
