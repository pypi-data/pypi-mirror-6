#!/usr/bin/python

from colorful import colorful

if __name__ == "__main__":
    print(colorful.bold_red_on_black("Hello World"))
    print(colorful.black_on_white("Hello World!"))
    print(colorful.underline("Hello World"))
    print(colorful.bold_and_underline_green("Hello World!"))
    print(colorful.bold_and_underline_green_on_red("Hello World!"))
    print(colorful.bold_and_underline_and_strikethrough_green_on_red("Hello World!"))
    print(colorful.strikethrough("dfgsfdg"))
    colorful.out.bold_red_on_black("dfgdfg")
    attr = "bold_red_on_black"
    if colorful.exists(attr):
        print attr, "exists"
        f = colorful.get(attr)
        print f("Hallo Welt")
    else:
        print attr, "doesn't exist"
