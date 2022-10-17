
 # -*- coding: utf-8-*-
 #待解决问题：
"""Copyright <YEAR> <COPYRIGHT HOLDER>

Permission is hereby granted, free of charge, 
to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit 
persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or 
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", 
WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. 
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import os
from typing import KeysView
import numpy as np
import pandas as pd
import re
import chardet
import time
import timeout_decorator
TIMEOUT=5

def read_license_lib():
    """获取license_lib.csv文件中的开源协议列表，返回值为df,
    df["name"]:协议名
    df["abbr"]:协议简称
    df["key_word"]:用于识别协议的关键字
    df["license_head"]:使用该协议的文件头
    df["license_fulltext"]:协议全文
    df["category"]:协议分类，分为copyleft和permissive两类
      """
    df=pd.read_excel(r"license_lib.xlsx")
    #if __debug__:
       # print("fulltext:{full}\nkeyword:{key}".format(full=df["license_fulltext"],key=df["key_word"]))
    return df

def encoding_det(target_file_path):
    """
    检测文件编码类型
    Parameters:
    target_file_path:目标文件路径
    Return:
    <string>
    """
    f=open(file=target_file_path,mode='rb')
    data=f.read()
    f.close()
    print("detecting {0}".format(target_file_path))
    res=chardet.detect(data)
    print("{0} is encoded by {1}".format(target_file_path,res))
    return(res['encoding'])


def get_target_files():
    """获取target_files文件夹下的所有文件清单"""
    file_list=[]
    i=0
    for root,dirs,files in os.walk(r"target_files"):
        if i>=0:  #废代码，加着玩的
            j=0
            for f in files:
                f=root+"\\"+f
                files[j]=f
                j+=1
        file_list+=files
        i+=1
        
    return file_list
def process_keys_list(keys_list):
    """
    对关键词进行预处理，插入\s代替原来的所有空格，防止出现多空格或特殊空格影响搜索
    """
    res=[]
    for key in keys_list:
        res.append(key.replace(' ',r'\s+'))
    print(res)
    return res
def lines_combine(lines):
    """
    将多行的字符合并到一个字符中
    """
    res_str=""
    for line in lines:
        res_str+=line
    #print(res_str)
    return res_str

def clear_comment_mark(code_text):
    cmt_mk=[r'//',r"#",r'"""',r'',r"/*",r"*/",r"*"]
    for mk in cmt_mk:
        code_text=code_text.replace(mk,"")
    print(code_text)
    return code_text
def count_lines(text,pos):
    """数字符串中的索引对应的行数"""
    i=0
    for c in text[0:pos]:
        if c=='\n':
            i+=1;
    return i
def simple_search(target_file_path,license_df):
    """以正则表达式方法识别开源许可证文件
    parameters:
    target_file_path:目标文件路径
    license_df:许可证列表
      """
    enc=encoding_det(target_file_path)

    target_file=open(target_file_path,encoding=enc)
    try:
        print("reading {0}".format(target_file_path))
        lines=target_file.readlines()
        line=lines_combine(lines)
        line=clear_comment_mark(line)
    except:
        print("{0} is not a readable file".format(target_file_path,enc))
        return [0]

    keys_list=license_df["key_word"]
    keys_list=process_keys_list(keys_list)
    res_list=[]
    for key in keys_list:
        pattern=re.compile(key,re.IGNORECASE)
        i=1

        temp=pattern.findall(line)
        i+=1
        if len(temp)>0:
            pos=line.index(temp[0])
            lc=count_lines(line,pos)
            res=[target_file_path.replace(r"target_files/",""),lc,license_df[license_df['key_word']==key.replace(r'\s+',' ')]['name'].iloc[0],license_df[license_df['key_word']==key.replace(r'\s+',' ')]['category'].iloc[0]]
            res_list.append(res)

    #print(res_dict_list)
    target_file.close()
    return res_list

def file_screen(file_list,stop_list=['.xlsx','.doc','.pptx','.ppt','.sln','.svg','.pdf','.docx','.jpg','.png','.ipch']):
    """
    用于筛选无需审查的文件，主要有.xlsx,.docx,.pptx,.sln
    可随使用情况添加
    """
    res=file_list.copy()
    print("deleting none source files")
    for f in file_list:
        if os.path.splitext(f)[-1] in stop_list:
            print("{0} is removed".format(f))
            res.remove(f)
    return res
    
if __name__=='__main__':
    license_df=read_license_lib()
    file_list=get_target_files()
    file_list=file_screen(file_list)
    target_file_path=r"target_files/"
    res_list=[]
    for target_file in file_list:
        target_file=target_file.replace("target_files\\","")
        res=simple_search(target_file_path+target_file,license_df)
        if res==[0]:
            continue
        else:
            print("检索 {0}后发现{1}处开源许可证特征点".format(target_file,len(res)))
            res_list+=res
            res=[]
    res_df=pd.DataFrame(res_list,columns=["file_name","line","license_name","catagory"])
    res_df.to_excel("Scrutiny_result.xlsx")