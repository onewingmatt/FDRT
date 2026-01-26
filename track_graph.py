"""Simple helper for walking track connectivity based on Formula D geometry."""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from formula_d_game import Track, TrackSpace


class TrackGraph:
    """A lightweight graph wrapper that exposes path-based helpers for movement."""

    def __init__(self, track: Track):
        self.track = track
        self._spaces: Dict[int, TrackSpace] = {space.id: space for space in track.spaces}
        self._adjacency: Dict[int, List[int]] = {
            space.id: list(space.connected_spaces) for space in track.spaces
        }

    def get_space(self, space_id: int) -> Optional[TrackSpace]:
        return self._spaces.get(space_id)

    def walk(self, start_space_id: int, steps: int) -> List[List[int]]:
        """Return every unique path of exactly ``steps`` edges starting from ``start_space_id``."""

        if steps <= 0:
            return []

        paths: List[List[int]] = []

        def dfs(current_space_id: int, depth: int, path: List[int]) -> None:
            if depth == steps:
                paths.append(path.copy())
                return

            neighbors = self._adjacency.get(current_space_id, [])
            for next_space_id in neighbors:
                if next_space_id not in self._spaces:
                    continue
                path.append(next_space_id)
                dfs(next_space_id, depth + 1, path)
                path.pop()

        dfs(start_space_id, 0, [start_space_id])
        return paths

    def iter_space_lanes(self, path: Iterable[int]) -> List[int]:
        """Return lane IDs for the supplied path sequence."""

        lanes: List[int] = []
        for space_id in path:
            space = self.get_space(space_id)
            if space is None:
                continue
            lanes.append(space.lane)
        return lanes


_TRACK_GRAPH_CACHE: Dict[str, TrackGraph] = {}


def get_track_graph(track: Track) -> TrackGraph:
    """Return or build a cached TrackGraph for the provided track."""

    cache_key = track.name
    if cache_key not in _TRACK_GRAPH_CACHE:
        _TRACK_GRAPH_CACHE[cache_key] = TrackGraph(track)
    return _TRACK_GRAPH_CACHE[cache_key]
