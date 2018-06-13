### 运行程序:
```
$ python base_check/main.py
```
+ --log-file-level: 设置日志文件的打印等级
+ --log-stdout-level: 设置标准输出的打印等级
+ --log-file: 设置日志文件路径，默认输出到/tmp/base_check/base_check.log

### pep8检测
```
tox -e pep8
```
+ 在tox.ini中配置[flake8]，对flak8进行配置
+ [flake8]中配置max-complexity = 10对代码复杂度进行检查，nova配置的是35
