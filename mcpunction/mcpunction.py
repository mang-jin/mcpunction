import inspect
import os
import shutil
from pathlib import Path
from functools import wraps
from types import MethodType

def assrt(cond,msg="Error occurred due to a bug. Please report it to mcpunction dev"):
        if not cond:
                raise AssertionError(msg)

version_table = [
        [11300,11404,4],
        [11500,11601,5],
        [11602,11605,6],
        [11700,11701,7],
        [11800,11801,8],
        [11802,11802,9],
        [11900,11903,10],
        [11904,11904,12],
        [12000,12001,15],
        [12002,12002,18],
        [12003,12004,26],
        [12005,12006,41],
        [12100,12101,48],
        [12102,12103,57],
        [12104,12104,61],
        [12105,12105,71],
        [12106,12106,80],
        [12107,12108,81],
        [12109,12110,88.0],
        [12111,12111,94.1],
]

def version_to_pack_format(version):
        versions=version.split(".")
        assrt(len(versions) == 2 or len(versions) == 3, "version must be like xx.xx.xx or xx.xx")
        int_version = 0
        for i,ver in enumerate(versions):
                int_version += int(ver)*(10**(4-i*2))
        pack_format = -1
        for ver_range in version_table:
                if ver_range[0] <= int_version <= ver_range[1]:
                        pack_format = ver_range[2]
                        break
        return pack_format

class UserData:
        def __init__(self,dtpks,version,output_path,namespace):
                self.pack_format=version_to_pack_format(version)
                self.fn_dir_name="function" if self.pack_format>=48 else "functions"
                self.func_dir_path=f"{output_path}/data/{namespace}/{self.fn_dir_name}"
                self.output_path=output_path
                self.dtpks=dtpks
                self.namespace=namespace
                self.cur_files=[]
                self.context=[]
        def make_fn_path(self,fn_name):
                return f"{self.func_dir_path}/{fn_name}.mcfunction"

user_data=None

def raw(*args):
        global user_data
        assrt(user_data and len(user_data.cur_files)>0 and len(user_data.context)>0)
                
        code=""
        if len(user_data.context[-1])>0:
                code+="execute "
                code+=''.join(user_data.context[-1])
                code+=" run "
        code+=''.join(args)

        print("wrote raw:",code,"to",user_data.cur_files[-1].name)
        user_data.cur_files[-1].write(f"{code}\n")

def wrapper(func,cls):
        if hasattr(func,"_mcpunction_wrapped"):
                return func
        @wraps(func)
        def inner(*args,**kwargs):
                global user_data
                assrt(user_data)
                is_init=kwargs.pop("_mcpunction_is_init",False)
                is_mac=getattr(func,"_mcpunction_ismac",False)
                if is_mac:
                        return func(*args,**kwargs)
                if is_init:
                        with open(user_data.make_fn_path(f"{cls.__name__}_{func.__name__}"),'w') as fn_file:
                                user_data.cur_files.append(fn_file)
                                user_data.context.append([])
                                func(args[0],user_data.dtpks,*args[1:],**kwargs)
                                user_data.context.pop()
                                user_data.cur_files.pop()
                else:
                        raw(f"function {user_data.namespace}:{cls.__name__}_{func.__name__}")
        inner._mcpunction_wrapped = True
        inner._mcpunction_fn_name = f"{cls.__name__}_{func.__name__}"
        return inner

def mac(func):
        func._mcpunction_ismac = True
        return func

def onload(func):
        func._mcpunction_onload = True
        return func

def ontick(func):
        func._mcpunction_ontick = True
        return func

def nowrap(func):
        func._mcpunction_nowrap = True
        return func

class Dtpk:
        def __init_subclass__(cls,**kwargs):
                super().__init_subclass__(**kwargs)

                if any(char.isupper() for char in cls.__name__):
                        raise AssertionError("클래스의 이름은 대문자를 포함할 수 없습니다"
                                             "(함수 이름에 클래스 이름이 포함되기 때문에 대문자가 들어가면 인식되지 않습니다)")

                for name, method in inspect.getmembers(cls, inspect.isfunction):
                        if name[0].isupper() or name.startswith("__") or hasattr(method,"_mcpunction_nowrap"):
                                continue
                        setattr(cls, name, wrapper(method,cls))
        # @nowrap
        # def Init(self,version):
        #         self.version=version

