import math
import random
from functools import lru_cache 
import numpy as np
import bisect


#-----targil_1-----:
def targil_1_original(costs_list):
    function_calls = [0]
    cost_starting_at_0 = targil_1_rec(costs_list, 0, 0, function_calls)
    cost_starting_at_1 = targil_1_rec(costs_list, 0, 1, function_calls)
    return min(cost_starting_at_0, cost_starting_at_1), function_calls[0]

def targil_1_rec(costs_list, total_cost, current_location, function_calls):
    function_calls[0] += 1
    if len(costs_list)<=current_location: return total_cost
    
    total_cost += costs_list[current_location]
    return min(targil_1_rec(costs_list, total_cost, current_location + 1, function_calls),
                targil_1_rec(costs_list, total_cost, current_location + 2, function_calls))

def targil_1_dyn(costs_list):
    # the two integers representing the min-route for each odd/even iteration of the loop:
    min_even: int = 0
    min_odd: int = 0 

    # the two base-cases included in the loop:
    # entry at step=0:
    # enters the first if-block => min_even = min(0, 0) => min_even = 0 => min_even += cost (10 in our case) => min_even = cost (10).
    # entry at step=1:
    # enters the second if-block => min_odd = min(0, 10) => min_odd = 0 => min_odd += cost (11 in our case) => min_odd = cost (11).
    #
    # these account for the two stairs-entry states provided in the exercise.

    for step, cost in enumerate(costs_list):
        # print(f"step: {step}, cost: {cost}, min_even: {min_even}, min_odd: {min_odd}.")
        if step % 2 == 0: # even-ended-route:
            min_even = min(min_odd, min_even)
            min_even += cost
        else: # odd-ended-route:
            min_odd = min(min_odd, min_even)
            min_odd += cost
    
    return min(min_even, min_odd) # this part makes sure we return the smallest of the two sums, passing the n'th step. 
#-----targil_1-----:


#-----targil_2-----:
def targil_2_naive_wrapper(nums, shuffle: bool):
    if shuffle: 
        random.shuffle(nums)
        print(f"shuffled nums: {nums}")
    return targil_2_naive_rec(nums)

def targil_2_naive_rec(nums):
    nums_length = len(nums)
    # print(f"nums: {nums}, balloons_left: {nums_length}")
    if nums_length == 0: return 0, []
    if nums_length == 1: return nums[0], [nums[0]]

    largest_score = 0
    best_sequence = []

    for index, value in enumerate(nums):
        
        if index == 0: # current_calc = 1 * nums[0] * nums[1]
            middle_mul = value * nums[1] 

        elif index == nums_length - 1: # current_calc = nums[n] * nums[n-1] * 1    (n = balloons_left)
            middle_mul = value * nums[nums_length - 2]   

        else: # (0 < index < balloons_left):
            middle_mul = nums[index - 1] * value * nums[index + 1]

        left_nums = nums[:index]
        right_nums = nums[index + 1:]

        # print(f"index: {index}, nums: {nums}, balloons_left: {nums_length}, left_nums: {left_nums}, right_nums: {right_nums}")
        left_score, left_seq = targil_2_naive_rec(left_nums)
        right_score, right_seq = targil_2_naive_rec(right_nums)

        current_score = left_score + middle_mul + right_score

        if largest_score < current_score: 
            largest_score = current_score
            best_sequence = [value] + left_seq + right_seq # concatenation of lists in  python.
    return largest_score, best_sequence

