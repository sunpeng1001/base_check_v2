# coding=utf-8
import sys
import os
import inspect
import ast
import ConfigParser
from collections import OrderedDict
from base_check.common import log as logging


LOG = logging.getLogger(__name__)
# records the classes and methods which need to run in the module
# {module_name: {class_name: [method1_name, method2_name, ...]}}
# eg: {'base_check.checks.network.demo.check':
#           {'Demo': ['check_baz', 'check_foo', 'check_bar']}}
# 使用OrderedDict代替dict，OrderedDict.keys()获取到key的顺序和
# OrderedDict.setdefault设置key的顺序一致
_need_checks = OrderedDict()
_check_faileds = []


def import_module(import_str):
    """Import a module."""
    __import__(import_str)
    return sys.modules[import_str]


def find_files(dirname, exts):
    """Use os.walk to find all files with particular extension"""
    for root, dirs, files in os.walk(dirname):
        for basename in files:
            _ext = os.path.splitext(basename)[1]
            if _ext in exts:
                filename = os.path.join(root, basename)
                yield filename


def import_module_and_dir(mod_str):
    """import module and all submodules

    If module.__file__ is __init__.py or __init__.pyc, try to find
    all *.py or *.pyc files in the directory and import them.
    """
    exts = ['.py', '.pyc']
    # import current mod_str
    mod = import_module(mod_str)
    mod_file = os.path.abspath(mod.__file__)
    dirname, basename = os.path.split(mod_file)
    root, ext = os.path.splitext(basename)
    # If file is __init__.py or __init__.pyc, it's a directory
    if root == '__init__' and ext in exts:
        LOG.trace('import dirname:%s' % dirname)
        sub_files = find_files(dirname, exts)
        for sub_file in sub_files:
            # import all files end with .py or .pyc
            relative_path = os.path.relpath(sub_file, dirname)
            LOG.trace(relative_path)
            relative_root = os.path.splitext(relative_path)[0]
            sub_mod = '%s.%s' % (mod_str, relative_root.replace(os.sep, '.'))
            import_module(sub_mod)


def import_module_list(modules):
    for mod_str in modules:
        import_module_and_dir(mod_str)


class CheckMeta(type):
    """Metaclass for defining Check classes."""
    def __new__(cls, name, bases, attrs):
        """
        :param name: 类的名称
        :param bases: 基类列表
        :param attrs: 类中的method列表
        """
        new_cls = super(CheckMeta, cls).__new__(cls, name, bases, attrs)
        # 元类继承自type类，当__metaclass__为CheckMeta的类被import时，
        # CheckMeta的__new__方法会被调用。当被创建的类继承自BaseCheck时，
        # 就认为该类是需要被调用check的类。
        if name != 'BaseCheck' and BaseCheck in bases:
            mod = new_cls.__module__
            _need_checks.setdefault(mod, OrderedDict())
            _need_checks[mod].setdefault(name, [])
            for k, v in attrs.items():
                # 如果attr是以'check_'开头的方法，就记录到_need_checks中，
                if (k.startswith('check_') and
                        inspect.isfunction(v) or inspect.ismethod(v)):
                    _need_checks[mod][name].append(k)
        return new_cls


class BaseCheck(object):
    """
    when the module be imported , the metaclass will record
    module's method which starts with 'check_' to dict '_need_check'
    """
    __metaclass__ = CheckMeta

    def __init__(self, cf=None):
        self.cf = cf
        self.check_result = {}

    def failed(self, msg=None):
        """record failed msgs, get msgs by get_all_fails"""
        args = None
        caller = inspect.stack()[1]
        filename = caller[1]
        line = caller[2]
        func = caller[3]
        # 通过inspect.stack获取调用栈信息，如果check_XX方法中调用了
        # self.failed，将该方法对应的执行结果设置为False
        self.check_result[func] = False
        if self.cf is not None:
            args = self.cf.items(func)
        caller_str = ('%s:%s [%s] args:%s msg:%s' %
                      (filename, line, func, args, msg))
        _check_faileds.append(caller_str)


class DictObj(dict):
    """inherit from dict

    Can use '.' method to get key
    """
    def __init__(self, d):
        for a, b in d.items():
            if isinstance(b, (list, tuple)):
                setattr(self, a, [DictObj(x) if isinstance(x, dict)
                                  else x for x in b])
            else:
                setattr(self, a, DictObj(b) if isinstance(b, dict) else b)
        return super(DictObj, self).__init__(d)


def config_items_to_obj(items):
    """
    convert the data of ConfigParser.items(section) to DictObj
    which inherts from dict.
    """
    d = {}
    for x, y in items:
        try:
            d[x] = ast.literal_eval(y)
        except SyntaxError:
            d[x] = y
    return DictObj(d)


def get_configparser(mod_name):
    """create ConfigParser from module dir .conf files"""
    mod = sys.modules[mod_name]
    dirname = os.path.dirname(os.path.abspath(mod.__file__))
    basename = mod_name.split('.')[-1]
    foldername = os.path.basename(dirname)
    cf = ConfigParser.ConfigParser()
    # 首先读取和目录名称相同的conf文件，再读取和要运行module
    # 名称相同的conf文件
    for name in [foldername, basename]:
        name = '%s.conf' % name
        config_name = os.path.join(dirname, name)
        if os.path.exists(config_name):
            cf.read(config_name)
    return cf


def do_check_module(mod_name, cf=None):
    """
    Run the module's all check methods which were
    recorded in _need_checks
    """
    if cf is None:
        cf = get_configparser(mod_name)
    mod = sys.modules[mod_name]
    # cls_info records the class and method in the module
    # {'Demo': ['check_baz', 'check_foo', 'check_bar']}
    cls_info = _need_checks.get(mod_name, {})
    for cls_name, methods in cls_info.items():
        cls = getattr(mod, cls_name)
        obj = cls(cf)
        for method in methods:
            obj.check_result[method] = True
            check = getattr(obj, method)
            # if the method has configuration in config file, call
            # method with arg
            if cf is not None and cf.has_section(method):
                arg = config_items_to_obj(cf.items(method))
                check(arg)
            else:
                try:
                    check()
                except TypeError, e:
                    LOG.error('%s.%s.%s TypeError, %s',
                              mod_name, cls_name, method, e)

            if obj.check_result[method]:
                LOG.trace('%s.%s.%s check passed!',
                          mod_name, cls_name, method)


def run_all_checks(modules=None):
    """run all checks which have been imported

    1. modules为None，按照key的顺序执行_need_checks中的所有check方法
    2. modules为list，遍历modules，查找_need_checks对应的keys执行check方法

    :param modules: a list of modules
    """
    LOG.trace(_need_checks)
    final_check_modules = []
    if modules is None:
        final_check_modules = _need_checks.keys()
    else:
        for mod_name in modules:
            if mod_name in _need_checks:
                final_check_modules.append(mod_name)
            else:
                # 查找_need_checks中以parent_name开头的keys
                parent_name = '%s.' % mod_name
                final_check_modules += [mod for mod in _need_checks.keys()
                                        if mod.startswith(parent_name)]
    for mod_name in final_check_modules:
        do_check_module(mod_name)


def check_all_passed():
    """detect whether all check passed"""
    return len(_check_faileds) == 0


def get_all_fails():
    """get all msgs recorded by self.failed method"""
    return _check_faileds
