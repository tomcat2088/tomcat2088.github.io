#!env python
# -*- coding: UTF-8 -*-

import time
filename_suffix = raw_input("请输入标题: ")
time_prefix = time.strftime("%Y-%m-%d", time.localtime())
time_content = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
file_name = str.format("./_posts/{0}-{1}.markdown", time_prefix, filename_suffix)
with open(file_name, "w") as file:
    file.write("---\n")
    file.write("layout: post\n")
    file.write("title: " + filename_suffix + "\n")
    file.write(str.format("date: {0} +0800\n", time_content))
    file.write("categories: 学习OpenGLES系列文章\n")
    file.write("---\n")

