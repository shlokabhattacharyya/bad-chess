# Bad Chess

A set of chess engines, each trained with some particular specialization, all of which were created to be intentionally awful at playing chess. This project was inspired by the YouTube video [30 Weird Chess Algorithms: Elo World](https://www.youtube.com/watch?v=DpXy041BIlA&t=29s) and its corresponding paper [Elo World, a framework for benchmarking weak chess engines](http://tom7.org/chess/weak.pdf).

## Process

I saw this YouTube video pop up on my home page, likely as one of many attempts made by my algorithm to push me to get better at chess. While that still has yet to happen (please don't ask me what my chess.com rating is), I was fairly intrigued by the idea of creating chess engines made to be intentionally bad at playing chess, given the volume of them that do exactly the opposite. I appreciated the variety and creativity of the engines in the paper and decided to try and implement some of them myself using Python.

This project is currently still a work in progress. So far, I have built engines for all 18 of the simple players (Section 2.1 in the paper). 

## Installation
1. Clone this repository:
```
git clone https://github.com/shlokabhattacharyya/bad-chess.git
cd bad-chess
```
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Run the project:
```
python main.py
```