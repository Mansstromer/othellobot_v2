# metrics.py

from collections import defaultdict
import threading

_store = threading.local()

def _ensure_init():
    """Initialize thread‐local storage on first use."""
    if not hasattr(_store, 'nodes'):
        _store.nodes = 0
        _store.cutoffs = 0
        _store.tt_hits = 0
        _store.per_depth = defaultdict(lambda: {'nodes':0, 'cutoffs':0, 'tt_hits':0})
        _store.current_depth = None

def reset():
    """Zero out all counters and timers."""
    _store.nodes = 0
    _store.cutoffs = 0
    _store.tt_hits = 0
    _store.per_depth = defaultdict(lambda: {'nodes':0, 'cutoffs':0, 'tt_hits':0})
    _store.current_depth = None

def inc_node():
    _ensure_init()
    _store.nodes += 1
    if _store.current_depth is not None:
        _store.per_depth[_store.current_depth]['nodes'] += 1

def inc_cutoff():
    _ensure_init()
    _store.cutoffs += 1
    if _store.current_depth is not None:
        _store.per_depth[_store.current_depth]['cutoffs'] += 1

def inc_tthit():
    _ensure_init()
    _store.tt_hits += 1
    if _store.current_depth is not None:
        _store.per_depth[_store.current_depth]['tt_hits'] += 1

def set_depth(d: int):
    _ensure_init()
    _store.current_depth = d

def snapshot():
    _ensure_init()
    return {
        'nodes':     _store.nodes,
        'cutoffs':   _store.cutoffs,
        'tt_hits':   _store.tt_hits,
        'per_depth': dict(_store.per_depth)
    }