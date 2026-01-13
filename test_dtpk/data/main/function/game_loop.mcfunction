execute as @a[tag=used_gun] run function main:shoot_gun
execute as @a[tag=used_gun] run tag @s remove used_gun
execute as @a if items entity @s weapon.offhand gun run tag @s add used_gun
