from typing import List
import itertools
from typing import List
import collections

def find_maxflow_paths(graph: List[List[int]], source: int, sink: int) -> List[List[int]]:
    """
    寻找所有能够实现最大流的路径组合
    :param graph: 图
    :param source: 源点
    :param sink: 汇点
    :return: 所有能够实现最大流的路径组合
    """
    # 使用BFS寻找一条增广路径，并返回该路径
    def bfs(graph, source, sink, parent):
        visited = [False] * len(graph)
        queue = []
        queue.append(source)
        visited[source] = True
        while queue:
            u = queue.pop(0)
            for ind, val in enumerate(graph[u]):
                if not visited[ind] and val > 0:
                    queue.append(ind)
                    visited[ind] = True
                    parent[ind] = u
                    if ind == sink:
                        return True
        return False

    # 获取图的最大流
    def get_maxflow(graph, source, sink):
        parent = [-1] * len(graph)
        max_flow = 0
        while bfs(graph, source, sink, parent):
            path_flow = float("Inf")
            s = sink
            while s != source:
                path_flow = min(path_flow, graph[parent[s]][s])
                s = parent[s]
            max_flow += path_flow
            v = sink
            while v != source:
                u = parent[v]
                graph[u][v] -= path_flow
                graph[v][u] += path_flow
                v = parent[v]
        return max_flow


    def find_maxflow_paths(graph, source, sink):

        max_flow = get_maxflow(graph, source, sink)
        visited = set()
        paths = []
        while True:
            # Find all augmenting paths.
            augmenting_paths = find_augmenting_paths(graph, source, sink, visited)
            if not augmenting_paths:
                break
            # Merge the augmenting paths into a single path.
            merged_path = merge_augmenting_paths(graph, augmenting_paths)
            # Update the graph by increasing flow along the merged path.
            for i in range(len(merged_path) - 1):
                u = merged_path[i]
                v = merged_path[i + 1]
                graph[u][v] -= 1
                graph[v][u] += 1
            visited.clear()
            # Calculate the new maximum flow.
            new_flow = get_maxflow(graph, source, sink)
            if new_flow == max_flow:
                # The augmenting paths can be combined to achieve the maximum flow.
                paths.append(merged_path)
        print(paths)
        print('='*100)
        return paths

    import collections

    def find_augmenting_paths(graph, source, sink, visited):
        # 初始化存储所有增广路径的列表和使用FIFO模式的队列。
        paths = []
        queue = collections.deque([[source]])

        # 取出队首元素（当前路径），并将其最后一个节点作为“当前节点”。
        while queue:
            path = queue.popleft()
            node = path[-1]
            # 如果当前节点与汇点相同，则将当前路径添加到增广路径列表中。
            if node == sink:
                paths.append(path)
            # 否则，如果当前节点尚未被访问，则将其标记为已访问，并遍历它的邻居节点。
            elif node not in visited:
                visited.add(node)
                for neighbor, capacity in enumerate(graph[node]):
                    # 如果某个邻居节点未被访问且与当前节点之间存在一条边，则将其添加到队列中。
                    if capacity > 0 and neighbor not in visited:
                        queue.append(path + [neighbor])
            print(path)
        
        # 输出找到的所有增广路径，并返回这些路径。
        print(paths)
        print('-'*100)
        return paths


    def merge_augmenting_paths(graph, paths):
        """
        Merge augmenting paths into a single path.
        """
        merged_path = []
        for i in range(len(paths[0])):
            node = paths[0][i]
            for j in range(1, len(paths)):
                if node != paths[j][i]:
                    return merged_path
            merged_path.append(node)
        return merged_path

    # 找到所有能够实现最大流的路径组合
    maxflow = get_maxflow(graph, source, sink)
    all_paths = find_maxflow_paths(graph, source, sink)
    maxflow_paths = []
    for paths in itertools.product(all_paths, repeat=2):
        p = list(set(sum(paths, [])))
        if len(p) == len(set(p)) and get_maxflow(graph, source, sink) == maxflow:
            maxflow_paths.append(paths[0])
    return maxflow_paths


import unittest

class TestFindMaxFlowPaths(unittest.TestCase):
    def test_find_maxflow_paths(self):
        graph = [[0, 7, 0, 5, 0, 0],
                 [0, 0, 4, 0, 0, 0],
                 [0, 0, 0, 2, 6, 0],
                 [0, 0, 0, 0, 0, 7],
                 [0, 0, 0, 0, 0, 3],
                 [0, 0, 0, 0, 0, 0]]
        source = 0
        sink = 5
        maxflow_paths = find_maxflow_paths(graph, source, sink)
        expected_maxflow_paths = [
            ([0, 1, 2, 4, 5], [0, 1, 2, 3, 5]),
            ([0, 1, 2, 4, 5], [0, 3, 5])
        ]
        print(maxflow_paths)
        self.assertEqual(maxflow_paths, expected_maxflow_paths)

if __name__ == '__main__':
    unittest.main()
