# Makefile for generating legacy blog redirects

# 可配置路径
BLOG_DIR := ../../hexo/public
SITE_DIR := .
SCRIPT := gen_redirects.py

# 生成参数
BASE_URL := /blog/
EXCLUDES := --exclude tags --exclude categories --exclude assets --exclude css --exclude js

# Python 解释器
PYTHON := python3

# 默认目标
all: redirects

# 实际生成重定向文件
redirects:
	@echo "🔧 Generating redirect pages from $(BLOG_DIR) to $(SITE_DIR) ..."
	$(PYTHON) $(SCRIPT) --blog $(BLOG_DIR) --site $(SITE_DIR) --base $(BASE_URL) $(EXCLUDES)
	@echo "✅ Redirects generated successfully."

# 预览模式（dry-run）
preview:
	@echo "👀 Previewing redirect generation (dry-run)..."
	$(PYTHON) $(SCRIPT) --blog $(BLOG_DIR) --site $(SITE_DIR) --base $(BASE_URL) $(EXCLUDES) --dry-run
	@echo "✅ Preview finished."

# 强制覆盖模式
overwrite:
	@echo "⚠️  Generating redirects and overwriting existing files..."
	$(PYTHON) $(SCRIPT) --blog $(BLOG_DIR) --site $(SITE_DIR) --base $(BASE_URL) $(EXCLUDES) --overwrite
	@echo "✅ Redirects generated with overwrite."

# 清理旧 redirect 文件（可选）
clean:
	@echo "🧹 Cleaning all generated redirect files..."
	find $(SITE_DIR) -type f -path '*/[0-9][0-9][0-9][0-9]/*/index.html' -exec rm -f {} \;
	@echo "✅ Cleanup done."

.PHONY: all redirects preview overwrite clean
