#!/usr/bin/env python
"""
unwordle

Shamelessly cheating at https://www.powerlanguage.co.uk/wordle/

Uses a wordlist (by default from the site) and your input from
guess attempts to narrow results.

"""

import json
import signal
import sys
from pprint import pprint

from termcolor import colored

import fetchdict


class Quit(Exception):
    pass


class Refresh(Exception):
    pass


class StartOver(Exception):
    pass


def get_letters(prompt):
    """Prompt user for input and accept only letters or
    empty input. Reprompt if validation fails.

    Args:
        prompt (string): prompt string, passed to input()

    Returns:
        value: the user's validated input
    """
    while True:
        value = wordprompt(prompt)
        menu_options(value)

        if value.isalpha() or value == "":
            break
        else:
            print("Enter just letters, lowercase. Ex: ahx")
            continue

    return value


def get_pairs(prompt):
    """Prompt user for input and accept only
    pairs of letter + position. Reprompts if validation fails.

    Example: a1 p3 e5

    Args:
        prompt (string): prompt string, passed to input()

    Returns:
        value: the user's validated input
    """
    while True:
        error = ""
        value = wordprompt(prompt)
        menu_options(value)

        for pair in value.split():
            if pair[0].isalpha():
                pass
            else:
                error = "Enter only pairs of letters and numbers. Separate multiple with spaces."

            try:
                if 0 < int(pair[1]) < 6:
                    pass
                else:
                    error = "Position number must be from 1-5."

            except ValueError:
                error = "Pairs must be letter and then a number."

        if error:
            print(error)
            print("Ex: a1 c3 y5")
        else:
            return value


def menu_options(user_input):
    """Check user input for special strings to start over, exit, or refresh
    the word list.

    Args:
        user_input (string): the user input to inspect

    Raises:
        Refresh: Refresh word list
        StartOver: Clear data and start a new word
        Quit: Exit unwordle
    """

    if user_input == "refresh":
        raise Refresh

    if user_input == "!":
        raise StartOver

    endgame = ["quit", "exit", "stop"]
    if any(x for x in user_input if user_input in endgame):
        raise Quit


# Filter functions
def exclude_letters(letters, words):
    """Exclude words containing letters.

    Args:
        letters (string): A string containing letters we want to filter out of
        words list.

        words (list): The word list to remove entries from

    Returns:
        list: the filtered word list
    """
    removals = []
    for word in words:
        if any(letter in word for letter in letters):
            removals.append(word)

    matches = [word for word in words if word not in removals]
    return matches


def include_letters(letters, words):
    """Explicitly include words containing letters.

    Args:
        letters (string): A string containing letters we want to select from
        words list.

        words (list): The word list to select entries from

    Returns:
        list: the filtered word list
    """
    matches = []
    for word in words:
        if all(letter in word for letter in letters):
            matches.append(word)

    return matches


def letter_in_pos(letter, pos, words):
    """Find words with a letter in a given position.

    Args:
        letter (string): The letter to search for

        pos (int): The positon to check for the letter

        words (list): The word list to select entries from

    Returns:
        list: the filtered word list
    """
    matches = []
    for word in words:
        if word[pos - 1] == letter:
            matches.append(word)

    return matches


def letter_not_in_pos(letter, pos, words):
    """Find words with a letter NOT in a given position

    Args:
        letter (string): The letter to search for

        pos (int): The positon to check for the letter

        words (list): The word list to select entries from

    Returns:
        list: the filtered word list
    """
    removals = []
    for word in words:
        if word[pos - 1] == letter:
            removals.append(word)

    matches = [word for word in words if word not in removals]
    return matches


def filter_words(include, exclude, known_good, known_bad, words):
    """Run include, exclude, and both letter position filters on a list of
    words.

    Args:
        include (string): Letters to include in results
        exclude (string): Letters to exclude from results
        known_good (list): List of tuples to include, letter and position ['x', 2]
        known_bad (string): List of tuples to exclude, letter and pos ['x', 3]
        words (list): List of words to filter the above from

    Returns:
        list: The filtered list of words
    """
    for letter, pos in known_good:
        words = letter_in_pos(letter, pos, words)

    for letter, pos in known_bad:
        words = letter_not_in_pos(letter, pos, words)

    words = include_letters(include, words)
    words = exclude_letters(exclude, words)
    return words

def signal_handler(sig, frame):
    """Catch Ctrl-C"""
    raise Quit

def wordprompt(prompt):
    """Prompt the user for input, normalize, and check for special strings

    Args:
        prompt (string): input() prompt string

    Returns:
        string: lowered, stripped user input. Raises Exceptions if user
        enters a magic word.
    """
    try:
        value = str(input(prompt))
        menu_options(value)
    except EOFError as control_d:
        raise StartOver from control_d

    return value.lower().strip()


def main():
    """Let's unwordle interactively!"""

    signal.signal(signal.SIGINT, signal_handler)

    try:
        with open("words.json", encoding="utf-8") as word_file:
            all_words = json.load(word_file)
    except EnvironmentError:
        print("Could not open wordlist. Try fetchdict.py!")
        sys.exit(1)

    exclude = ""
    include = ""
    known_good = []
    known_bad = []
    words = all_words

    print(colored("\nLet's unWordle!", "green"))

    print("""
    Hints:
      - E is the most common letter in English
      - T, A, O, I, N, S, R are the next most common
      - Good starters might be: NOTES, RESIN, TARES, SONAR
    """)

    while True:
        try:

            print("Try a wordle, and tell me what you find out.")
            print(
                "Enter "
                + colored('"!"', "red")
                + " or Control-D to start over, or "
                + colored('"exit"', "red")
                + " or Control-C to quit!\n"
            )

            user = get_letters(f"Enter grey letters: ({exclude}) ")
            for letter in user:
                # Don't exclude letters that are already included (if tried twice, for example)
                if letter not in exclude and letter not in include:
                    exclude += letter

            user = get_pairs(
                f"Enter {colored('green', 'green')} letters and positions, 1-5 (ex: s1 h2): {known_good} "
            )
            known_good += [
                (pair[0], int(pair[1]))
                for pair in user.split()
                if (pair[0], int(pair[1])) not in known_good
            ]
            for letter, _ in known_good:
                if letter not in include:
                    include += letter

            user = get_pairs(
                f"Enter {colored('yellow', 'yellow')} letters and positions, 1-5 (ex: a3 z5): {known_bad} "
            )
            known_bad += [
                (pair[0], int(pair[1]))
                for pair in user.split()
                if (pair[0], int(pair[1])) not in known_bad
            ]
            for letter, _ in known_bad:
                if letter not in include:
                    include += letter

            words = filter_words(include, exclude, known_good, known_bad, words)

            print("Possible words:")
            pprint(f" {words}")

        except StartOver:
            exclude = ""
            include = ""
            known_good = []
            known_bad = []
            words = all_words

            print("\n\nClearing this word and starting over\n")

        except Refresh:
            fetchdict.fetch()
            print("\nDownloaded a fresh dictionary.\n")

        except Quit:
            print("\nBye!")
            sys.exit(0)


if __name__ == "__main__":
    main()
