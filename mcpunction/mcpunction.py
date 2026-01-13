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

def raw(*args):
        global cur_file
        assert cur_file
        code="".join(args)
        print(f"wrote text to {cur_file.name}: {code}")
        cur_file.write(code+"\n")

def wrapper(func):
        @wraps(func)
        def inner(*args,**kwargs):
                global cur_file
                print(f"[{func.__name__}] CUR FILE: {cur_file.name}")
                if kwargs.pop("_mcpuntion_funcinit",False) or getattr(func,"_mcpunction_ismac",False):
                        result = func(*args,**kwargs)
                        return result
                else:
                        raw(f"function main:{func.__name__}")
        return inner

class Dtpk:
        def __init_subclass__(cls,**kwargs):
                super().__init_subclass__(**kwargs)

                for name, method in inspect.getmembers(cls, inspect.isfunction):
                        if name[0].isupper() or name.startswith("__"):
                                continue
                        setattr(cls, name, wrapper(method))
                
def mac(func):
        func._mcpunction_ismac = True
        return func

def onload(func):
        func._mcpunction_onload = True
        return func

def ontick(func):
        func._mcpunction_ontick = True
        return func

def make(pkg,output_path):
        namespace=pkg.namespace
        pack_format=version_to_pack_format(pkg.version)

        function_dir_name = "function" if pack_format >= 48 else "functions"

        print(f"datapack output path = {output_path}")
        print(f"datapack namespace = {namespace}")
        print(f"datapack pack_format = {pack_format}")
        func_dir_path=f"{output_path}/data/{namespace}/{function_dir_name}"
        try:
                os.makedirs(output_path)
                os.makedirs(func_dir_path)
        except FileExistsError:
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
        print("="*50)

        global cur_file
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
