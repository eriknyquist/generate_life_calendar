import datetime
import argparse
import os

import cairo

# A1 standard international paper size
DOC_WIDTH = 1683   # 594mm / 23 3/8 inches
DOC_HEIGHT = 2383  # 841mm / 33 1/8 inches

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

Y_MARGIN = 144
BOX_MARGIN = 6

MIN_AGE = 80
MAX_AGE = 100

BOX_LINE_WIDTH = 3
NUM_COLUMNS = 52

BIRTHDAY_COLOUR = (0.5, 0.5, 0.5)
NEWYEAR_COLOUR = (0.8, 0.8, 0.8)
DARKENED_COLOUR_DELTA = (-0.4, -0.4, -0.4)

ARROW_HEAD_LENGTH = 36
ARROW_HEAD_WIDTH = 8


def parse_date(date):
    formats = ['%d/%m/%Y', '%d-%m-%Y']

    for f in formats:
        try:
            ret = datetime.datetime.strptime(date.strip(), f)
        except ValueError:
            continue
        else:
            return ret

    raise ValueError("Incorrect date format: must be dd-mm-yyyy or dd/mm/yyyy")


def draw_square(ctx, pos_x, pos_y, box_size, fillcolour=(1, 1, 1)):
    """
    Draws a square at pos_x,pos_y
    """

    ctx.set_line_width(BOX_LINE_WIDTH)
    ctx.set_source_rgb(0, 0, 0)
    ctx.move_to(pos_x, pos_y)

    ctx.rectangle(pos_x, pos_y, box_size, box_size)
    ctx.stroke_preserve()

    ctx.set_source_rgb(*fillcolour)
    ctx.fill()


def text_size(ctx, text):
    _, _, width, height, _, _ = ctx.text_extents(text)
    return width, height


def back_up_to_monday(date):
    while date.weekday() != 0:
        date -= datetime.timedelta(days=1)
    return date


def is_current_week(now, month, day):
    end = now + datetime.timedelta(weeks=1)
    date1 = datetime.datetime(now.year, month, day)
    date2 = datetime.datetime(now.year + 1, month, day)

    return (now <= date1 < end) or (now <= date2 < end)


def get_darken_until_date():
    today = datetime.date.today()
    today_datetime = datetime.datetime(today.year, today.month, today.day)
    return back_up_to_monday(today_datetime)


def get_darkened_fill(fill):
    return tuple(map(sum, zip(fill, DARKENED_COLOUR_DELTA)))


def draw_row(ctx, pos_y, birthdate, date, box_size, x_margin, darken_until_date):
    """
    Draws a row of 52 squares, starting at pos_y
    """

    pos_x = x_margin

    for i in range(NUM_COLUMNS):
        fill = (1, 1, 1)

        if is_current_week(date, birthdate.month, birthdate.day):
            fill = BIRTHDAY_COLOUR
        elif is_current_week(date, 1, 1):
            fill = NEWYEAR_COLOUR

        if darken_until_date and date < darken_until_date:
            fill = get_darkened_fill(fill)

        draw_square(ctx, pos_x, pos_y, box_size, fillcolour=fill)
        pos_x += box_size + BOX_MARGIN
        date += datetime.timedelta(weeks=1)


def draw_key_item(ctx, pos_x, pos_y, desc, box_size, colour):
    draw_square(ctx, pos_x, pos_y, box_size, fillcolour=colour)
    pos_x += box_size + (box_size / 2)

    ctx.set_source_rgb(0, 0, 0)
    w, h = text_size(ctx, desc)
    ctx.move_to(pos_x, pos_y + (box_size / 2) + (h / 2))
    ctx.show_text(desc)

    return pos_x + w + (box_size * 2)


