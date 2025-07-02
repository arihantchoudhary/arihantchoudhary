from typing import List

class Solution:
    def exists(self, board: List[List[str]], word: str) -> bool:
        def backtrack(i: int, j: int, k: int) -> bool:
            if k == len(word):
                return True
            if i < 0 or i >= len(board) or j < 0 or j >= len(board[0]) or board[i][j] != word[k]:
                return False
            temp = board[i][j]
            board[i][j] = "#"
            found = (backtrack(i + 1, j, k + 1) or backtrack(i - 1, j, k + 1) or
                      backtrack(i, j + 1, k + 1) or backtrack(i, j - 1, k + 1))
            board[i][j] = temp
            return found

        for i in range(len(board)):
            for j in range(len(board[0])):
                if backtrack(i, j, 0):
                    return True
        return False


def test_word_search():
    solution = Solution()
    
    # Test case 1: Word exists
    board1 = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]
    word1 = "ABCCED"
    assert solution.exists(board1, word1) == True, f"Test 1 failed: expected True"
    
    # Test case 2: Word exists
    board2 = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]
    word2 = "SEE"
    assert solution.exists(board2, word2) == True, f"Test 2 failed: expected True"
    
    # Test case 3: Word does not exist
    board3 = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]]
    word3 = "ABCB"
    assert solution.exists(board3, word3) == False, f"Test 3 failed: expected False"
    
    # Test case 4: Single character
    board4 = [["A"]]
    word4 = "A"
    assert solution.exists(board4, word4) == True, f"Test 4 failed: expected True"
    
    # Test case 5: Single character not found
    board5 = [["A"]]
    word5 = "B"
    assert solution.exists(board5, word5) == False, f"Test 5 failed: expected False"
    
    print("All test cases passed!")


if __name__ == "__main__":
    test_word_search()