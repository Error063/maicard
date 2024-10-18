import argparse
import logging
import os
import math
from datetime import datetime


import colorsys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logger = logging.getLogger(__name__)

maimaiImgPath = str(os.path.join(os.getcwd(), "res", "images")) + '/'
materialPath = str(os.path.join(os.getcwd(), "res", "material")) + '/'

def get_star_info(level):
    # 定义星级觉醒的等级区间
    awakening_levels = [9, 49, 99, 299, 999, 9999]
    max_stars = len(awakening_levels)

    # 计算当前星级
    current_star = 0
    for awakening_level in awakening_levels:
        if level >= awakening_level:
            current_star += 1
        else:
            break

    # 如果已经满星
    if current_star == max_stars:
        return current_star, 100

    # 计算距离下一星级的百分比
    current_awakening_level = awakening_levels[current_star - 1] if current_star > 0 else 0
    next_awakening_level = awakening_levels[current_star]
    progress = (level - current_awakening_level) / (next_awakening_level - current_awakening_level) * 100

    return current_star, int((progress // 10) * 10)

def circle_corner(img, radii=30):
    # 白色区域透明可见，黑色区域不可见
    circle = Image.new('L', (radii * 2, radii * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, radii * 2, radii * 2), fill=255)

    img = img.convert("RGBA")
    w, h = img.size

    # 画角
    alpha = Image.new('L', img.size, 255)
    alpha.paste(circle.crop((0, 0, radii, radii)), (0, 0))  # 左上角
    alpha.paste(circle.crop((radii, 0, radii * 2, radii)), (w - radii, 0))  # 右上角
    alpha.paste(circle.crop((radii, radii, radii * 2, radii * 2)), (w - radii, h - radii))  # 右下角
    alpha.paste(circle.crop((0, radii, radii, radii * 2)), (0, h - radii))  # 左下角

    img.putalpha(alpha)

    return img

def drawUserImg(title,totalRating,rankRating,userName,icon,plate,title_rare="Normal",classRank=-1):
    UserImg = Image.new('RGBA', (724, 120))

    plateImg = Image.open(plate).resize((720,116))
    UserImg.paste(plateImg, (0, 2), plateImg)

    iconImg = Image.open(icon).resize((100,100))
    UserImg.paste(iconImg,(8,10),iconImg)

    ratingPlateImg = Image.open(rf"{maimaiImgPath}/Rating/{getRatingBgImg(totalRating)}").resize((174,36))
    UserImg.paste(ratingPlateImg, (110, 6), ratingPlateImg)

    # 定义偏移量和初始x坐标
    offset = 14
    start_x = 250
    x_positions = [start_x - i * offset for i in range(len(str(totalRating)))][:5]

    # 根据totalRating的位数处理图片
    for i, x_pos in enumerate(x_positions):
        # 计算当前位上的数字
        digit = int(totalRating / (10 ** i) % 10)
        # 打开并调整图片大小
        numImg = Image.open(rf"{maimaiImgPath}/num/UI_NUM_Drating_{digit}.png").resize((19, 23))
        # 粘贴图片
        UserImg.paste(numImg, (x_pos, 13), numImg)

    if 25 >= int(classRank) >= 0:
        classRankImg = Image.open(rf"{maimaiImgPath}/classRank/UI_CMN_Class_S_{int(classRank):02d}.png").resize((100, 60))
        UserImg.paste(classRankImg, (284, -8), classRankImg)


    UserIdImg = circle_corner(Image.new('RGBA', (270, 40), color=(255, 255, 255)),5)
    UserIdDraw = ImageDraw.Draw(UserIdImg)
    UserIdDraw.text((7, 8), f"{userName}", font=ImageFont.truetype(rf'{materialPath}/GenSenMaruGothicTW-Medium.ttf', 20),fill=(0, 0, 0))
    UserImg.paste(UserIdImg, (113, 44), UserIdImg)

    if 23 >= int(rankRating) >= 0:
        rankImg = Image.open(rf"{maimaiImgPath}/Ranks/{int(rankRating)}.png").resize((94, 44))
        UserImg.paste(rankImg, (290, 42), rankImg)

    totalRatingImg = Image.open(rf"{maimaiImgPath}/shougou/UI_CMN_Shougou_{title_rare.title()}.png")
    totalRatingDraw = ImageDraw.Draw(totalRatingImg)
    font = ImageFont.truetype(rf'{materialPath}/GenSenMaruGothicTW-Bold.ttf', 11)
    _, _, text_width, text_height = totalRatingDraw.textbbox((0, 0), title, font=font)
    draw_text_with_stroke_and_spacing(
        totalRatingDraw,
        (abs(240-text_width)//2, 7),
        title,
        font=font,
        fill_color="white",
        stroke_width=2,
        stroke_color='black',
        spacing=1
    )
    UserImg.paste(totalRatingImg, (113, 83), totalRatingImg)

    return UserImg

def _getCharWidth(o) -> int:
    widths = [
        (126, 1), (159, 0), (687, 1), (710, 0), (711, 1), (727, 0), (733, 1), (879, 0), (1154, 1), (1161, 0),
        (4347, 1), (4447, 2), (7467, 1), (7521, 0), (8369, 1), (8426, 0), (9000, 1), (9002, 2), (11021, 1),
        (12350, 2), (12351, 1), (12438, 2), (12442, 0), (19893, 2), (19967, 1), (55203, 2), (63743, 1),
        (64106, 2), (65039, 1), (65059, 0), (65131, 2), (65279, 1), (65376, 2), (65500, 1), (65510, 2),
        (120831, 1), (262141, 2), (1114109, 1),
    ]
    if o == 0xe or o == 0xf:
        return 0
    for num, wid in widths:
        if o <= num:
            return wid
    return 1

def getRatingBgImg(rating):
    totalRating = int(rating)
    if 0 <= totalRating <= 999:
        ratingPlate = "UI_CMN_DXRating_01.png"
    elif 1000 <= totalRating <= 1999:
        ratingPlate = "UI_CMN_DXRating_02.png"
    elif 2000 <= totalRating <= 3999:
        ratingPlate = "UI_CMN_DXRating_03.png"
    elif 4000 <= totalRating <= 6999:
        ratingPlate = "UI_CMN_DXRating_04.png"
    elif 7000 <= totalRating <= 9999:
        ratingPlate = "UI_CMN_DXRating_05.png"
    elif 10000 <= totalRating <= 11999:
        ratingPlate = "UI_CMN_DXRating_06.png"
    elif 12000 <= totalRating <= 12999:
        ratingPlate = "UI_CMN_DXRating_07.png"
    elif 13000 <= totalRating <= 13999:
        ratingPlate = "UI_CMN_DXRating_08.png"
    elif 14000 <= totalRating <= 14499:
        ratingPlate = "UI_CMN_DXRating_09.png"
    elif 14500 <= totalRating <= 14999:
        ratingPlate = "UI_CMN_DXRating_10.png"
    else:
        ratingPlate = "UI_CMN_DXRating_11.png"
    return ratingPlate

def apply_gradient_blur(image, blur_radius=10, start_height=0, end_height=35):
    # 创建一个与原始图像大小相同的空白渐变蒙版
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)

    # 将 start_height 和 end_height 转换为绝对像素位置
    start_pixel = int(start_height * image.height)
    end_pixel = int(end_height * image.height)

    # 绘制渐变蒙版，模糊从 start_pixel 开始，到 end_pixel 结束
    for y in range(image.height):
        if y < start_pixel:
            intensity = 0
        elif y > end_pixel:
            intensity = 255
        else:
            # 根据 y 位置线性插值计算模糊程度
            intensity = int(255 * (y - start_pixel) / (end_pixel - start_pixel))
        draw.line((0, y, image.width, y), fill=intensity)

    # 对图像进行模糊处理
    blurred_image = image.filter(ImageFilter.GaussianBlur(blur_radius))

    # 将模糊图像和原始图像混合，使用渐变蒙版控制模糊区域
    result = Image.composite(blurred_image, image, mask)

    return result

def drawCharaImgNewSub(charaId, charaLevel):
    if int(charaLevel) > 9999:
        charaLevel = 9999
    if int(charaLevel) < 0:
        charaLevel = 0
    star, progress = get_star_info(int(charaLevel))
    alpha = Image.open(rf"{maimaiImgPath}/maicard/alpha.png").convert("L")
    base = Image.open(rf"{maimaiImgPath}/maicard/UI_Chara_RBase.png").convert("RGBA")
    frame = Image.open(rf"{maimaiImgPath}/maicard/UI_Chara_RFrame.png").convert("RGBA").resize((152, 268))
    level_img = Image.open(rf"{maimaiImgPath}/maicard/UI_NUM_MLevelDAMMY_14.png").convert("RGBA").resize((20, 14))

    if not os.path.exists(rf"{maimaiImgPath}/Chara/UI_Chara_{charaId:06d}.png"):
        charaId = 0
    chara_img = Image.new("RGBA", (264, 300), (255, 255, 255, 0))
    c = Image.open(rf"{maimaiImgPath}/Chara/UI_Chara_{charaId:06d}.png").convert("RGBA").resize((170, 170))
    chara_img.paste(c, (0, 40), c)

    chara_img = chara_img.crop((12, -32, 12 + alpha.width, alpha.height - 32))

    base.paste(chara_img, (0, 0), chara_img)
    base.paste(frame, (-2, -2), frame)
    base.putalpha(alpha)

    new_base = Image.new(mode="RGBA", size=(152, 298), color=(255, 255, 255, 0))
    new_base.paste(base, (0, 0), base)

    if star >= 6:
        main_star = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Chara_star_big_MAX.png").convert("RGBA").resize((53, 50))
        sub_star = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Chara_star_small_MAX.png").convert("RGBA").resize((35, 35))
    elif star >= 5:
        main_star = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Chara_Star_big.png").convert("RGBA").resize(
            (53, 50))
        sub_star = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Chara_Star_Small.png").convert("RGBA").resize(
            (35, 35))
    else:
        main_star = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Chara_Star_Big_Gauge01_{progress}.png").convert("RGBA").resize((53, 50))
        sub_star = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Chara_Star_Small.png").convert("RGBA").resize((35, 35))

    if star >= 1:
        new_base.paste(main_star, (47, 234), main_star)
    if star >= 2:
        new_base.paste(sub_star, (16, 226), sub_star)
    if star >= 3:
        new_base.paste(sub_star, (97, 226), sub_star)
    if star >= 4:
        sub_star = sub_star.resize((26, 26))
        new_base.paste(sub_star, (6, 206), sub_star)
    if star >= 5:
        new_base.paste(sub_star, (116, 206), sub_star)

    new_base.paste(level_img, (20, 17), level_img)
    num_x = 46
    for num in str(charaLevel):
        num_img = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Num_26p_{num}.png").convert("RGBA").resize((25, 28))
        new_base.paste(num_img, (num_x, 6), num_img)
        num_x += 18

    return new_base

