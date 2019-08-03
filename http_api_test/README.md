# http_api_test

简单的接口自动化测试框架，仅学习使用，功能少，估计bug也很多，如果边学习边完善吧。

##  使用方法

1. 安装需要的模块，`pip install -r requirements.txt` 
2. 编辑conf.ini文件
3. 在testcases目录中填写测试用例的excel表格
4. 如果http请求需要上传文件，将文件放入res目录中
5. 执行run.py
6. 在logs目录中得到log，在reports目录中得到测试报告。log与测试报告会以邮件的方式发给conf.ini中填写的收件人

## 执行测试用例

测试用例的excel表格只能放在testcases目录下。

执行testcases目录下的所有测试用例表格：  
python run.py

执行指定excel中所有的测试用例：  
`python run.py <excel文件的名字>`
或者：  
`python run.py <excel文件的名字>.<工作表的名字>`

指定多张表格：  
`python run.py <excel文件的名字> <excel文件的名字>.<工作表的名字> ...`

## 设计说明

conf.ini中每个属性都有注释，这里不再赘述。

### 测试用例表格填写

测试用例表格中，几个字段说明一下：  
ignore：只要填写了，不管填了什么，都会忽略该测试用例。  
headers：填写为json格式

如果Content-Type为multipart/form-data，则body的格式如下：
```json
[
    //上传纯文本
    {
        "name": "key",
        "file_obj": "value"
    },
    //上传文件
    {
        "name": "key",
        //file_name是文件相对于res目录的路径
        "file_name": "file path",
        "Content-type": "mime type"
    }
    //...
]
```

statuscode：不填的话默认为200  

checkpoints：检查response body，body必须是json。  
checkpoints的格式如下  
相等：json表达式==python支持的数据类型（int、str、bool、None）  
使用正则表达式搜索：json表达式=~字符串  
支持同时使用多个检查点，用换行符隔开  
例如：  
$.id==12345  
$.name==None  
$.ok==True  

setprops：将response body中的属性保存下来，供后续的测试用例使用。  
格式："key"="json表达式"  
保存下来的属性都会被转化成字符产，在后续测试用例的url、headers、body中可以使用{{key}}获得先前保存的属性的值。

### 项目工程目录结构

- base：放代码的
- HtmlTestRunner：网上找的，输出html测试报告。不用pip安装，而是直接放在项目中，因为它生成的测试报告没有显示指定为utf-8，我要改它的代码。
- logs：放log的
- reports：放测试报告的
- res：放需要被http请求上传的文件的
- testcases：放测试用例表格的
- tests：放单元测试的
- conf.ini：配置文件
- run.py：执行文件

## 用到的第三方模块

- ddt：自动将多组数据代入testcase中，效果类似于unittest的subTest，但是更方便。参考博客[python ddt 实现数据驱动一](https://www.cnblogs.com/nancyzhu/p/8563884.html)
- openpyxl：操作excel。参考博客[OpenPyXL的使用教程（一）](https://www.jianshu.com/p/642456aa93e2)
- requests
- HtmlTestRunner：生成html格式的测试报告
- jsonpath2：处理json表达式的。参考[jsonpath2 doc](https://jsonpath2.readthedocs.io/en/latest/index.html)

