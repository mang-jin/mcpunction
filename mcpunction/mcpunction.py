import inspect
import os
import shutil
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

cur_file=None
cur_dtpk=None
block_count=0

def raw(*args):
        global cur_file,cur_dtpk
        assert cur_file and cur_dtpk
        code="".join(args)
        context=" ".join(cur_dtpk._mcpunction_contexts)
        print("contexts:",cur_dtpk._mcpunction_contexts)
        print("code:",code)
        if cur_dtpk._mcpunction_contexts:
                cur_file.write(f"execute {context} run ")
        cur_file.write(code+"\n")

def wrapper(func):
        if hasattr(func,"_mcpunction_wrapped"):
                return func

        @wraps(func)
        def inner(*args,**kwargs):
                global cur_file,cur_dtpk
                is_init=kwargs.pop("_mcpuntion_funcinit",False)
                is_mac=getattr(func,"_mcpunction_ismac",False)
                if is_init or is_mac:
                        if is_init:
                                last= cur_dtpk._mcpunction_contexts if hasattr(cur_dtpk,"_mcpunction_contexts") else []
                                cur_dtpk._mcpunction_contexts=[]
                        result = func(*args,**kwargs)
                        cur_dtpk._mcpunction_contexts=last
                        return result
                else:
                        raw(f"function main:{func.__name__}")
        inner._mcpunction_wrapped = True
        return inner

class Dtpk:
        def __init_subclass__(cls,**kwargs):
                super().__init_subclass__(**kwargs)

                for name, method in inspect.getmembers(cls, inspect.isfunction):
                        if name[0].isupper() or name.startswith("__"):
                                continue
                        setattr(cls, name, wrapper(method))

class Context:
        def __init__(self,context):
                self.context=context
        def __enter__(self):
                global cur_dtpk
                cur_dtpk._mcpunction_contexts.append(self.context)
        def __exit__(self,*exec):
                cur_dtpk._mcpunction_contexts.pop()
        def __add__(self,other):
                if not isinstance(other,Context):
                        return
                new_context = self.context+" "+other.context
                return Context(new_context)

class Block:
        # TODO: implement Block
        def __init__(self,context):
                self.context=context
        def __enter__(self):
                global cur_dtpk,cur_file
                self.last=cur_file
                cur_file=open("",'w')
        def __exit__(self,*exec):
                cur_dtpk.context.pop()
        def __add__(self,other):
                if not isinstance(other,Context):
                        return
                new_context = self.context+" "+other.context
                return Context(new_context)
                
def mac(func):
        func._mcpunction_ismac = True
        return func

def onload(func):
        func._mcpunction_onload = True
        return func

def ontick(func):
        func._mcpunction_ontick = True
        return func

def make(pkg,output_path,overwrite=False):
        global cur_file,cur_dtpk,cur_func_dir_path
        cur_dtpk=pkg
        namespace=pkg.namespace
        pack_format=version_to_pack_format(pkg.version)
        if not hasattr(cur_dtpk,"context") or not isinstance(cur_dtpk.context,list):
                cur_dtpk.context=[]

        function_dir_name = "function" if pack_format >= 48 else "functions"

        print(f"datapack output path = {output_path}")
        print(f"datapack namespace = {namespace}")
        print(f"datapack pack_format = {pack_format}")
        func_dir_path=f"{output_path}/data/{namespace}/{function_dir_name}"
        cur_func_dir_path=func_dir_path
        try:
                os.makedirs(output_path)
                os.makedirs(func_dir_path)
        except FileExistsError:
                if not overwrite:
                        yorn = input("이미 폴더가 존재합니다. 덮어쓰시겠습니까? (y/N): ").lower()
                        if yorn != "y":
                                print("취소되었습니다.")
                                return
                shutil.rmtree(output_path)
                os.makedirs(func_dir_path)
        func_tags_dir = f"{output_path}/data/minecraft/tags/{function_dir_name}"
        os.makedirs(func_tags_dir)
        load_funcs = []
        tick_funcs = []

        with open(f"{output_path}/pack.mcmeta",'w') as f:
                f.write(f'{{"pack":{{"description":"Made with McPunction","pack_format":{pack_format}}}}}')

        for name, method in inspect.getmembers(pkg):
                if name[0].isupper() or name.startswith("__"):
                        continue
                if isinstance(method,MethodType) and not getattr(method,"_mcpunction_ismac",False):
                        cur_file=open(f"{output_path}/data/{namespace}/{function_dir_name}/{name}.mcfunction",'w')
                        if getattr(method,"_mcpunction_onload",False):
                                load_funcs.append(f'"{namespace}:{name}"')
                        if getattr(method,"_mcpunction_ontick",False):
                                tick_funcs.append(f'"{namespace}:{name}"')
                        method(_mcpuntion_funcinit=True)
                        cur_file.close()
        with open(f"{func_tags_dir}/load.json",'w') as f:
                f.write('{"values":[')
                f.write(",".join(load_funcs))
                f.write(']}')                        
        with open(f"{func_tags_dir}/tick.json",'w') as f:
                f.write('{"values":[')
                f.write(",".join(tick_funcs))
                f.write(']}')
        cur_file=None
        cur_dtpk=None
        print("생성 완료")
