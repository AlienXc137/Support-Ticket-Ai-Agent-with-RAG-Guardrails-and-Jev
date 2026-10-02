const state = {
    currentTicketId: null,
    currentState: null,
};

const $ = (id) => document.getElementById(id);

function escapeHtml(value) {
    const div = document.createElement("div");

    div.textContent = value ?? "";

    return div.innerHTML;
}

function formatPercent(value) {
    const numeric = Number(value || 0);

    return `${Math.round(numeric * 100)}%`;
}

function formatLabel(value) {
    return String(value || "—")
        .replaceAll("_", " ")
        .toLowerCase()
        .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function showToast(message) {
    const toast = $("toast");

    toast.textContent = message;

    toast.classList.remove("hidden");

    window.clearTimeout(showToast.timeout);

    showToast.timeout = window.setTimeout(() => {
        toast.classList.add("hidden");
    }, 3200);
}

function setTagList(
    elementId,
    values,
    emptyText = "None",
) {
    const element = $(elementId);

    if (!values || values.length === 0) {
        element.innerHTML = `
            <span class="tag">
                ${escapeHtml(emptyText)}
            </span>
        `;

        return;
    }

    element.innerHTML = values
        .map(
            (value) =>
                `<span class="tag">${escapeHtml(value)}</span>`,
        )
        .join("");
}

function collectEvidence(ticketState) {
    const items = [];

    for (
        const document of ticketState.retrieved_documents || []
    ) {
        const metadata = document.metadata || {};

        items.push({
            id: metadata.id || "KB",
            type: "INTERNAL_KB",
            title:
                metadata.title ||
                "Knowledge document",
            content:
                document.content ||
                "",
            url: "",
        });
    }

    for (
        let index = 0;
        index < (ticketState.web_results || []).length;
        index += 1
    ) {
        const result =
            ticketState.web_results[index] || {};

        items.push({
            id: `web-${index + 1}`,
            type: "APPROVED_WEB",
            title:
                result.title ||
                "Web result",
            content:
                result.content ||
                "",
            url:
                result.url ||
                "",
        });
    }

    return items;
}

function renderEvidence(ticketState) {
    const items = collectEvidence(ticketState);

    $("evidenceCount").textContent =
        `${items.length} ${items.length === 1
            ? "source"
            : "sources"
        }`;

    if (items.length === 0) {
        $("evidenceList").innerHTML = `
            <div class="evidence-card">
                <div class="evidence-content">
                    No evidence was returned for this ticket.
                </div>
            </div>
        `;

        return;
    }

    $("evidenceList").innerHTML = items
        .map(
            (item) => `
                <article class="evidence-card">
                    <div class="evidence-top">
                        <div>
                            <div class="evidence-id">
                                ${escapeHtml(item.id)}
                            </div>

                            <div class="evidence-title">
                                ${escapeHtml(item.title)}
                            </div>
                        </div>

                        <span class="tag">
                            ${escapeHtml(item.type)}
                        </span>
                    </div>

                    <p class="evidence-content">
                        ${escapeHtml(item.content)}
                    </p>

                    ${item.url
                    ? `
                                <div class="evidence-url">
                                    ${escapeHtml(item.url)}
                                </div>
                            `
                    : ""
                }
                </article>
            `,
        )
        .join("");
}

function buildWorkflow(ticketState) {
    const reasonCodes =
        ticketState.reason_codes || [];

    const webRequired =
        Boolean(ticketState.web_required);

    const webUsed =
        Boolean(ticketState.web_used);

    const guardrailKnown =
        typeof ticketState.input_allowed ===
        "boolean";

    const guardrailBlocked =
        guardrailKnown &&
        !ticketState.input_allowed;

    const coverageKnown =
        typeof ticketState.kb_coverage ===
        "boolean";

    const verificationKnown =
        typeof ticketState.verification_passed ===
        "boolean" ||
        ticketState.verification_grounding_probability !==
        undefined ||
        ticketState.verification_citation_probability !==
        undefined;

    const verificationFailed =
        verificationKnown &&
        !ticketState.verification_passed;

    const stages = [
        {
            number: "01",
            title: "Sanitize",
            tech: "Presidio",
            description:
                "Redact sensitive data before model and web boundaries.",
            status:
                ticketState.masked_message
                    ? "EXECUTED"
                    : "PENDING",
            kind:
                ticketState.masked_message
                    ? "executed"
                    : "skipped",
            meta:
                `${(
                    ticketState.pii_detected ||
                    []
                ).length} PII types detected`,
        },

        {
            number: "02",
            title: "Guardrails",
            tech: "NeMo",
            description:
                "Check the sanitized ticket for prompt injection and unsafe input.",
            status:
                guardrailBlocked
                    ? "BLOCKED"
                    : guardrailKnown
                        ? "PASSED"
                        : "PENDING",
            kind:
                guardrailBlocked
                    ? "warning"
                    : guardrailKnown
                        ? "executed"
                        : "skipped",
            meta:
                ticketState.guardrail_status
                    ? formatLabel(
                        ticketState.guardrail_status,
                    )
                    : "Waiting for result",
        },

        {
            number: "03",
            title: "Analyze",
            tech: "Structured LLM",
            description:
                "Extract category, urgency, complexity, anger, and risk flags.",
            status:
                ticketState.primary_category
                    ? "EXECUTED"
                    : "PENDING",
            kind:
                ticketState.primary_category
                    ? "executed"
                    : "skipped",
            meta:
                ticketState.primary_category
                    ? formatLabel(
                        ticketState.primary_category,
                    )
                    : "No analysis yet",
        },

        {
            number: "04",
            title: "Retrieve",
            tech: "Hybrid RAG",
            description:
                "Combine lexical and semantic retrieval against the internal KB.",
            status:
                ticketState.retrieved_documents
                    ? "EXECUTED"
                    : "PENDING",
            kind:
                ticketState.retrieved_documents
                    ? "executed"
                    : "skipped",
            meta:
                `${(
                    ticketState.retrieved_documents ||
                    []
                ).length
                } KB documents`,
        },

        {
            number: "05",
            title: "Coverage",
            tech: "Coverage Gate",
            description:
                "Decide whether the internal KB is sufficient to answer safely.",
            status:
                coverageKnown
                    ? "BRANCH"
                    : "PENDING",
            kind:
                coverageKnown
                    ? "branch"
                    : "skipped",
            meta:
                coverageKnown
                    ? ticketState.kb_coverage
                        ? "KB sufficient → skip web"
                        : "KB insufficient → web fallback"
                    : "Waiting for coverage",
        },

        {
            number: "06",
            title: "Web Search",
            tech: "Policy + Tavily",
            description:
                "Only run when coverage is insufficient and policy permits it.",
            status:
                !webRequired
                    ? "SKIPPED"
                    : webUsed
                        ? "EXECUTED"
                        : reasonCodes.includes(
                            "WEB_NOT_ALLOWED",
                        )
                            ? "BLOCKED"
                            : "NO RESULT",
            kind:
                !webRequired
                    ? "skipped"
                    : webUsed
                        ? "executed"
                        : "warning",
            meta:
                !webRequired
                    ? "Internal evidence was enough"
                    : webUsed
                        ? `${(
                            ticketState.web_results ||
                            []
                        ).length
                        } approved web results`
                        : ticketState.web_reason ||
                        "External evidence unavailable",
        },

        {
            number: "07",
            title: "Draft",
            tech: "Response LLM",
            description:
                "Construct a response strictly from the supplied evidence.",
            status:
                ticketState.draft
                    ? "EXECUTED"
                    : "PENDING",
            kind:
                ticketState.draft
                    ? "executed"
                    : "skipped",
            meta:
                `${(
                    ticketState.citations ||
                    []
                ).length
                } citation(s)`,
        },

        {
            number: "08",
            title: "Verify",
            tech: "Jev",
            description:
                "Independently test grounding and citation support before routing.",
            status:
                !verificationKnown
                    ? "PENDING"
                    : ticketState.verification_passed
                        ? "PASSED"
                        : "FAILED",
            kind:
                !verificationKnown
                    ? "skipped"
                    : ticketState.verification_passed
                        ? "executed"
                        : "warning",
            meta:
                !verificationKnown
                    ? "Waiting for verification"
                    : ticketState.verification_passed
                        ? "Grounding + citations passed"
                        : "Verification threshold not met",
        },

        {
            number: "09",
            title: "Retry",
            tech: "Controlled Loop",
            description:
                "Rewrite once using verification feedback; no infinite agent loop.",
            status:
                Number(
                    ticketState.retry_count ||
                    0,
                ) > 0
                    ? `RETRY #${ticketState.retry_count
                    }`
                    : "SKIPPED",
            kind:
                Number(
                    ticketState.retry_count ||
                    0,
                ) > 0
                    ? "branch"
                    : "skipped",
            meta:
                Number(
                    ticketState.retry_count ||
                    0,
                ) > 0
                    ? "Draft regenerated with verification feedback"
                    : "No retry required",
        },

        {
            number: "10",
            title: "Decision",
            tech: "Deterministic Gate",
            description:
                "Apply business rules; route automatically only when all gates pass.",
            status:
                ticketState.decision
                    ? "EXECUTED"
                    : "PENDING",
            kind:
                ticketState.decision ===
                    "HUMAN_APPROVE"
                    ? "warning"
                    : ticketState.decision ===
                        "AUTO_REPLY"
                        ? "executed"
                        : "skipped",
            meta:
                ticketState.decision
                    ? ticketState.decision ===
                        "AUTO_REPLY"
                        ? "Safe for automatic delivery"
                        : "Requires human approval"
                    : "Waiting for decision",
        },

        {
            number: "11",
            title: "HITL",
            tech: "Reviewer",
            description:
                "Human approval, edit, or rejection is applied outside the graph route.",
            status:
                ticketState.review_status ===
                    "PENDING"
                    ? "WAITING"
                    : ticketState.review_status
                        ? formatLabel(
                            ticketState.review_status,
                        )
                        : ticketState.decision ===
                            "AUTO_REPLY"
                            ? "SKIPPED"
                            : "PENDING",
            kind:
                ticketState.review_status ===
                    "PENDING"
                    ? "warning"
                    : ticketState.review_status
                        ? "executed"
                        : "skipped",
            meta:
                ticketState.review_status ===
                    "PENDING"
                    ? "Reviewer action required"
                    : ticketState.review_status
                        ? "Review state recorded"
                        : "Not required for auto-reply",
        },
    ];

    return {
        stages,
        verificationFailed,
        webRequired,
        webUsed,
        guardrailBlocked,
    };
}

function renderWorkflow(ticketState) {
    const workflow =
        buildWorkflow(ticketState);

    const stages =
        workflow.stages;

    const executedCount =
        stages.filter(
            (stage) =>
                stage.kind === "executed" ||
                stage.kind === "branch" ||
                stage.kind === "warning",
        ).length;

    const path =
        workflow.webUsed
            ? "Internal KB → approved web → draft → Jev → route"
            : workflow.webRequired
                ? "Internal KB → web policy gate → draft → Jev → route"
                : "Internal KB → draft → Jev → route";

    $("workflowSummary").innerHTML = `
        <div class="workflow-stat">
            <span>Executed control points</span>
            <strong>
                ${executedCount} / ${stages.length}
            </strong>
        </div>

        <div class="workflow-stat">
            <span>Evidence path</span>
            <strong>
                ${escapeHtml(
        workflow.webUsed
            ? "KB + Approved Web"
            : "Internal KB",
    )}
            </strong>
        </div>

        <div class="workflow-stat">
            <span>Loop state</span>
            <strong>
                ${escapeHtml(
        Number(
            ticketState.retry_count ||
            0,
        ) > 0
            ? `Verification retry ${ticketState.retry_count
            } / 1`
            : "No retry used",
    )}
            </strong>
        </div>
    `;

    $("workflowTrace").innerHTML =
        stages
            .map(
                (stage) => `
                    <article class="workflow-node ${stage.kind}">
                        <div class="node-top">
                            <div class="node-number">
                                ${stage.number}
                            </div>

                            <span class="node-status">
                                ${escapeHtml(
                    stage.status,
                )}
                            </span>
                        </div>

                        <div class="node-title">
                            ${escapeHtml(
                    stage.title,
                )}
                        </div>

                        <div class="node-tech">
                            ${escapeHtml(
                    stage.tech,
                )}
                        </div>

                        <p class="node-description">
                            ${escapeHtml(
                    stage.description,
                )}
                        </p>

                        <div class="node-meta">
                            ${escapeHtml(
                    stage.meta,
                )}
                        </div>
                    </article>
                `,
            )
            .join("");

    $("workflowPathNote").innerHTML = `
        <strong>Executed route:</strong>
        ${escapeHtml(path)}.

        ${workflow.guardrailBlocked
            ? " The safety gate blocked the ticket, so downstream model processing did not continue."
            : workflow.verificationFailed &&
                Number(
                    ticketState.retry_count ||
                    0,
                ) > 0
                ? " Verification failed, so the response was regenerated once using verification feedback before the final routing decision."
                : ticketState.decision ===
                    "HUMAN_APPROVE"
                    ? " The deterministic decision gate stopped automatic delivery and placed the ticket in human review."
                    : ticketState.decision ===
                        "AUTO_REPLY"
                        ? " All current automatic-response gates passed, so the draft is marked ready for delivery."
                        : ""
        }
    `;
}

function renderState(ticketState) {
    state.currentState =
        ticketState;

    $("emptyState")
        .classList
        .add("hidden");

    $("dashboard")
        .classList
        .remove("hidden");

    $("ticketIdentity").textContent =
        ticketState.ticket_id ||
        "Unknown ticket";

    $("ticketChannel").textContent =
        ticketState.channel ||
        "—";

    $("sidePii").textContent =
        (
            ticketState.pii_detected ||
            []
        ).length > 0
            ? `${ticketState.pii_detected.length
            } detected`
            : "None detected";

    $("ticketTitle").textContent =
        ticketState.ticket_id ||
        "Support ticket";

    $("ticketMessagePreview").textContent =
        ticketState.masked_message ||
        ticketState.raw_message ||
        "—";

    $("metricCategory").textContent =
        formatLabel(
            ticketState.primary_category,
        );

    $("metricUrgency").textContent =
        formatLabel(
            ticketState.urgency,
        );

    $("metricComplexity").textContent =
        formatLabel(
            ticketState.complexity,
        );

    $("metricKb").textContent =
        typeof ticketState.kb_coverage ===
            "boolean"
            ? ticketState.kb_coverage
                ? "Sufficient"
                : "Insufficient"
            : "—";

    $("metricKbSub").textContent =
        ticketState.web_required
            ? "web fallback evaluated"
            : "internal evidence gate";

    setTagList(
        "piiDetected",
        ticketState.pii_detected ||
        [],
    );

    setTagList(
        "riskFlags",
        ticketState.risk_flags ||
        [],
    );

    $("angerScore").textContent =
        ticketState.anger_score ===
            undefined
            ? "—"
            : Number(
                ticketState.anger_score,
            ).toFixed(2);

    $("webSource").textContent =
        formatLabel(
            ticketState.web_source_type,
        );

    $("webUsed").textContent =
        ticketState.web_used
            ? `Yes · ${(
                ticketState.web_results ||
                []
            ).length
            } results`
            : ticketState.web_required
                ? "Required · unavailable"
                : "No · not required";

    $("retryCount").textContent =
        `${ticketState.retry_count ||
        0
        } / 1`;

    renderWorkflow(
        ticketState,
    );

    renderEvidence(
        ticketState,
    );

    $("draftResponse").textContent =
        ticketState.draft ||
        "No draft generated.";

    setTagList(
        "citationPills",
        ticketState.citations ||
        [],
        "No citations",
    );

    const grounding =
        Number(
            ticketState
                .verification_grounding_probability ||
            0,
        );

    const citation =
        Number(
            ticketState
                .verification_citation_probability ||
            0,
        );

    $("groundingValue").textContent =
        formatPercent(
            grounding,
        );

    $("citationValue").textContent =
        formatPercent(
            citation,
        );

    $("groundingBar").style.width =
        `${Math.max(
            0,
            Math.min(
                1,
                grounding,
            ),
        ) * 100
        }%`;

    $("citationBar").style.width =
        `${Math.max(
            0,
            Math.min(
                1,
                citation,
            ),
        ) * 100
        }%`;

    $("verificationStatus")
        .textContent =
        ticketState.verification_passed
            ? "Verified"
            : "Review required";

    $("verificationStatus")
        .classList
        .remove(
            "success",
            "warning",
            "danger",
        );

    $("verificationStatus")
        .classList
        .add(
            ticketState.verification_passed
                ? "success"
                : "warning",
        );

    $("verificationReason")
        .textContent =
        ticketState.verification_reason ||
        ticketState.verification_feedback ||
        "—";

    const analysisSignal =
        $("analysisSignal");

    analysisSignal.textContent =
        (
            ticketState.risk_flags ||
            []
        ).length > 0
            ? "Risk flags present"
            : "No risk flags";

    analysisSignal
        .classList
        .remove(
            "success",
            "warning",
            "danger",
        );

    analysisSignal
        .classList
        .add(
            (
                ticketState.risk_flags ||
                []
            ).length > 0
                ? "warning"
                : "success",
        );

    const decisionBadge =
        $("decisionBadge");

    decisionBadge.textContent =
        ticketState.decision ||
        "—";

    decisionBadge
        .classList
        .remove(
            "auto",
            "human",
        );

    if (
        ticketState.decision ===
        "AUTO_REPLY"
    ) {
        decisionBadge
            .classList
            .add("auto");
    } else if (
        ticketState.decision ===
        "HUMAN_APPROVE"
    ) {
        decisionBadge
            .classList
            .add("human");
    }

    const topDecision =
        $("topDecision");

    topDecision.textContent =
        ticketState.decision ||
        "READY";

    topDecision
        .classList
        .remove(
            "auto",
            "human",
            "ready",
            "review",
        );

    if (
        ticketState.decision ===
        "AUTO_REPLY"
    ) {
        topDecision
            .classList
            .add("auto");
    } else if (
        ticketState.decision ===
        "HUMAN_APPROVE"
    ) {
        topDecision
            .classList
            .add("human");
    } else {
        topDecision
            .classList
            .add("ready");
    }

    const activityPill =
        $("activityPill");

    activityPill
        .classList
        .remove(
            "auto",
            "human",
            "danger",
        );

    if (
        ticketState.decision ===
        "HUMAN_APPROVE" &&
        ticketState.review_status ===
        "PENDING"
    ) {
        activityPill.textContent =
            "Awaiting human review";

        activityPill
            .classList
            .add("human");

        $("runtimeStatus")
            .textContent =
            "REVIEW REQUIRED";
    } else if (
        ticketState.delivery_status ===
        "READY_TO_SEND"
    ) {
        activityPill.textContent =
            "Ready for delivery";

        activityPill
            .classList
            .add("auto");

        $("runtimeStatus")
            .textContent =
            "WORKFLOW COMPLETE";
    } else if (
        ticketState.guardrail_status &&
        !ticketState.input_allowed
    ) {
        activityPill.textContent =
            "Input blocked";

        activityPill
            .classList
            .add("danger");

        $("runtimeStatus")
            .textContent =
            "INPUT BLOCKED";
    } else {
        activityPill.textContent =
            "Workflow complete";

        activityPill
            .classList
            .add("auto");

        $("runtimeStatus")
            .textContent =
            "WORKFLOW COMPLETE";
    }

    $("whatHappened").textContent =
        buildWhatHappened(
            ticketState,
        );

    $("sideDecision").textContent =
        ticketState.decision ||
        "—";

    $("sideReview").textContent =
        ticketState.review_status ||
        "—";

    $("sideDelivery").textContent =
        ticketState.delivery_status ||
        "—";

    const reasons =
        ticketState.reason_codes ||
        [];

    $("reasonCodes").innerHTML =
        reasons.length
            ? reasons
                .map(
                    (reason) =>
                        `
                            <span class="reason-code">
                                ${escapeHtml(
                            reason,
                        )}
                            </span>
                        `,
                )
                .join("")
            : `
                <span class="tag">
                    No escalation reason
                </span>
            `;

    const reviewControls =
        $("reviewControls");

    const finalSection =
        $("finalResponseSection");

    if (
        ticketState.decision ===
        "HUMAN_APPROVE" &&
        ticketState.review_status ===
        "PENDING"
    ) {
        reviewControls
            .classList
            .remove("hidden");
    } else {
        reviewControls
            .classList
            .add("hidden");
    }

    if (
        ticketState.delivery_status ===
        "READY_TO_SEND"
    ) {
        finalSection
            .classList
            .remove("hidden");

        $("finalResponse")
            .textContent =
            ticketState.final_response ||
            ticketState.draft ||
            "";
    } else {
        finalSection
            .classList
            .add("hidden");
    }

    if (
        ticketState.review_status ===
        "REJECTED"
    ) {
        $("reviewTitle")
            .textContent =
            "Rejected by reviewer";
    } else if (
        ticketState.review_status ===
        "APPROVED_WITH_EDIT"
    ) {
        $("reviewTitle")
            .textContent =
            "Approved with edit";
    } else if (
        ticketState.review_status ===
        "APPROVED"
    ) {
        $("reviewTitle")
            .textContent =
            "Approved by reviewer";
    } else if (
        ticketState.decision ===
        "HUMAN_APPROVE"
    ) {
        $("reviewTitle")
            .textContent =
            "Human approval required";
    } else {
        $("reviewTitle")
            .textContent =
            "Automatic route selected";
    }

    $("deliveryStatus")
        .textContent =
        ticketState.delivery_status ||
        "—";
}

function buildWhatHappened(
    ticketState,
) {
    if (
        ticketState.guardrail_status &&
        !ticketState.input_allowed
    ) {
        return (
            "The ticket was sanitized and then "
            + "blocked by the input-safety gate, "
            + "so downstream model processing "
            + "should not continue."
        );
    }

    const evidenceCount =
        (
            ticketState.retrieved_documents ||
            []
        ).length +
        (
            ticketState.web_results ||
            []
        ).length;

    const retryCount =
        Number(
            ticketState.retry_count ||
            0,
        );

    if (
        ticketState.decision ===
        "HUMAN_APPROVE" &&
        ticketState.review_status ===
        "PENDING"
    ) {
        return (
            `The agent found ${evidenceCount
            } evidence source(s), generated `
            + "a response, and sent it through Jev. "
            + "The final gate kept automatic delivery "
            + "off and opened human review."
        );
    }

    if (
        ticketState.decision ===
        "AUTO_REPLY"
    ) {
        return (
            `The workflow completed with ${evidenceCount
            } evidence source(s). Jev verification `
            + "passed the configured gate, and the "
            + "deterministic decision node marked the "
            + "response ready for delivery."
        );
    }

    if (retryCount > 0) {
        return (
            "The first verification pass did not meet "
            + "the configured threshold, so the response "
            + "was regenerated once using verification "
            + "feedback before the final routing decision."
        );
    }

    return (
        "The workflow processed the ticket through "
        + "its current control points and stored the "
        + "resulting routing state for review."
    );
}

async function readJsonResponse(
    response,
) {
    let data;

    try {
        data =
            await response.json();
    } catch {
        throw new Error(
            "The server returned an invalid response.",
        );
    }

    if (!response.ok) {
        throw new Error(
            data.detail ||
            "Request failed.",
        );
    }

    return data;
}

async function runWorkflow() {
    const message =
        $("ticketMessage")
            .value
            .trim();

    if (!message) {
        showToast(
            "Enter a support ticket first.",
        );

        return;
    }

    const button =
        $("runButton");

    const original =
        button.innerHTML;

    button.disabled = true;

    button.innerHTML = `
        <span>Running agent...</span>
        <span class="button-arrow">
            • • •
        </span>
    `;

    $("runtimeStatus")
        .textContent =
        "EXECUTING WORKFLOW";

    try {
        const response =
            await fetch(
                "/api/tickets",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        message,
                        channel: "web",
                    }),
                },
            );

        const data =
            await readJsonResponse(
                response,
            );

        state.currentTicketId =
            data.ticket_id;

        renderState(
            data.state,
        );

        $("editBox")
            .classList
            .add("hidden");

        $("reviewNote").value =
            "";

        $("editedResponse").value =
            "";

        showToast(
            `Workflow completed for ${data.ticket_id
            }.`,
        );
    } catch (error) {
        $("runtimeStatus")
            .textContent =
            "WORKFLOW ERROR";

        showToast(
            error.message,
        );
    } finally {
        button.disabled =
            false;

        button.innerHTML =
            original;
    }
}