class Context:
        def __init__(self,context):
                self.context=context
        def __enter__(self):
                global user_data
                assrt(len(user_data.context)>0)
                user_data.context[-1].append(self.context)
        def __exit__(self,*exc):
                global user_data
                assrt(len(user_data.context)>0)
                user_data.context[-1].pop()
        def __add__(self,other):
                if not isinstance(other,Context):
                        return
                new_context = self.context+" "+other.context
                return Context(new_context)

block_id=0
class Block:
        # TODO: reset context when entered
        def __init__(self):
                global user_data,block_id
                assrt(user_data)

                block_file_name=f"{block_id}_block"
                raw(f"function {user_data.namespace}:{block_file_name}")

                self.path=user_data.make_fn_path(block_file_name)

                block_id+=1
        def __enter__(self):
                global user_data
                assrt(user_data and len(user_data.context)>0)
                user_data.context.append([])
                self.fn_file=open(self.path,'w')
                self.fn_file.__enter__()
                user_data.cur_files.append(self.fn_file)
        def __exit__(self,*exc):
                global user_data
                assrt(user_data and len(user_data.context)>0)
                user_data.context.pop()
                user_data.cur_files.pop()
                self.fn_file.__exit__(*exc)
               

def _compile_funcs(dtpk):
        global user_data
        assrt(user_data)

        load_funcs=[]
        tick_funcs=[]

        for name, method in inspect.getmembers(dtpk):
                if name[0].isupper() or name.startswith("__"):
                        continue
                if isinstance(method,MethodType) and not getattr(method,"_mcpunction_ismac",False) \
                   and not hasattr(method,"_mcpunction_nowrap"):
                        if getattr(method,"_mcpunction_onload",False):
                                load_funcs.append(f'"{user_data.namespace}:{getattr(method,"_mcpunction_fn_name")}"')
                        if getattr(method,"_mcpunction_ontick",False):
                                tick_funcs.append(f'"{user_data.namespace}:{getattr(method,"_mcpunction_fn_name")}"')
                        method(_mcpunction_is_init=True)
        return (load_funcs,tick_funcs)


def make(*dtpks,version="1.21.11",output_path="./dtpk",namespace="main",overwrite=False):

        global user_data
        user_data=UserData(dtpks,version,output_path,namespace)

        try:
                os.makedirs(output_path)
                os.makedirs(user_data.func_dir_path)
        except FileExistsError:
                if not overwrite:
                        yorn = input("이미 폴더가 존재합니다. 덮어쓰시겠습니까? (y/N): ").lower()
                        if yorn != 'y':
                                print("취소되었습니다.")
                                return
                shutil.rmtree(output_path)
                os.makedirs(user_data.func_dir_path)

        func_tags_dir = f"{user_data.output_path}/data/minecraft/tags/{user_data.fn_dir_name}"
        os.makedirs(func_tags_dir)
        load_funcs = []
        tick_funcs = []

        with open(f"{output_path}/pack.mcmeta",'w') as f:
                f.write(f'{{"pack":{{"description":"Made with McPunction","pack_format":{user_data.pack_format}}}}}')
                pass

        for dtpk in dtpks:
                (l_fn, t_fn) = _compile_funcs(dtpk)
                if len(l_fn): load_funcs.append(*l_fn)
                if len(t_fn): tick_funcs.append(*t_fn)

        with open(f"{func_tags_dir}/load.json",'w') as f:
                f.write('{"values":[')
                f.write(",".join(load_funcs))
                f.write(']}')                        
        with open(f"{func_tags_dir}/tick.json",'w') as f:
                f.write('{"values":[')
                f.write(",".join(tick_funcs))
                f.write(']}')
        print("Done.")
