import mcpunction as pn

class pkg(pn.Dtpk):
        def __init__(self):
                self.version="1.21.11"
                self.namespace="main"
                return
        def main(self,fn):
                with pn.Context(fn,"as @a"):
                        with pn.Block(fn) as fn:
                                fn.raw("hello")
                fn.raw("say hi")
                return
p=pkg()
pn.make(p,"../test_dtpk")
