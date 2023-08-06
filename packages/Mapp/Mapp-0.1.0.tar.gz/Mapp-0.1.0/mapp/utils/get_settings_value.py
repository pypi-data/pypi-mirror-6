'''
This script print value from settings
Created on Jan 10, 2014

'''
import argparse
from ConfigParser import SafeConfigParser


def main():
    parser = argparse.ArgumentParser(description='Prints value from settings file.')
    parser.add_argument('path', help='<path to settings file> section value', nargs=3)
    args = parser.parse_args()
    
    config = SafeConfigParser()
    config.read(args.path[0])
    print(config.get(args.path[1], args.path[2]))

if __name__ == '__main__':
    main()