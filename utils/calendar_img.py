import calendar
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageOps
import requests
import io
import pytz

BG_COLOR = "#f5f6fa"
HEADER_BG = "#00aaff"
HEADER_FONT_COLOR = "#ffffff"
CELL_BG = "#ffffff"
CELL_BORDER = "#dcdde1"
TODAY_BG = "#ffe082"
AVATAR_BORDER = "#00aaff"
SHADOW_COLOR = "#b2bec3"
FONT_PATH = "Roboto-Regular.ttf"

def rounded_rectangle(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

async def create_calendar_image(study_data, bot):
    tz = pytz.timezone("America/Sao_Paulo")
    now = datetime.now(tz)
    year, month = now.year, now.month
    cal = calendar.monthcalendar(year, month)

    cell_size = 80
    padding = 40
    week_height = cell_size + 16
    header_height = cell_size
    width = cell_size * 7 + padding * 2
    height = week_height * (len(cal)+1) + header_height + padding

    img = Image.new("RGBA", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    shadow_offset = 8
    shadow_box = [padding+shadow_offset, padding+header_height+shadow_offset,
                  width-padding-shadow_offset, height-padding-shadow_offset]
    rounded_rectangle(draw, shadow_box, 24, SHADOW_COLOR)

    cal_box = [padding, padding+header_height, width-padding, height-padding]
    rounded_rectangle(draw, cal_box, 24, CELL_BG, outline=CELL_BORDER, width=2)

    font_title = ImageFont.truetype(FONT_PATH, 38)
    month_name = datetime(year, month, 1).strftime("%B %Y").capitalize()
    bbox = font_title.getbbox(month_name)
    w_title, h_title = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((width-w_title)/2, padding), month_name, fill=HEADER_BG, font=font_title)

    font_week = ImageFont.truetype(FONT_PATH, 24)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for i, d in enumerate(days):
        x = padding + i * cell_size + cell_size // 2
        y = padding + header_height
        bbox = font_week.getbbox(d)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.rectangle([x-cell_size//2, y, x+cell_size//2, y+cell_size//2], fill=HEADER_BG, outline=None)
        draw.text((x-w/2, y+8), d, fill=HEADER_FONT_COLOR, font=font_week)

    font_day = ImageFont.truetype(FONT_PATH, 26)
    max_avatars_per_cell = 5

    for week_idx, week in enumerate(cal):
        for day_idx, day in enumerate(week):
            x = padding + day_idx * cell_size
            y = padding + header_height + (week_idx+1) * week_height
            cell_rect = [x+4, y+4, x+cell_size-4, y+cell_size-4]

            if day == now.day:
                rounded_rectangle(draw, cell_rect, 20, TODAY_BG, outline=HEADER_BG, width=3)
            else:
                rounded_rectangle(draw, cell_rect, 20, CELL_BG, outline=CELL_BORDER, width=2)

            if day > 0:
                date_str = f"{year}-{month:02d}-{day:02d}"
                bbox = font_day.getbbox(str(day))
                w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                draw.text((x+cell_size/2-w/2, y+cell_size/2-h/2-14), str(day), fill="#222", font=font_day)

                avatars = [
                    data.get("avatar_url")
                    for user_id, data in study_data.items()
                    if data["confirmations"].get(date_str)
                ]

                total = min(len(avatars), max_avatars_per_cell)
                avatar_size = cell_size // 2
                gap = 6
                total_width = total * avatar_size + (total-1)*gap if total > 0 else 0
                start_x = x + (cell_size - total_width)//2

                for i, avatar_url in enumerate(avatars[:max_avatars_per_cell]):
                    try:
                        response = requests.get(avatar_url)
                        avatar_img = Image.open(io.BytesIO(response.content)).convert("RGBA")
                        avatar_img = avatar_img.resize((avatar_size, avatar_size))
                        avatar_img = ImageOps.fit(avatar_img, (avatar_size, avatar_size), centering=(0.5, 0.5))
                        mask = Image.new('L', (avatar_size, avatar_size), 0)
                        draw_mask = ImageDraw.Draw(mask)
                        draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)
                        avatar_img.putalpha(mask)
                        border_img = Image.new("RGBA", (avatar_size+8, avatar_size+8), (0,0,0,0))
                        border_draw = ImageDraw.Draw(border_img)
                        border_draw.ellipse((0,0,avatar_size+8,avatar_size+8), fill=AVATAR_BORDER)
                        border_img.paste(avatar_img, (4,4), avatar_img)
                        ax = start_x + i * (avatar_size + gap)
                        ay = y + cell_size - avatar_size - 8
                        img.paste(border_img, (int(ax), int(ay)), border_img)
                    except Exception:
                        pass

    path = "calendar_img.png"
    img.save(path)
    return path