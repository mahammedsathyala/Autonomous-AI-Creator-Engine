document.addEventListener("DOMContentLoaded", () => {
    let currentAgentId = "ada-sec-8f2a";
    let currentAgentName = "Ada";
    let currentAgentDomain = "AI Security";
    let countdownValue = 40;
    const intervalSeconds = 40;

    // UI Elements
    const postsContainer = document.getElementById("posts-container");
    const decisionsContainer = document.getElementById("decisions-container");
    const memoryContainer = document.getElementById("memory-container");
    const countdownTimerEl = document.getElementById("countdown-timer");
    const countdownProgressEl = document.getElementById("countdown-progress");
    const feedCountBadge = document.getElementById("feed-count-badge");
    const decisionsCountBadge = document.getElementById("decisions-count-badge");
    
    // Metrics
    const metricPosts = document.getElementById("metric-posts");
    const metricDiscovered = document.getElementById("metric-discovered");
    const metricRejectionRate = document.getElementById("metric-rejection-rate");
    const metricMemories = document.getElementById("metric-memories");

    // Agent Badges
    const currentAgentNameEl = document.getElementById("current-agent-name");
    const currentAgentDomainEl = document.getElementById("current-agent-domain");
    const curlFeedExample = document.getElementById("curl-feed-example");

    // Modal
    const initModal = document.getElementById("init-modal");
    const btnOpenModal = document.getElementById("btn-open-init-modal");
    const btnCloseModal = document.getElementById("btn-close-modal");
    const initForm = document.getElementById("init-agent-form");
    const presetCards = document.querySelectorAll(".preset-card");
    const personaNameInput = document.getElementById("persona-name");
    const personaDomainInput = document.getElementById("persona-domain");

    // Manual Tick Button
    const btnTriggerTick = document.getElementById("btn-trigger-tick");

    // Tab Switching Logic
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));
            btn.classList.add("active");
            const target = btn.getAttribute("data-tab");
            document.getElementById(target).classList.add("active");
        });
    });

    // Preset Selection in Modal
    presetCards.forEach(card => {
        card.addEventListener("click", () => {
            presetCards.forEach(c => c.classList.remove("selected"));
            card.classList.add("selected");
            const preset = card.getAttribute("data-preset");
            if (preset === "ada") {
                personaNameInput.value = "Ada";
                personaDomainInput.value = "AI Security";
            } else if (preset === "marcus") {
                personaNameInput.value = "Marcus";
                personaDomainInput.value = "ML Systems";
            } else if (preset === "elena") {
                personaNameInput.value = "Elena";
                personaDomainInput.value = "AI Product";
            }
        });
    });

    // Modal Handlers
    btnOpenModal.addEventListener("click", () => initModal.classList.add("active"));
    btnCloseModal.addEventListener("click", () => initModal.classList.remove("active"));
    initModal.addEventListener("click", (e) => {
        if (e.target === initModal) initModal.classList.remove("active");
    });

    // Form Submit -> POST /api/agent/init
    initForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = personaNameInput.value.trim();
        const domain = personaDomainInput.value.trim();

        try {
            const resp = await fetch("/api/agent/init", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ persona: { name, domain } })
            });

            if (resp.ok) {
                const data = await resp.json();
                currentAgentId = data.agentId;
                currentAgentName = name;
                currentAgentDomain = domain;

                updateAgentBadges();
                initModal.classList.remove("active");
                fetchFeed();
                fetchStatus();
                fetchDecisions();
            }
        } catch (err) {
            console.error("Error initializing agent:", err);
        }
    });

    // Manual Tick -> POST /api/agent/tick
    btnTriggerTick.addEventListener("click", async () => {
        btnTriggerTick.disabled = true;
        btnTriggerTick.querySelector("span").textContent = "⌛ Executing Cycle...";
        try {
            await fetch(`/api/agent/tick?agentId=${currentAgentId}`, { method: "POST" });
            countdownValue = intervalSeconds;
            await refreshAllData();
        } catch (err) {
            console.error("Error triggering tick:", err);
        } finally {
            btnTriggerTick.disabled = false;
            btnTriggerTick.querySelector("span").textContent = "⚡ Run Autonomous Cycle Now";
        }
    });

    function updateAgentBadges() {
        currentAgentNameEl.textContent = currentAgentName;
        currentAgentDomainEl.textContent = currentAgentDomain;
        if (curlFeedExample) {
            curlFeedExample.textContent = `curl http://localhost:8000/api/agent/feed?agentId=${currentAgentId}`;
        }
    }

    // Fetch Published Posts Feed (GET /api/agent/feed)
    async function fetchFeed() {
        try {
            const resp = await fetch(`/api/agent/feed?agentId=${currentAgentId}`);
            if (!resp.ok) return;
            const data = await resp.json();
            const posts = data.posts || [];
            
            feedCountBadge.textContent = posts.length;
            metricPosts.textContent = posts.length;

            if (posts.length === 0) {
                postsContainer.innerHTML = `<div class="loading-spinner">No posts published yet. Autonomous cycle running...</div>`;
                return;
            }

            postsContainer.innerHTML = posts.map(post => {
                const formattedDate = new Date(post.createdAt).toLocaleString();
                const sourcesHtml = post.sources && post.sources.length > 0
                    ? post.sources.map(s => `<a href="${s}" target="_blank" rel="noopener" class="source-link">🔗 Source Link</a>`).join(" ")
                    : '<span class="source-link">Verified Web Feed</span>';

                return `
                    <article class="post-card">
                        <div class="post-header">
                            <div class="post-author">
                                <div class="author-avatar">${getAvatarIcon(currentAgentName)}</div>
                                <div class="author-info">
                                    <h4>${currentAgentName}</h4>
                                    <span class="post-timestamp">${formattedDate}</span>
                                </div>
                            </div>
                            <span class="post-id-tag">id: ${post.id}</span>
                        </div>
                        <div class="post-text">${escapeHtml(post.text)}</div>
                        
                        <div class="rationale-box">
                            <div class="rationale-title">🧠 Publishing Rationale & Context</div>
                            <div class="rationale-text">${escapeHtml(post.rationale)}</div>
                        </div>

                        <div class="post-sources">
                            <span>Information Sources:</span>
                            ${sourcesHtml}
                        </div>
                    </article>
                `;
            }).join("");
        } catch (err) {
            console.error("Error fetching feed:", err);
        }
    }

    // Fetch Status & Metrics (GET /api/agent/status)
    async function fetchStatus() {
        try {
            const resp = await fetch(`/api/agent/status?agentId=${currentAgentId}`);
            if (!resp.ok) return;
            const data = await resp.json();
            const metrics = data.metrics || {};

            metricDiscovered.textContent = metrics.totalEvaluations || 0;
            metricRejectionRate.textContent = `${metrics.acceptanceRate || 100}%`;
            metricMemories.textContent = metrics.memoryItemsCount || 0;

            if (data.agent) {
                currentAgentName = data.agent.name;
                currentAgentDomain = data.agent.domain;
                updateAgentBadges();
            }

            // Render Memories tab items
            const memories = data.memories || [];
            if (memories.length === 0) {
                memoryContainer.innerHTML = `<div class="loading-spinner">No memory items recorded yet.</div>`;
            } else {
                memoryContainer.innerHTML = memories.map(m => `
                    <div class="memory-card">
                        <div class="memory-topic">${escapeHtml(m.topic_key)}</div>
                        <div class="memory-summary">${escapeHtml(m.summary)}</div>
                        <div class="memory-tags">
                            ${(m.keywords || []).map(k => `<span class="memory-tag">#${escapeHtml(k)}</span>`).join("")}
                        </div>
                    </div>
                `).join("");
            }
        } catch (err) {
            console.error("Error fetching status:", err);
        }
    }

    // Fetch Decision Log (GET /api/agent/rejections)
    async function fetchDecisions() {
        try {
            const resp = await fetch(`/api/agent/rejections?agentId=${currentAgentId}`);
            if (!resp.ok) return;
            const data = await resp.json();
            const evaluations = data.evaluations || [];

            decisionsCountBadge.textContent = evaluations.length;

            if (evaluations.length === 0) {
                decisionsContainer.innerHTML = `<div class="loading-spinner">No evaluation records log yet.</div>`;
                return;
            }

            decisionsContainer.innerHTML = evaluations.map(ev => {
                const statusClass = ev.status.toLowerCase();
                return `
                    <div class="decision-card">
                        <span class="decision-status ${statusClass}">${ev.status} (${ev.score}/100)</span>
                        <div class="decision-info">
                            <div class="decision-title">${escapeHtml(ev.topic_title)}</div>
                            <div class="decision-reason">${escapeHtml(ev.reason)}</div>
                        </div>
                    </div>
                `;
            }).join("");
        } catch (err) {
            console.error("Error fetching decision log:", err);
        }
    }

    async function refreshAllData() {
        await Promise.all([fetchFeed(), fetchStatus(), fetchDecisions()]);
    }

    // Countdown Timer Loop
    setInterval(() => {
        countdownValue--;
        if (countdownValue <= 0) {
            countdownValue = intervalSeconds;
            refreshAllData();
        }
        countdownTimerEl.textContent = `${countdownValue}s`;
        const percentage = (countdownValue / intervalSeconds) * 100;
        countdownProgressEl.style.width = `${percentage}%`;
    }, 1000);

    function getAvatarIcon(name) {
        if (name.toLowerCase().includes("ada")) return "🛡️";
        if (name.toLowerCase().includes("marcus")) return "⚡";
        if (name.toLowerCase().includes("elena")) return "💡";
        return "🤖";
    }

    function escapeHtml(text) {
        if (!text) return "";
        return text.replace(/&/g, "&amp;")
                   .replace(/</g, "&lt;")
                   .replace(/>/g, "&gt;")
                   .replace(/"/g, "&quot;")
                   .replace(/'/g, "&#039;");
    }

    // Initial Load
    refreshAllData();
});
