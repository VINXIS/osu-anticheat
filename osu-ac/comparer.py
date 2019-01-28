import itertools

import numpy as np

from draw import Draw
from replay import Replay
from config import WHITELIST

class Comparer:
    """
    A class for managing a set of replay comparisons.

    Attributes:
        List replays1: A list of Replay instances to compare against replays2.
        List replays2: A list of Replay instances to be compared against. Optional, defaulting to None. No attempt to error check
                       this is made - if a compare() call is made, the program will throw an AttributeError. Be sure to only call
                       methods that involve the first set of replays if this argument is not passed.
        Integer threshold: If a comparison scores below this value, the result is printed.

    See Also:
        Investigator
    """

    def __init__(self, threshold, replays1, replays2=None):
        """
        Initializes a Comparer instance.

        Note that the order of the two replay lists has no effect; they are only numbered for consistency.
        Comparing 1 to 2 is the same as comparing 2 to 1.

        Args:
            List replays1: A list of Replay instances to compare against replays2.
            List replays2: A list of Replay instances to be compared against. Optional, defaulting to None. No attempt to error check
                           this is made - if a compare() call is made, the program will throw an AttributeError. Be sure to only call
                           methods that involve the first set of replays.
            Integer threshold: If a comparison scores below this value, the result is printed.
        """

        self.replays1 = replays1
        self.replays2 = replays2
        self.threshold = threshold

    def compare(self, mode):
        """
        If mode is "double", compares all replays in replays1 against all replays in replays2.
        If mode is "single", compares all replays in replays1 against all other replays in replays1 (len(replays1) choose 2 comparisons).
        In both cases, prints the result of each comparison according to _print_result.

        Args:
            String mode: One of either "double" or "single", determining how to choose which replays to compare.
        """

        if(mode == "double"):
            print("comparing first set of replays to second set of replays")
            iterator = itertools.product(self.replays1, self.replays2)
        elif (mode == "single"):
            print("comparing first set of replays to itself")
            iterator = itertools.combinations(self.replays1, 2)
        else:
            raise Exception("`mode` must be one of 'double' or 'single'")

        for replay1, replay2 in iterator:
            if(self.check_names(replay1.player_name, replay2.player_name)):
                continue
            result = Comparer._compare_two_replays(replay1, replay2)
            self._print_result(result, replay1, replay2)

    def check_names(self, player1, player2):
        """
        Returns True if both players are in the whitelist or are the same name, False otherwise.

        Args:
            String player1: The name of the first player.
            String player2: The name of the second player.
        """

        return ((player1 in WHITELIST and player2 in WHITELIST) or (player1 == player2))

    def divide(self, criterion):
        """
        Splits this comparer in to multiple comparers that are grouped
        by the criterion.
        
        Warning:
            This implementation uses no thresholds and just applies
            some cuts at set intervals so will likely still falsely split replays.
        
        Args:
            Func criterion: A function that takes a Replay and returns the dividing statistic.
            
            
        Returns:
            3 Comparers that are grouped by the criterion.
        """
        
        replays = list(set(self.replays1 + self.replays2))
        
        scored = [(criterion(replay), replay) for replay in replays]
        scored.sort(lambda replay: replay[0])
        
        replays = [replay[0] for replay in scored]
        n = len(replays)
        
        return replays[:n//2], replays[n//4:-n//4], replays[-n//2:]

    def _print_result(self, result, replay1, replay2):
        """
        Prints a human readable version of the result if the average distance
        is below the threshold set from the command line.

        Args:
            Tuple result: A tuple containing (average distance, standard deviation) of a comparison.
            Replay replay1: The replay to print the name of and to draw against replay2
            Replay replay2: The replay to print the name of and to draw against replay1
        """

        mean = result[0]
        sigma = result[1]
        if(mean > self.threshold):
            return
        print("{:.1f} similarity, {:.1f} std deviation ({} vs {})".format(mean, sigma, replay1.player_name, replay2.player_name))
        answer = input("Would you like to see a visualization of both replays? ")
        if answer[0].lower() == "y":
            animation = Draw.draw_replays(replay1, replay2)

    @staticmethod
    def _compare_two_replays(replay1, replay2):
        """
        Compares two Replays and return their average distance
        and standard deviation of distances.
        """

        # get all coordinates in numpy arrays so that they're arranged like:
        # [ x_1 x_2 ... x_n
        #   y_1 y_2 ... y_n ]
        # indexed by columns first.
        data1 = replay1.as_list_with_timestamps()
        data2 = replay2.as_list_with_timestamps()

        # interpolate
        (data1, data2) = Replay.interpolate(data1, data2)

        # remove time from each tuple
        data1 = [d[1:] for d in data1]
        data2 = [d[1:] for d in data2]

        (mu, sigma) = Comparer._compute_data_similarity(data1, data2)

        return (mu, sigma)

    @staticmethod
    def _compute_data_similarity(data1, data2):
        """
        Finds the similarity and standard deviation between two datasets.

        Args:
            List data1: A list of tuples containing the (x, y) coordinate of points
            List data2: A list of tuples containing the (x, y) coordinate of points

        Returns:
            A tuple containing (similarity value, standard deviation) between the two datasets
        """

        data1 = np.array(data1)
        data2 = np.array(data2)

        # switch if the second is longer, so that data1 is always the longest.
        if len(data2) > len(data1):
            (data1, data2) = (data2, data1)

        shortest = len(data2)

        distance = data1[:shortest] - data2
        # square all numbers and sum over the second axis (add row 2 to row 1),
        # finally take the square root of each number to get all distances.
        # [ x_1 x_2 ... x_n   => [ x_1 ** 2 ... x_n ** 2
        #   y_1 y_2 ... y_n ] =>   y_1 ** 2 ... y_n ** 2 ]
        # => [ x_1 ** 2 + y_1 ** 2 ... x_n ** 2 + y_n ** 2 ]
        # => [ d_1 ... d_2 ]
        distance = (distance ** 2).sum(axis=1) ** 0.5

        mu, sigma = distance.mean(), distance.std()

        return (mu, sigma)
