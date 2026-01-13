import mcpunction as pn

class pkg(pn.Dtpk):
        def __init__(self):
                self.version="1.21.11"
                self.namespace="main"
        @pn.mac
        def get_nearby_entities(self):
                return "as @e[distance=..5]"
        def say_and_kill(self):
                pn.raw("say hi")
                pn.raw("kill @s")
        @pn.onload
        def main(self):
                self.context = self.get_nearby_entities()
                self.say_and_kill()
p=pkg()
pn.make(p,"../test_dtpk")