def drawCharaImgNewMain(charaId, charaLevel):
    if int(charaLevel) > 9999:
        charaLevel = 9999
    if int(charaLevel) < 0:
        charaLevel = 0
    star, progress = get_star_info(int(charaLevel))

    frame = Image.open(rf"{maimaiImgPath}/maicard/UI_Chara_LFrame.png").convert("RGBA").resize((235, 101))
    level_img = Image.open(rf"{maimaiImgPath}/maicard/UI_NUM_MLevelDAMMY_14.png").convert("RGBA").resize((36, 23))

    if not os.path.exists(rf"{maimaiImgPath}/Chara/UI_Chara_{charaId:06d}.png"):
        charaId = 0
    base = Image.open(rf"{maimaiImgPath}/Chara/UI_Chara_{charaId:06d}.png").convert("RGBA").resize((512, 512))

    base.paste(frame, (140, 381), frame)

    if star >= 6:
        main_star = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Chara_star_big_MAX.png").convert("RGBA").resize((65, 61))
        sub_star = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Chara_star_small_MAX.png").convert("RGBA").resize((45, 45))
    elif star >= 5:
        main_star = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Chara_Star_big.png").convert("RGBA").resize((65, 61))
        sub_star = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Chara_Star_Small.png").convert("RGBA").resize((45, 45))
    else:
        main_star = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Chara_Star_Big_Gauge01_{progress}.png").convert("RGBA").resize((65, 61))
        sub_star = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Chara_Star_Small.png").convert("RGBA").resize((45, 45))

    if star >= 1:
        base.paste(main_star, (225, 443), main_star)
    if star >= 2:
        base.paste(sub_star, (185, 446), sub_star)
    if star >= 3:
        base.paste(sub_star, (285, 446), sub_star)
    if star >= 4:
        sub_star = sub_star.resize((30, 30))
        base.paste(sub_star, (158, 438), sub_star)
    if star >= 5:
        base.paste(sub_star, (327, 438), sub_star)


    base.paste(level_img, (170, 405), level_img)
    num_x = 229
    for num in str(charaLevel):
        num_img = Image.open(rf"{maimaiImgPath}/maicard/UI_CMN_Num_26p_{num}.png").convert("RGBA").resize((38, 44))
        base.paste(num_img, (num_x, 394), num_img)
        num_x += 27

    return apply_gradient_blur(base.resize((264, 264)), 100)

