from typing import List

class TrieNode:
    def __init__(self):
        self.children = {}
        self.word = None

class Solution:
    def findWords(self, board: List[List[str]], words: List[str]) -> List[str]:
        root = TrieNode()
        
        # Build Trie
        for word in words:
            node = root
            for char in word:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.word = word
        
        result = []
        
        def backtrack(i: int, j: int, node: TrieNode):
            if i < 0 or i >= len(board) or j < 0 or j >= len(board[0]):
                return
            
            char = board[i][j]
            if char not in node.children:
                return
            
            node = node.children[char]
            
            if node.word:
                result.append(node.word)
                node.word = None  # Avoid duplicates
            
            # Mark as visited
            board[i][j] = "#"
            
            # Explore all 4 directions
            backtrack(i + 1, j, node)
            backtrack(i - 1, j, node)
            backtrack(i, j + 1, node)
            backtrack(i, j - 1, node)
            
            # Restore the cell
            board[i][j] = char
        
        for i in range(len(board)):
            for j in range(len(board[0])):
                backtrack(i, j, root)
        
        return result


def test_word_search_ii():
    solution = Solution()
    
    # Test case 1: Example 1
    board1 = [["o","a","a","n"],["e","t","a","e"],["i","h","k","r"],["i","f","l","v"]]
    words1 = ["oath","pea","eat","rain"]
    result1 = solution.findWords(board1, words1)
    expected1 = ["eat","oath"]
    assert sorted(result1) == sorted(expected1), f"Test 1 failed: got {result1}, expected {expected1}"
    
    # Test case 2: Example 2
    board2 = [["a","b"],["c","d"]]
    words2 = ["abcb"]
    result2 = solution.findWords(board2, words2)
    expected2 = []
    assert result2 == expected2, f"Test 2 failed: got {result2}, expected {expected2}"
    
    # Test case 3: Single letter words
    board3 = [["a","b"],["c","d"]]
    words3 = ["a","b","c","d","e"]
    result3 = solution.findWords(board3, words3)
    expected3 = ["a","b","c","d"]
    assert sorted(result3) == sorted(expected3), f"Test 3 failed: got {result3}, expected {expected3}"
    
    # Test case 4: No words found
    board4 = [["a","b"],["c","d"]]
    words4 = ["xyz","efg"]
    result4 = solution.findWords(board4, words4)
    expected4 = []
    assert result4 == expected4, f"Test 4 failed: got {result4}, expected {expected4}"
    
    # Test case 5: All words found
    board5 = [["a","b","c"],["d","e","f"],["g","h","i"]]
    words5 = ["abc","def","ghi","adg","beh","cfi"]
    result5 = solution.findWords(board5, words5)
    expected5 = ["abc","def","ghi","adg","beh","cfi"]
    assert sorted(result5) == sorted(expected5), f"Test 5 failed: got {result5}, expected {expected5}"
    
    print("All test cases passed!")


if __name__ == "__main__":
    test_word_search_ii()