import datetime
import argparse
import sys
import os
import cairo

DOC_WIDTH = 1872   # 26 inches
DOC_HEIGHT = 2880  # 40 inches
DOC_NAME = "life_calendar.pdf"

KEY_NEWYEAR_DESC = "First week of the new year"
KEY_BIRTHDAY_DESC = "Week of your birthday"

XAXIS_DESC = "Weeks of the year"
YAXIS_DESC = "Years of your life"

FONT = "Brocha"
BIGFONT_SIZE = 40
SMALLFONT_SIZE = 16
TINYFONT_SIZE = 14

MAX_TITLE_SIZE = 30
DEFAULT_TITLE = "LIFE CALENDAR"

NUM_ROWS = 90
NUM_COLUMNS = 52

Y_MARGIN = 144
BOX_MARGIN = 6

BOX_LINE_WIDTH = 3
BOX_SIZE = ((DOC_HEIGHT - (Y_MARGIN + 36)) / NUM_ROWS) - BOX_MARGIN
X_MARGIN = (DOC_WIDTH - ((BOX_SIZE + BOX_MARGIN) * NUM_COLUMNS)) / 2

BIRTHDAY_COLOUR = (0.5, 0.5, 0.5)
NEWYEAR_COLOUR = (0.8, 0.8, 0.8)

ARROW_HEAD_LENGTH = 36
ARROW_HEAD_WIDTH = 8

def parse_date(date):
    formats = ['%d/%m/%Y', '%d-%m-%Y']
    stripped = date.strip()

    for f in formats:
        try:
            ret = datetime.datetime.strptime(date, f)
        except:
            continue
        else:
            return ret

    raise ValueError("Incorrect date format: must be dd-mm-yyyy or dd/mm/yyyy")

def draw_square(ctx, pos_x, pos_y, fillcolour=(1, 1, 1)):
    """
    Draws a square at pos_x,pos_y
    """

    ctx.set_line_width(BOX_LINE_WIDTH)
    ctx.set_source_rgb(0, 0, 0)
    ctx.move_to(pos_x, pos_y)

    ctx.rectangle(pos_x, pos_y, BOX_SIZE, BOX_SIZE)
    ctx.stroke_preserve()

    ctx.set_source_rgb(*fillcolour)
    ctx.fill()

def text_size(ctx, text):
    _, _, width, height, _, _ = ctx.text_extents(text)
    return width, height

def is_current_week(now, month, day):
    end = now + datetime.timedelta(weeks=1)
    date1 = datetime.datetime(now.year, month, day)
    date2 = datetime.datetime(now.year + 1, month, day)

    return (now <= date1 < end) or (now <= date2 < end)

def draw_row(ctx, pos_y, start_date, date):
    """
    Draws a row of 52 squares, starting at pos_y
    """

    pos_x = X_MARGIN

    for i in range(NUM_COLUMNS):
        fill=(1, 1, 1)

        if is_current_week(date, start_date.month, start_date.day):
            fill = BIRTHDAY_COLOUR
        elif is_current_week(date, 1, 1):
            fill = NEWYEAR_COLOUR

        draw_square(ctx, pos_x, pos_y, fillcolour=fill)
        pos_x += BOX_SIZE + BOX_MARGIN
        date += datetime.timedelta(weeks=1)

def draw_key_item(ctx, pos_x, pos_y, desc, colour):
    draw_square(ctx, pos_x, pos_y, fillcolour=colour)
    pos_x += BOX_SIZE + (BOX_SIZE / 2)

    ctx.set_source_rgb(0, 0, 0)
    w, h = text_size(ctx, desc)
    ctx.move_to(pos_x, pos_y + (BOX_SIZE / 2) + (h / 2))
    ctx.show_text(desc)

    return pos_x + w + (BOX_SIZE * 2)

