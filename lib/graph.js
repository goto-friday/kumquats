function fade(node, reset=false) {
    node.style.opacity = reset ? "" : "20%";
}
function getDisconnectedElems(node) {
    const nodeId = node.getAttribute("x-title");
    const connectedIds = [nodeId];
    const ret = [];
    for (const edge of document.querySelectorAll('.edge')) {
        const edgeId = edge.getAttribute("x-title");
        const nodeIds = edgeId.split('->');
        if (nodeIds.includes(nodeId)) {
            const otherNodeId = nodeIds[Number(nodeIds[0] == nodeId)];
            if (!ret.includes(otherNodeId))
                connectedIds.push(otherNodeId);
            connectedIds.push(edgeId);
        }
    }
    for (const el of document.querySelectorAll('.node, .edge')) {
        const id = el.getAttribute("x-title");
        if (!connectedIds.includes(id))
            ret.push(el);
    }
    return ret;
}
function highlight(ev) {
    const el = ev.target;
    const reset = ev.type == 'mouseleave';
    if (el.className.baseVal != "node" && !reset)
        return;
    for (const elem of getDisconnectedElems(el))
        fade(elem, reset);
}
for (const el of document.querySelectorAll('.node, .edge'))
    el.onmouseenter = el.onmouseleave = highlight;
