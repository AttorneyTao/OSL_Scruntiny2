
 # -*- coding: gbk -*-
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

def simple_search(target_file_path,license_df):
    target_file=open(target_file_path)
    try:
        lines=target_file.readlines()
    except:
        print("{0} is not a source code file".format(target_file_path))
        return [0]
    keys_list=license_df["key_word"]
    res_list=[]
    for key in keys_list:
        pattern=re.compile(key)
        i=1
        for line in lines:
            temp=pattern.findall(line)
            i+=1
            if len(temp)>0:
                res=[target_file_path.replace(r"target_files/",""),i,license_df[license_df['key_word']==key]['name'].iloc[0],license_df[license_df['key_word']==key]['category'].iloc[0]]
                res_list.append(res)

    #print(res_dict_list)
    return res_list

    
if __name__=='__main__':
    license_df=read_license_lib()
    file_list=get_target_files()
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