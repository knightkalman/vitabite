const LOCATION_LABELS = {
  vienna: "Vienna",
  europe: "Europe",
  us: "US",
  asia: "Asia",
  other: "Global",
};

const storyList = document.querySelector("#story-list");
const feedFreshness = document.querySelector("#feed-freshness");
const filterStatus = document.querySelector("#filter-status");
const headlineCount = document.querySelector("#headline-count");
const filterButtons = [...document.querySelectorAll("[data-location]")];
let events = [];
let selectedLocation = "all";
let feedError = false;

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (character) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    };
    return entities[character];
  });
}

function safeSourceUrl(value) {
  try {
    const url = new URL(value);
    return url.protocol === "https:" ? url.href : null;
  } catch {
    return null;
  }
}

function displayDate(value, precision = "day", rawValue = null) {
  if (precision !== "day") {
    return rawValue || "Date unavailable";
  }
  const date = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(date.getTime())) {
    return rawValue || "Date unavailable";
  }
  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  }).format(date);
}

function setFeedMessage({ label, heading, description, foot }) {
  storyList.innerHTML = `
    <div class="feed-message">
      <span class="message-ornament" aria-hidden="true">✳</span>
      <p class="message-label">${escapeHtml(label)}</p>
      <h3>${escapeHtml(heading)}</h3>
      <p>${escapeHtml(description)}</p>
      <span class="message-foot">${escapeHtml(foot)}</span>
    </div>
  `;
}

function matchesLocation(eventItem, locationFilter) {
  if (locationFilter === "all") {
    return true;
  }
  if (eventItem.location === locationFilter) {
    return true;
  }
  if (
    Array.isArray(eventItem.location_groups) &&
    eventItem.location_groups.includes(locationFilter)
  ) {
    return true;
  }
  if (locationFilter === "europe" && eventItem.location === "vienna") {
    return true;
  }
  return false;
}

function formatLocationBadge(eventItem, isCandidate) {
  const groups = Array.isArray(eventItem.location_groups)
    ? eventItem.location_groups
    : [];
  const labels = groups
    .map((group) => LOCATION_LABELS[group])
    .filter(Boolean);
  const regionText =
    labels.length > 0
      ? labels.join(" · ")
      : LOCATION_LABELS[eventItem.location] ?? "Global";
  return `${isCandidate ? "Provisional · " : ""}${regionText}`;
}

function renderEvents() {
  if (feedError) {
    return;
  }
  const visibleEvents = events.filter((eventItem) =>
    matchesLocation(eventItem, selectedLocation),
  );

  filterStatus.textContent =
    visibleEvents.length === 1
      ? "1 event shown."
      : `${visibleEvents.length} events shown.`;

  if (visibleEvents.length === 0) {
    if (events.length === 0) {
      setFeedMessage({
        label: "The VitaBite calendar",
        heading: "No collected event listings are available.",
        description:
          "The last collection may not have produced records. Check the source and run status before treating this as an empty calendar.",
        foot: "NO SOURCE RECORDS IN THIS FEED",
      });
    } else {
      setFeedMessage({
        label: "A quieter corner",
        heading: "No events in this location group yet.",
        description:
          "Try another location filter (such as Europe or All) to browse the conferences and symposia currently in the collection.",
        foot: LOCATION_LABELS[selectedLocation]?.toUpperCase() ?? "NO EVENTS",
      });
    }
    return;
  }

  storyList.innerHTML = visibleEvents
    .map((eventItem) => {
      const sourceUrl = safeSourceUrl(eventItem.source_url);
      if (!sourceUrl) {
        return "";
      }
      const hiddenTags = new Set([
        "needs_review",
        eventItem.location,
        ...(eventItem.location_groups ?? []),
      ]);
      const tags = (eventItem.tags ?? [])
        .filter((tag) => !hiddenTags.has(tag))
        .map(
          (tag) =>
            `<span class="story-tag">${escapeHtml(tag.replaceAll("_", " "))}</span>`,
        )
        .join("");
      const author = eventItem.author
        ? `<span>${escapeHtml(eventItem.author)}</span>`
        : "";
      const evidence = eventItem.evidence_notes
        ? `<p class="story-evidence">${escapeHtml(eventItem.evidence_notes)}</p>`
        : "";
      const publicationDate = displayDate(
        eventItem.publication_date,
        eventItem.publication_date_precision,
        eventItem.publication_date_raw,
      );
      const isCandidate = eventItem.review_state === "candidate";
      const summary = isCandidate
        ? "Source event listing only. No summary or editorial review has been provided."
        : eventItem.summary;
      const locationLabel = formatLocationBadge(eventItem, isCandidate);

      return `
        <article class="story-card">
          <div class="story-meta">
            <span class="story-category">${escapeHtml(locationLabel)}</span>
            <span>${escapeHtml(publicationDate)}</span>
            <span>${escapeHtml(eventItem.publisher)}</span>
            ${author}
          </div>
          <div>
            <h3>${escapeHtml(eventItem.title)}</h3>
            ${isCandidate ? '<p class="story-review-label">Unreviewed event listing</p>' : ""}
            <p class="story-summary">${escapeHtml(summary)}</p>
            ${evidence}
            <div class="story-tags" aria-label="Event tags">${tags}</div>
            <a class="source-link" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">
              View at ${escapeHtml(eventItem.publisher)} <span aria-hidden="true">↗</span>
            </a>
          </div>
        </article>
      `;
    })
    .join("");
}

