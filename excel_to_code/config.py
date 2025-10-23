#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件
"""

# LLM 配置
LLM_PROVIDER = "gemini"  # 選項: "gemini", "anthropic", "openai", "local"
API_KEY = None  # 從環境變數讀取或在此設置
MODEL_NAME = "gemini-2.0-flash-exp"  # 或其他模型

# Gemini 配置
GEMINI_API_KEY = None  # 或設置環境變數 GEMINI_API_KEY
GEMINI_MODEL = "gemini-2.0-flash-exp"

# Anthropic 配置
ANTHROPIC_API_KEY = None  # 或設置環境變數 ANTHROPIC_API_KEY
ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"

# OpenAI 配置
OPENAI_API_KEY = None  # 或設置環境變數 OPENAI_API_KEY
OPENAI_MODEL = "gpt-4"

# 輸出配置
OUTPUT_DIR = "output"
CONTEXTS_DIR = f"{OUTPUT_DIR}/contexts"
PROMPTS_DIR = f"{OUTPUT_DIR}/prompts"
GENERATED_CODE_DIR = f"{OUTPUT_DIR}/generated_code"
REPORTS_DIR = f"{OUTPUT_DIR}/reports"

# 驗證配置
VALIDATION_RTOL = 1e-5  # 相對誤差容忍度
VALIDATION_ATOL = 1e-8  # 絕對誤差容忍度

# 提取配置
EXTRACT_VBA = True
DETECT_PATTERNS = True
ANALYZE_DEPENDENCIES = True

# 代碼生成配置
GENERATE_TESTS = True
GENERATE_DOCS = True
CODE_STYLE = "black"  # black, pep8

# 性能配置
MAX_CONTEXT_LENGTH = 100000  # 最大上下文長度（字符）
ENABLE_CACHING = True