def draw_grid(ctx, date):
    """
    Draws the whole grid of 52x90 squares
    """
    start_date = date
    pos_x = X_MARGIN / 4
    pos_y = pos_x

    # Draw the key for box colours
    ctx.set_font_size(TINYFONT_SIZE)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_NORMAL)

    pos_x = draw_key_item(ctx, pos_x, pos_y, KEY_BIRTHDAY_DESC, BIRTHDAY_COLOUR)
    draw_key_item(ctx, pos_x, pos_y, KEY_NEWYEAR_DESC, NEWYEAR_COLOUR)

    # draw week numbers above top row
    ctx.set_font_size(TINYFONT_SIZE)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_NORMAL)

    pos_x = X_MARGIN
    pos_y = Y_MARGIN
    for i in range(NUM_COLUMNS):
        text = str(i + 1)
        w, h = text_size(ctx, text)
        ctx.move_to(pos_x + (BOX_SIZE / 2) - (w / 2), pos_y - BOX_SIZE)
        ctx.show_text(text)
        pos_x += BOX_SIZE + BOX_MARGIN

    ctx.set_font_size(TINYFONT_SIZE)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_ITALIC,
        cairo.FONT_WEIGHT_NORMAL)

    for i in range(NUM_ROWS):
        # Generate string for current date
        ctx.set_source_rgb(0, 0, 0)
        date_str = date.strftime('%d %b, %Y')
        w, h = text_size(ctx, date_str)

        # Draw it in front of the current row
        ctx.move_to(X_MARGIN - w - BOX_SIZE,
            pos_y + ((BOX_SIZE / 2) + (h / 2)))
        ctx.show_text(date_str)

        # Draw the current row
        draw_row(ctx, pos_y, start_date, date)

        # Increment y position and current date by 1 row/year
        pos_y += BOX_SIZE + BOX_MARGIN
        date += datetime.timedelta(weeks=52)

def gen_calendar(start_date, title, filename):
    if len(title) > MAX_TITLE_SIZE:
        raise ValueError("Title can't be longer than %d characters"
            % MAX_TITLE_SIZE)

    # Fill background with white
    surface = cairo.PDFSurface (filename, DOC_WIDTH, DOC_HEIGHT)
    ctx = cairo.Context(surface)

    ctx.set_source_rgb(1, 1, 1)
    ctx.rectangle(0, 0, DOC_WIDTH, DOC_HEIGHT)
    ctx.fill()

    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD)
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_font_size(BIGFONT_SIZE)
    w, h = text_size(ctx, title)
    ctx.move_to((DOC_WIDTH / 2) - (w / 2), (Y_MARGIN / 2) - (h / 2))
    ctx.show_text(title)

    # Back up to the last monday
    date = start_date
    while date.weekday() != 0:
        date -= datetime.timedelta(days=1)

    # Draw 52x90 grid of squares
    draw_grid(ctx, date)
    ctx.show_page()

def main():
    parser = argparse.ArgumentParser(description='\nGenerate a personalized "Life '
        ' Calendar", inspired by the calendar with the same name from the '
        'waitbutwhy.com store')

    parser.add_argument(type=str, dest='date', help='starting date; your birthday,'
        'in either dd/mm/yyyy or dd-mm-yyyy format')

    parser.add_argument('-f', '--filename', type=str, dest='filename',
        help='output filename', default=DOC_NAME)

    parser.add_argument('-t', '--title', type=str, dest='title',
        help='Calendar title text (default is "%s")' % DEFAULT_TITLE,
        default=DEFAULT_TITLE)

    parser.add_argument('-e', '--end', type=str, dest='enddate',
        help='end date; If this is set, then a calendar with a different start date'
        ' will be generated for each day between the starting date and this date')

    args = parser.parse_args()

    try:
        start_date = parse_date(args.date)
    except Exception as e:
        print("Error: %s" % e)
        return

    doc_name = '%s.pdf' % (os.path.splitext(args.filename)[0])

    if args.enddate:
        start = start_date

        try:
            end = parse_date(args.enddate)
        except Exception as e:
            print("Error: %s" % e)
            return

        while start <= end:
            date_str = start.strftime('%d-%m-%Y')
            name = "life_calendar_%s.pdf" % date_str

            try:
                gen_calendar(start, args.title, name)
            except Exception as e:
                print("Error: %s" % e)
                return

            start += datetime.timedelta(days=1)

    else:
        try:
            gen_calendar(start_date, args.title, doc_name)
        except Exception as e:
            print("Error: %s" % e)
            return

        print('Created %s' % doc_name)

if __name__ == "__main__":
    main()
