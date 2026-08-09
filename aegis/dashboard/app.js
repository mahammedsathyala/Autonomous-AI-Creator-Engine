document.addEventListener("DOMContentLoaded", () => {
    let currentAgentId = "ada-sec-8f2a";
    let countdownVal = 40;
    const intervalSec = 40;

    const postsContainer = document.getElementById("posts-container");
    const auditContainer = document.getElementById("audit-container");
    const beliefsContainer = document.getElementById("beliefs-container");
    const countdownTimerEl = document.getElementById("countdown-val");
    const progressFillEl = document.getElementById("progress-fill");

    const metricPosts = document.getElementById("metric-posts");
    const metricEvaluated = document.getElementById("metric-evaluated");
    const metricAcceptance = document.getElementById("metric-acceptance");
    const metricBeliefs = document.getElementById("metric-beliefs");

    const feedBadge = document.getElementById("feed-badge");
    const auditBadge = document.getElementById("audit-badge");

    const personaNameDisplay = document.getElementById("persona-name-display");
    const personaDomainDisplay = document.getElementById("persona-domain-display");
    const curlFeedCmd = document.getElementById("curl-feed-cmd");

    const initModal = document.getElementById("init-modal");
    const btnInitModal = document.getElementById("btn-init-modal");
    const btnCloseModal = document.getElementById("btn-close-modal");
    const initForm = document.getElementById("init-form");

    const btnForceTick = document.getElementById("btn-force-tick");

    // Tabs
    const tabBtns = document.querySelectorAll(".cyber-tab-btn");
    const tabPanels = document.querySelectorAll(".tab-panel");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            tabPanels.forEach(p => p.classList.remove("active"));
            btn.classList.add("active");
            const target = btn.getAttribute("data-tab");
            document.getElementById(target).classList.add("active");
        });
    });

    // Modal
    btnInitModal.addEventListener("click", () => initModal.classList.add("active"));
    btnCloseModal.addEventListener("click", () => initModal.classList.remove("active"));

    initForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = document.getElementById("input-name").value.trim();
        const domain = document.getElementById("input-domain").value.trim();

        try {
            const resp = await fetch("/api/agent/init", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ persona: { name, domain } })
            });
            if (resp.ok) {
                const data = await resp.json();
                currentAgentId = data.agentId;
                personaNameDisplay.textContent = name;
                personaDomainDisplay.textContent = domain;
                if (curlFeedCmd) curlFeedCmd.textContent = `curl http://localhost:8000/api/agent/feed?agentId=${currentAgentId}`;
                initModal.classList.remove("active");
                refreshAll();
            }
        } catch (err) {
            console.error("Init failed:", err);
        }
    });

    btnForceTick.addEventListener("click", async () => {
        btnForceTick.disabled = true;
        try {
            await fetch(`/api/agent/tick?agentId=${currentAgentId}`, { method: "POST" });
            countdownVal = intervalSec;
            await refreshAll();
        } catch (err) {
            console.error("Tick failed:", err);
        } finally {
            btnForceTick.disabled = false;
        }
    });

    async function fetchFeed() {
        try {
            const resp = await fetch(`/api/agent/feed?agentId=${currentAgentId}`);
            if (!resp.ok) return;
            const data = await resp.json();
            const posts = data.posts || [];

            feedBadge.textContent = posts.length;
            metricPosts.textContent = posts.length;

            if (posts.length === 0) {
                postsContainer.innerHTML = `<div class="terminal-msg">No posts published yet. Continuous cycle running...</div>`;
                return;
            }

            postsContainer.innerHTML = posts.map(p => `
                <div class="post-card">
                    <div class="post-hdr">
                        <span>ID: ${p.id}</span>
                        <span>${new Date(p.createdAt).toLocaleString()}</span>
                    </div>
                    <div class="post-txt">${escapeHtml(p.text)}</div>
                    <div class="rat-box">
                        <div class="rat-hdr">// PUBLISHING RATIONALE</div>
                        <div>${escapeHtml(p.rationale)}</div>
                    </div>
                    <div class="sources-box">
                        ${(p.sources || []).map(s => `<a href="${s}" target="_blank">🔗 ${s}</a>`).join(" ")}
                    </div>
                </div>
            `).join("");
        } catch (err) {
            console.error("Error fetching feed:", err);
        }
    }

    async function fetchStatus() {
        try {
            const resp = await fetch(`/api/agent/status?agentId=${currentAgentId}`);
            if (!resp.ok) return;
            const data = await resp.json();
            const m = data.metrics || {};

            metricEvaluated.textContent = m.totalEvaluations || 0;
            metricAcceptance.textContent = `${m.acceptanceRate || 100}%`;
            metricBeliefs.textContent = m.beliefsCount || 0;

            const beliefs = data.beliefs || [];
            if (beliefs.length === 0) {
                beliefsContainer.innerHTML = `<div class="terminal-msg">No persistent belief nodes stored yet.</div>`;
            } else {
                beliefsContainer.innerHTML = beliefs.map(b => `
                    <div class="belief-card">
                        <div class="belief-hdr">
                            <span>TYPE: ${b.evidence_type}</span>
                            <span>CONF: ${Math.round(b.confidence * 100)}%</span>
                        </div>
                        <div style="font-weight: 700; font-size: 0.85rem; margin-top: 4px;">${escapeHtml(b.subject)}</div>
                        <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 4px;">${escapeHtml(b.statement)}</div>
                    </div>
                `).join("");
            }
        } catch (err) {
            console.error("Error fetching status:", err);
        }
    }

    async function fetchAudit() {
        try {
            const resp = await fetch(`/api/agent/rejections?agentId=${currentAgentId}`);
            if (!resp.ok) return;
            const data = await resp.json();
            const evals = data.evaluations || [];

            auditBadge.textContent = evals.length;

            if (evals.length === 0) {
                auditContainer.innerHTML = `<div class="terminal-msg">No evaluation logs recorded yet.</div>`;
                return;
            }

            auditContainer.innerHTML = evals.map(e => `
                <div class="audit-card">
                    <span class="badge-status ${e.status.toLowerCase()}">${e.status} (${e.score}/100)</span>
                    <div style="flex:1; margin-left: 12px;">
                        <div style="font-weight: 700;">${escapeHtml(e.topic_title)}</div>
                        <div style="color: var(--text-muted); font-size: 0.78rem;">${escapeHtml(e.reason)}</div>
                    </div>
                </div>
            `).join("");
        } catch (err) {
            console.error("Error fetching audit log:", err);
        }
    }

    async function refreshAll() {
        await Promise.all([fetchFeed(), fetchStatus(), fetchAudit()]);
    }

    setInterval(() => {
        countdownVal--;
        if (countdownVal <= 0) {
            countdownVal = intervalSec;
            refreshAll();
        }
        countdownTimerEl.textContent = `${countdownVal}s`;
        progressFillEl.style.width = `${(countdownVal / intervalSec) * 100}%`;
    }, 1000);

    function escapeHtml(t) {
        if (!t) return "";
        return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    refreshAll();
});
