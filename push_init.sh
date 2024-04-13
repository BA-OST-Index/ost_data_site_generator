#!/bin/bash

# ----------------------------------------------------
# BA OST Index 全自动化脚本 V1.0
# 为去掉中间过程，使checkout时更快，遂于是决定将整个流程进行
# 完全统一，进行一个mono script的写（不是
# ----------------------------------------------------

# 首先新建全部文件夹，不管是否存在
mkdir -p data_html exported_data

# 然后 clone 一下 ost_data_parser
git clone https://github.com/BA-OST-Index/ost_data_parser.git data_parser

# clone 一下 ost_data
cd data_parser
git clone https://github.com/BA-OST-Index/ost_data.git data
mkdir -p data_export

# 继续装requirements
pip install -r requirements.txt

# 在？弄个 symbolic link 保持向下兼容
cd ..
rm -rf exported_data
ln -s ./data_parser/data_export ./exported_data