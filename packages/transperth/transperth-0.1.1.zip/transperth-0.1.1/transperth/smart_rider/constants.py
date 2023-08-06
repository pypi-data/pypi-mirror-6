from .post_back import _unique_ID_to_client_ID


def _updateControls(d, a, c, b):
    _commitControls(
        _processUpdatePanelArrays(d, a, c),
        b
    )


def _processUpdatePanelArrays(e, l, n):
    if e:
        f = e.length
        d = []
        c = []
        b = []
        for (var a = 0; a < f; a++):
        # for thing in a
            k = e[a].substr(1)
            m = e[a].charAt(0) == "t"
            b[a] = m
            d[a] = k
            c[a] = _unique_ID_to_client_ID(k)
    else:
        d = []
        c = []
        b = []

    i = []
    g = []
    i, g = _convertToClientIDs(l, i, g)
    j = []
    h = []
    i, g = _convertToClientIDs(n, j, h)
    return {
        'updatePanelIDs': d,
        'updatePanelClientIDs': c,
        'updatePanelHasChildrenAsTriggers': b,
        'asyncPostBackControlIDs': i,
        'asyncPostBackControlClientIDs': g,
        'postBackControlIDs': j,
        'postBackControlClientIDs': h
    }


def _convertToClientIDs(a, d, c):
    if a:
        for b in a:
            d.append(b)
            c.append(_uniqueIDToClientID(b))

    return d, c