def targil_2_DP_wrapper(nums, shuffle=False):
    if shuffle:
        random.shuffle(nums)
        print(f"shuffled nums: {nums}")

    padded_nums = [1] + nums + [1] # gemini recommended doing the 1' paddings instead of introducing =>
    # unnecessary branching logic inside each iteration itself, which slightly increases overhead.

    @lru_cache(maxsize=256) # limiting the maximum cached number of calls. =>
    # for the assignment's time and space complexity, we assume that the cache is of infinite size.  
    def dp2(left, right):
        max_coins = 0
        best_sequence = []
        # the recursive dp() function accounts for the empty set containing no balloons =>
        # and returns the base case: max_coins = 0, best_sequence = [] as it is initialized here.

        for i in range(left + 1, right): # this range makes sure to account the left-padding on each iteration.
            left_score, left_seq = dp2(left, i)
            right_score, right_seq = dp2(i, right)
            current_coins = left_score + (padded_nums[left] * padded_nums[i] * padded_nums[right]) + right_score

            if  max_coins < current_coins:
                max_coins = current_coins
                best_sequence = left_seq + right_seq + [i]
        
        return  max_coins, best_sequence

    result = dp2(0, len(padded_nums) - 1) # =>
    # executing the first dp() call on the full nums[] array.

    #---{
    # doing this to tie dp()'s lru_cache's methods to the wrapper function's for evaluation in main():
    targil_2_DP_wrapper.cache_info = dp2.cache_info                                                 # pyright: ignore[reportFunctionMemberAccess]
    targil_2_DP_wrapper.cache_clear = dp2.cache_clear                                               # pyright: ignore[reportFunctionMemberAccess] =>
    # the pyright linter really doesn't like attaching new function attributes... (static-typing FTW!!)
    #---}

    return result
#-----targil_2-----:


#-----targil_3-----:
# failed attempt:
# region
"""
def targil_3_DP(dungeon, rows, cols, shuffle=False):
    if  shuffle:
        np_matrix = np.array(dungeon)
        flattened = np_matrix.ravel()
        np.random.shuffle(flattened)
        rows, cols = np_matrix.shape
        dungeon = flattened.reshape(np_matrix.shape).tolist()
        print(f"shuffled dungeon[][]:") 
        for row in dungeon:                                                                         # pyright: ignore[reportGeneralTypeIssues]
            print(row)

    original_rows, original_cols = rows, cols

    # padding the matrix into a square matrix (makes the boundary checks easier):
    if  rows < cols: # adding more rows:
        padding = [[None] * cols for _ in range(cols - rows)]
        dungeon = padding + dungeon                                   # pyright: ignore[reportOperatorIssue]
        rows = rows # =>
        # rows will later be passed into dp3 and will serve the purpose of keeping the size dungeon's rows and columns (now equal) sizes.

    elif cols < rows: # adding more columns:
        for i in range(rows):                                                                       
            dungeon[i] = [None] * (rows - cols) + dungeon[i] # adding cols from the "left side" of the =>                   # pyright: ignore
            # matrix. this will find later use when we need to find the first value of each =>
            # iteration across the anti-diagonal of dungeon[][]... and the same goes =>
            # for the rows- we padded the rows from it's upper side.
            cols = rows

    print(f"padded dungeon[][]:")
    for row in dungeon:                                                                             # pyright: ignore[reportGeneralTypeIssues]
            print(row)

    return dp3(dungeon, (2 * rows) - 2, rows, 1, original_rows, original_cols) # =>
    # current_iter loops across the matrix's diagonal in reverse([rows-1,cols-1]->[0,0]) =>
    # while dp3()'s inner for-loop iterates over every element across the anti-diagonal =>
    # calculating the best route, based on the previous anti-diagonal's best routes, which =>
    # override the previous values in the dungeon-matrix, as they are no longer needed.
    # dp3 will start from the second anti-diagonal (current_iter=1), representing the two =>
    # values at the coordinates: [rows-2][cols-1], [rows-1][cols-2]:

def dp3(dungeon, last_iter, rows, current_iter, original_rows, original_cols):

# NOTE: I'm keeping this block as a reminder of making poor early coding choices. and to laugh at it from time to time:
#######################################################################################################################################################
# base case (last iteration):                                                                                                                         #
#---                                                                                                                                                  #
# P.S.: a pretty intimidating-looking base-case check. =>                                                                                             #
# I'ma add another drawing to show the idea behind running by both the first row, and first column. NOTE: DRAW AND TAKE PICTURE                       #
# if  current_iter == last_iter:                                                                                                                      #
#     for _ in rows:                                                                                                                                  #
#         values_in_first_row = dungeon[0][_]                                                                                                         #
#         values_in_first_col = dungeon[_][0]                                                                                                         #
#         if  values_in_first_row != None: return values_in_first_row # this accounts for the empty cols added by the square-matrix-padding.          #
#         if  values_in_first_col != None: return values_in_first_col # same story but for column-paddings.                                           #
#         # NOTE: this can't keep running forever, since our matrix does have non-'None' values in it, but still... =>                                #
#         # pretty inefficient if you ask me. nothing that a fast static language can't fix with some extra time, but this assignment isn't about it. #
#         else: continue                                                                                                                              #
# #---                                                                                                                                                #
###################################################################################################################################3###################


    # how many iterations required across this specific anti-diagonal:
    iterations = rows - abs(rows - (current_iter + 1)) # don't question it.. => 
    # at this point my brain is fully fried, no idea why I decided on doing this without AI..

    # I know it looks a bit confusing, but the main point of this line is moving across the upmost => 
    # north-eastern part of each anti-diagonal in dungeon[][]:
    first_value_i, first_value_j = (rows - 1 - current_iter, rows - 1) if current_iter < rows else (0, iterations - 1) # =>
    # it happens to be that when the value is on the first row, the row's index is equal the number of iterations required. 
    print(f"first value: {dungeon[first_value_i][first_value_j]}")

    
    running_i, running_j = first_value_i, first_value_j
    for i in range(iterations):

        # skipping padding values:
        if  dungeon[running_i][running_j] == None: continue

        # I updated the padding so that it doesn't interfere with the wall-boundaries-checks, so now =>
        # both - (below_of_running / right_of_running) can't be equal None. saves a headache and a half..
        below_of_running = dungeon[running_i + 1][running_j]
        right_of_running = dungeon[running_i][running_j + 1]

        #---
        # updating the first value on it's right-wall:
        if running_j == rows: dungeon[running_i][running_j] += dungeon[running_i - 1][running_j] # =>
        # starting from the right-most wall, we only take values from below the value.

        # updating the first value on it's bottom-wall:
        if running_i == rows: dungeon[running_i][running_j] += dungeon[running_i][running_j - 1] # =>
        # hitting the bottom-most wall, we only take values from the right of the value.
        
        # NOTE: no need for a unified check of both conditions, since our iteration starts from 0, =>
        #       because there's no need for updating the value at dungeon[rows-1][rows-1].
        #---

        # updating the value:
        dungeon[running_i][running_j] += max(below_of_running, right_of_running) 

        # updating the running indexes to match the anti-diagonal's coordinates:
        running_i += 1
        running_j -= 1
    
    
    return dp3(dungeon, last_iter, rows, current_iter + 1)
    """
