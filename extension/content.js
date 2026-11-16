// Раз на 3 секунди читає поточний трек/відео зі сторінки
(() => {
  const isMusic = location.hostname === "music.youtube.com";

  function videoId() {
    if (location.pathname.startsWith("/shorts/")) {
      return location.pathname.split("/")[2] || "";
    }
    return new URL(location.href).searchParams.get("v") || "";
  }

  function snapshot() {
    const md = navigator.mediaSession && navigator.mediaSession.metadata;
    const video =
      document.querySelector("video.html5-main-video") || document.querySelector("video");
    if (!md || !md.title || !video) return null;

    const id = videoId();
    let cover = "";
    let url = location.href;

    if (isMusic) {
      const art = md.artwork && md.artwork.length ? md.artwork[md.artwork.length - 1].src : "";
      cover = art.startsWith("http") ? art : "";
      if (id) url = `https://music.youtube.com/watch?v=${id}`;
    } else {
      // на YouTube metadata лишається в пам'яті й поза відео — перевіряємо адресу
      if (!id) return null;
      cover = `https://i.ytimg.com/vi/${id}/hqdefault.jpg`;
      url = `https://www.youtube.com/watch?v=${id}`;
    }

    return {
      source: isMusic ? "ytmusic" : "youtube",
      title: md.title,
      artist: md.artist || "",
      album: md.album || "",
      cover,
      url,
      playing: !video.paused && !video.ended,
      position: video.currentTime || 0,
      duration: isFinite(video.duration) ? video.duration : 0,
    };
  }

  setInterval(() => {
    const data = snapshot();
    if (data) chrome.runtime.sendMessage(data);
  }, 3000);
})();
