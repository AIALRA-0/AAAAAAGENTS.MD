    const dagrePlugin = window.cytoscapeDagre;
    if (typeof dagrePlugin === "function") cytoscape.use(dagrePlugin);

    const navTreeEl = document.getElementById("nav-tree");
    const docCountEl = document.getElementById("doc-count");
    const docStatePill = document.getElementById("doc-state-pill");
    const runtimeStatus = document.getElementById("runtime-status");
    const docTitleEl = document.getElementById("doc-title");
    const docMetaEl = document.getElementById("doc-meta");
    const docHtml = document.getElementById("doc-html");
    const graphPanel = document.getElementById("graph-panel");
    const treePanel = document.getElementById("tree-panel");
    const editPanel = document.getElementById("edit-panel");
    const graphCanvas = document.getElementById("graph-canvas");
    const graphViewWrap = document.getElementById("graph-view-wrap");
    const graphListWrap = document.getElementById("graph-list-wrap");
    const graphListEl = document.getElementById("graph-list");
    const graphDetail = document.getElementById("graph-detail");
    const graphListDetail = document.getElementById("graph-list-detail");
    const treeExplorer = document.getElementById("tree-explorer");
    const treeDetail = document.getElementById("tree-detail");
    const rawEditor = document.getElementById("raw-editor");
    const nodeListEl = document.getElementById("node-list");
    const nodeForm = document.getElementById("node-form");

    const syncTreeBtn = document.getElementById("sync-tree-btn");
    const verifyBtn = document.getElementById("verify-btn");
    const baselineBtn = document.getElementById("baseline-btn");
    const toggleModeBtn = document.getElementById("toggle-mode-btn");
    const saveRawBtn = document.getElementById("save-raw-btn");
    const saveNodeBtn = document.getElementById("save-node-btn");
    const resetBtn = document.getElementById("reset-btn");
    const graphFitBtn = document.getElementById("graph-fit-btn");
    const graphSaveLayoutBtn = document.getElementById("graph-save-layout-btn");
    const graphModeGraphBtn = document.getElementById("graph-mode-graph-btn");
    const graphModeListBtn = document.getElementById("graph-mode-list-btn");
    const milestoneNodeActions = document.getElementById("milestone-node-actions");
    const nodeCreateBtn = document.getElementById("node-create-btn");
    const nodeDeleteBtn = document.getElementById("node-delete-btn");
    const tabRawBtn = document.getElementById("tab-raw-btn");
    const tabNodeBtn = document.getElementById("tab-node-btn");
    const tabNodeItem = document.getElementById("tab-node-item");
    const actionModalEl = document.getElementById("action-modal");
    const actionModalTitle = document.getElementById("action-modal-title");
    const actionModalBody = document.getElementById("action-modal-body");
    const actionModalInput = document.getElementById("action-modal-input");
    const actionModalConfirm = document.getElementById("action-modal-confirm");
    const verifyModalEl = document.getElementById("verify-modal");
    const verifyModalSummary = document.getElementById("verify-modal-summary");
    const verifyModalErrors = document.getElementById("verify-modal-errors");
    const verifyModalHints = document.getElementById("verify-modal-hints");
    const toastRegion = document.getElementById("toast-region");

    const actionModal = window.bootstrap ? new window.bootstrap.Modal(actionModalEl) : null;
    const verifyModal = window.bootstrap ? new window.bootstrap.Modal(verifyModalEl) : null;

    const TREE_DOC = "TREE.md";
    const MILESTONE_DOC = "MILESTONE.md";
    const CHANGE_DOC = "CHANGE.md";
    const TREE_LIST_KEYS = new Set(["prerequisites", "postnodes", "why", "what", "how", "verify", "notes", "reason", "action", "observation", "suggestions"]);

    const state = {
      docs: [],
      tree: window.__INITIAL_TREE__ || [],
      currentDoc: null,
      currentEditable: false,
      currentDocKind: "plain_doc",
      currentGraphEnabled: false,
      uiMode: "preview",
      editTab: "raw",
      currentModel: { node_key: "", nodes: [] },
      currentTreeExplorer: null,
      selectedNodeId: null,
      selectedTreeNode: null,
      selectedGraphPreviewId: null,
      cy: null,
      graphMode: "graph",
      graphLayoutDirty: false,
      baselineCandidates: ["/api/baseline/refresh", "/api/baseline/sync", "/api/baseline", "/api/baseline_refresh", "/api/baseline-refresh"],
    };

    function showToast(message, isError = false) {
      if (!toastRegion) return;
      const item = document.createElement("div");
      item.className = "toast";
      item.setAttribute("role", "status");
      item.setAttribute("aria-live", "polite");
      item.setAttribute("aria-atomic", "true");
      item.innerHTML = `
        <div class="toast-body ${isError ? "text-danger" : "text-primary"}">${escapeHtml(message)}</div>
      `;
      toastRegion.appendChild(item);
      if (window.bootstrap && typeof window.bootstrap.Toast === "function") {
        const toast = new window.bootstrap.Toast(item, { delay: isError ? 5200 : 3200 });
        item.addEventListener("hidden.bs.toast", () => item.remove(), { once: true });
        toast.show();
      } else {
        setTimeout(() => item.remove(), isError ? 5200 : 3200);
      }
    }

    function setRuntimeStatus(text, isError = false, notify = false) {
      runtimeStatus.textContent = text;
      runtimeStatus.style.background = isError ? "var(--danger-soft)" : "#f8fbff";
      runtimeStatus.style.borderColor = isError ? "#fecaca" : "var(--line)";
      runtimeStatus.style.color = isError ? "#991b1b" : "#234162";
      if (notify) showToast(text, isError);
    }

    function docKindLabel(kind) {
      if (kind === "graph_doc") return "flowchart";
      if (kind === "tree_doc") return "tree view";
      return "document";
    }

    function docTagClass(kind) {
      if (kind === "graph_doc") return "tag-graph";
      if (kind === "tree_doc") return "tag-tree";
      return "tag-plain";
    }

    function escapeHtml(value) {
      return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/\"/g, "&quot;")
        .replace(/'/g, "&#39;");
    }

    function encodePath(path) {
      return path.split("/").map(encodeURIComponent).join("/");
    }

    async function fetchJson(url, options = {}) {
      const resp = await fetch(url, options);
      let data = null;
      try { data = await resp.json(); } catch (_) { data = null; }
      if (!resp.ok) {
        const message = data && (data.detail || data.message || data.stderr) ? (data.detail || data.message || data.stderr) : `Request failed: ${resp.status}`;
        throw new Error(message);
      }
      return data || {};
    }

    function showVerifyModal(payload) {
      const errors = Array.isArray(payload.errors) ? payload.errors : [];
      const hints = Array.isArray(payload.hints) ? payload.hints : [];
      const status = payload.status || "failed";
      const code = payload.exit_code ?? "-";
      const errorCount = payload.error_count ?? errors.length;
      verifyModalSummary.innerHTML = `
        <div class="alert ${status === "ok" ? "alert-success" : "alert-danger"} mb-0">
          Status: ${escapeHtml(status === "ok" ? "Passed" : "Failed")} | Return code: ${escapeHtml(code)} | Number of errors: ${escapeHtml(errorCount)}
        </div>
      `;
      verifyModalErrors.innerHTML = "";
      verifyModalHints.innerHTML = "";
      if (!errors.length) {
        const li = document.createElement("li");
        li.textContent = "No error";
        verifyModalErrors.appendChild(li);
      } else {
        for (const err of errors) {
          const li = document.createElement("li");
          li.textContent = String(err);
          verifyModalErrors.appendChild(li);
        }
      }
      if (!hints.length) {
        const li = document.createElement("li");
        li.textContent = "No suggestions";
        verifyModalHints.appendChild(li);
      } else {
        for (const hint of hints) {
          const li = document.createElement("li");
          li.textContent = String(hint);
          verifyModalHints.appendChild(li);
        }
      }
      if (verifyModal) {
        verifyModal.show();
      }
    }

    function askAction(options) {
      const title = options.title || "Operation Confirmation";
      const body = options.body || "";
      const confirmText = options.confirmText || "Confirm";
      const confirmClass = options.confirmClass || "btn-primary";
      const showInput = Boolean(options.showInput);
      const inputPlaceholder = options.inputPlaceholder || "";
      const inputValue = options.inputValue || "";
      return new Promise((resolve) => {
        actionModalTitle.textContent = title;
        actionModalBody.textContent = body;
        actionModalInput.classList.toggle("hidden", !showInput);
        actionModalInput.placeholder = inputPlaceholder;
        actionModalInput.value = inputValue;
        actionModalConfirm.textContent = confirmText;
        actionModalConfirm.className = `btn ${confirmClass}`;
        if (!actionModal) {
          resolve({ confirmed: false, value: "" });
          return;
        }

        let resolved = false;
        const cleanup = () => {
          actionModalConfirm.removeEventListener("click", onConfirm);
          actionModalEl.removeEventListener("hidden.bs.modal", onHidden);
        };
        const onConfirm = () => {
          if (resolved) return;
          resolved = true;
          const value = actionModalInput.value;
          cleanup();
          if (actionModal) actionModal.hide();
          resolve({ confirmed: true, value });
        };
        const onHidden = () => {
          if (resolved) return;
          resolved = true;
          cleanup();
          resolve({ confirmed: false, value: "" });
        };
        actionModalConfirm.addEventListener("click", onConfirm);
        actionModalEl.addEventListener("hidden.bs.modal", onHidden);
        actionModal.show();
        if (showInput) {
          setTimeout(() => actionModalInput.focus(), 80);
        }
      });
    }

    async function uiConfirm(title, body, danger = false) {
      const result = await askAction({
        title,
        body,
        confirmText: "Confirm",
        confirmClass: danger ? "btn-danger" : "btn-primary",
      });
      return result.confirmed;
    }

    async function uiPrompt(title, body, placeholder = "", defaultValue = "") {
      const result = await askAction({
        title,
        body,
        confirmText: "Continue",
        confirmClass: "btn-primary",
        showInput: true,
        inputPlaceholder: placeholder,
        inputValue: defaultValue,
      });
      if (!result.confirmed) return null;
      return String(result.value || "");
    }

    function buildDocMap() {
      const map = new Map();
      for (const item of state.docs) map.set(item.name, item);
      return map;
    }
    function renderNavTree() {
      navTreeEl.innerHTML = "";
      const docMap = buildDocMap();
      let fileCount = 0;

      function createFolder(node, level = 0) {
        const details = document.createElement("details");
        details.className = "nav-folder";
        details.open = level < 2;

        const summary = document.createElement("summary");
        const left = document.createElement("div");
        left.className = "folder-left";
        left.innerHTML = `<span class="nav-emoji">📁</span><span class="folder-name">${escapeHtml(node.name)}</span>`;

        const right = document.createElement("div");
        right.className = "folder-actions";
        const count = document.createElement("span");
        count.className = "folder-meta";
        count.textContent = `${(node.children || []).length} items`;
        right.appendChild(count);

        if (node.path === "agents_standards") {
          const createBtn = document.createElement("button");
          createBtn.type = "button";
          createBtn.className = "btn btn-sm file-action file-action-create";
          createBtn.textContent = "New";
          createBtn.addEventListener("click", async (event) => {
            event.preventDefault();
            event.stopPropagation();
            await createStandardDoc();
          });
          right.appendChild(createBtn);
        }

        summary.appendChild(left);
        summary.appendChild(right);
        details.appendChild(summary);

        const childWrap = document.createElement("div");
        childWrap.className = "ms-1";
        for (const child of node.children || []) {
          if (child.type === "dir") {
            childWrap.appendChild(createFolder(child, level + 1));
          } else {
            childWrap.appendChild(createFileNode(child, docMap));
            fileCount += 1;
          }
        }
        details.appendChild(childWrap);
        return details;
      }

      function createFileNode(node, docMapLocal) {
        const meta = docMapLocal.get(node.path) || {};
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "nav-file";
        btn.dataset.name = node.path;
        if (state.currentDoc === node.path) btn.classList.add("active");

        const line1 = document.createElement("div");
        line1.className = "file-line";
        const fileName = document.createElement("span");
        fileName.className = "file-name";
        fileName.innerHTML = `<span class="nav-emoji">📄</span><span>${escapeHtml(node.name)}</span>`;
        line1.appendChild(fileName);

        const right = document.createElement("div");
        right.className = "d-flex align-items-center gap-2 flex-nowrap justify-content-end";
        const tag = document.createElement("span");
        const kind = meta.doc_kind || node.doc_kind || "plain_doc";
        tag.className = `file-tag ${docTagClass(kind)}`;
        tag.textContent = docKindLabel(kind);
        right.appendChild(tag);

        if (String(node.path || "").startsWith("agents_standards/")) {
          const delBtn = document.createElement("button");
          delBtn.type = "button";
          delBtn.className = "btn btn-sm file-action file-action-delete";
          delBtn.textContent = "Delete";
          delBtn.title = "Delete standard file";
          delBtn.addEventListener("click", async (event) => {
            event.preventDefault();
            event.stopPropagation();
            await deleteStandardDoc(node.path);
          });
          right.appendChild(delBtn);
        }
        line1.appendChild(right);

        const line2 = document.createElement("div");
        line2.className = "file-sub";
        line2.textContent = node.path;

        btn.appendChild(line1);
        btn.appendChild(line2);
        btn.addEventListener("click", () => loadDoc(node.path));
        return btn;
      }

      for (const node of state.tree || []) {
        if (node.type === "dir") {
          navTreeEl.appendChild(createFolder(node, 0));
        } else {
          navTreeEl.appendChild(createFileNode(node, docMap));
          fileCount += 1;
        }
      }
      docCountEl.textContent = `${fileCount} file`;
    }

    function updateDocHead() {
      if (!state.currentDoc) {
        docTitleEl.textContent = "Document Preview";
        docMetaEl.innerHTML = "";
        return;
      }
      docTitleEl.textContent = state.currentDoc;
      docMetaEl.innerHTML = `
        <span class="file-tag ${docTagClass(state.currentDocKind)}">${docKindLabel(state.currentDocKind)}</span>
        <span class="file-tag tag-plain">User editable</span>
        <span class="file-tag tag-plain">${state.uiMode === "edit" ? "Edit Mode" : "Preview Mode"}</span>
      `;
    }

    function updateStatePills() {
      if (!state.currentDoc) {
        docStatePill.textContent = "Document not loaded";
      } else {
        docStatePill.textContent = `${state.currentDoc} | ${docKindLabel(state.currentDocKind)} | User editable | ${state.uiMode === "edit" ? "Edit Mode" : "Preview Mode"}`;
      }
    }

    function supportsNodeEdit() {
      return state.currentGraphEnabled && state.currentModel && Boolean(state.currentModel.node_key);
    }

    function activateTab(button) {
      if (!button) return;
      if (window.bootstrap && typeof window.bootstrap.Tab === "function") {
        new window.bootstrap.Tab(button).show();
      } else {
        button.click();
      }
    }

    function setEditTab(tab) {
      state.editTab = tab === "node" ? "node" : "raw";
      if (state.editTab === "raw") {
        activateTab(tabRawBtn);
      } else if (supportsNodeEdit()) {
        activateTab(tabNodeBtn);
      }
      updateButtons();
    }

    function updateButtons() {
      const canEdit = Boolean(state.currentDoc);
      const inEdit = state.uiMode === "edit";
      const hasSelectedNode = Boolean(state.selectedNodeId);
      const nodeEditable = supportsNodeEdit();
      toggleModeBtn.disabled = false;
      toggleModeBtn.textContent = inEdit ? "Return to preview" : "Enter editing";
      saveRawBtn.classList.toggle("hidden", !(inEdit && state.editTab === "raw"));
      saveNodeBtn.classList.toggle("hidden", !(inEdit && state.editTab === "node" && nodeEditable));
      saveRawBtn.disabled = !(canEdit && inEdit && state.editTab === "raw");
      saveNodeBtn.disabled = !(canEdit && inEdit && state.editTab === "node" && hasSelectedNode && nodeEditable);
      resetBtn.disabled = !(canEdit && inEdit);
      graphFitBtn.disabled = !(state.currentGraphEnabled && state.cy);
      graphSaveLayoutBtn.disabled = !(state.currentGraphEnabled && state.cy && state.graphLayoutDirty);
      graphModeGraphBtn.disabled = !state.currentGraphEnabled;
      graphModeListBtn.disabled = !state.currentGraphEnabled;
      graphModeGraphBtn.classList.toggle("active", state.graphMode === "graph");
      graphModeListBtn.classList.toggle("active", state.graphMode === "list");
      milestoneNodeActions.classList.toggle("hidden", !(inEdit && state.currentDoc === MILESTONE_DOC));
      tabNodeItem.classList.toggle("hidden", !nodeEditable);
    }

    function applyMode(mode) {
      if (mode === "edit" && !state.currentDoc) return;
      state.uiMode = mode;
      if (!supportsNodeEdit()) {
        state.editTab = "raw";
      }
      editPanel.classList.toggle("hidden", !(state.uiMode === "edit" && state.currentEditable));
      updateDocHead();
      updateStatePills();
      updateButtons();
    }
    function resetGraphDetail() {
      const html = `<h3 class="detail-title">Node details</h3><div class="text-muted">Click the node to view the structured fields</div>`;
      graphDetail.innerHTML = html;
      if (graphListDetail) graphListDetail.innerHTML = html;
    }

    function asLines(value) {
      if (Array.isArray(value)) return value.length ? value.join("\n") : "(empty)";
      if (value === null || value === undefined || value === "") return "(empty)";
      return String(value);
    }

    function kvBlock(label, value) {
      return `<div class="kv-block"><div class="kv-key">${escapeHtml(label)}</div><div class="kv-value">${escapeHtml(asLines(value))}</div></div>`;
    }

    function renderGraphDetail(raw) {
      if (!raw) { resetGraphDetail(); return; }
      let html = `<h3 class="detail-title">Node details</h3>`;
      if (state.currentDoc === MILESTONE_DOC) {
        html += kvBlock("id", raw.id);
        html += kvBlock("title", raw.title);
        html += kvBlock("status", raw.status);
        html += kvBlock("prerequisites", raw.prerequisites);
        html += kvBlock("postnodes", raw.postnodes);
        html += kvBlock("why", raw.why);
        html += kvBlock("what", raw.what);
        html += kvBlock("how", raw.how);
        html += kvBlock("verify", raw.verify);
        html += kvBlock("ddl", raw.ddl);
        html += kvBlock("notes", raw.notes);
        html += kvBlock("updated_at", raw.updated_at);
      } else if (state.currentDoc === CHANGE_DOC) {
        html += kvBlock("version", raw.version);
        html += kvBlock("date", raw.date);
        html += kvBlock("reason", raw.reason);
        html += kvBlock("action", raw.action);
        html += kvBlock("observation", raw.observation);
        html += kvBlock("impacted_files", raw.impacted_files);
        html += kvBlock("notes", raw.notes);
        html += kvBlock("suggestions", raw.suggestions);
      } else {
        html += kvBlock("data", JSON.stringify(raw, null, 2));
      }
      graphDetail.innerHTML = html;
      if (graphListDetail) graphListDetail.innerHTML = html;
    }

    function markGraphListSelection() {
      graphListEl.querySelectorAll(".node-item").forEach((node) => node.classList.remove("active"));
      if (!state.selectedGraphPreviewId) return;
      const target = graphListEl.querySelector(`.node-item[data-id="${CSS.escape(String(state.selectedGraphPreviewId))}"]`);
      if (target) target.classList.add("active");
    }

    function graphElements(graph) {
      const nodes = (graph.nodes || []).map((node) => ({ data: node.data }));
      const edges = (graph.edges || []).map((edge) => ({
        data: {
          ...edge.data,
          line_color: edge.data.required ? "#64748b" : "#94a3b8",
          line_style: edge.data.required ? "solid" : "dashed"
        }
      }));
      return nodes.concat(edges);
    }

    function renderGraphList(graph) {
      graphListEl.innerHTML = "";
      const nodes = (graph.nodes || []).map((item) => item.data || {});
      if (!nodes.length) {
        graphListEl.innerHTML = "<div class='text-muted'>No nodes currently</div>";
        if (graphListDetail) graphListDetail.innerHTML = "<div class='text-muted'>No node details currently</div>";
        return;
      }
      for (const node of nodes) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "node-item";
        btn.dataset.id = String(node.id || "");
        const title = state.currentDoc === MILESTONE_DOC
          ? (node.raw?.title || "")
          : (state.currentDoc === CHANGE_DOC ? (node.raw?.date || "") : "");
        btn.textContent = `${node.id || ""} | ${title}`;
        btn.addEventListener("click", () => {
          state.selectedGraphPreviewId = String(node.id || "");
          markGraphListSelection();
          renderGraphDetail(node.raw || null);
          if (state.cy) {
            const target = state.cy.getElementById(String(node.id || ""));
            if (target && target.length) {
              state.cy.elements().unselect();
              target.select();
              state.cy.center(target);
            }
          }
        });
        graphListEl.appendChild(btn);
      }
      markGraphListSelection();
    }

    function focusGraph() {
      if (!state.cy) return;
      requestAnimationFrame(() => {
        state.cy.resize();
        state.cy.fit(undefined, 72);
      });
    }

    function renderGraph(graph) {
      if (!state.currentGraphEnabled) {
        if (state.cy) { state.cy.destroy(); state.cy = null; }
        resetGraphDetail();
        graphListEl.innerHTML = "";
        return;
      }
      const rawPositions = (graph && graph.positions && typeof graph.positions === "object") ? graph.positions : {};
      const nodeIds = new Set((graph?.nodes || []).map((item) => String(item?.data?.id || "")).filter(Boolean));
      const positions = {};
      for (const [nodeId, pos] of Object.entries(rawPositions)) {
        if (!nodeIds.has(String(nodeId)) || !pos || typeof pos !== "object") continue;
        const x = Number(pos.x);
        const y = Number(pos.y);
        if (!Number.isFinite(x) || !Number.isFinite(y)) continue;
        positions[String(nodeId)] = { x, y };
      }
      const hasFullPreset = nodeIds.size > 0 && Object.keys(positions).length === nodeIds.size;
      state.selectedGraphPreviewId = null;
      renderGraphList(graph || {});
      if (state.cy) { state.cy.destroy(); state.cy = null; }
      const baseConfig = {
        container: graphCanvas,
        elements: graphElements(graph || {}),
        wheelSensitivity: 0.18,
        minZoom: 0.06,
        maxZoom: 5.5,
        style: [
          {
            selector: "node",
            style: {
              "background-color": "data(fill)",
              "label": "data(label)",
              "color": "data(text)",
              "shape": "round-rectangle",
              "text-wrap": "wrap",
              "text-max-width": 210,
              "font-size": 13,
              "font-family": "Segoe UI, Microsoft YaHei, PingFang SC, sans-serif",
              "text-valign": "center",
              "text-halign": "center",
              "line-height": 1.2,
              "width": 240,
              "height": 110,
              "padding": 14,
              "border-width": 2,
              "border-color": "data(border)"
            }
          },
          {
            selector: "node[width]",
            style: {
              "text-max-width": "data(width)",
              "width": "data(width)",
            }
          },
          {
            selector: "node[height]",
            style: {
              "height": "data(height)",
            }
          },
          {
            selector: "node[font_size]",
            style: {
              "font-size": "data(font_size)",
            }
          },
          {
            selector: "edge",
            style: {
              "curve-style": "bezier",
              "control-point-step-size": 58,
              "edge-distances": "node-position",
              "source-endpoint": "outside-to-node",
              "target-endpoint": "outside-to-node",
              "line-color": "data(line_color)",
              "line-style": "data(line_style)",
              "width": 2,
              "target-arrow-shape": "triangle",
              "target-arrow-color": "data(line_color)",
              "arrow-scale": 1.05
            }
          },
          {
            selector: ":selected",
            style: { "border-width": 3, "border-color": "#1d4ed8" }
          }
        ],
      };
      const presetLayout = { name: "preset", positions, fit: true, padding: 72, animate: false };
      const dagreLayout = {
        name: "dagre",
        rankDir: "TB",
        nodeDimensionsIncludeLabels: true,
        rankSep: 170,
        nodeSep: 130,
        edgeSep: 92,
        marginx: 68,
        marginy: 68,
        ranker: "network-simplex",
        acyclicer: "greedy",
        spacingFactor: 1.15,
        fit: true,
        padding: 72,
        animate: false,
      };
      try {
        state.cy = cytoscape({
          ...baseConfig,
          layout: hasFullPreset ? presetLayout : dagreLayout,
        });
      } catch (error) {
        setRuntimeStatus(`Flowchart rendering failed: ${error.message || error}`, true);
        return;
      }
      resetGraphDetail();
      state.graphLayoutDirty = false;
      state.cy.on("tap", "node", (evt) => {
        const data = evt.target.data();
        state.selectedGraphPreviewId = String(data.id || "");
        markGraphListSelection();
        renderGraphDetail(data.raw || null);
        if (state.currentModel.node_key) {
          state.selectedNodeId = String(data.id || "");
          renderNodeList();
          renderNodeForm();
          updateButtons();
        }
      });
      state.cy.on("dragfree", "node", () => {
        state.graphLayoutDirty = true;
        setRuntimeStatus("Node position change detected, please click "Save Layout" to persist");
        updateButtons();
      });
      focusGraph();
      updateButtons();
    }

    function renderTreeDetail() {
      const node = state.selectedTreeNode;
      if (!node) { treeDetail.innerHTML = "<div class='text-muted'>Click on the left node to view details</div>"; return; }
      treeDetail.innerHTML = `
        <dl class="mb-0">
          <dt>Path</dt><dd class="mono">${escapeHtml(node.path)}</dd>
          <dt>Type</dt><dd>${escapeHtml(node.type)}</dd>
          <dt>Status</dt><dd>${escapeHtml(node.status)}</dd>
          <dt>Last modified</dt><dd class="mono">${escapeHtml(node.last_modified)}</dd>
          <dt>Editable</dt><dd>${node.editable ? "Yes" : "No"}</dd>
          <dt>File function</dt><dd>${escapeHtml(node.note || "")}</dd>
        </dl>
      `;
    }

    function markTreeSelection() {
      treeExplorer.querySelectorAll(".tree-node").forEach((node) => node.classList.remove("active"));
      if (!state.selectedTreeNode) return;
      const target = treeExplorer.querySelector(`.tree-node[data-path="${CSS.escape(state.selectedTreeNode.path)}"]`);
      if (target) target.classList.add("active");
    }

    function makeTreeNode(node) {
      const wrap = document.createElement("div");
      const children = Array.isArray(node.children) ? node.children : [];
      if (node.type === "dir" && children.length) {
        const details = document.createElement("details");
        details.open = node.path === "." || node.path === "agents_standards";
        const summary = document.createElement("summary");
        summary.className = "tree-node";
        summary.dataset.path = node.path || "";
        summary.innerHTML = `<span class="d-inline-flex align-items-center gap-2"><span class="nav-emoji">📁</span><span>${escapeHtml(node.name)}</span></span><span class="tree-meta">${escapeHtml(node.path)}</span>`;
        summary.addEventListener("click", (event) => {
          event.stopPropagation();
          state.selectedTreeNode = node;
          markTreeSelection();
          renderTreeDetail();
        });
        details.appendChild(summary);
        const childWrap = document.createElement("div");
        childWrap.className = "ms-3";
        for (const child of children) childWrap.appendChild(makeTreeNode(child));
        details.appendChild(childWrap);
        wrap.appendChild(details);
      } else {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "tree-node";
        btn.dataset.path = node.path || "";
        const iconText = node.type === "dir" ? "📁" : "📄";
        btn.innerHTML = `<span class="d-inline-flex align-items-center gap-2"><span class="nav-emoji">${iconText}</span><span>${escapeHtml(node.name)}</span></span><span class="tree-meta">${escapeHtml(node.path)}</span>`;
        btn.addEventListener("click", () => {
          state.selectedTreeNode = node;
          markTreeSelection();
          renderTreeDetail();
        });
        wrap.appendChild(btn);
      }
      return wrap;
    }
    function renderTreeExplorer(explorer) {
      treeExplorer.innerHTML = "";
      state.selectedTreeNode = null;
      renderTreeDetail();
      if (!explorer || !explorer.root) {
        treeExplorer.innerHTML = "<div class='text-muted'>TREE structure is empty</div>";
        return;
      }
      treeExplorer.appendChild(makeTreeNode(explorer.root));
    }

    function parseFieldValue(key, raw) {
      const text = String(raw ?? "");
      if (TREE_LIST_KEYS.has(key)) {
        return text.split("\n").map((line) => line.trim()).filter((line) => line.length > 0);
      }
      return text.trim();
    }

    function fieldText(value) {
      if (Array.isArray(value)) return value.join("\n");
      if (value === null || value === undefined) return "";
      return String(value);
    }

    function editableFieldsByDoc(name) {
      if (name === MILESTONE_DOC) return ["title", "prerequisites", "postnodes", "why", "what", "how", "verify", "ddl", "status", "notes"];
      if (name === CHANGE_DOC) return ["date", "reason", "action", "observation", "notes", "suggestions"];
      if (name === TREE_DOC) return ["note"];
      return [];
    }

    function renderNodeList() {
      nodeListEl.innerHTML = "";
      const key = state.currentModel.node_key;
      if (!key) return;
      for (const node of state.currentModel.nodes || []) {
        const id = String(node[key] ?? "");
        if (!id) continue;
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "node-item" + (state.selectedNodeId === id ? " active" : "");
        let label = id;
        if (state.currentDoc === MILESTONE_DOC) label += ` | ${node.title || ""}`;
        if (state.currentDoc === CHANGE_DOC) label += ` | ${node.date || ""}`;
        if (state.currentDoc === TREE_DOC) label += ` | ${node.status || ""}`;
        btn.textContent = label;
        btn.addEventListener("click", () => {
          state.selectedNodeId = id;
          renderNodeList();
          renderNodeForm();
          updateButtons();
        });
        nodeListEl.appendChild(btn);
      }
    }

    function renderNodeForm() {
      nodeForm.innerHTML = "";
      const key = state.currentModel.node_key;
      if (!key || !state.selectedNodeId) return;
      const node = (state.currentModel.nodes || []).find((item) => String(item[key]) === String(state.selectedNodeId));
      if (!node) return;
      for (const field of editableFieldsByDoc(state.currentDoc)) {
        const wrap = document.createElement("div");
        wrap.className = "mb-2";
        const label = document.createElement("label");
        label.className = "form-label";
        label.textContent = field;
        wrap.appendChild(label);

        if (field === "status" && state.currentDoc === MILESTONE_DOC) {
          const select = document.createElement("select");
          select.className = "form-select form-select-sm";
          select.name = field;
          for (const value of ["unfinished", "done", "archived", "deleted"]) {
            const option = document.createElement("option");
            option.value = value;
            option.textContent = value;
            if (String(node[field]) === value) option.selected = true;
            select.appendChild(option);
          }
          wrap.appendChild(select);
        } else if (field === "ddl" || field === "date") {
          const input = document.createElement("input");
          input.className = "form-control form-control-sm";
          input.type = "text";
          input.name = field;
          if (field === "date") input.placeholder = "YYYY-MM-DD-HH-MM";
          if (field === "ddl") input.placeholder = "YYYY-MM-DD";
          input.value = fieldText(node[field]);
          wrap.appendChild(input);
        } else if (Array.isArray(node[field])) {
          const textarea = document.createElement("textarea");
          textarea.className = "form-control form-control-sm";
          textarea.name = field;
          textarea.value = fieldText(node[field]);
          wrap.appendChild(textarea);
        } else {
          const input = document.createElement("textarea");
          input.className = "form-control form-control-sm";
          input.name = field;
          input.value = fieldText(node[field]);
          wrap.appendChild(input);
        }
        nodeForm.appendChild(wrap);
      }
    }

    function refreshPanels() {
      graphPanel.classList.toggle("hidden", !state.currentGraphEnabled);
      treePanel.classList.toggle("hidden", state.currentDoc !== TREE_DOC);
      editPanel.classList.toggle("hidden", !(state.uiMode === "edit" && state.currentEditable));
      graphViewWrap.classList.toggle("hidden", state.graphMode !== "graph");
      graphListWrap.classList.toggle("hidden", state.graphMode !== "list");
      tabNodeItem.classList.toggle("hidden", !supportsNodeEdit());
      if (state.currentGraphEnabled) focusGraph();
    }

    async function loadMeta() {
      try {
        const data = await fetchJson("/api/meta");
        const routes = Array.isArray(data.baseline_routes) ? data.baseline_routes : [];
        if (routes.length) state.baselineCandidates = routes;
        const version = data.version ? `v${data.version}` : "unknown";
        setRuntimeStatus(`Backend connected ${version}`);
      } catch (error) {
        setRuntimeStatus(`Failed to read backend meta information: ${error.message}`, true, true);
      }
    }

    async function refreshDocsIndex() {
      const data = await fetchJson("/api/docs");
      state.docs = Array.isArray(data.docs) ? data.docs : [];
      state.tree = Array.isArray(data.tree) ? data.tree : [];
      renderNavTree();
    }

    async function loadDoc(name) {
      try {
        const data = await fetchJson(`/api/docs/${encodePath(name)}`);
        state.currentDoc = data.name;
        state.currentEditable = true;
        state.currentDocKind = data.doc_kind || "plain_doc";
        state.currentGraphEnabled = Boolean(data.graph_enabled);
        state.editTab = "raw";
        state.graphLayoutDirty = false;
        state.currentModel = data.model || { node_key: "", nodes: [] };
        state.currentTreeExplorer = data.tree_explorer || null;
        state.selectedNodeId = null;
        state.selectedGraphPreviewId = null;
        rawEditor.value = data.raw || "";
        rawEditor.readOnly = false;
        docHtml.innerHTML = data.rendered_html || "";

        updateDocHead();
        updateStatePills();
        renderNavTree();
        refreshPanels();

        if (state.currentGraphEnabled) {
          renderGraph(data.graph || {});
        } else if (state.cy) {
          state.cy.destroy();
          state.cy = null;
          resetGraphDetail();
        } else {
          resetGraphDetail();
        }

        if (state.currentDoc === TREE_DOC) {
          renderTreeExplorer(state.currentTreeExplorer);
        } else {
          treeExplorer.innerHTML = "";
          treeDetail.innerHTML = "<div class='text-muted'>Click on the left node to view details</div>";
        }

        activateTab(tabRawBtn);
        renderNodeList();
        renderNodeForm();
        updateButtons();
        setRuntimeStatus("Document loading completed");
      } catch (error) {
        setRuntimeStatus(`Loading failed: ${error.message}`, true, true);
        updateButtons();
      }
    }
    async function createStandardDoc() {
      const raw = await uiPrompt(
        "New Standard",
        "Please enter a standard name (only letters, numbers, and underscores), the system will automatically append _STANDARD.md",
        "For example: PYTHON_STYLE",
        ""
      );
      if (raw === null) return;
      const name = String(raw).trim();
      if (!name) { setRuntimeStatus("Standard name cannot be empty", true, true); return; }
      try {
        const data = await fetchJson("/api/standards/create", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name })
        });
        setRuntimeStatus(`Standard created: ${data.file}`, false, true);
        await refreshDocsIndex();
        await loadDoc(data.file);
        applyMode("edit");
      } catch (error) {
        setRuntimeStatus(`Failed to create standard: ${error.message}`, true, true);
      }
    }

    async function deleteStandardDoc(path) {
      const ok = await uiConfirm("Delete standard file", `Confirm to delete ${path}? This operation is irreversible.`, true);
      if (!ok) return;
      try {
        await fetchJson(`/api/standards/${encodePath(path)}`, { method: "DELETE" });
        setRuntimeStatus(`Standard deleted: ${path}`, false, true);
        const fallback = state.currentDoc === path ? "AGENTS.md" : state.currentDoc;
        await refreshDocsIndex();
        if (fallback) await loadDoc(fallback);
      } catch (error) {
        setRuntimeStatus(`Delete standard failed: ${error.message}`, true, true);
      }
    }

    async function syncTree() {
      try {
        const data = await fetchJson("/api/tree/sync", { method: "POST" });
        if (data.exit_code !== 0) throw new Error(data.stderr || data.stdout || "TREE synchronization failed");
        setRuntimeStatus("TREE synchronization completed", false, true);
        await refreshDocsIndex();
        if (state.currentDoc) await loadDoc(state.currentDoc);
      } catch (error) {
        setRuntimeStatus(`TREE synchronization failed: ${error.message}`, true, true);
      }
    }

    async function verifyFinalize() {
      try {
        const data = await fetchJson("/api/verify/finalize", { method: "POST" });
        if (data.exit_code !== 0 || (data.error_count || 0) > 0) {
          showVerifyModal(data);
          const first = Array.isArray(data.errors) && data.errors.length ? data.errors[0] : "Unknown error";
          throw new Error(first);
        }
        const fixText = data.fix_count ? `, automatically fix ${data.fix_count} items`: "";
        setRuntimeStatus(`Final inspection passed${fixText}`, false, true);
        await refreshDocsIndex();
        if (state.currentDoc) await loadDoc(state.currentDoc);
      } catch (error) {
        setRuntimeStatus(`Final check failed: ${error.message}`, true, true);
      }
    }

    async function refreshBaseline() {
      const candidates = Array.from(new Set([
        ...(Array.isArray(state.baselineCandidates) ? state.baselineCandidates : []),
        "/api/baseline/refresh",
        "/api/baseline/sync",
        "/api/baseline",
        "/api/baseline_refresh",
        "/api/baseline-refresh",
      ]));
      let lastError = "";
      let all404 = true;
      for (const endpoint of candidates) {
        for (const method of ["POST", "GET"]) {
          try {
            const resp = await fetch(endpoint, { method });
            let data = {};
            try { data = await resp.json(); } catch (_) { data = {}; }
            if (resp.status !== 404) all404 = false;
            if (!resp.ok) {
              if (resp.status === 405) continue;
              lastError = `${method} ${endpoint} -> ${resp.status} ${data.detail || data.message || data.stderr || ""}`.trim();
              continue;
            }
            if (data.exit_code && data.exit_code !== 0) {
              lastError = `${method} ${endpoint} -> exit_code=${data.exit_code} ${data.stderr || data.message || ""}`.trim();
              continue;
            }
            setRuntimeStatus(`Final inspection baseline has been synchronized (${method} ${endpoint})`, false, true);
            return;
          } catch (error) {
            lastError = `${method} ${endpoint} -> ${error.message}`;
          }
        }
      }
      const hint = all404 ? ";The backend route does not exist, please restart the service and hard refresh the page" : "";
      setRuntimeStatus(`Baseline synchronization failed: ${lastError || "Unknown error"}${hint}`, true, true);
    }

    async function saveRaw() {
      if (!state.currentDoc || !state.currentEditable || state.uiMode !== "edit") return;
      try {
        const data = await fetchJson(`/api/docs/${encodePath(state.currentDoc)}`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content: rawEditor.value })
        });
        setRuntimeStatus(`Original text saved successfully: ${data.backup}`, false, true);
        await refreshDocsIndex();
        await loadDoc(state.currentDoc);
        applyMode("edit");
      } catch (error) {
        setRuntimeStatus(`Failed to save original text: ${error.message}`, true, true);
      }
    }

    async function resetDoc() {
      if (!state.currentDoc || !state.currentEditable || state.uiMode !== "edit") return;
      const ok = await uiConfirm("Reset Document", `Confirm to roll back ${state.currentDoc} to the latest backup version?`, true);
      if (!ok) return;
      try {
        const data = await fetchJson(`/api/docs/${encodePath(state.currentDoc)}/reset`, { method: "POST" });
        setRuntimeStatus(`Document restored: ${data.restored_from}`, false, true);
        await refreshDocsIndex();
        await loadDoc(state.currentDoc);
        applyMode("edit");
      } catch (error) {
        setRuntimeStatus(`Reset failed: ${error.message}`, true, true);
      }
    }

    async function saveNode() {
      if (!state.currentDoc || !state.currentEditable || state.uiMode !== "edit" || !state.selectedNodeId) {
        setRuntimeStatus("Please select the node in edit mode first", true, true);
        return;
      }
      const keepId = state.selectedNodeId;
      const fields = {};
      for (const input of nodeForm.querySelectorAll("[name]")) fields[input.name] = parseFieldValue(input.name, input.value || "");
      try {
        await fetchJson(`/api/model/${encodePath(state.currentDoc)}/node/${encodePath(state.selectedNodeId)}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ fields })
        });
        setRuntimeStatus("Node saved successfully", false, true);
        await refreshDocsIndex();
        await loadDoc(state.currentDoc);
        applyMode("edit");
        state.selectedNodeId = keepId;
        renderNodeList();
        renderNodeForm();
        updateButtons();
      } catch (error) {
        setRuntimeStatus(`Node saving failed: ${error.message}`, true, true);
      }
    }
    async function createMilestoneNode() {
      if (state.currentDoc !== MILESTONE_DOC || state.uiMode !== "edit") return;
      const id = await uiPrompt("Create a new milestone node", "Please enter the node ID", "For example: MS-INIT-010", "");
      if (id === null) return;
      const nodeId = String(id).trim();
      if (!nodeId) { setRuntimeStatus("Node ID cannot be empty", true, true); return; }
      const titleRaw = await uiPrompt("New milestone node", "Please enter the node title (can be left blank to use ID)", "Node title", nodeId);
      if (titleRaw === null) return;
      try {
        await fetchJson(`/api/model/${encodePath(MILESTONE_DOC)}/nodes/create`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id: nodeId, title: String(titleRaw || "").trim() })
        });
        setRuntimeStatus(`Milestone node has been created: ${nodeId}`, false, true);
        await refreshDocsIndex();
        await loadDoc(MILESTONE_DOC);
        applyMode("edit");
        state.selectedNodeId = nodeId;
        renderNodeList();
        renderNodeForm();
        updateButtons();
      } catch (error) {
        setRuntimeStatus(`Failed to create new node: ${error.message}`, true, true);
      }
    }

    async function deleteMilestoneNode() {
      if (state.currentDoc !== MILESTONE_DOC || state.uiMode !== "edit" || !state.selectedNodeId) return;
      const ok = await uiConfirm("Delete milestone node", `Confirm to delete ${state.selectedNodeId}? This operation is not reversible.`, true);
      if (!ok) return;
      const deletingId = state.selectedNodeId;
      try {
        await fetchJson(`/api/model/${encodePath(MILESTONE_DOC)}/node/${encodePath(deletingId)}`, { method: "DELETE" });
        state.selectedNodeId = null;
        setRuntimeStatus(`Milestone node deleted: ${deletingId}`, false, true);
        await refreshDocsIndex();
        await loadDoc(MILESTONE_DOC);
        applyMode("edit");
      } catch (error) {
        setRuntimeStatus(`Failed to delete node: ${error.message}`, true, true);
      }
    }

    function setGraphMode(mode) {
      if (!["graph", "list"].includes(mode)) return;
      state.graphMode = mode;
      refreshPanels();
      updateButtons();
    }

    async function saveGraphLayout() {
      if (!state.currentGraphEnabled || !state.cy || !state.currentDoc) return;
      const positions = {};
      state.cy.nodes().forEach((node) => {
        const id = node.id();
        const pos = node.position();
        positions[id] = { x: Number(pos.x), y: Number(pos.y) };
      });
      try {
        const data = await fetchJson(`/api/graph/${encodePath(state.currentDoc)}/layout`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ positions }),
        });
        state.graphLayoutDirty = false;
        setRuntimeStatus(`Layout saved successfully: ${data.saved_count} nodes`, false, true);
        updateButtons();
      } catch (error) {
        setRuntimeStatus(`Failed to save layout: ${error.message}`, true, true);
      }
    }

    function bindEvents() {
      syncTreeBtn.addEventListener("click", syncTree);
      verifyBtn.addEventListener("click", verifyFinalize);
      baselineBtn.addEventListener("click", refreshBaseline);

      toggleModeBtn.addEventListener("click", () => {
        if (!state.currentDoc) return;
        applyMode(state.uiMode === "edit" ? "preview" : "edit");
        refreshPanels();
      });

      saveRawBtn.addEventListener("click", saveRaw);
      saveNodeBtn.addEventListener("click", saveNode);
      resetBtn.addEventListener("click", resetDoc);
      graphFitBtn.addEventListener("click", () => focusGraph());
      graphSaveLayoutBtn.addEventListener("click", saveGraphLayout);
      graphModeGraphBtn.addEventListener("click", () => setGraphMode("graph"));
      graphModeListBtn.addEventListener("click", () => setGraphMode("list"));
      nodeCreateBtn.addEventListener("click", createMilestoneNode);
      nodeDeleteBtn.addEventListener("click", deleteMilestoneNode);
      tabRawBtn.addEventListener("shown.bs.tab", () => {
        state.editTab = "raw";
        updateButtons();
      });
      tabNodeBtn.addEventListener("shown.bs.tab", () => {
        state.editTab = "node";
        updateButtons();
      });

      window.addEventListener("resize", () => {
        if (state.currentGraphEnabled) focusGraph();
      });
    }

    async function initApp() {
      bindEvents();
      treeDetail.innerHTML = "<div class='text-muted'>Click on the left node to view details</div>";
      resetGraphDetail();
      await loadMeta();
      await refreshDocsIndex();
      const defaultDoc = (state.docs || []).find((item) => item.name === "AGENTS.md") || (state.docs || [])[0];
      if (defaultDoc) {
        await loadDoc(defaultDoc.name);
      } else {
        setRuntimeStatus("No loadable document found", true, true);
      }
      updateButtons();
    }

    initApp();
  
