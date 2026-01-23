import inspect
import os
import shutil
from pathlib import Path
from functools import wraps
from types import MethodType

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
        assert len(versions) == 2 or len(versions) == 3 and "version must be like xx.xx.xx or xx.xx"
        int_version = 0
        for i,ver in enumerate(versions):
                int_version += int(ver)*(10**(4-i*2))
        pack_format = -1
        for ver_range in version_table:
                if ver_range[0] <= int_version <= ver_range[1]:
                        pack_format = ver_range[2]
                        break
        return pack_format

class FnBuilder:
        def __init__(self,user_data,output_path):
                self.user_data=user_data
                self.output_path=user_data["make_fn_path"](output_path)
                self.context=[]
        def raw(self,*args):
                print(f"output_path: {self.output_path}, context: {self.context}")
                code="".join(args)
                print("wrote raw:",code)
        def close(self):
                print("FnBuilder Closed")

def get_fn_dir(pack_format):
        return "function" if pack_format>=48 else "functions"

def wrapper(func,cls):
        if hasattr(func,"_mcpunction_wrapped"):
                return func

        @wraps(func)
        def inner(*args,**kwargs):
                user_data=kwargs.pop("_mcpunction_dtpk_data",None)
                is_init=True if user_data else False
                is_mac=getattr(func,"_mcpunction_ismac",False)
                if is_mac:
                        return func(*args,**kwargs)
                if is_init:
                        builder=FnBuilder(user_data,f"{cls.__name__}_{func.__name__}")
                        func(user_data["dtpk"],builder)
                        builder.close()
                else:
                        if len(args)>1 or len(kwargs)>0:
                                raise ValueError("마인크래프트 함수는 인자를 받을 수 없습니다")
                        raw(f"function main:{cls.__name__}_{func.__name__}")
        inner._mcpunction_wrapped = True
        return inner

class Dtpk:
        def __init_subclass__(cls,**kwargs):
                super().__init_subclass__(**kwargs)

                for name, method in inspect.getmembers(cls, inspect.isfunction):
                        if name[0].isupper() or name.startswith("__"):
                                continue
                        setattr(cls, name, wrapper(method,cls))

class Context:
        def __init__(self,func_builder,context):
                self.context=context
                self.builder=func_builder
        def __enter__(self):
                self.builder.context.append(self.context)
        def __exit__(self,*exec):
                self.builder.context.pop()
        def __add__(self,other):
                if not isinstance(other,Context):
                        return
                new_context = self.context+" "+other.context
                return Context(new_context)

block_id=0

class Block:
        def __init__(self,fn):
                global block_id

                block_file_name=f"{block_id}_block.mcfunction"
                fn.raw(f"function {fn.user_data['namespace']}:{block_id}_block")

                self.fn=FnBuilder(fn.user_data,block_file_name)

                block_id+=1
        def __enter__(self):
                return self.fn
        def __exit__(self,*exec):
                self.fn.close()
                
def mac(func):
        func._mcpunction_ismac = True
        return func

def onload(func):
        func._mcpunction_onload = True
        return func

def ontick(func):
        func._mcpunction_ontick = True
        return func

def make(dtpk: Dtpk,output_path: str,namespace="main"):
        pack_format=version_to_pack_format(dtpk.version)
        fn_dir_name="function" if pack_format>=48 else "functions"
        func_dir_path=f"{output_path}/data/{namespace}/{fn_dir_name}"
        def make_fn_path(fn_name):
                return f"{func_dir_path}/{fn_name}.mcfunction"
        dtpk_data = {
                "make_fn_path": make_fn_path,
                "func_dir_path": func_dir_path,
                "namespace": namespace,
                "dtpk": dtpk,
        }
        for name, method in inspect.getmembers(dtpk):
                if name[0].isupper() or name.startswith("__"):
                        continue
                if isinstance(method,MethodType) and not getattr(method,"_mcpunction_ismac",False):
                        method(_mcpunction_dtpk_data=dtpk_data)
        

# class Maker:
#         def make(self,dtpk,output_path,overwrite=False):
#                 self.dtpk=dtpk
#                 self.output_path=output_path
#                 self.namespace=dtpk.namespace
#                 self.pack_format=version_to_pack_format(self.dtpk.version)                
#                 if not hasattr(cur_dtpk,"context") or not isinstance(cur_dtpk.context,list):
#                         self.dtpk.context=[]
#                 self.function_dir_name = "function" if self.pack_format >= 48 else "functions"
#                 print(f"datapack output path = {self.output_path}")
#                 print(f"datapack namespace = {self.namespace}")
#                 print(f"datapack pack_format = {self.pack_format}")
#                 self.func_dir_path=f"{self.output_path}/data/{self.namespace}/{self.function_dir_name}"
#                 try:
#                         os.makedirs(self.output_path)
#                         os.makedirs(self.func_dir_path)
#                 except FileExistsError:
#                         if not overwrite:
#                                 yorn = input("이미 폴더가 존재합니다. 덮어쓰시겠습니까? (y/N): ").lower()
#                                 if yorn != "y":
#                                         print("취소되었습니다.")
#                                         return
#                         shutil.rmtree(self.output_path)
#                         os.makedirs(self.func_dir_path)
#                 self.func_tags_dir = f"{self.output_path}/data/minecraft/tags/{self.function_dir_name}"
#                 os.makedirs(self.func_tags_dir)
#                 self.load_funcs = []
#                 self.tick_funcs = []

#                 with open(f"{output_path}/pack.mcmeta",'w') as f:
#                         f.write(f'{{"pack":{{"description":"Made with McPunction","pack_format":{self.pack_format}}}}}')
#                 for name, method in inspect.getmembers(self.dtpk):
#                         if name[0].isupper() or name.startswith("__"):
#                                 continue
#                         if isinstance(method,MethodType) and not getattr(method,"_mcpunction_ismac",False):
#                                 with open(f"{self.output_path}/data/{self.namespace}/{self.function_dir_name}/{name}.mcfunction",'w') as cur_file:
#                                         self.cur_file=cur_file
#                                         if getattr(method,"_mcpunction_onload",False):
#                                                 load_funcs.append(f'"{self.namespace}:{name}"')
#                                         if getattr(method,"_mcpunction_ontick",False):
#                                                 tick_funcs.append(f'"{self.namespace}:{name}"')
#                                         method(_mcpuntion_funcinit=True)
#                 with open(f"{self.func_tags_dir}/load.json",'w') as f:
#                         f.write('{"values":[')
#                         f.write(",".join(self.load_funcs))
#                         f.write(']}')                        
#                 with open(f"{self.func_tags_dir}/tick.json",'w') as f:
#                         f.write('{"values":[')
#                         f.write(",".join(self.tick_funcs))
#                         f.write(']}')
#                 self.cur_file=None
#                 self.dtpk=None
#                 print("생성 완료")

