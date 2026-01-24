import mcpunction as pn

name="Steve"

class lib(pn.Dtpk):
        def func(self,*libs):
                global name
                pn.raw(f"say Hello, {name}")

class pkg(pn.Dtpk):
        def func(self,*libs):
                pn.raw("say Hello from Pkg!")
        @pn.onload
        def main(self,*_):
                self.func()

pn.make(pkg(),version="1.21.11",output_path="../test_dtpk",overwrite=True)