def get_dominant_color(image):
    # 颜色模式转换，以便输出rgb颜色值
    image = image.convert('RGBA')
    # 生成缩略图，减少计算量，减小cpu压力
    image.thumbnail((200, 200))
    max_score = 0
    dominant_color = (0,0,0)
    for count, (r, g, b, a) in image.getcolors(image.size[0] * image.size[1]):
        # 跳过纯黑色
        if (a == 0) or (sum((r, g, b, a)) == 0):
            continue
        saturation = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)[1]
        y = min(abs(r * 2104 + g * 4130 + b * 802 + 4096 + 131072) >> 13, 235)
        y = (y - 16.0) / (235 - 16)
        # 忽略高亮色
        if y > 0.9:
            continue
        score = (saturation + 0.1) * count
        if score > max_score:
            max_score = score
            dominant_color = (r, g, b)
    return dominant_color

def draw_text_with_stroke(draw: ImageDraw, pos, text, font, fill_color, stroke_width=2, stroke_color='white'):
    # 绘制描边
    for x_offset in range(-stroke_width+1, stroke_width):
        for y_offset in range(-stroke_width+1, stroke_width):
            if x_offset == 0 and y_offset == 0:
                continue
            draw.text((pos[0] + x_offset, pos[1] + y_offset), text, font=font, fill=stroke_color)

    # 在正确位置绘制文本
    draw.text(pos, text, font=font, fill=fill_color)

