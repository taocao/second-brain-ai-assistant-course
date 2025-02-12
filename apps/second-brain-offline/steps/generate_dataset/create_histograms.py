from io import BytesIO

import matplotlib.pyplot as plt
from PIL import Image
from typing_extensions import Annotated
from zenml import ArtifactConfig, step

from second_brain_offline.domain import Document


@step
def create_histograms(
    documents: list[Document],
) -> Annotated[Image.Image, ArtifactConfig(name="histogram_chart")]:
    """Create histograms showing content length and quality score distributions.

    Args:
        documents: List of Document objects containing content and quality scores

    Returns:
        PIL.Image: Combined histogram chart showing both distributions
    """

    # Extract content lengths and quality scores
    content_lengths = [len(doc.content) for doc in documents]
    quality_scores = [
        doc.content_quality_score
        for doc in documents
        if doc.content_quality_score is not None
    ]

    # Create a figure with two subplots with a light background style
    plt.style.use("default")
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Plot content length histogram with darker blue for better contrast
    ax1.hist(content_lengths, bins=50, color="#1E5AA8", alpha=0.8, edgecolor="black")
    ax1.set_title("Distribution of Content Lengths", fontsize=14, pad=15)
    ax1.set_xlabel("Content Length (characters)", fontsize=12)
    ax1.set_ylabel("Frequency", fontsize=12)
    ax1.tick_params(labelsize=10)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)

    # Plot quality score histogram with darker green for better contrast
    ax2.hist(quality_scores, bins=20, color="#2E7D32", alpha=0.8, edgecolor="black")
    ax2.set_title("Distribution of Quality Scores", fontsize=14, pad=15)
    ax2.set_xlabel("Quality Score", fontsize=12)
    ax2.set_ylabel("Frequency", fontsize=12)
    ax2.tick_params(labelsize=10)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # Add a super title
    fig.suptitle("Document Analysis", fontsize=16, y=1.02)

    # Adjust layout with more space
    plt.tight_layout(pad=2.0)

    # Convert matplotlib figure to PIL Image with higher DPI
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
    buf.seek(0)
    histogram_chart = Image.open(buf)

    # Close matplotlib figure to free memory
    plt.close(fig)

    return histogram_chart
