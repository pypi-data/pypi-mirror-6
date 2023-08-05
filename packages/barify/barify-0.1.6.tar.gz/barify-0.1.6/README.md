A simple library to generate text progress bars for given values.

To install:

`pip install barify`

Example:

````
from barify import barify

print barify(84)
````

Prints out:

`[||||||||--]`

Here are the available optional arguments:

- `min_value`: The minimum value in the interval of the passed value. Default is 0.
- `max_val`: The maximum value in the interval of the passed value. Default is 100.
- `delimiters`: A 2 character string; left character is used for the left delimiter of the progress bar, and right character is used for the right delimiter of the progress bar. Default is '[]'
- `bar`: A 1 character string; character to use to represent a full bar. Default is '|'
- `empty`: A 1 character string; character to use to represent an empty bar. Default is '-'
- `num_bars`: The number of bars (both full and empty) that should compose the progress bar. Default is 10.

