# -*- coding: utf-8 -*-
import argparse
import json


def generate_map(min_x, min_y, max_x, max_y, map_name, default):
    default_name = default
    screen_config_dict = {}

    for x in xrange(min_x, max_x + 1):
        for y in xrange(min_y, max_y + 1):
            left = (x - 1) if x - 1 >= min_x else max_x
            down = (y - 1) if y - 1 >= min_y else max_y
            right = (x + 1) if x + 1 <= max_x else min_x
            up = (y + 1) if y + 1 <= max_y else min_y

            screen_config_dict[default_name.format(x, y)] = {"left": default_name.format(left, y),
                                                             "right": default_name.format(right, y),
                                                             "up": default_name.format(x, up),
                                                             "down": default_name.format(x, down),
                                                             "map": map_name}
    return screen_config_dict


def write_to_file(filename, data):
    with open(filename + ".json", "w") as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a .json file for the map in a block fashion. "
                                                 "Best matched on a distributed display wall")
    parser.add_argument("x_min", help="Start x pos", type=int)
    parser.add_argument("y_min", help="Start y pos", type=int)
    parser.add_argument("x_max", help="End x pos", type=int)
    parser.add_argument("y_max", help="End y pos", type=int)
    parser.add_argument("filename", help="filename of the output", type=str)
    parser.add_argument("-default_host_name",
                        help="How the host names should match. Must written in a standard python string.format way",
                        type=str, default="tile-{0}-{1}.local")
    parser.add_argument("-map",
                        help="Which map should be used for all. Uses default if not specified",
                        type=str, default="default")
    args = parser.parse_args()
    data = generate_map(min_x=args.x_min, min_y=args.y_min,
                                 max_x=args.x_max, max_y=args.y_max, map_name=args.map, default=args.default_host_name)
    write_to_file(args.filename, data)
