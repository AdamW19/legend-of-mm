# The Legend of MM
This uses MIDI files from The Legend of Zelda series and implements a Markov Model to attempt to create unique pieces of music.

## Output
You can see our output in the `output` folder. You can see some example MIDI and MP3 files.

## How to Run
There are 2 files in `src`:
* `genWithInstruments_graph_output.py`: This generates a graph visualizing the probability matrix.
* `genWithInstruments_midi_output.py`: This generates the actual MIDI output.

This is written in Python 3.6. The required dependencies are in `requirements.txt`.

You may need to change the 3 instruments in your track and the path to your MIDI files. 


## Why?
This project was created as a Final Project for UCSD's [CSE 190: Mashine Learning for Music and Audio](https://sites.google.com/eng.ucsd.edu/ucsd-cse-190-summer-2020/) from 2020's Summer Session 1 at UCSD.
We would like to thank Professor Shlomo Dubnov and TA Ross Greer for all their help.

## Who?
This project was created by Jose Garcia, Liu He, and me. I would like to thank my teammates for helping so much, as I had personal issues during the project. 
