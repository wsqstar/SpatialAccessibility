#!/bin/bash

# 清理旧构建
rm -rf ./build ./dist ./*.egg-info

# 安装最新构建工具
# python3 -m pip install --upgrade hatchling build twine

# 强制重新生成元数据
python3 -m build --no-isolation  # 关键修复：禁用隔离环境确保配置生效

# 验证元数据
twine check dist/*

# 上传到TestPyPI
python3 -m twine upload --repository testpypi dist/*