function updateFreshness(feed) {
  if (feed.collection_status === "not_connected_to_publication") {
    feedFreshness.textContent =
      "Feed status: collector data is not connected to approved publication.";
    return;
  }
  if (!feed.last_successful_collection) {
    feedFreshness.textContent =
      "Feed status: no successful collection time is available.";
    return;
  }

  const collectedAt = new Date(feed.last_successful_collection);
  if (Number.isNaN(collectedAt.getTime())) {
    feedFreshness.textContent = "Feed status: collection time is invalid.";
    return;
  }

  const staleAfterDays = 3;
  const ageInDays = (Date.now() - collectedAt.getTime()) / 86_400_000;
  const formattedTime = new Intl.DateTimeFormat("en", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(collectedAt);
  const staleNotice =
    ageInDays > staleAfterDays ? " · Update may be delayed" : "";
  const partialNotice =
    feed.collection_status === "partial"
      ? `Partial collection (${feed.sources_succeeded ?? 0}/${feed.sources_total ?? 0} sources)`
      : "Successful collection";
  feedFreshness.textContent = `${partialNotice}: ${formattedTime}${staleNotice}`;
}

async function loadFeed() {
  try {
    const response = await fetch("./events.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Feed request failed with status ${response.status}`);
    }

    const feed = await response.json();
    if (
      feed.schema_version !== 1 ||
      !Array.isArray(feed.items) ||
      !["editorial_pipeline_pending", "live", "metadata_roundup"].includes(
        feed.publication_status,
      )
    ) {
      throw new Error("Feed metadata does not match the expected public schema");
    }

    updateFreshness(feed);
    const candidateCount = feed.items.filter(
      (eventItem) => eventItem.review_state === "candidate",
    ).length;
    headlineCount.textContent = `${candidateCount} collected event${candidateCount === 1 ? "" : "s"} · unreviewed`;
    events = feed.items.filter(
      (eventItem) =>
        (eventItem.review_state === "candidate" ||
          (eventItem.review_state === "approved" &&
            typeof eventItem.summary === "string" &&
            eventItem.summary.trim())) &&
        typeof eventItem.title === "string" &&
        typeof eventItem.publisher === "string" &&
        Array.isArray(eventItem.tags) &&
        eventItem.tags.every((tag) => typeof tag === "string") &&
        Array.isArray(eventItem.location_groups) &&
        LOCATION_LABELS[eventItem.location] &&
        safeSourceUrl(eventItem.source_url),
    );
    renderEvents();
  } catch {
    feedError = true;
    feedFreshness.textContent =
      "Feed status: unable to load publication data.";
    setFeedMessage({
      label: "Feed temporarily unavailable",
      heading: "We couldn't load the events collection.",
      description:
        "Please try again later. If the problem continues, the publication feed may need attention.",
      foot: "PUBLICATION DATA UNAVAILABLE",
    });
    filterStatus.textContent = "The events feed could not be loaded.";
  } finally {
    storyList.setAttribute("aria-busy", "false");
  }
}

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    selectedLocation = button.dataset.location;
    filterButtons.forEach((filterButton) => {
      const active = filterButton === button;
      filterButton.classList.toggle("is-active", active);
      filterButton.setAttribute("aria-pressed", String(active));
    });
    renderEvents();
  });
});

loadFeed();