def draw_text_with_stroke_and_spacing(draw: ImageDraw.ImageDraw, pos, text, font, fill_color, stroke_width=2, stroke_color='white', spacing=5):
    # 绘制描边
    for x_offset in range(-stroke_width+1, stroke_width):
        for y_offset in range(-stroke_width+1, stroke_width):
            if x_offset == 0 and y_offset == 0:
                continue
            xx, yy = (pos[0] + x_offset, pos[1] + y_offset)
            draw_text_with_spacing(draw, (xx, yy), text, font, stroke_color, spacing)

    draw_text_with_spacing(draw, pos, text, font, fill_color, spacing)

def draw_text_with_spacing(draw: ImageDraw.ImageDraw, pos, text, font, fill_color, spacing=5):
    # 逐字符绘制并调整位置
    x, y = pos
    for char in text:
        _, _, char_width, _ = draw.textbbox((0, 0), char, font=font)
        draw.text((x, y), char, font=font, fill=fill_color)
        x += char_width + spacing  # 增加间距

def call_user_img(user_data, no_chara=False):
    try:
        frame_path = rf"{maimaiImgPath}/Frame/UI_Frame_{user_data['frame']:06d}.png"
        frame_img = Image.open(frame_path).resize((1080, 452))
    except:
        frame_path = rf"{maimaiImgPath}/Frame/UI_Frame_000000.png"
        frame_img = Image.open(frame_path).resize((1080, 452))

    theme_color = get_dominant_color(frame_img)
    img = Image.new("RGBA", (1080, 477), theme_color)
    text_color = tuple(abs(c-100)%255 for c in theme_color)

    img.paste(frame_img, (0, 0))

    plate = rf"{maimaiImgPath}/Plate/UI_Plate_{user_data['plate']:06d}.png"
    icon = rf"{maimaiImgPath}/Icon/UI_Icon_{user_data['icon']:06d}.png"

    UserImg: Image = drawUserImg(user_data["title"], user_data["rating"], user_data['courseRank'], user_data['nickname'], icon, plate,user_data["titleRare"],user_data["classRank"])
    img.paste(UserImg, (25, 25), UserImg)

    network_status_img = Image.open(rf"{maimaiImgPath}/network/on.png")
    img.paste(network_status_img, (1014, 25), network_status_img)

    if not no_chara:
        main_chara = drawCharaImgNewMain(user_data["chara"][0], user_data["charaLevel"][0]).resize((309, 309))
        img.paste(main_chara, (-36, 143), main_chara)
        chara_start_x = 204
        chara_start_y = 170
        for chara in zip(user_data["chara"][1:], user_data["charaLevel"][1:]):
            chara_img = drawCharaImgNewSub(*chara).resize((147, 290))
            img.paste(chara_img, (chara_start_x, chara_start_y), chara_img)
            chara_start_x += 138

    designDraw = ImageDraw.Draw(img)
    # 保留这些可以喵？
    designDraw.text((20, 457),
                    f"Generated by maicard-py at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 图片仅供参考",
                    font=ImageFont.truetype(rf'{materialPath}/GenSenMaruGothicTW-Bold.ttf', 12), fill=text_color)

    return img

