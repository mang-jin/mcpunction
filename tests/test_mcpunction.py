import mcpunction as pn

class pkg(pn.Dtpk):
        def __init__(self):
                self.version="1.21.11"
                self.namespace="main"
        @pn.mac
        def player_shooting_gun(self):
                return pn.Context("as @a[tag=used_gun]")
        def shoot_gun(self):
                pn.raw("say phew!")
        @pn.mac
        def has_gun_in_offhand(self):
                return pn.Context("if items entity @s weapon.offhand gun")
        @pn.ontick
        def game_loop(self):
                with self.player_shooting_gun():
                        self.shoot_gun()
                        pn.raw("tag @s remove used_gun")
                with pn.Context("as @a")+self.has_gun_in_offhand():
                        pn.raw("tag @s add used_gun")
                
p=pkg()
pn.make(p,"../test_dtpk",overwrite=True)
