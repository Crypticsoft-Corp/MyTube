
fetch('videos.html')
  .then(response => response.text())
  .then(data => {
    const tempElement = document.createElement('div');
    tempElement.innerHTML = data;

    const videoButtons = Array.from(tempElement.querySelectorAll('#videos a'));

    if (videoButtons.length >= 3) {
      const uniqueButtons = Array.from(new Set(videoButtons));

      if (uniqueButtons.length >= 3) {
        const shuffledButtons = uniqueButtons.sort(() => Math.random() - 0.5);
        const randomButtons = shuffledButtons.slice(0, 3);

        const videosNav = document.getElementById('videos-nav');
        randomButtons.forEach(button => {
          const paragraph = document.createElement('p');
          paragraph.appendChild(button.cloneNode(true));
          videosNav.appendChild(paragraph);
        });
      } else {
        console.error('Not enough unique buttons in the "videos.html" page.');
      }
    } else {
      console.error('Not enough buttons in the "videos.php" page.');
    }
  })
  .catch(error => console.error('Error fetching videos.php:', error));
