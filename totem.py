import sys
import requests
from PIL import Image, ImageOps
from io import BytesIO

def username_to_uuid(username):
    return requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}").json()["id"]

def get_skin(uuid):
    response = requests.get(f"https://crafatar.com/skins/{uuid}")
    return Image.open(BytesIO(response.content))

def make_totem(username, use_outer_layer=True):
    canvas = Image.new("RGBA", (32, 32))

    full_skin = get_skin(username_to_uuid(username))
    is_old_skin = full_skin.size[1] == 32

    head = full_skin.crop((8, 8, 16, 16))
    if use_outer_layer:
        head_l2 = full_skin.crop((40, 8, 48, 16))
        head.paste(head_l2, (0, 0), head_l2)

    torso = full_skin.crop((20, 20, 28, 32))
    if use_outer_layer:
        torso_l2 = full_skin.crop((20, 36, 28, 48))
        torso.paste(torso_l2, (0, 0), torso_l2)

    legs = Image.new("RGBA", (8, 12))
    if is_old_skin:
        leg = full_skin.crop((4, 20, 8, 32))
        legs.paste(leg, (0, 0))
        leg = ImageOps.mirror(leg)
        legs.paste(leg, (4, 0))
    else:
        leg_rl1 = full_skin.crop((4, 20, 8, 32))
        legs.paste(leg_rl1, (0, 0))
        leg_ll1 = full_skin.crop((20, 52, 24, 64))
        legs.paste(leg_ll1, (4, 0))
        if use_outer_layer:
            leg_rl2 = full_skin.crop((4, 36, 8, 48))
            legs.paste(leg_rl2, (0, 0), leg_rl2)
            leg_ll2 = full_skin.crop((4, 52, 8, 64))
            legs.paste(leg_ll2, (4, 0), leg_ll2)
    legs = legs.resize((8, 8))

    right_arm = full_skin.crop((44, 20, 48, 32))
    if is_old_skin:
        left_arm = ImageOps.mirror(right_arm)
    else:
        left_arm = full_skin.crop((36, 52, 40, 64))
        if use_outer_layer:
            right_arm_l2 = full_skin.crop((44, 36, 48, 48))
            right_arm.paste(right_arm_l2, (0, 0), right_arm_l2)
            left_arm_l2 = full_skin.crop((52, 52, 56, 64))
            left_arm.paste(left_arm_l2, (0, 0), left_arm_l2)
    right_arm = right_arm.resize((4, 9))
    left_arm = left_arm.resize((4, 9))

    right_arm_warped = Image.new("RGBA", (6, 9))
    right_arm_warped.paste(right_arm.crop((0, 6, 4, 9)), (0, 6))
    right_arm_warped.paste(right_arm.crop((0, 5, 4, 6)), (1, 5))
    right_arm_warped.paste(right_arm.crop((0, 4, 4, 5)).resize((5, 1)), (1, 4))
    right_arm_warped.paste(right_arm.crop((0, 2, 4, 4)), (2, 2))
    right_arm_warped.paste(right_arm.crop((1, 1, 4, 2)), (3, 1))
    right_arm_warped.paste(right_arm.crop((3, 0, 4, 1)), (5, 0))

    if is_old_skin: #time saver
        left_arm_warped = ImageOps.mirror(right_arm_warped)
    else:
        left_arm_warped = Image.new("RGBA", (6, 9))
        left_arm_warped.paste(left_arm.crop((0, 6, 4, 9)), (2, 6))
        left_arm_warped.paste(left_arm.crop((0, 5, 4, 6)), (1, 5))
        left_arm_warped.paste(left_arm.crop((0, 4, 4, 5)).resize((5, 1)), (0, 4))
        left_arm_warped.paste(left_arm.crop((0, 2, 4, 4)), (0, 2))
        left_arm_warped.paste(left_arm.crop((1, 1, 4, 2)), (0, 1))
        left_arm_warped.paste(left_arm.crop((3, 0, 4, 1)), (0, 0))

    canvas.paste(head, (12, 4))
    canvas.paste(torso, (12, 12))
    canvas.paste(legs, (12, 24))
    canvas.paste(right_arm_warped, (6, 12))
    canvas.paste(left_arm_warped, (20, 12))
    return canvas

use_outer_layer = len(sys.argv) < 3 or sys.argv[2].lower() in ["t", "true", "y", "yes"]
totem = make_totem(sys.argv[1], use_outer_layer)
totem.save("totem_of_undying.png")
