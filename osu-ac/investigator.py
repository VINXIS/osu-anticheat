import numpy as np

class Investigator:
    """
    A class for checking isolated replays for cheats. 

    See Also:
        Comparer
    """
    def __init__(self):
        pass

    @staticmethod
    def as_time_space(replay):
        # take in a replay and output it in the format of:
        #
        # [  t1, t2 ... tn ],
        #
        # [[ x1, x2 ... xn ],
        #  [ y1, y2 ... yn ]]
        
        data = replay.as_list_with_timestamps()
        
        data = np.transpose(data)

        return data[0], data[1:]

    @staticmethod
    def velocity(time, space):
        # differentiate both time and space so we get
        # [[ dx1, dx2 ... dxn ], =
        #  [ dy1, dy2 ... dyn ]] = [[ vx1, vx2 ... vxn ],
        # ---------------------- =  [ vy1, vy2 ... vyn ]]
        # [  dt1, dt2 ... dtn ]  =
        return np.diff(space) / np.diff(time)
        