# endregion

def targil_3_DP(dungeon, rows, cols, shuffle=False):
    if  shuffle:
        np_matrix = np.array(dungeon)
        flattened = np_matrix.ravel()
        np.random.shuffle(flattened)
        rows, cols = np_matrix.shape
        dungeon = flattened.reshape(np_matrix.shape).tolist()
        print(f"shuffled dungeon[][]:") 
        for row in dungeon:                                                                         # pyright: ignore[reportGeneralTypeIssues]
            print(row)
    
    dp3(dungeon, rows, cols, rows - 1, cols - 1) # =>
    # the first dp3() call will start at dungeon[rows-1][cols-1]. on each call of =>
    # dp3(), we check the-2 (possible) blocks: below, and to the right, of the =>
    # current location in the matrix, append the min() of the 2 to the current =>
    # block, and keep moving and comparing until we get to dungeon[0][0]. 

    return dungeon[0][0]                                                                            # pyright: ignore[reportIndexIssue]

def dp3(dungeon, rows, cols, current_row, current_col):
    
    # a single updating of the dungeon[rows-1][cols-1] block:
    if  current_row == rows - 1 and current_col == cols - 1: 
        dungeon[current_row][current_col] = max(1, 1 - dungeon[current_row][current_col])
    
    else:
        # assigning the below/right blocks and checking boundaries:
        below_block = dungeon[current_row + 1][current_col] if current_row + 1 < rows else math.inf
        right_block = dungeon[current_row][current_col + 1] if current_col + 1 < cols else math.inf

        # calculating minimum required health from the current-block to dungeon[rows-1][cols-1]:
        dungeon[current_row][current_col] = max(1, min(right_block, below_block) - dungeon[current_row][current_col]) # =>
        # took me hours until I realized I was calculating the maximum path length and not checking health => 
        # bounds on each iteration like a real videogame smh...

    # base case checking condition:
    if  current_row == 0 and current_col == 0:  
        return # we've arrived at dungeon[0][0] and should return to targil_3_DP().
    
    # new dp3() calls:
    #-----
    go_up = (current_row!=0) # all blocks call up.
    go_left = (current_col!=0) and (current_row == rows - 1) # making only current blocks which are in =>
    # row: dungeon[row-1] make 2 calls. any other block will only call on the block above him, making an => 
    # "activation chain" looking-pattern where only the lowest block activates an entire column, making sure => 
    # every comparison of previous below/right blocks has already been updated, and never calling twice on the same block.

    if  go_up:   dp3(dungeon, rows, cols, current_row - 1, current_col)
    if  go_left: dp3(dungeon, rows, cols, current_row, current_col - 1)
    #-----
