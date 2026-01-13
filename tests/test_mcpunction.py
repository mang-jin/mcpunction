import mcpunction as pn

class pkg(pn.Dtpk):
        def __init__(self):
                self.version="1.21.11"
                self.namespace="main"
        @pn.mac
        def get_nearby_entities(self):
                return pn.Context("as @e[distance=..5]")
        @pn.onload
        def main(self):
                with self.get_nearby_entities():
                        pn.raw("say hello")
                        pn.raw("kill @s")
                with pn.Context("as @a"):
                        pn.raw("say hi")
p=pkg()
pn.make(p,"../test_dtpk")
