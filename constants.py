# Connection
PORT = 8080
IP = 'localhost'
GAME_ID = 58

# Minmax
M_CONST = 10*10
MAX_DEPTH = 3
VERT_POS = [5,5,5,5,5,
                    6,6,6,6,6,6,
                    7,7,7,7,7,7,7,
                    8,8,8,8,8,8,8,8,
                    9,9,9,9,9,9,9,9,9,
                    10,10,10,10,10,10,10,10,
                    11,11,11,11,11,11,11,
                    12,12,12,12,12,12,
                    13,13,13,13,13,
                    4,4,4,4,
                    3,3,3,
                    2,2,
                    1,
                    5,6,7,8,
                    5,6,7,
                    5,6,
                    5,
                    10,11,12,13,
                    11,12,13,
                    12,13,
                    13,
                    14,14,14,14,
                    15,15,15,
                    16,16,
                    17,
                    13,12,11,10,
                    13,12,11,
                    13,12,
                    13,
                    8,7,6,5,
                    7,6,5,
                    6,5,
                    5]

HOR_POS = [9,8,7,6,5,
                      9.5,8.5,7.5,6.5,5.5,4.5,
                      10,9,8,7,6,5,4,
                      10.5,9.5,8.5,7.5,6.5,5.5,4.5,3.5,
                      11,10,9,8,7,6,5,4,3,
                      10.5,9.5,8.5,7.5,6.5,5.5,4.5,3.5,
                      10,9,8,7,6,5,4,
                      9.5,8.5,7.5,6.5,5.5,4.5,
                      9,8,7,6,5,
                      8.5,7.5,6.5,5.5,
                      8,7,6,
                      7.5,6.5,
                      7,                    
                      4,3.5,3,2.5,
                      3,2.5,2,
                      2,1.5,
                      1,
                      2.5,3,3.5,4,
                      2,2.5,3,
                      1.5,2,
                      1,
                      5.5,6.5,7.5,8.5,
                      6,7,8,
                      6.5,7.5,
                      7,
                      10,10.5,11,11.5,
                      11,11.5,12,
                      12,12.5,
                      13,
                      11.5,11,10.5,10,
                      12,11.5,11,
                      12.5,12,
                      13]