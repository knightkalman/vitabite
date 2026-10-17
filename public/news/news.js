const CATEGORY_LABELS = {
  scientific: "Scientific research",
  consumer_goods: "Consumer goods",
  nutrients: "Nutrients",
  medication: "Medication",
};

const storyList = document.querySelector("#story-list");
const feedMessage = document.querySelector("#feed-message");
const feedFreshness = document.querySelector("#feed-freshness");
const filterStatus = document.querySelector("#filter-status");
const filterButtons = [...document.querySelectorAll("[data-category]")];
let stories = [];
let selectedCategory = "all";
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

function renderStories() {
  if (feedError) {
    return;
  }
  const visibleStories = stories.filter(
    (story) =>
      selectedCategory === "all" || story.category === selectedCategory,
  );

  filterStatus.textContent =
    visibleStories.length === 1
      ? "1 story shown."
      : `${visibleStories.length} stories shown.`;

  if (visibleStories.length === 0) {
    if (stories.length === 0) {
      setFeedMessage({
        label: "A thoughtful start",
        heading: "Stories will find their place here.",
        description:
          "Once the summary and editorial review stages are connected, this space will share concise, source-linked longevity news. Until then, there are no approved articles to display.",
        foot: "NO APPROVED STORIES YET",
      });
    } else {
      setFeedMessage({
        label: "A quieter corner",
        heading: "No stories in this category yet.",
        description:
          "Try another topic to browse the approved stories currently in the collection.",
        foot: CATEGORY_LABELS[selectedCategory]?.toUpperCase() ?? "NO STORIES",
      });
    }
    return;
  }

  storyList.innerHTML = visibleStories
    .map((story) => {
      const sourceUrl = safeSourceUrl(story.source_url);
      if (!sourceUrl) {
        return "";
      }
      const tags = (story.tags ?? [])
        .map((tag) => `<span class="story-tag">${escapeHtml(tag.replaceAll("_", " "))}</span>`)
        .join("");
      const author = story.author
        ? `<span>${escapeHtml(story.author)}</span>`
        : "";
      const evidence = story.evidence_notes
        ? `<p class="story-evidence">${escapeHtml(story.evidence_notes)}</p>`
        : "";
      const publicationDate = displayDate(
        story.publication_date,
        story.publication_date_precision,
        story.publication_date_raw,
      );

      return `
        <article class="story-card">
          <div class="story-meta">
            <span class="story-category">${escapeHtml(CATEGORY_LABELS[story.category] ?? "News")}</span>
            <span>${escapeHtml(publicationDate)}</span>
            <span>${escapeHtml(story.publisher)}</span>
            ${author}
          </div>
          <div>
            <h3>${escapeHtml(story.title)}</h3>
            <p class="story-summary">${escapeHtml(story.summary)}</p>
            ${evidence}
            <div class="story-tags" aria-label="Story tags">${tags}</div>
            <a class="source-link" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">
              Read at ${escapeHtml(story.publisher)} <span aria-hidden="true">↗</span>
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
  feedFreshness.textContent = `Last successful collection: ${formattedTime}${staleNotice}`;
}

async function loadFeed() {
  try {
    const response = await fetch("./news.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`Feed request failed with status ${response.status}`);
    }

    const feed = await response.json();
    if (
      feed.schema_version !== 1 ||
      !Array.isArray(feed.items) ||
      !["editorial_pipeline_pending", "live"].includes(feed.publication_status)
    ) {
      throw new Error("Feed metadata does not match the expected public schema");
    }

    updateFreshness(feed);
    stories = feed.items.filter(
      (story) =>
        story.review_state === "approved" &&
        typeof story.summary === "string" &&
        story.summary.trim() &&
        typeof story.title === "string" &&
        typeof story.publisher === "string" &&
        Array.isArray(story.tags) &&
        story.tags.every((tag) => typeof tag === "string") &&
        CATEGORY_LABELS[story.category] &&
        safeSourceUrl(story.source_url),
    );
    renderStories();
  } catch {
    feedError = true;
    feedFreshness.textContent =
      "Feed status: unable to load publication data.";
    setFeedMessage({
      label: "Feed temporarily unavailable",
      heading: "We couldn't load the news collection.",
      description:
        "Please try again later. If the problem continues, the publication feed may need attention.",
      foot: "PUBLICATION DATA UNAVAILABLE",
    });
    filterStatus.textContent = "The news feed could not be loaded.";
  } finally {
    storyList.setAttribute("aria-busy", "false");
  }
}

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    selectedCategory = button.dataset.category;
    filterButtons.forEach((filterButton) => {
      const active = filterButton === button;
      filterButton.classList.toggle("is-active", active);
      filterButton.setAttribute("aria-pressed", String(active));
    });
    renderStories();
  });
});

loadFeed();
