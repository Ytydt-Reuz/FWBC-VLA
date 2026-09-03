(function () {
  const copyButton = document.getElementById("copy-bibtex");
  const bibtex = document.getElementById("bibtex-code");
  const status = document.getElementById("copy-status");

  if (!copyButton || !bibtex || !status) {
    return;
  }

  copyButton.addEventListener("click", async () => {
    const text = bibtex.textContent.trim();

    try {
      await navigator.clipboard.writeText(text);
      status.textContent = "Copied.";
    } catch (error) {
      status.textContent = "Copy failed. Select the BibTeX text manually.";
    }

    window.setTimeout(() => {
      status.textContent = "";
    }, 2400);
  });
})();
