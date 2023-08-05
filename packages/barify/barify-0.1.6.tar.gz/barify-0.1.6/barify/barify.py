#!/usr/bin/env python
# coding: utf-8
import sys

def barify(value, min_value=0,
                  max_val=100,
                  delimiters='[]',
                  bar='|',
                  empty='-',
                  num_bars=10):
    if type(delimiters) != str or len(delimiters) != 2:
      raise ValueError("Invalid delimiters")
    if type(bar) != str or len(bar) != 1:
      raise ValueError("Invalid bar char")
    if type(empty) != str or len(empty) != 1:
      raise ValueError("Invalid empty char")
    if type(value) != int or value > max_val:
      raise ValueError("Value is greater than max value")
    if type(value) != int or value < min_value:
      raise ValueError("Value is lesser than min value")

    scaled_value = int( float(value) / float(max_val) * num_bars )
 
    output = delimiters[0]
    for i in range(0, scaled_value):
      output += bar

    for i in range(0, num_bars - scaled_value):
      output += empty

    output += delimiters[1]

    return output

if __name__ == "__main__":
    sys.exit()
