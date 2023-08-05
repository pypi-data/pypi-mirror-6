from argparse import ArgumentParser
from coolasciifaces import all_faces, face


def main():
    parser = ArgumentParser(description='get some cool ascii faces')
    parser.add_argument('-a', '--all', help='print all faces', dest='show_all', action='store_true')

    args = parser.parse_args()
    if args.show_all:
        [print(f) for f in all_faces()]
    else:
        print(face())


if __name__ == '__main__':
    main()