#-----targil_3-----:


#-----targil_4-----:
def targil_4_DP(prices, Rest, Sell, Buy, shuffle=False):
    
    if shuffle:
        random.shuffle(prices)
        print(f"shuffled prices: {prices}")

    Rest_prev = Rest
    Sell_prev = Sell
    buy_prev = Buy

    for price in prices:
        Rest = max(Rest_prev, Sell_prev)
        Sell = buy_prev + price
        Buy = max(buy_prev, Rest_prev - price)

        # updating prevs:
        Rest_prev = Rest
        Sell_prev = Sell
        buy_prev = Buy
    
    return max(Rest, Sell)
#-----targil_4-----:


#-----targil_5-----:
def targil_5_DP(times, jobs, profits):

    # restructuring the data into lists: entries = [(start, end, profit, original_id), ...]
    entries = [(times[i][0], times[i][1], profits[i], i + 1) for i in range(jobs)] 

    # sorting jobs by end-time (Ascending):
    entries.sort(key=lambda x: x[1])

    sorted_end_times = [entry[1] for entry in entries] # this is going to be =>
    # the list used to binary search jobs and then fetching the coresponding job entry.

    # cache that store the currently maximum profit achievable:
    dp_cache = [0] * (jobs + 1) # includes the base: 0 jobs (= 0 profit).
    

    for i in range(1, jobs + 1): 

        current_start, _, current_profit, _ = entries[i - 1]

        # using binary-search to find a job that ended BEFORE OR AT our current_start.
        # the built-in bisec_right returns an index indicating the jobs to the left of =>
        # that index in- sorted_end_times are all compatible with the condition.
        compatible_job_idx = bisect.bisect_right(sorted_end_times, current_start)
        
        #splitting options comparison (2 per each entry in: entries[i] ):
        #---
        # option A: Exclude current job (take previous max):
        exclude_profit = dp_cache[i - 1]
        # option B: Include current job (take its profit + max profit of previous (time compatible) max profit):
        include_profit = current_profit + dp_cache[compatible_job_idx]
        #---

        dp_cache[i] = max(exclude_profit, include_profit)
    
    backtracking = []
    current_i = jobs

    # we traverse the DP array backward, starting from the final calculated maximum.
    # at each step, we determine if the current job contributed to the total profit:
    while current_i > 0:
        current_start, _, _, original_id = entries[current_i - 1]

        # if the profit is greater than it's previous we know that: =>
        # that job's profit must have been included:
        if  dp_cache[current_i - 1] < dp_cache[current_i]: 
            backtracking.append(f"J{original_id:02d}") # => this job was chosen.
            # jumping to the latest compatible (non-overlapping) end_time:
            current_i = bisect.bisect_right(sorted_end_times, current_start)  

        # and if the profit is equal to it's previous then: =>
        # that job's profit was skipped by the algorithm (a better sequence of choices was chosen instead of it.)..
        else:
            current_i -= 1 # incrementing the index to check the next profit's comparison and so on...
            
    return dp_cache[jobs], backtracking