def draw_grid(ctx, date, birthdate, age, darken_until_date):
    """
    Draws the whole grid of 52x90 squares
    """
    num_rows = age
    box_size = ((DOC_HEIGHT - (Y_MARGIN + 36)) / num_rows) - BOX_MARGIN
    x_margin = (DOC_WIDTH - ((box_size + BOX_MARGIN) * NUM_COLUMNS)) / 2

    pos_x = x_margin / 4
    pos_y = pos_x

    # Draw the key for box colours
    ctx.set_font_size(TINYFONT_SIZE)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_NORMAL)

    pos_x = draw_key_item(ctx, pos_x, pos_y, KEY_BIRTHDAY_DESC, box_size, BIRTHDAY_COLOUR)
    draw_key_item(ctx, pos_x, pos_y, KEY_NEWYEAR_DESC, box_size, NEWYEAR_COLOUR)

    # draw week numbers above top row
    ctx.set_font_size(TINYFONT_SIZE)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL,
                         cairo.FONT_WEIGHT_NORMAL)

    pos_x = x_margin
    pos_y = Y_MARGIN
    for i in range(NUM_COLUMNS):
        text = str(i + 1)
        w, h = text_size(ctx, text)
        ctx.move_to(pos_x + (box_size / 2) - (w / 2), pos_y - box_size)
        ctx.show_text(text)
        pos_x += box_size + BOX_MARGIN

    ctx.set_font_size(TINYFONT_SIZE)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_ITALIC,
                         cairo.FONT_WEIGHT_NORMAL)

    for i in range(num_rows):
        # Generate string for current date
        ctx.set_source_rgb(0, 0, 0)
        date_str = date.strftime('%d %b, %Y')
        w, h = text_size(ctx, date_str)

        # Draw it in front of the current row
        ctx.move_to(x_margin - w - box_size,
                    pos_y + ((box_size / 2) + (h / 2)))
        ctx.show_text(date_str)

        # Draw the current row
        draw_row(ctx, pos_y, birthdate, date, box_size, x_margin, darken_until_date)

        # Increment y position and current date by 1 row/year
        pos_y += box_size + BOX_MARGIN
        date += datetime.timedelta(weeks=52)


def gen_calendar(birthdate, title, age, filename, darken_until_date):
    if len(title) > MAX_TITLE_SIZE:
        raise ValueError("Title can't be longer than %d characters"
                         % MAX_TITLE_SIZE)

    age = int(age)
    if (age < MIN_AGE) or (age > MAX_AGE):
        raise ValueError("Invalid age, must be between %d and %d" % (MIN_AGE, MAX_AGE))

    # Fill background with white
    surface = cairo.PDFSurface(filename, DOC_WIDTH, DOC_HEIGHT)
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

    date = back_up_to_monday(birthdate)

    # Draw 52x90 grid of squares
    draw_grid(ctx, date, birthdate, age, darken_until_date)
    ctx.show_page()


def main():
    parser = argparse.ArgumentParser(
        description='\nGenerate a personalized "Life '
                    'Calendar", inspired by the calendar with the same name '
                    'from the waitbutwhy.com store'
    )

    parser.add_argument(
        type=parse_date,
        dest='date',
        help='starting date; your birthday,'
             'in either yyyy/mm/dd or dd/mm/yyyy format '
             '(dashes \'-\' may also be used in place of slashes \'/\')'
    )

    parser.add_argument('-f', '--filename', type=str, dest='filename',
                        help='output filename', default=DOC_NAME)

    parser.add_argument('-t', '--title', type=str, dest='title',
                        help='Calendar title text (default is "%s")' % DEFAULT_TITLE,
                        default=DEFAULT_TITLE)

    parser.add_argument(
        '-e',
        '--end',
        type=parse_date,
        dest='enddate',
        help='end date; If this is set, then a calendar with a '
             'different start date will be generated for each day between '
             'the starting date and this date'
    )

    parser.add_argument('-a', '--age', type=int, dest='age',
                        choices=range(MIN_AGE, MAX_AGE + 1),
                        metavar='[%s-%s]' % (MIN_AGE, MAX_AGE),
                        help='Number of rows to generate, representing years of life',
                        default=90)
    parser.add_argument('-d', '--darken-past', dest='darken_past',
                        action='store_true', help='flag: darken boxes for past weeks')

    args = parser.parse_args()

    doc_name = '%s.pdf' % (os.path.splitext(args.filename)[0])
    darken_until_date = get_darken_until_date() if args.darken_past else None

    if args.enddate:
        start = args.date

        while start <= args.enddate:
            date_str = start.strftime('%d-%m-%Y')
            name = "life_calendar_%s.pdf" % date_str

            try:
                gen_calendar(start, args.title, args.age, name, darken_until_date)
            except Exception as e:
                print("Error: %s" % e)
                return

            start += datetime.timedelta(days=1)

    else:
        try:
            gen_calendar(args.date, args.title, args.age, doc_name, darken_until_date)
        except Exception as e:
            print("Error: %s" % e)
            return

        print('Created %s' % doc_name)


if __name__ == "__main__":
    main()
