function child(el, tag) {
    for (c of el.children)
        if (c.tagName == tag)
            return c;
}
function colorNode(node, reset=false) {
    const container = child(node, "polygon") || child(node, "ellipse");
    const color = reset ? "black" : "#f00";
    container.style.stroke = color;
}
function colorEdge(edge, reset=false) {
    const path = child(edge, "path");
    const polygon = child(edge, "polygon");
    const color = reset ? "black" : "#f00";
    path.style.stroke = color;
    if (polygon) {
        polygon.style.fill = color;
        polygon.style.stroke = color;
    }
}
function connectedEdges(node) {
    const nodeTitle = child(node, "title").textContent;
    const ret = [];
    for (const edge of document.querySelectorAll('.edge')) {
        const edgeTitle = child(edge, "title").textContent;
        if (edgeTitle.includes(nodeTitle))
            ret.push(edge);
    }
    return ret;
}
function highlight(ev) {
    const el = ev.target;
    if (el.className.baseVal != "node")
        return;
    colorNode(el);
    for (const edge of connectedEdges(el))
        colorEdge(edge);
}
function unhighlight() {
    for (const el of document.querySelectorAll("g")) {
        if (el.className.baseVal == "node") {
            colorNode(el, reset=true);
        } else if (el.className.baseVal == "edge") {
            colorEdge(el, reset=true);
        }
    }
}
for (const el of document.querySelectorAll("g")) {
    el.onmouseenter = highlight;
    el.onmouseleave = unhighlight;
}