#-----targil_5-----:






def main():
#-----targil_1-----:
    costs_list = [10, 11, 1, 14, 0, 7, 5, 8, 3, 12,
                             15, 2, 9, 6, 4, 13, 11, 4, 8, 0, 9]
    # NAIVE:
    # targil 1 recursively (slow and inefficient):
    # print("minimum total cost: %i, number of calls: %i." %targil_1_original(costs_list))

    # DP: 
    # NOTE: uncomment this section:
    #-----
    print("\n|-----targil_1-START-----|\n")
    # targil 1 dynamically (fast and time/space cheap):
    print("minimum total cost: %i." %targil_1_dyn(costs_list))
    print("\n|-----targil_1-END-----|\n\n")
    #-----
#-----targil_1-----:

#-----targil_2-----:
    # nums = [11, 2, 1, 12, 5, 4, 4, 3, 7]
    # nums = list(range(1, 6))
    m = random.randint(1, 20)
    nums = random.choices(range(1, 101), k=m)
    #print(f"original nums: {nums}")
    #print(f"number of balloons: {m}.")

    # NAIVE:
    # max_total_sum_rec, sequence_rec = targil_2_naive_wrapper(nums, shuffle=False)
    # print(f"sequence:      {sequence_rec}\nmax_total_sum: {max_total_sum_rec}.") # =>
    # sequence is evaluated by value, the recursive approach makes tracking the previous =>
    # state's index more difficult: each recursive call requires full bottom-up evaluation => 
    # before we know whether the current call returned the max_value and the index is useful... 
    
    # DP: 
    # NOTE: uncomment this section:
    #-----
    print("\n|-----targil_2-START-----|\n")
    targil_2_dyn = targil_2_DP_wrapper
    max_total_sum_dyn, sequence_dyn = targil_2_dyn(nums, shuffle=False)
    print(f"sequence:      {sequence_dyn}\nmax_total_sum: {max_total_sum_dyn}.") # =>
    # here sequence is represented by the index, found it easier to review the order.
    #---{
    print(targil_2_dyn.cache_info())                                                               # pyright: ignore[reportFunctionMemberAccess]
    targil_2_dyn.cache_clear()                                                                     # pyright: ignore[reportFunctionMemberAccess]
    #---}
    print("\n|-----targil_2-END-----|\n\n")
    #-----
#-----targil_2-----:

#-----targil_3-----:
    # dungeon = [[-1,-1,0],[-1,0,1],[-1,0,-1]] # should return "1".
    # rows, columns = 3, 3

    rows = random.randint(2, 20)
    columns = random.randint(2, 20)
    dungeon = [[random.randint(-50, 51) for _ in range(columns)] for _ in range(rows)]

    # rows = random.randint(2, 20)
    # columns = random.randint(2, 20)
    # dungeon = [[random.randint(-10, 11) for _ in range(columns)] for _ in range(rows)]

    # NOTE: uncomment this section:
    #-----
    print("\n|-----targil_3-START-----|\n")
    print(f"rows: {rows}")
    print(f"columns: {columns}")
    print(f"original dungeon[][]:") 
    for row in dungeon: 
        print(row)
    print(f"amount of health required: {targil_3_DP(dungeon, rows, columns, shuffle=False)}.")
    print("\n|-----targil_3-END-----|\n\n")
    #-----
#-----targil_3-----:

