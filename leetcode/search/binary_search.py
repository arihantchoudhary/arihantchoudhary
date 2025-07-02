from typing import List

def binary_search(nums: List[int], target: int) -> int:
    left, right = 0, len(nums) - 1
    
    while left <= right:
        mid = (left + right) // 2
        
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# Test cases
assert binary_search([-1,0,3,5,9,12], 9) == 4, "Test case 1 failed"
assert binary_search([-1,0,3,5,9,12], 2) == -1, "Test case 2 failed"
assert binary_search([1,2,3,4,5,6,7,8,9], 5) == 4, "Test case 3 failed"
assert binary_search([1,2,3,4,5,6,7,8,9], 10) == -1, "Test case 4 failed"
print("All test cases passed!")
