import mcpunction as pn

class pkg(pn.Dtpk):
        def __init__(self):
                self.version="1.21.11"
                self.namespace="main"
        @pn.onload
        def main(self):
                pn.raw("say Hello, World!")
p=pkg()
pn.make(p,"../test_dtpk")
