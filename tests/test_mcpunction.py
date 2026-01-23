import mcpunction as pn

class pkg(pn.Dtpk):
        def __init__(self):
                self.version="1.21.11"
                self.namespace="main"
                return
        def func(self):
                pn.raw("say Hello, World!")
        def main(self):
                with pn.Block():
                        self.func()
                pn.raw("say hi")
                return
p=pkg()
pn.make(p,"../test_dtpk")
