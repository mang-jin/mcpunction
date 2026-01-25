import mcpunction as pn

name="Steve"

class lib(pn.Dtpk):
        def func(self):
                global name
                pn.raw(f"say Hello, {name}")

class pkg(pn.Dtpk):
        def __init__(self):
                self.lib=lib()
        def func(self):
                pn.raw("say Hello from Pkg!")
        @pn.onload
        def main(self):
                global libs
                libs["lib"].func()
                self.func()

libs={
        "pkg":pkg(),
        "lib":lib()
}

pn.make(libs,version="1.21.11",output_path="../test_dtpk",overwrite=True)