async function submitReview(
    action,
    editedResponse = "",
) {
    if (!state.currentTicketId) {
        showToast(
            "No ticket is loaded.",
        );

        return;
    }

    const reviewerNote =
        $("reviewNote")
            .value
            .trim();

    try {
        const response =
            await fetch(
                `/api/tickets/${encodeURIComponent(
                    state.currentTicketId,
                )}/review`,
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        action,
                        reviewer_note:
                            reviewerNote,
                        edited_response:
                            editedResponse,
                    }),
                },
            );

        const data =
            await readJsonResponse(
                response,
            );

        renderState(
            data.state,
        );

        $("editBox")
            .classList
            .add("hidden");

        showToast(
            `Review action '${action}' applied.`,
        );
    } catch (error) {
        showToast(
            error.message,
        );
    }
}

function startEdit() {
    const current =
        state.currentState?.draft ||
        "";

    $("editedResponse")
        .value =
        current;

    $("editBox")
        .classList
        .remove("hidden");

    $("editedResponse")
        .focus();
}

function updateClock() {
    const now =
        new Date();

    $("clock")
        .textContent =
        now.toLocaleTimeString();
}

$("runButton").addEventListener(
    "click",
    runWorkflow,
);

$("approveButton").addEventListener(
    "click",
    () =>
        submitReview(
            "approve",
        ),
);

$("rejectButton").addEventListener(
    "click",
    () =>
        submitReview(
            "reject",
        ),
);

$("editButton").addEventListener(
    "click",
    startEdit,
);

$("saveEditButton")
    .addEventListener(
        "click",
        () => {
            const edited =
                $("editedResponse")
                    .value
                    .trim();

            if (!edited) {
                showToast(
                    "The edited response cannot be empty.",
                );

                return;
            }

            submitReview(
                "edit",
                edited,
            );
        },
    );

$("ticketMessage")
    .addEventListener(
        "keydown",
        (event) => {
            if (
                event.ctrlKey &&
                event.key === "Enter"
            ) {
                event.preventDefault();

                runWorkflow();
            }
        },
    );

updateClock();

window.setInterval(
    updateClock,
    1000,
);