def call_user_img_preview(user_data):
    base_img = Image.open(f"{maimaiImgPath}/prof/UI_ENT_Base_Myprof.png")

    draw = ImageDraw.Draw(base_img)
    draw.text((268,101), f"{user_data['nickname']}", font=ImageFont.truetype(rf'{materialPath}/GenSenMaruGothicTW-Medium.ttf', 20), fill="black")

    icon = rf"{maimaiImgPath}/Icon/UI_Icon_{user_data['icon']:06d}.png"
    iconImg = Image.open(icon).resize((156, 156))
    base_img.paste(iconImg, (68, 114), iconImg)

    awake_star_img = Image.open(rf"{maimaiImgPath}/prof/UI_ENT_Base_Myprof_Starchip.png").resize((80, 52))
    base_img.paste(awake_star_img, (311, 253), awake_star_img)

    draw_text_with_stroke(
        draw,
        (411, 256),
        str(user_data["awake"]),
        ImageFont.truetype(rf'{materialPath}/GenSenMaruGothicTW-Bold.ttf', 46),
        "white",
        stroke_width=2,
        stroke_color='black'
    )

    ratingPlateImg = Image.open(rf"{maimaiImgPath}/Rating_big/{getRatingBgImg(int(user_data['rating']))}").resize((312,58))
    base_img.paste(ratingPlateImg, (253, 163), ratingPlateImg)

    # 定义偏移量和初始x坐标
    offset = 25
    start_x = 496
    start_y = 177
    x_positions = [start_x - i * offset for i in range(len(str(int(user_data["rating"]))))][-5:]

    # 根据totalRating的位数处理图片
    for i, x_pos in enumerate(x_positions):
        # 计算当前位上的数字
        digit = int(int(user_data["rating"]) / (10 ** i) % 10)
        # 打开并调整图片大小
        numImg = Image.open(rf"{maimaiImgPath}/num/UI_NUM_Drating_{digit}.png")
        # 粘贴图片
        base_img.paste(numImg, (x_pos, start_y), numImg)

    return base_img

def main():
    parser = argparse.ArgumentParser(description="基于Python的玩家收藏品组合的图片生成器", formatter_class=argparse.ArgumentDefaultsHelpFormatter, add_help=True)
    parser.add_argument("--nickname", type=str, default="Ｈｏｓｈｉｎｏ☆", help="玩家昵称")
    parser.add_argument("--title", type=str, default="游戏中心岛今天也很平静呢", help="玩家称号")
    parser.add_argument("--icon", type=int, default=350101, help="玩家头像ID")
    parser.add_argument("--frame", type=int, default=350101, help="玩家背景板ID")
    parser.add_argument("--plate", type=int, default=350101, help="玩家姓名框ID")
    parser.add_argument("--rating", type=int, default=12345, help="玩家Rating")
    parser.add_argument("--classRank", type=int, default=7, help="玩家友人对战等级")
    parser.add_argument("--courseRank", type=int, default=10, help="玩家段位认定等级")
    parser.add_argument("--titleRare", type=str, default="Normal", help="玩家称号稀有度")
    parser.add_argument("--chara", nargs='+', type=int, default=[101, 104, 355610, 355611, 355612], help="玩家设置的旅行伙伴ID列表")
    parser.add_argument("--charaLevel", nargs='+', type=int, default=[1000, 9999, 1000, 9999, 9999], help="玩家设置的旅行伙伴等级列表")
    parser.add_argument("--output", type=str, default="./output.png", help="图片输出路径")

    args = parser.parse_args()

    user_data = {
        "nickname": args.nickname,
        "title": args.title,
        "icon": args.icon,
        "frame": args.frame,
        "plate": args.plate,
        "rating": args.rating,
        "classRank": args.classRank,
        "courseRank": args.courseRank,
        "titleRare": args.titleRare,
        "chara": args.chara,
        "charaLevel": args.charaLevel,
    }
    for k, v in user_data.items():
        print(f"{k}: {v}")

    a = call_user_img(user_data, False)
    a.save(args.output)
    print("\nDone")
    print(f"File path: {args.output}")
    # a.show()

if __name__ == "__main__":
    main()