#-----targil_4-----:

    # NOTE: completely unnecessary... this stemmed from the amount of uncpecified implicit =>
    # details in this problem that made it really hard for me to understand the exact objective.
    ##############################################################################
    # class Three_States(Enum):                                                  #
    #     RESTING = 0                                                            #
    #     HOLDING = 1                                                            #
    #     JUST_SOLD = 2                                                          #
    #                                                                            #
    # class Status:                                                              #
    #     def __init__(self, status: Three_States, starting_value: int) -> None: #
    #         self._status = status                                              #
    #         self._cha_ching = starting_value                                   #
    #                                                                            #
    #     # "getters":                                                           #
    #     def __str__(self):                                                     #
    #         return f"{self._status.name}"                                      #
    #                                                                            #
    #     def money_made (self):                                                 #
    #         return self._cha_ching # returning a reference to an Enum is safe, #
    #         # Enums are immutable by default in standard python.               #
    #                                                                            #
    #     # setter:                                                              #
    #     def add_profit (self, dif) -> None:                                    #
    #         if  isinstance(dif, int):                                          #
    #             self._cha_ching += dif                                         #
    ##############################################################################

    prices: list[int] = [4,1,3,7,2,3,5]

    # NOTE: uncomment this section:
    #-----
    print("\n|-----targil_4-START-----|\n")
    print(f"prices: {prices}.")
    
    # initializing the 3 states to their start position:
    Rest = 0
    Sell = -math.inf
    Buy = -prices[0] 
    
    print(f"Maximum profit: {targil_4_DP(prices[1:], Rest, Sell, Buy, False)}.")
    print("\n|-----targil_4-END-----|\n\n")
    #-----
#-----targil_4-----:

#-----targil_5-----:
    # NOTE: just uncomment the entire thing:
    ##-----
    print("\n|-----targil_5-START-----|\n")
    gantt_show_payment = True

    start_time_range, end_time_range, start_profit_range, end_profit_range, jobs = 0, 23, 1, 99, 10
    # generating job profits, start-times and end-times, sorted and filtered for the comfort of the eye.
    # the algorithm's logic would still work if the 'cyclic' job hours could be sliced per sections into =>
    # different days and fed as a pipline, saving previous best_profits and times, but that's an insane =>
    # amount of effort (even for me), even though it works in theory and that's enough for me for the time being.
    #-----
    times = [(random.randint(start_time_range, end_time_range), random.randint(start_time_range, end_time_range)) for _ in range(jobs)]
    # print(f"random unsorted times: \n{times}.")
    times = [(random.sample(range(start_time_range, end_time_range), 2)) if t[0] == t[1] else t for t in times] 
    # print(f"uniquely resampling 0 lasting jobs: \n{times}.")
    times = [sorted(time) for time in times]
    print(f"random sorted times: \n{times}.\n")
    startTime = [t[0] for t in times]
    endTime = [t[1] for t in times]
    profit = [random.randint(start_profit_range, end_profit_range) for _ in range(jobs)]
    #-----

    # vertical table: 
    #---
    print(f"idx:       {' '.join(f"{i:02d}" for i in range(1, jobs+1))}")
    print(f"startTime: {' '.join(f"{st:02d}" for st in startTime)}")
    print(f"endTime:   {' '.join(f"{et:02d}" for et in endTime)}")
    print(f"profit:    {' '.join(f"{pt:02d}" for pt in profit)}")
    #---
    print("\nsimple gantt chart: (job", "\\", "time):\n  |", end="")
    for hour in range(end_time_range + 1):
        print(f"{hour:02d}|", end="")

    print()
    for job in range(jobs):
        job_str = f"{job+1:02d}|"
        profit_str = f"{profit[job]:02d}|" if gantt_show_payment else "##|"
        
        interval = endTime[job]-startTime[job]
        if  interval == 1:
            job_span = profit_str
        elif interval == 2:
            job_span = profit_str * 2
        else:
            job_span = profit_str + "$$|" * (interval - 2) + profit_str

        prefix_padding = "  |" * startTime[job]
        suffix_padding = "  |" * ((end_time_range + 1) - endTime[job])

        print(job_str + prefix_padding + job_span + suffix_padding)

    max_profit, backtracking = targil_5_DP(times, jobs, profit)
    print(f"\nmax profit reachable: {max_profit}.")
    print(f"backtracking best sequence: {backtracking}.")
    print("\n|-----targil_5-END-----|\n\nthanks.:).")
    ##-----
#-----targil_5-----:

main()