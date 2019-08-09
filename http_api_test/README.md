# http api test

简单的接口自动化测试框架，在excel中填写测试用例，执行后输出测试报告。测试报告格式如下：

![](https://wx3.sinaimg.cn/mw690/a9ab7d54ly1g5tt4jzs8gj20rf0het9n.jpg)

##  使用流程

1. 安装需要的模块，`pip install -r requirements.txt` 
2. 编辑conf.ini文件
3. 在testcases目录中填写测试用例的excel表格
4. 将http请求需要用到的文件放入res目录中
5. 执行run.py
6. 执行完成后，log输出在logs目录中，测试报告输出在reports目录中，log与测试报告以邮件的方式发出

### debug模式

在conf.ini中将Debug设置为true，有如下效果：

1. logger的level设置为debug，能打印更多log
2. log输出到屏幕而不是生成文件
3. 不生成report文件
4. 测试用例中设置的属性保存到文件props，debug模式运行的测试用例会从props文件中读取属性
5. 不发送邮件

## 工程目录结构

- base：放代码的
- HtmlTestRunner：网上找的，输出html测试报告。不用pip安装，因为我要改它代码。
- logs：放log的
- reports：放测试报告的
- res：放http请求需要用到的文件的
- testcases：放测试用例表格的
- tests：放单元测试的
- conf.ini：配置文件
- props：debug模式下用来存储属性的
- run.py：程序入口

## 具体使用方法

### 编辑conf.ini

conf.ini文件中有详细的注释，此处不再赘述

### 编辑测试用例表格

测试用例表格的格式必须为xlsx！！！

测试用例表格中的各个字段的说明如下：

|字段名|说明|
|-|-|
|id||
|name||
|ignore|只要填了，就忽略当前测试用例，一般填个 y|
|method|http请求方法|
|url||
|params|http请求的参数，一般用在get请求上，使用json格式填写|
|headers|使用json格式填写|
|body|见下文详细说明|
|timeout|单位秒，不填就默认5秒|
|statuscode|预期的statuscode，不填就默认200|
|checkpoints|见下文详细说明|
|setprops|见下文详细说明|

#### body

如果content-type不是multipart/form-data，则body中填写相应格式的内容。  
比如content-type为application/x-www-form-urlencoded，则需要手动将内容做url编码后再填入，这个工具不会自动给body编码。

如果content-type是multipart/form-data，则填写的格式如下：

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
        //比如将1.jpg放在res目录中，则只需要填写1.jpg即可，不用再加路径
        "file_name": "file path",
        "Content-type": "mime type"
    }
    //...
]
```

#### checkpoints

检查response body是否符合要求，body必须是json，如果body不是json，那就不要填checkpoints。  

checkpoints的格式如下：  
**相等**：json表达式==python支持的数据类型（int、str、bool、None）  
**使用正则表达式搜索**：json表达式=~字符串  
还支持**<、>、<=、>=、!=**这种比较运算符。

支持同时使用多个检查点，用换行符隔开  
例如：  
$.id==12345  
$.name==None  
$.ok==True  
$.msg=='message'

#### setprops

将response body中的属性保存下来，供后续的测试用例使用。  
普通模式会将属性保存再全局变量props中，debug会保存在文件props中。

格式："key"="json表达式"  
保存下来的属性都会被转化成字符串，在后续测试用例的url、headers、body中可以使用{{key}}获得先前保存的属性的值。

一个测试用例可以保存多个属性，也就是说可以在setprops中填写多条记录，用换行符隔开。

### 执行

执行testcases目录下的所有测试用例表格：  
`python run.py`

执行指定excel中所有的测试用例：  
因为测试用例的表格必须为xlsx格式，且必须放在testcases目录下，所以这里只需要指定表格名字，不需要路径和后缀名。  
`python run.py <excel文件的名字>`
或者执行excel文件中的某一个sheet：  
`python run.py <excel文件的名字>.<工作表的名字>`

指定多张表格：  
`python run.py <excel文件的名字> <excel文件的名字>.<工作表的名字> ...`


## 用到的第三方模块

- ddt：自动将多组数据代入testcase中，效果类似于unittest的subTest，但是更方便。参考博客[python ddt 实现数据驱动一](https://www.cnblogs.com/nancyzhu/p/8563884.html)
- openpyxl：操作excel。参考博客[OpenPyXL的使用教程（一）](https://www.jianshu.com/p/642456aa93e2)
- requests
- HtmlTestRunner：生成html格式的测试报告
- jsonpath2：处理json表达式的。参考[jsonpath2 doc](https://jsonpath2.readthedocs.io/en/latest/index.html)

